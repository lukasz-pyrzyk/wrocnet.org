#!/bin/sh
set -eu

cd -- "$(dirname -- "$0")"

docker build --pull -t wrocnet-local .

exec docker run --rm \
  --name wrocnet-local \
  -p 127.0.0.1:4001:4001 \
  -p 127.0.0.1:35730:35730 \
  --mount "type=bind,source=$PWD,target=/app" \
  --mount type=volume,source=wrocnet-gems-alpine,target=/usr/local/bundle \
  --mount type=volume,source=wrocnet-site,target=/app/_site \
  --mount type=volume,source=wrocnet-cache,target=/app/.jekyll-cache \
  wrocnet-local bundle exec jekyll serve --host 0.0.0.0 --port 4001 \
  --livereload --livereload-port 35730 "$@"
