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
)

type Backend struct {
	db                      db.DB
	pendingLock             sync.RWMutex
	pendingOrdersByTerminal map[string]*db.PendingOrder
}

func NewBackend(useDB db.DB) *Backend {
	return &Backend{
		db: useDB,
		pendingOrdersByTerminal: make(map[string]*db.PendingOrder),
	}
}

func (b *Backend) lazyPendingOrders(terminalID string) (*db.PendingOrder) {
	po, ok := b.pendingOrdersByTerminal[terminalID]
	if !ok || po == nil {
		po = &db.PendingOrder{
			LastModified: time.Now(),
			Products: make([]db.Product, 0, 10),
		}
		b.pendingOrdersByTerminal[terminalID] = po
		return po
	}
	return po
}

func (b *Backend) resetPendingOrders(terminalID string) {
	delete(b.pendingOrdersByTerminal, terminalID)
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
			for _, t := range a.FinishedTransactions {
				balance.Add(t.Amount)
			}
			res.Accounts[i] = &rpc.TerminalStateResponse_Account{
				a.ID, a.DisplayName, balance.Cents(),
			}
		}
	}

	b.pendingLock.RLock()
	defer b.pendingLock.RUnlock()
	po := b.lazyPendingOrders(req.TerminalID)
	var pendingTotal db.Money
	res.PendingOrders = make([]*rpc.TerminalStateResponse_Order, len(po.Products))
	for i, p := range po.Products {
		pendingTotal.Add(p.UnitPrice)
		res.PendingOrdersContainsNotInventoried = res.PendingOrdersContainsNotInventoried || p.NotInventoried
		res.PendingOrders[i] = &rpc.TerminalStateResponse_Order{
			p.DisplayName, p.UnitPrice.Cents(), p.NotInventoried,
		}
	}
	res.PendingOrdersTotal = pendingTotal.Cents()

	return res, nil
}


func (b *Backend) Abort(ctx context.Context, req *rpc.AbortRequest) (*rpc.AbortResponse, error) {
	if req.TerminalID == "" {
		return nil, errors.New("TerminalID missing")
	}
	b.pendingLock.Lock()
	defer b.pendingLock.Unlock()
	b.resetPendingOrders(req.TerminalID)
	return &rpc.AbortResponse{}, nil
}

func (b *Backend) Buy(ctx context.Context, req *rpc.TerminalBuyRequest) (*rpc.TerminalBuyResponse, error) {

	if req.TerminalID == "" {
		return nil, errors.New("TerminalID missing")
	}
	if req.AccountID == "" {
		return nil, errors.New("TerminalID missing")
	}

	b.pendingLock.Lock()
	defer b.pendingLock.Unlock()

	po := b.lazyPendingOrders(req.TerminalID)
	inputErr, err := b.db.CommitPendingOrder(req.AccountID, po)
	if err != nil {
		if inputErr {
			log.Printf("input error on committing pending order: %s", err)
			return nil, err
		} else {
			log.Panicf("database error commmitting pending order: %s", err)
		}
	} else {
		log.Println("committed pending orders, resetting pending orders list")
		b.pendingOrdersByTerminal[req.TerminalID] =  nil
	}
	return &rpc.TerminalBuyResponse{}, nil
}

func (b *Backend) Scan(ctx context.Context, req *rpc.TerminalScanRequest) (res *rpc.TerminalScanResponse, err error) {

	if req.TerminalID == "" {
		return nil, errors.New("TerminalID missing")
	}

	prod, err := b.db.GetOrDeriveProduct(req.ProductID)
	if err != nil {
		log.Panicf("could not get product: %s", err)
	}

	b.pendingLock.Lock()
	defer b.pendingLock.Unlock()

	po := b.lazyPendingOrders(req.TerminalID)
	po.LastModified = time.Now()
	po.Products = append(po.Products, prod)

	return &rpc.TerminalScanResponse{}, nil

}

func (b *Backend) AddDepositOrder(context.Context, *rpc.TerminalAddDepositOrderRequest) (*rpc.TerminalAddDepositOrderResponse, error) {
	panic("implement me")
}
