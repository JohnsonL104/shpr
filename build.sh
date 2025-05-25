#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

VERSION="$1"
IMAGE_NAME="shpr"

docker build -t "${IMAGE_NAME}:latest" -t "${IMAGE_NAME}:${VERSION}" .