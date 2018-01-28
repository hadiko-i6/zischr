package db_test

import (
	"testing"
	"github.com/stretchr/testify/assert"
	"github.com/hadiko-i6/i6getraenkeabrechnungssystem3000/backend/db"
	"encoding/json"
	"fmt"
	"math"
)

func TestMoney_JSON(t *testing.T) {

	cents := []int32{-1,  10, 23, 0}

	for _, c := range cents {
		m := db.NewMoney(c)
		assert.Equal(t, c, m.Cents())
		j, err := json.Marshal(m)
		assert.NoError(t, err)
		assert.Equal(t, []byte(fmt.Sprintf("%d", c)), j)
		var dec db.Money
		err = json.Unmarshal(j, &dec)
		assert.NoError(t, err)
		assert.Equal(t, m, dec)
		assert.Equal(t, m.Cents(), dec.Cents())
	}

}

func TestMoney_Overflow(t *testing.T) {

	const MaxInt = int32(math.MaxInt32)
	const MinInt = int32(math.MinInt32)

	m := db.NewMoney(MaxInt)
	assert.Equal(t, MaxInt, m.Cents(), "MaxInt should be storable")
	assert.Panics(t, func() { m.Add(db.NewMoney(1)) }, "Overflow should panic")
	assert.Equal(t,int32(MaxInt-1), m.Add(db.NewMoney(-1)).Cents(), "MaxInt should be subtractable")

	m = db.NewMoney(MinInt)
	assert.Equal(t, MinInt, m.Cents(), "MinInt should be storable")
	assert.Panics(t, func() { m.Add(db.NewMoney(-1)) }, "Underflow should panic")
	assert.Equal(t,int32(MinInt+1), m.Add(db.NewMoney(1)).Cents(), "MinInt should be addable")

}
