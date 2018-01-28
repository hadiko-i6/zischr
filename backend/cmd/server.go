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
)

var argsServer struct {
	port string
}

func init() {
	RootCmd.AddCommand(serverCmd)
	serverCmd.Flags().StringVar(&argsServer.port, "listen", ":8080", "")
}

// serverCmd represents the server command
var serverCmd = &cobra.Command{
	Use:   "server",
	Short: "Run backend server.",
	Run: func(cmd *cobra.Command, args []string) {

		db, err := NewFSDB(argsGlobal.dbDir)
		if err != nil {
			log.Fatal(err)
		}

		lis, err := net.Listen("tcp", argsServer.port)
		if err != nil {
			log.Fatalf("failed to listen: %v", err)
		}
		log.Printf("listening: %s", argsServer.port)

		grpcServer := grpc.NewServer()
		srv := NewBackend(db)
		rpc.RegisterTerminalBackendServer(grpcServer, srv)
		grpcServer.Serve(lis)
	},
}
