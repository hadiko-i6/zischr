//
// Copyright (C) 2018 Christian Schwarz
//
// This work is open source software, licensed under the terms of the
// MIT license as described in the LICENSE file in the top-level directory.

package db

import (
	"errors"
	"log"
	"regexp"
	"sync"
	"encoding/json"
	"os"
	"path"
	"strings"
	"fmt"
	"io/ioutil"
)

type FSDB struct {
	dbDir string

	lock         sync.RWMutex
	productsByID map[string]*Product
	accountsByID map[string]*Account

	postChangeHook func()
}


func (d *FSDB) SetPostChangeHook(hook func()) {
	d.lock.Lock()
	defer d.lock.Unlock()
	d.postChangeHook = hook
}

func (d *FSDB) deriveProduct(productID string) (*Product, error) {
	d.lock.Lock()
	defer d.lock.Unlock()

	var EANProductIDRegex *regexp.Regexp = regexp.MustCompile(`^EAN:([0-9])+$`)

	if !EANProductIDRegex.MatchString(productID) {
		return nil, errors.New("not an EAN ProductID")
	}
	return &Product{
		ID:             productID,
		DisplayName:    productID,
		NotInventoried: true,
	}, nil
}

func (d *FSDB) validateFilename(filename string) (error) {
	base := path.Base(filename)
	switch {
	case base != filename:
		return errors.New("filename must not be a path")
	case strings.HasPrefix(base, "."):
		return errors.New("file must not start with a '.'")
	case base == "." || base == "..":
		return errors.New("filename must not be '.' or '..'")
	}
	return nil
}

func (d *FSDB) validateAccountFilename(accountFilename string) (err error) {
	if err = d.validateFilename(accountFilename); err != nil {
		return err
	}
	if !strings.HasSuffix(path.Base(accountFilename), ".account.json") {
		return errors.New("filename must end with '.account.json'")
	}
	return nil
}

func (d *FSDB) persistAccount(account *Account) (err error) {
	log.Printf("persisting account '%s (%s)'", account.ID, account.DisplayName)
	return d.atomicallyPersistJSON(account, account.ID)
}

var DBInconsistentError = errors.New("database inconsistent")
var DBFSError = errors.New("database filesystem error")
var DBSerializationErrror = errors.New("database serialization error")

const PRODUCTS_FILE_FILENAME = "products.json"
const ATOMIC_SAVE_NEW_SUFFIX = ".fsdb.new"
const ATOMIC_SAVE_OLD_SUFFIX = ".fsdb.old"

func (d *FSDB) atomicallyPersistJSON(i interface{}, filename string) (err error) {

	if err = d.validateFilename(filename); err != nil {
		return err
	}

	newPath := path.Join(d.dbDir, filename + ATOMIC_SAVE_NEW_SUFFIX)
	bakPath := path.Join(d.dbDir, filename + ATOMIC_SAVE_OLD_SUFFIX)
	filePath := path.Join(d.dbDir, filename)

	// file must not exist
	newFile, err := os.OpenFile(newPath, os.O_WRONLY|os.O_EXCL|os.O_CREATE, 0600)
	if err != nil {
		log.Printf("cannot open new file '%s': %s", newFile, err)
		return DBFSError
	}
	defer newFile.Close()

	enc := json.NewEncoder(newFile)
	enc.SetIndent("", "  ")
	err = enc.Encode(i)
	if err != nil {
		log.Printf("cannot encode: %s", err)
		return DBSerializationErrror
	}

	if err = newFile.Sync(); err != nil {
		log.Printf("sync error: %s", err)
		return DBFSError
	}
	if err = newFile.Close(); err != nil {
		log.Printf("close error: %s", err)
		return DBFSError
	}

	return d.atomicallyReplaceFile(filePath, newPath, bakPath)
}

func (d *FSDB) atomicallyReplaceFile(filePath, newPath, bakPath string) (err error) {

	if err = os.Link(filePath, bakPath); err != nil {
		log.Printf("could not hard-link '%s' to '%s': %s", filePath, bakPath, err)
		return DBFSError
	}
	// On Linux, rename is atomic since we know tmpPath and newPath are on the same partition
	// (since they are in same dir)
	if err = os.Rename(newPath, filePath); err != nil {
		log.Printf("could not rename '%s' to '%s': %s", newPath, filePath, err)
		return DBFSError
	}
	if err = os.Remove(bakPath); err != nil {
		log.Printf("could not unlink backup file '%s': %s", bakPath, err)
		// return error anyways since otherwise the next attempt is inconsistent
		return DBFSError
	}

	defer func() {
		if r := recover(); r != nil {
			log.Printf("discarding panic by postChangeHook: %s", r)
		}
	}()
	if d.postChangeHook != nil {
		log.Println("running postChangeHook")
		d.postChangeHook()
		log.Println("finished running postChangeHook")
	}


	return nil
}

// filePath relative to dbDir
func (db *FSDB) isAtomicReplaceCorruptionArtifact(filePath string) bool {
	return strings.HasSuffix(filePath, ATOMIC_SAVE_OLD_SUFFIX) ||
		strings.HasSuffix(filePath, ATOMIC_SAVE_NEW_SUFFIX)
}

// mainFile relative to dbDir
func (db *FSDB) repairAtomicReplaceCorruption(mainFilePath string) (err error) {

	mainFilePath = path.Join(db.dbDir, mainFilePath)

	if db.isAtomicReplaceCorruptionArtifact(mainFilePath) {
		log.Panicf("corruption artifact passed as mainFilePath: %s", mainFilePath)
	}

	main, err := os.Stat(mainFilePath)
	if err != nil {
		return DBFSError
	}
	oldPath := mainFilePath + ATOMIC_SAVE_OLD_SUFFIX
	old, err := os.Stat(oldPath)
	if err != nil {
		if os.IsNotExist(err) {
			old = nil
		} else {
			return DBFSError
		}
	}
	newPath := mainFilePath + ATOMIC_SAVE_NEW_SUFFIX
	new, err := os.Stat(newPath)
	if err != nil {
		if os.IsNotExist(err) {
			new = nil
		} else {
			return DBFSError
		}
	}
	checkDir := func(stat os.FileInfo) (err error){
		if stat == nil {
			return nil
		}
		if main.IsDir() {
			log.Printf("%s is a directory")
			return DBInconsistentError
		}
		return nil
	}

	if err := checkDir(main); err != nil {
		return err
	}
	if err := checkDir(old); err != nil {
		return err
	}
	if err := checkDir(new); err != nil {
		return err
	}

	if new == nil && old == nil {
		// nothing to repair
		return nil
	}

	log.Printf("assessing corruption of '%s'", mainFilePath)

	if new == nil && old != nil {
		log.Printf("removing stale backup file %s", oldPath)
		if err := os.Remove(oldPath); err != nil {
			log.Printf("error: %s", err)
			return DBFSError
		}
		return nil
	}

	if new != nil && old != nil {
		log.Printf("assuming rename operation failed, complete it")
		if err := db.atomicallyReplaceFile(mainFilePath, newPath, oldPath); err != nil {
			log.Printf("error: %s", err)
			return err
		}
		return nil
	}
	if new != nil && old == nil {
		log.Printf("assuming started but uncommitted transaction: abort it")
		if err := os.Remove(newPath); err != nil {
			log.Println("error: %s", err)
			return DBFSError
		}
		return nil
	}

	return DBInconsistentError
}

func NewFSDB(dbDir string) (*FSDB, error) {

	db := &FSDB{
		dbDir: dbDir,
	}

	entries, err := ioutil.ReadDir(dbDir)
	if err != nil {
		log.Printf("cannot list dbDir '%s': %s", dbDir, err)
		return nil, DBFSError
	}

	// Load state from disk
	var productsFileInfo os.FileInfo
	accountsFileInfos := make([]os.FileInfo, 0, len(entries))
	for i := range entries {
		if entries[i].Name() == PRODUCTS_FILE_FILENAME {
			log.Printf("found products file: %s", entries[i].Name())
			if err := db.repairAtomicReplaceCorruption(entries[i].Name()); err != nil {
				log.Printf("error reparing products file corruption: %s", err)
				return nil, DBInconsistentError
			}
			productsFileInfo = entries[i]
			continue
		}
		if perr := db.validateAccountFilename(entries[i].Name()); perr == nil {
			log.Printf("found account filename: %s", entries[i].Name())
			if err := db.repairAtomicReplaceCorruption(entries[i].Name()); err != nil {
				log.Printf("error repairing account file: %s", err)
				return nil, DBInconsistentError
			}
			accountsFileInfos = append(accountsFileInfos, entries[i])
			continue
		}
		// check if it's a corruption artifact of an account where the main file was moved
		if db.isAtomicReplaceCorruptionArtifact(entries[i].Name()) {
			log.Panicf("found atomic replace corruption artifact: %s", entries[i].Name())
		}
		log.Printf("warning: unknown file %s in dbDir", entries[i].Name())
	}

	openAndUnmarshal := func(fi os.FileInfo, i interface{}) (err error) {
		p := path.Join(dbDir, fi.Name())
		f, err := os.Open(p)
		if err != nil {
			log.Printf("cannot open %s: %s", p, err)
			return DBFSError
		}
		defer f.Close()
		if err := json.NewDecoder(f).Decode(i); err != nil {
			log.Printf("cannot unmarshal %s: %s", p, err)
			return DBSerializationErrror
		}
		return nil
	}

	// load products
	if productsFileInfo == nil {
		return nil, errors.New(fmt.Sprintf("%s not found", PRODUCTS_FILE_FILENAME))
	}
	if err = openAndUnmarshal(productsFileInfo, &db.productsByID); err != nil {
		log.Printf("cannot unmarshal %s: %s", productsFileInfo.Name(), err)
		return nil, err
	}
	for pid, p := range db.productsByID {
		if p.ID != "" {
			log.Printf("Product.ID specified redundantly in object member 'ID' of product '%s'", pid)
			return nil, DBInconsistentError
		}
		p.ID = pid
	}

	// load accounts
	db.accountsByID = make(map[string]*Account)
	for _, afi := range accountsFileInfos {
		var account Account
		if err = openAndUnmarshal(afi, &account); err != nil {
			return nil, err
		}
		if account.ID != "" {
			log.Printf("account.ID set on dis for account %s", afi.Name())
			return nil, DBInconsistentError
		}
		account.ID = afi.Name()
		db.accountsByID[account.ID] = &account // TODO check excape analysis
	}

	return db, nil

}

var DBDeriveProductError = errors.New("cannot derive product")

func (db *FSDB) GetOrDeriveProduct(productID string) (prod Product, err error) {

	if len(productID) == 0 {
		return Product{}, DBDeriveProductError
	}

	db.lock.RLock()
	product, exists := db.productsByID[productID]
	db.lock.RUnlock()
	if !exists {
		log.Printf("deriving product from product ID: %s", productID)
		product, err = db.deriveProduct(productID)
		if err != nil {
			log.Printf("error deriving product from product ID: %s", err)
			return Product{}, DBDeriveProductError
		} else {
			log.Printf("adding product to products list")
			db.lock.Lock()
			defer db.lock.Unlock()
			db.productsByID[product.ID] = product
			if err = db.atomicallyPersistJSON(db.productsByID, PRODUCTS_FILE_FILENAME); err != nil {
				log.Println("failed to persist products list: %s", err)
				return Product{}, err
			}
		}
	}

	return *product, nil
}

func (db *FSDB) CommitTransactions(accountID string, transactions []Transaction) (inputError bool, err error) {
	db.lock.Lock()
	defer db.lock.Unlock()

	if transactions == nil {
		log.Panic("transactions is nil")
	}

	account, ok := db.accountsByID[accountID]
	if !ok {
		log.Printf("invalid account ID: %s", account)
		return true, errors.New("account does not exist")
	}

	// Copy transactions to provide rollback on error
	newTxes := make([]Transaction, len(transactions))
	for i, p := range transactions {
		var tx = p
		newTxes [i] = tx
	}

	// Atomically update transactions on disk
	prevFinishedTx := account.Transactions[:]
	account.Transactions = append(account.Transactions, newTxes...)
	err = db.persistAccount(account)
	if  err != nil {
		log.Printf("error persisting account '%s': %s", account.ID, err)
		log.Printf("rolling back to pre-transaction state")
		account.Transactions = prevFinishedTx
		return false, err
	}

	return false, nil
}

func (db *FSDB) Accounts() (accounts []Account, err error) {
	db.lock.RLock()
	defer db.lock.RUnlock()

	// Copy accounts list
	accounts = make([]Account, 0, len(db.accountsByID))
	for aid := range db.accountsByID {
		accounts = append(accounts, *db.accountsByID[aid])
	}

	return accounts, nil
}

func (db *FSDB) ProcessNeedsReviewTransactions() (err error) {
	db.lock.Lock()
	defer db.lock.Unlock()

	productWarnings := make(map[string]bool, len(db.productsByID))
	for _, a := range db.accountsByID {
		newTransactions := make([]Transaction, len(a.Transactions))
		containsUpdates := false
		for i := range a.Transactions {
			newTransactions[i] = a.Transactions[i] // copy
			tx := &newTransactions[i]
			if !tx.NeedsReview {
				continue
			}
			if tx.ProductIdentifier == "" {
				log.Printf("error: transaction with NeedsReview but no ProductIdentifier: Account=%s Date=%s", a.ID, tx.Date)
				return DBInconsistentError
			}
			product, ok := db.productsByID[tx.ProductIdentifier]
			if !ok {
				log.Printf("error: transaction with NeedsReview but unknown ProductIdentifier: Account=%s Date=%s", a.ID, tx.Date)
				return DBInconsistentError
			}
			if product.NotInventoried && !productWarnings[product.ID]{
				productWarnings[product.ID] = true
				log.Printf("product ID=%s is not inventoried", product.ID)
				continue
			}
			// not warning / aborting about products with Price == 0, this may make sense
			if tx.Amount != NewMoney(0) {
				log.Printf("error: transaction with NeedsReview but Amount != 0: Account=%s Date=%s Amount=%d", a.ID, tx.Date, tx.Amount)
				return DBInconsistentError
			}
			log.Printf("updating transaction: Account=%s Date=%s Amount=%s", a.ID, tx.Date, product.UnitPrice)
			tx.Amount = product.UnitPrice.Negate()
			tx.Description = product.DisplayName
			tx.NeedsReview = false
			containsUpdates = true
		}
		if !containsUpdates {
			continue
		}
		log.Printf("updated transactions in account %s, persisting to disk", a.ID)
		oldTransactions := a.Transactions
		a.Transactions = newTransactions
		if err := db.persistAccount(a); err != nil {
			log.Printf("error persisting account: '%s': %s", a.ID, err)
			log.Printf("rolling back to old transactions in memory: %s")
			a.Transactions = oldTransactions
			return err// we have not implemented rollback
		}
	}
	return nil
}