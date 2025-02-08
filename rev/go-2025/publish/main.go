package main

import (
	"flag"
	"os"
)

var (
	input  = flag.String("input", "", "The file to read as input")
	output = flag.String("output", "", "The file to write as output")
)

func main() {
	flag.Parse()

	if *input == "" || *output == "" {
		flag.Usage()
		os.Exit(1)
	}

	// Enable the brand new go2025 feature.
	os.EnableVirusScanning()

	// Read the input file.
	inputFile, err := os.ReadFile(*input)
	if err != nil {
		panic(err)
	}

	// Write the output file.
	err = os.WriteFile(*output, inputFile, 0644)
	if err != nil {
		panic(err)
	}

	os.Exit(0)
}
