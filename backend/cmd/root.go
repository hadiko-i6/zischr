//
// Copyright (C) 2018 Christian Schwarz
//
// This work is open source software, licensed under the terms of the
// MIT license as described in the LICENSE file in the top-level directory.

package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var argsGlobal struct {
	dbDir string
}

var RootCmd = &cobra.Command{
	Use:   "backend",
	Short: "zischr backend",
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	if err := RootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() { 
	RootCmd.PersistentFlags().StringVar(&argsGlobal.dbDir, "dbdir", "", "path to database directory")
}
