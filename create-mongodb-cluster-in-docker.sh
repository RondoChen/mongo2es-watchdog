#!/bin/sh

docker network create mongo2es

docker run -d --rm -p 27017:27017 --name mongo1 --network mongo2es mongo:5 mongod --replSet docker-rs --port 27017
docker run -d --rm -p 27018:27018 --name mongo2 --network mongo2es mongo:5 mongod --replSet docker-rs --port 27018
docker run -d --rm -p 27019:27019 --name mongo3 --network mongo2es mongo:5 mongod --replSet docker-rs --port 27019

# docker run -d --rm -p 9200:9200 -p 9300:9300 --name docker-es --network mongo2es -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.2
