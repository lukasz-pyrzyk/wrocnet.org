#!/bin/sh
set -eu

cd -- "$(dirname -- "$0")"

container_ids=$(docker ps -aq)
site_containers=""
named_container=""
for id in $container_ids; do
  identity=$(docker inspect --format '{{.Config.Image}}|{{index .Config.Labels "org.wrocnet.local"}}|{{.Name}}' "$id")
  case "$identity" in
    wrocnet-local\|*|wrocnet-local:*\|*|*\|true\|*)
      site_containers="$site_containers $id"
      case "$identity" in
        *\|/wrocnet-local) named_container="$id" ;;
      esac
      ;;
    *\|/wrocnet-local)
      echo "Container wrocnet-local is not a recognized Wroc.NET instance; leaving it untouched." >&2
      exit 1
      ;;
  esac
done

port_containers=$(docker ps -q --filter publish=4001 --filter publish=35730)
for id in $port_containers; do
  case " $site_containers " in
    *" $id "*) ;;
    *)
      echo "Container $id uses a preview port but is not a recognized Wroc.NET instance; leaving it untouched." >&2
      exit 1
      ;;
  esac
done

docker build --pull -t wrocnet-local .

for id in $site_containers; do
  echo "Stopping previous Wroc.NET container: $id"
  docker stop "$id"
done
if [ -n "$named_container" ]; then
  remaining_container=$(docker ps -aq --filter "id=$named_container")
  if [ -n "$remaining_container" ]; then
    docker rm "$remaining_container"
  fi
fi

exec docker run --rm \
  --name wrocnet-local \
  --label org.wrocnet.local=true \
  -p 127.0.0.1:4001:4001 \
  -p 127.0.0.1:35730:35730 \
  --mount "type=bind,source=$PWD,target=/app" \
  --mount type=volume,source=wrocnet-gems-alpine,target=/usr/local/bundle \
  --mount type=volume,source=wrocnet-site,target=/app/_site \
  --mount type=volume,source=wrocnet-cache,target=/app/.jekyll-cache \
  wrocnet-local bundle exec jekyll serve --host 0.0.0.0 --port 4001 \
  --livereload --livereload-port 35730 "$@"
