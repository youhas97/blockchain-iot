#!/bin/bash

containers=()
for (( i = 1; i <= $(docker ps -a | grep iroha_ | wc -l); ++i)); do
  container=$(docker ps -a | grep iroha_ | cut -d$'\n' -f $i | cut -d' ' -f 1)
  containers+=($container)
done

for cont in "${containers[@]}"; do
  echo $cont
  docker container stop $cont
  docker container rm $cont
done

volumes=()
for (( i = 1; i <= $(docker volume ls | grep blockstore_ | wc -l); ++i)); do
  volume=$(docker volume ls | grep blockstore_ | cut -d$'\n' -f $i | awk '{print $2}')
  volumes+=($volume)
done

for vol in "${volumes[@]}"; do
  docker volume rm $vol
done

