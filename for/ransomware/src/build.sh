#!/usr/bin/env bash

set -ex

rm -f $(tinyrange env build-dir)/persist/ransomware_persist.img

tinyrange login -c build.yaml --rebuild

# Copy the disk image to the current directory
cp $(tinyrange env build-dir)/persist/ransomware_persist.img disk.img