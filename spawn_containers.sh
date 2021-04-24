#!/bin/bash

set -e

command -v python >/dev/null 2>&1 || { echo "I require python but it's not installed.  Remember to source your venv. Aborting." >&2; exit 1; }
#command -v docker-compose >/dev/null 2>&1 || { echo "I require docker-compose but it's not installed. Remember to source your venv. Aborting." >&2; exit 1; }

if [ $# -ne 1 ]; then
  echo The scripts accepts exactly one integer argument.
  exit 1
fi 

if ! [[ $1 =~ ^[1-9][0-9]*$ ]]; then
  echo The argument has to be of type positive integer.
  exit 1
fi

#docker-compose up -d
NODES_PER_DB=10

{
  python autoconfigure_nodes.py $1
} ||
{
  echo "Something went wrong when trying to generate node files. Make sure to source your venv before running the script."
  #docker-compose down -v
  exit 1
}

docker network create iroha-network --subnet 10.1.0.0/16 --gateway 10.1.0.1

db_counter=0
for (( i = 0; i < $1; ++i ))
do
  if (( $(docker volume ls | grep blockstore_$((i)) | wc -l) > 0))
  then
    docker volume rm blockstore_$((i))
  fi

  if (( $i % $NODES_PER_DB == 0 )); then
    if (( $(docker volume ls | grep pgdata_$((db_counter)) | wc -l) > 0))
    then
      docker volume rm pgdata_$db_counter
    fi

    docker volume create pgdata_$db_counter
    docker run --name nodedb_$db_counter \
    --expose 5432 \
    -v pgdata_$db_counter:/var/lib/postgresql/data \
    --network=iroha-network \
    --ip=10.1.1.$db_counter \
    -e POSTGRES_USER="postgres" \
    -e POSTGRES_PASSWORD="QPtc2AssTNv2ugnD" \
    -d postgres:9.5 \
    -c 'max_prepared_transactions=100'

    (( db_counter+=1 ))
  fi

  docker volume create blockstore_$i
  docker run --name iroha_$i \
  -d \
  -p $((50051 + $i)):50051 \
  -p $((10001 + $i)):10001 \
  -v $(pwd)/nodes/node_$((i)):/opt/iroha_data \
  -v blockstore_$((i)):/tmp/block_store \
  --network=iroha-network \
  --ip=10.1.2.$i \
  -e KEY="node_${i}" \
  -e IROHA_POSTGRES_HOST=$(printf "nodedb_%d" $(expr $db_counter - 1)) \
  hyperledger/iroha:latest
done 

sleepTime=20

echo "Sleeping for ${sleepTime} seconds."
sleep $sleepTime

while : ; do  

  exited_containers=()
  for (( i = 1; i <= $(docker ps -f status=exited | grep iroha_ | wc -l); ++i)); do
    line=$(docker ps -f status=exited | grep iroha_ | cut -d$'\n' -f $i)
    container=$(echo $line | awk '{print $1}')
    exited_containers+=($container)
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