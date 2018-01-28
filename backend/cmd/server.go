//
// Copyright (C) 2018 Christian Schwarz
//
// This work is open source software, licensed under the terms of the
// MIT license as described in the LICENSE file in the top-level directory.

package cmd

import (
	"github.com/hadiko-i6/i6getraenkeabrechnungssystem3000/backend/rpc"
	"log"
	"github.com/spf13/cobra"
	"net"
	"google.golang.org/grpc"
	"github.com/hadiko-i6/i6getraenkeabrechnungssystem3000/backend/db"
	"os/exec"
	"bytes"
	"fmt"
)

var argsServer struct {
	port              string
	postStoreHookPath string
}

func init() {
	RootCmd.AddCommand(serverCmd)
	serverCmd.Flags().StringVar(&argsServer.port, "listen", ":8080", "")
	serverCmd.Flags().StringVar(&argsServer.postStoreHookPath, "post-store-hook", "", "path to post-store-hook, see backend/db/fsdb_git_hook.sh.example")
}

// serverCmd represents the server command
var serverCmd = &cobra.Command{
	Use:   "server",
	Short: "Run backend server.",
	Run: func(cmd *cobra.Command, args []string) {

		fsdb, err := db.NewFSDB(argsGlobal.dbDir)
		if err != nil {
			log.Fatal(err)
		}

		if (argsServer.postStoreHookPath) != "" {

			postStoreHook := func() {

				cmd := exec.Command(argsServer.postStoreHookPath)
				cmd.Env = []string{
					fmt.Sprintf("DBDIR=%s", argsGlobal.dbDir),
				}
				cmd.Dir = argsGlobal.dbDir

				var outbuf bytes.Buffer
				cmd.Stdout = &outbuf
				cmd.Stderr = &outbuf

				runErr := cmd.Run()
				if runErr != nil {
					exitErr, ok := runErr.(*exec.ExitError)
					if !ok {
						log.Printf("fsdb hook error: %s", runErr)
					} else {
						log.Printf("fsdb hook ExitError: %s", exitErr)
					}
				}
				log.Printf("fsdb hook output; %s", outbuf.String())
			}

			fsdb.SetPostChangeHook(postStoreHook)

		}

		lis, err := net.Listen("tcp", argsServer.port)
		if err != nil {
			log.Fatalf("failed to listen: %v", err)
		}
		log.Printf("listening: %s", argsServer.port)

		grpcServer := grpc.NewServer()
		srv := NewBackend(fsdb)
		rpc.RegisterTerminalBackendServer(grpcServer, srv)
		grpcServer.Serve(lis)
	},
}
