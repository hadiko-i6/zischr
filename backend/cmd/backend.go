//
// Copyright (C) 2018 Christian Schwarz
//
// This work is open source software, licensed under the terms of the
// MIT license as described in the LICENSE file in the top-level directory.


package cmd

import (
	"github.com/hadiko-i6/i6getraenkeabrechnungssystem3000/backend/db"
	"github.com/hadiko-i6/i6getraenkeabrechnungssystem3000/backend/rpc"
	"log"
	"golang.org/x/net/context"
	"errors"
	"time"
	"sync"
	"github.com/satori/go.uuid"
	"fmt"
)

type TerminalState struct {
	UUID  uuid.UUID
	PendingTransactions []db.Transaction
	CashInScanReceived bool
	LastScanError error
}

func (ts *TerminalState) UpdateUUID() {
	var err error
	ts.UUID, err = uuid.NewV4()
	if err != nil {
		panic(err)
	}
}

type Backend struct {
	db            db.DB
	terminalsLock sync.Mutex
	terminals     map[string]*TerminalState
}

func NewBackend(useDB db.DB) *Backend {
	return &Backend{
		db:        useDB,
		terminals: make(map[string]*TerminalState),
	}
}

func (b *Backend) lazyTerminalState(terminalID string) (*TerminalState) {
	po, ok := b.terminals[terminalID]
	if !ok || po == nil {
		po = &TerminalState{
			PendingTransactions: make([]db.Transaction, 0, 10),
		}
		po.UpdateUUID()
		b.terminals[terminalID] = po
		return po
	}
	return po
}

func (b *Backend) resetTerminalState(terminalID string) {
	delete(b.terminals, terminalID)
}

func (b *Backend) GetState(ctx context.Context, req *rpc.TerminalStateRequest) (*rpc.TerminalStateResponse, error) {

	if req.TerminalID == "" {
		return nil, errors.New("TerminalID missing")
	}

	res := &rpc.TerminalStateResponse{}

	accounts, err := b.db.Accounts()
	if err != nil {
		log.Panicf("db.Accounts() error: %s", err)
	} else {
		res.Accounts = make([]*rpc.TerminalStateResponse_Account, len(accounts))
		for i, a := range accounts {
			var balance db.Money
			for _, t := range a.Transactions {
				balance = balance.Add(t.Amount)
			}
			sortKey := a.SortKey
			if sortKey == "" {
				sortKey = a.ID
			}
			res.Accounts[i] = &rpc.TerminalStateResponse_Account{
				a.ID, a.DisplayName, balance.Cents(), sortKey,
			}
		}
	}

	b.terminalsLock.Lock()
	defer b.terminalsLock.Unlock()
	ts := b.lazyTerminalState(req.TerminalID)

	res.UUID = ts.UUID.String()
	res.CashInScanReceived = ts.CashInScanReceived
	if ts.LastScanError != nil {
		res.LastScanError = ts.LastScanError.Error()
	}

	var pendingTotal db.Money
	res.PendingOrders = make([]*rpc.TerminalStateResponse_Order, len(ts.PendingTransactions))
	for i, p := range ts.PendingTransactions {
		pendingTotal = pendingTotal.Add(p.Amount.Negate())
		res.PendingOrders[i] = &rpc.TerminalStateResponse_Order{
			p.Description,
			p.Amount.Negate().Cents(), // price is the negative tx amount
			p.NeedsReview,
		}
	}
	res.PendingOrdersTotal = pendingTotal.Cents()

	return res, nil
}


func (b *Backend) Abort(ctx context.Context, req *rpc.AbortRequest) (*rpc.AbortResponse, error) {
	if req.TerminalID == "" {
		return nil, errors.New("TerminalID missing")
	}
	b.terminalsLock.Lock()
	defer b.terminalsLock.Unlock()
	b.resetTerminalState(req.TerminalID)
	return &rpc.AbortResponse{}, nil
}

func (b *Backend) Buy(ctx context.Context, req *rpc.TerminalBuyRequest) (*rpc.TerminalBuyResponse, error) {

	if req.TerminalID == "" {
		return &rpc.TerminalBuyResponse{"TerminalID missing"}, nil
	}
	if req.AccountID == "" {
		return &rpc.TerminalBuyResponse{"TerminalID missing"}, nil
	}

	b.terminalsLock.Lock()
	defer b.terminalsLock.Unlock()

	ts := b.lazyTerminalState(req.TerminalID)

	if ts.UUID.String() != req.UUID {
		log.Printf("UUID mismatch: server state '%s' != request '%s'", ts.UUID, req.UUID)
		return &rpc.TerminalBuyResponse{"UUID mismatch"}, nil
	}

	inputErr, err := b.db.CommitTransactions(req.AccountID, ts.PendingTransactions)
	if err != nil {
		if inputErr {
			log.Printf("input error on committing pending order: %s", err)
			return nil, err
		} else {
			log.Panicf("database error commmitting pending order: %s", err)
		}
	} else {
		log.Println("committed pending orders, resetting pending orders list")
		b.terminals[req.TerminalID] =  nil
	}
	return &rpc.TerminalBuyResponse{}, nil
}

func TransactionFromProduct(product db.Product, date time.Time) db.Transaction {
	return db.Transaction{
		date,
		product.DisplayName,
		product.ID,
		product.UnitPrice.Negate(),
		product.NotInventoried,
	}
}

func CashInTransaction(amount db.Money, date time.Time) db.Transaction {
	return db.Transaction{
		date,
		"Cash-In",
		"",
		amount,
		false,
	}
}

const (
	PRODUCT_ID_MAGIC_CASHIN = "Magic:CashIn"
)

func (b *Backend) Scan(ctx context.Context, req *rpc.TerminalScanRequest) (res *rpc.TerminalScanResponse, err error) {

	if req.TerminalID == "" {
		return nil, errors.New("TerminalID missing")
	}

	b.terminalsLock.Lock()
	defer b.terminalsLock.Unlock()

	t := b.lazyTerminalState(req.TerminalID)
	t.LastScanError = nil

	if req.ProductID == PRODUCT_ID_MAGIC_CASHIN {
		t.CashInScanReceived = true
		t.UpdateUUID()
		return &rpc.TerminalScanResponse{}, nil
	}

	prod, err := b.db.GetOrDeriveProduct(req.ProductID)
	if err == db.DBDeriveProductError {
		err = fmt.Errorf("scan of product ID '%s' failed: %s", req.ProductID, err)
		t.LastScanError = err
		return &rpc.TerminalScanResponse{err.Error()}, nil
	} else if err != nil {
		log.Panic(err.Error())
	}
	t.PendingTransactions = append(t.PendingTransactions, TransactionFromProduct(prod, time.Now()))
	t.UpdateUUID()

	return &rpc.TerminalScanResponse{}, nil

}

func (b *Backend) AddDepositOrder(ctx context.Context, req *rpc.TerminalAddDepositOrderRequest) (*rpc.TerminalAddDepositOrderResponse, error) {

	b.terminalsLock.Lock()
	defer b.terminalsLock.Unlock()

	t := b.lazyTerminalState(req.TerminalID)

	tx := CashInTransaction(db.NewMoney(req.CashInAmount), time.Now())
	t.PendingTransactions = append(t.PendingTransactions, tx)


	t.CashInScanReceived = false

	t.UpdateUUID()
	return &rpc.TerminalAddDepositOrderResponse{}, nil
}
