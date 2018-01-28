package db

import "time"

// FIXME find better representation for this in cmd package
type PendingOrder struct {
	Products     []Product
	LastModified time.Time
}

type DB interface {
	GetOrDeriveProduct(productID string) (prod Product, err error)
	CommitPendingOrder(accountID string, po *PendingOrder) (inputError bool, err error)
	Accounts() (accounts []Account, err error)
}

type Product struct {
	DisplayName    string
	ID             string
	UnitPrice      Money
	NotInventoried bool
}

type Money struct {
	cents int32
}

func (m Money) Cents() int32 {
	return int32(m.cents)
}

func (m Money) Add(a Money) Money {
	return Money{m.cents + a.cents}
}

type Transaction struct {
	Date time.Time
	Description string
	ProductIdentifier string
	Amount Money
}

func TransactionFromProduct(product Product, date time.Time) Transaction {
	return Transaction{
		date,
		product.DisplayName,
		product.ID,
		product.UnitPrice,
	}
}

type Account struct {
	// ID is the filename, should not be in JSON of FSDB
	ID           string `json:"-"`
	DisplayName  string
	FinishedTransactions []Transaction
	ReviewTransactions []Transaction
}
