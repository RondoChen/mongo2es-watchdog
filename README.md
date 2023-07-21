# Introduction

This is a script can index the documents in MongoDB into Elasticsearch in two different modes:

- Monitor mode: scan a specific collection in MongoDB periodically, and index all the documents into Elasticsearch

- Watcher mode: do the same thing, but in real time base on MongoDB change stream

## requirements

- Python: 3.9

- Elasticsearch: 7.10

- MongoDB: 4.0-cmongo-Community

## Demo(quick start)

Before running this script, you'll need a MongoDB and Elasticsearch, I will make a demo in Docker:

### set up a Elasticsearch

Refer to [Starting a single node cluster with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/docker.html#docker-cli-run-dev-mode).

```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.10.2

docker run -d --name docker-es -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.2
```

Now we have a running Elasticsearch service:

```
rondo@docker:~$ curl -XGET http://127.0.0.1:9200
{
  "name" : "6cf988d402b5",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "p4DLa2lwReCuhzicQ26k-g",
  "version" : {
    "number" : "7.10.2",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "747e1cc71def077253878a59143c1f785afa92b9",
    "build_date" : "2021-01-13T00:42:12.435326Z",
    "build_snapshot" : false,
    "lucene_version" : "8.7.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

### set up a MongoDB

Use docker to start MongoDB.

Refer: [Install MongoDB Community with Docker](https://www.mongodb.com/docs/v4.4/tutorial/install-mongodb-community-with-docker/)

```
docker pull mongodb/mongodb-community-server:4.4.20-ubuntu2004

docker run -d --name mongodb -p 27017:27017 mongodb/mongodb-community-server:4.4.20-ubuntu2004
```

Connect into MongoDB and do some preparation for the demo:

```
# enter MongoDB shell
docker exec -it mongodb mongo
> use admin
switched to db admin
> db.createUser({user:"demo", pwd:"demo12345", roles:['readWrite','dbAdmin']});
Successfully added user: { "user" : "demo", "roles" : [ "readWrite", "dbAdmin" ] }
> 
```

Start the script `generate-random-data.py` in this project to add some sample documents into mongodb.

```

```


## Manual

# Backgroup(why I did this)

# Suggestion

