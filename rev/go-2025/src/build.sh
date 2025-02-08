#!/usr/bin/env bash

set -ex

tinyrange login -c build.yaml --rebuild

chmod +x go2025

strip go2025
mv go2025 ../publish/go2025
cp main.go ../publish/main.go