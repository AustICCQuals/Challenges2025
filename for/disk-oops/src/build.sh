#!/usr/bin/env bash

set -ex

rm -f $(tinyrange env build-dir)/persist/disk-oops_persist.img

go build -o disk-oops main.go

tinyrange login -c build.yaml --rebuild

# Copy the disk image to the current directory
cp $(tinyrange env build-dir)/persist/disk-oops_persist.img .

cp disk-oops_persist.img disk.img

# Replace the first 2 blocks with random data
dd if=/dev/urandom of=disk.img bs=4096 count=2 conv=notrunc

gzip disk.img