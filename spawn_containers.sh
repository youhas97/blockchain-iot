#!/bin/bash

if [ $# -ne 1 ]; then
  echo The scripts accepts exactly one integer argument.
  exit 1
fi 

if ! [[ $1 =~ ^[1-9][0-9]*$ ]]; then
  echo The argument has to be of type positive integer.
  exit 1
fi

docker-compose up -d

python autogen_nodes.py $1

for (( i = 0; i < $1; ++i ))
do
  if (( $(docker volume ls | grep blockstore_$((i)) | wc -l) > 0))
  then
    docker volume rm blockstore_$((i))
  fi
  docker volume create blockstore_$((i))
  docker run --name iroha_$i \
  -d \
  -p $((50051 + $i)):50051 \
  -p $((10001 + $i)):10001 \
  -v $(pwd)/nodes/node_$((i)):/opt/iroha_data \
  -v blockstore_$((i)):/tmp/block_store \
  --network=blockchain-iot_iroha-network \
  --ip=10.1.2.$i \
  -e KEY="node_${i}" \
  -e IROHA_POSTGRES_HOST="database" \
  hyperledger/iroha:latest
done 

sleepTime=20

echo "Sleeping for ${sleepTime} seconds."
sleep $sleepTime

while : ; do  

  exited_containers=()
  for (( i = 1; i <= $(docker ps -a | grep iroha_ | wc -l); ++i)); do
    line=$(docker ps -a | grep iroha_ | cut -d$'\n' -f $i)
    container=$(echo $line | awk '{print $1}')
    status=$(echo $line | awk '{print $8}')
    if [ "${status}" = "Exited" ]; then
      exited_containers+=($container)
    fi
  done

  if (( ${#exited_containers[@]} > 0 )); then
    echo "Restarting exited containers."
    for cont in "${exited_containers[@]}"; do
      docker start $cont
    done
  else
    break
  fi

  echo "Sleeping for ${sleepTime} seconds."
  sleep $sleepTime
done

echo "All containers successfully started."

exit 0