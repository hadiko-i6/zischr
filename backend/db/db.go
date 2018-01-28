package db

import "time"

type DB interface {
	GetOrDeriveProduct(productID string) (prod Product, err error)
	CommitTransactions(accountID string, txes []Transaction) (inputError bool, err error)
	Accounts() (accounts []Account, err error)
}

type Product struct {
	DisplayName    string
	ID             string
	UnitPrice      Money
	NotInventoried bool
}

type Money struct {
	cents int32 // FIXME not persistent
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
	NeedsReview bool
}


type Account struct {
	// ID is the filename, should not be in JSON of FSDB
	ID                 string `json:"-"`
	DisplayName        string
	Transactions       []Transaction
}
