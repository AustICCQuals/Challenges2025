#!/bin/bash

mkdir -p publish
mv flag.txt flag.tmp.txt
echo "oiccflag{test}" > flag.txt
tar -czvf publish/src-$(basename "$PWD").tar.gz flag.txt Dockerfile src
mv flag.tmp.txt flag.txt