#!/bin/bash
# Intended for local development
set -e

cd /home/johnsonl/shpr

docker-compose down

latest_tag=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep '^shpr:' | grep -v ':latest' | sort -Vr | head -n1 | cut -d: -f2)
if [[ $latest_tag =~ ([0-9]+)\.([0-9]+) ]]; then
    major="${BASH_REMATCH[1]}"
    patch="${BASH_REMATCH[2]}"
    new_patch=$((patch + 1))
    new_version="${major}.${new_patch}-dev"
else
    new_version="0.1-dev"
fi

echo "Latest tag: $latest_tag"
echo "New version: $new_version"

./build.sh "$new_version"

docker-compose up -d