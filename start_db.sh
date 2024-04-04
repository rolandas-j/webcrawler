#!/bin/bash

cassandra_name="crawler-cassandra"
network_name="cassandra"
hostname="cassandra"

if [ ! "$(docker network ls -q -f name=$network_name)" ]; then
    docker network create $network_name
fi

if [ "$(docker ps -aq -f status=exited -f name=$cassandra_name)" ]; then
    docker rm -f $cassandra_name
fi

if [ ! "$(docker ps -a -q -f name=$cassandra_name)" ]; then
    #startup new cassandra and load .cql file
    docker run --name $cassandra_name -p 9042:9042 --network $network_name --hostname $hostname -d cassandra:latest
    echo "Waiting for cluster to startup"
    sleep 90s
    docker run --rm --network $network_name -v "$(pwd)/data.cql:/scripts/data.cql" -e CQLSH_HOST=$hostname -e CQLSH_PORT=9042 -e CQLVERSION=3.4.6 nuvo/docker-cqlsh
fi
