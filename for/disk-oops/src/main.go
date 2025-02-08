package main

import (
	"flag"
	"log/slog"
	"math/rand"
	"os"
	"path/filepath"
	"sync"
	"time"
)

var (
	sourceDir = flag.String("source", "", "Source directory")
	targetDir = flag.String("target", "", "Target directory")
	blockSize = flag.Int("block-size", 4096, "Block size")
	minSleep  = flag.Int("min-sleep", 10, "Minimum sleep time (ms)")
	maxSleep  = flag.Int("max-sleep", 100, "Maximum sleep time (ms)")
)

func getFiles(dir string) ([]string, error) {
	ents, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}

	var filenames []string

	for _, ent := range ents {
		if ent.IsDir() {
			subdir := dir + "/" + ent.Name()
			subfiles, err := getFiles(subdir)
			if err != nil {
				return nil, err
			}
			filenames = append(filenames, subfiles...)
		} else {
			filenames = append(filenames, dir+"/"+ent.Name())
		}
	}

	return filenames, nil
}

func copyFile(
	filename string,
	targetName string,
	blockSize int,
	sleepTime time.Duration,
) error {
	dirName := filepath.Dir(targetName)
	if err := os.MkdirAll(dirName, 0755); err != nil {
		return err
	}

	source, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer source.Close()

	target, err := os.Create(targetName)
	if err != nil {
		return err
	}
	defer target.Close()

	buf := make([]byte, blockSize)

	frags := 0

	for {
		n, err := source.Read(buf)
		if err != nil {
			break
		}

		_, err = target.Write(buf[:n])
		if err != nil {
			return err
		}

		time.Sleep(sleepTime)
		frags++
	}

	slog.Info("copied", "filename", filename, "target", targetName, "fragments", frags)

	return nil
}

func main() {
	flag.Parse()

	var (
		filenames []string
		err       error
	)

	// get a list of all files recursively in the source directory
	filenames, err = getFiles(*sourceDir)
	if err != nil {
		panic(err)
	}

	errors := make(chan error)

	wg := sync.WaitGroup{}

	// Copy files from source to target directory in chunks with
	// random sleep between copies to fragment the files
	for _, filename := range filenames {
		wg.Add(1)
		go func() {
			defer wg.Done()
			targetName, err := filepath.Rel(*sourceDir, filename)
			if err != nil {
				errors <- err
			}

			sleepTime := rand.Intn(*maxSleep-*minSleep) + *minSleep

			err = copyFile(
				filename,
				filepath.Join(*targetDir, targetName),
				*blockSize,
				time.Duration(sleepTime)*time.Millisecond,
			)
			if err != nil {
				errors <- err
			}
		}()
	}

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		slog.Info("done")
	case err := <-errors:
		slog.Error("error", "error", err)
	}
}
