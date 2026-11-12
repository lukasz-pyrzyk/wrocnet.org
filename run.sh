#!/bin/sh
set -eu

cd -- "$(dirname -- "$0")"

docker_container() {
  container_id=$1
  shift
  if output=$(docker "$@" "$container_id" 2>&1); then
    printf '%s\n' "$output"
  else
    status=$?
    remaining=$(docker ps -aq --filter "id=$container_id") || return $?
    if [ -z "$remaining" ]; then
      echo "Container $container_id was removed; skipping docker $1." >&2
      return 0
    fi
    printf '%s\n' "$output" >&2
    return "$status"
  fi
}

container_ids=$(docker ps -aq)
site_containers=""
named_container=""
for id in $container_ids; do
  identity=$(docker_container "$id" inspect --format '{{.Config.Image}}|{{index .Config.Labels "org.wrocnet.local"}}|{{.Name}}')
  if [ -z "$identity" ]; then
    continue
  fi
  case "$identity" in
    wrocnet-local\|*|wrocnet-local:*\|*|*\|true\|*)
      site_containers="$site_containers $id"
      case "$identity" in
        *\|/wrocnet-local) named_container="$id" ;;
      esac
      continue
      ;;
    *\|/wrocnet-local)
      echo "Container wrocnet-local is not a recognized Wroc.NET instance; leaving it untouched." >&2
      exit 1
      ;;
  esac
  host_ports=$(docker_container "$id" inspect --format '{{range $port, $bindings := .NetworkSettings.Ports}}{{range $bindings}}{{printf "%s:%s " $port .HostPort}}{{end}}{{end}}')
  case " $host_ports " in
    *"/tcp:4001 "*|*"/tcp:35730 "*)
      echo "Container $id uses a preview port but is not a recognized Wroc.NET instance; leaving it untouched." >&2
      exit 1
      ;;
  esac
done

docker build --pull -t wrocnet-local .

for id in $site_containers; do
  echo "Stopping previous Wroc.NET container: $id"
  docker_container "$id" stop
done
if [ -n "$named_container" ]; then
  remaining_container=$(docker ps -aq --filter "id=$named_container")
  if [ -n "$remaining_container" ]; then
    docker_container "$remaining_container" rm
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
