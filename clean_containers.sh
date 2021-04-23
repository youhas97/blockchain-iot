#!/bin/bash

set -e

#scommand -v docker-compose >/dev/null 2>&1 || { echo "I require docker-compose but it's not installed. Remember to source your venv. Aborting." >&2; exit 1; }

containers=()
for (( i = 1; i <= $(docker ps -a | grep iroha_ | wc -l); ++i)); do
  container=$(docker ps -a | grep iroha_ | cut -d$'\n' -f $i | cut -d' ' -f 1)
  containers+=($container)
done
for (( i = 1; i <= $(docker ps -a | grep nodedb_ | wc -l); ++i)); do
  container=$(docker ps -a | grep nodedb_ | cut -d$'\n' -f $i | cut -d' ' -f 1)
  containers+=($container)
done

for cont in "${containers[@]}"; do
  if [ "$( docker container inspect -f '{{.State.Status}}' $cont )" == "running" ]; then
    docker container kill $cont
  fi
  docker container rm $cont
done

volumes=()
for (( i = 1; i <= $(docker volume ls | grep blockstore_ | wc -l); ++i)); do
  volume=$(docker volume ls | grep blockstore_ | cut -d$'\n' -f $i | awk '{print $2}')
  volumes+=($volume)
done
for (( i = 1; i <= $(docker volume ls | grep pgdata_ | wc -l); ++i)); do
  volume=$(docker volume ls | grep pgdata_ | cut -d$'\n' -f $i | awk '{print $2}')
  volumes+=($volume)
done

for vol in "${volumes[@]}"; do
  docker volume rm $vol
done

docker network rm iroha-network

#docker-compose down -v