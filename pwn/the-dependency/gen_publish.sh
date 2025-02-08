#!/bin/bash

set -euo pipefail

chal=$(basename "$PWD")

rm -rf $chal || true
rm -rf publish || true
cp -r service $chal
echo 'oiccflag{test}' > $chal/flag.txt

cp -r src $chal/src
mkdir -p publish
tar -czvf publish/$chal.tar.gz $chal
rm -rf $chal
