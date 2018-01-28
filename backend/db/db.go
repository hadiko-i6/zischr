package db

import (
	"time"
	"encoding/json"
)

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
	cents int32
}

func NewMoney(cents int32) Money {
	return Money{cents}
}

func (m *Money) UnmarshalJSON(data []byte) error {
	return json.Unmarshal(data, &m.cents)
}

func (m Money) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.cents)
}

func (m Money) Cents() int32 {
	return int32(m.cents)
}

func (m Money) Add(a Money) Money {
	newCents := m.cents + a.cents
	switch {
	case a.cents < 0:
		if !(newCents < m.cents) {
			panic("subtraction underflowed")
		}
	case a.cents > 0:
		if !(newCents > m.cents) {
			panic("addition overflowed")
		}
	}
	return Money{newCents}
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
