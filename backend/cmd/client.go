//
// Copyright (C) 2018 Christian Schwarz
//
// This work is open source software, licensed under the terms of the
// MIT license as described in the LICENSE file in the top-level directory.


package cmd

import (
	"github.com/spf13/cobra"
	"log"
	"github.com/hadiko-i6/zischr/backend/rpc"
	"google.golang.org/grpc"
	"context"
	"github.com/kr/pretty"
	"time"
)

var argsClient struct {
	terminalBackendEndpoint string
	terminalID string
}

var clientCmd = &cobra.Command{
	Use:   "client [scan PRODUCT_ID]",
	Short: "Not the real frontend.",
	Run:  doClient,
}

func init() {
	RootCmd.AddCommand(clientCmd)

	clientCmd.PersistentFlags().StringVar(&argsClient.terminalBackendEndpoint, "endpoint", ":8080", "Dial()able address of the terminal backend")
	clientCmd.PersistentFlags().StringVar(&argsClient.terminalID, "terminalID", "", "")
}

func doClient(cmd *cobra.Command, args []string) {

	if argsClient.terminalID == "" {
		log.Println("terminal ID not provided")
		log.Fatal(cmd.Usage())
	}

	if len(args) < 1 {
		log.Println("must provide a verb as first positional argument")
		log.Fatal(cmd.Usage())
	}

	gclient, err := grpc.Dial(argsClient.terminalBackendEndpoint, grpc.WithInsecure())
	if err != nil {
		log.Fatal(err)
	}
	defer gclient.Close()

	client := rpc.NewTerminalBackendClient(gclient)

	tid := argsClient.terminalID
	verb := args[0]

	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)

	switch verb {
	case "scan":
		req := rpc.TerminalScanRequest{tid, args[1]}
		res, err := client.Scan(ctx, &req)
		if err != nil {
			log.Fatal(err)
		}
		pretty.Println(res)

	case "buy":
		res, err := client.Buy(ctx, &rpc.TerminalBuyRequest{tid, args[1], args[2]})
		if err != nil {
			log.Fatal(err)
		}
		pretty.Println(res)

	case "getState":
		res, err := client.GetState(ctx, &rpc.TerminalStateRequest{tid})
		if err != nil {
			log.Fatal(err)
		}
		pretty.Println(res)

	default:
		log.Printf("unknown verb '%s'", verb)
		log.Fatal(cmd.Usage())
	}

}