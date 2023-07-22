# Introduction

This is a script can index the documents in MongoDB into Elasticsearch in two different modes:

- Monitor mode: scan a specific collection in MongoDB periodically, and index all the documents into Elasticsearch.

- Watcher mode: do the same thing, but in real time base on MongoDB change stream, requires a MongoDB cluster.

## Demo Info

- Python: 3.9

- Elasticsearch: 7.10

- MongoDB: 5.0

## Demo(quick start)

Before running this script, you'll need a MongoDB and Elasticsearch. And if you do not want to risk your database, I will make a demo in Docker:

First, create a docker network call `mongo2es`:

```
docker network create mongo2es
```

### set up a Elasticsearch

Refer to [Starting a single node cluster with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/docker.html#docker-cli-run-dev-mode).

```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.10.2

docker run -d --rm -p 9200:9200 -p 9300:9300 --name docker-es --network mongo2es -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.2
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

### set up a MongoDB cluster in Docker

Actually, mongo cluster is not necessary, however, when it comes to watcher mode, it has to use a mongo cluster which supports change stream feature.

In other words, you can not use the watcher mode if your mongodb is running in single node.

Use docker to create a mongodb cluster

Refer: [Deploying a MongoDB Cluster with Docker](https://www.mongodb.com/compatibility/deploying-a-mongodb-cluster-with-docker)

```
docker run -d --rm -p 27017:27017 --name mongo1 --network mongo2es mongo:5 mongod --replSet docker-rs --port 27017
docker run -d --rm -p 27018:27018 --name mongo2 --network mongo2es mongo:5 mongod --replSet docker-rs --port 27018
docker run -d --rm -p 27019:27019 --name mongo3 --network mongo2es mongo:5 mongod --replSet docker-rs --port 27019
```

Connect into MongoDB and do some preparation for the demo:

```
# enter MongoDB shell
docker exec -it mongo1 mongo
```

Do it in mongodb shell:
```
# initiate mongodb cluster

> config = {"_id" : "docker-rs", "members" : [{"_id" : 0,"host" : "mongo1:27017"},{"_id" : 1,"host" : "mongo2:27018"},{"_id" : 2,"host" : "mongo3:27019"}]}
{
        "_id" : "docker-rs",
        "members" : [
                {
                        "_id" : 0,
                        "host" : "mongo1:27017"
                },
                {
                        "_id" : 1,
                        "host" : "mongo2:27018"
                },
                {
                        "_id" : 2,
                        "host" : "mongo3:27019"
                }
        ]
}
> rs.initiate(config)
{
        "ok" : 1,
        "$clusterTime" : {
                "clusterTime" : Timestamp(1689997438, 1),
                "signature" : {
                        "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
                        "keyId" : NumberLong(0)
                }
        },
        "operationTime" : Timestamp(1689997438, 1)
}

# create demo user
> use admin
switched to db admin
> db.createUser({user:"demo", pwd:"demo12345", roles:['readWrite','dbAdmin']});
Successfully added user: { "user" : "demo", "roles" : [ "readWrite", "dbAdmin" ] }
> 

# check the replicaset status
docker-rs:PRIMARY> rs.status()
{
        "set" : "docker-rs",
        "date" : ISODate("2023-07-22T04:56:05.469Z"),
        "myState" : 1,
        "term" : NumberLong(1),
        "syncSourceHost" : "",
        "syncSourceId" : -1,
        "heartbeatIntervalMillis" : 
...
}
```

### Run the demo in docker

Again, since the databases are all in docker, I'll do this in docker environment.

Before starting the docker compose, you'll need to prepare an environment file:

```
# cat demo.env 
mongodb_url='mongodb://demo:demo12345@mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=docker-rs'
es_url='http://docker-es:9200/'
```

Onece the ES and MongoDB cluster are both ready, we can start this docker compose, it does these things:

- generate-demo-data: as the title means, it generates some sample documents into mongodb, and edit them randomly.

- mongo-monitor-demo: scan the documents in demoDatabase.demoCollection and do the query: `{"name":"rondo"}`, index the query result into elasticsearch in every 20 seconds.

- mongo-watcher-demo: scan the demoDatabase.demoCollection in real time, and record the documents changes into elasticsearch

Then bring up the docker compose, you'll see screen outputs like below:

```
# docker compose -f demo-docker-compose.yml up
[+] Building 0.0s (0/0)                                                                                                                                                                                                                                         
[+] Running 3/0
 ✔ Container generate-demo-data  Created                                                                                                                                                                                                                   0.0s 
 ✔ Container mongo-monitor-demo  Created                                                                                                                                                                                                                   0.0s 
 ✔ Container mongo-watcher-demo  Created                                                                                                                                                                                                                   0.0s 
Attaching to generate-demo-data, mongo-monitor-demo, mongo-watcher-demo
generate-demo-data  | now doing random change in MongoDB
mongo-monitor-demo  | 2023-07-22 05:04:09.068583+00:00
mongo-monitor-demo  | {'_index': 'monitor-index', '_type': '_doc', '_id': 'laz7e4kBOUoK6m8i1axv', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 4, '_primary_term': 1}
mongo-monitor-demo  | ----
generate-demo-data  | now doing random change in MongoDB
mongo-watcher-demo  | {'operationType': 'update', 'clusterTime': datetime.datetime(2023, 7, 22, 5, 4, 13, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'fullDocument': {'_id': '64bb63485b8516eac0223a1d', 'name': 'mike', 'age': 14, 'createAt': datetime.datetime(2023, 7, 22, 5, 4, 8, 517000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 13, 595000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'ns': {'db': 'demoDatabase', 'coll': 'demoCollection'}, 'documentKey': {'_id': '64bb63485b8516eac0223a1d'}, 'updateDescription': {'updatedFields': {'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 13, 595000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'removedFields': [], 'truncatedArrays': []}}
mongo-watcher-demo  | {'_index': 'watcher-index', '_type': '_doc', '_id': 'lqz7e4kBOUoK6m8i56wo', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 22, '_primary_term': 1}
mongo-watcher-demo  | ----
generate-demo-data  | now doing random change in MongoDB
mongo-watcher-demo  | {'operationType': 'update', 'clusterTime': datetime.datetime(2023, 7, 22, 5, 4, 18, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'fullDocument': {'_id': '64bb63485b8516eac0223a1d', 'name': 'mike', 'age': 14, 'createAt': datetime.datetime(2023, 7, 22, 5, 4, 8, 517000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 18, 610000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'ns': {'db': 'demoDatabase', 'coll': 'demoCollection'}, 'documentKey': {'_id': '64bb63485b8516eac0223a1d'}, 'updateDescription': {'updatedFields': {'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 18, 610000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'removedFields': [], 'truncatedArrays': []}}
mongo-watcher-demo  | {'_index': 'watcher-index', '_type': '_doc', '_id': 'l6z7e4kBOUoK6m8i-qy7', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 23, '_primary_term': 1}
mongo-watcher-demo  | ----
generate-demo-data  | now doing random change in MongoDB
mongo-watcher-demo  | {'operationType': 'update', 'clusterTime': datetime.datetime(2023, 7, 22, 5, 4, 23, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'fullDocument': {'_id': '64bb63485b8516eac0223a1d', 'name': 'mike', 'age': 14, 'createAt': datetime.datetime(2023, 7, 22, 5, 4, 8, 517000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 23, 622000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'ns': {'db': 'demoDatabase', 'coll': 'demoCollection'}, 'documentKey': {'_id': '64bb63485b8516eac0223a1d'}, 'updateDescription': {'updatedFields': {'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 23, 622000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'removedFields': [], 'truncatedArrays': []}}
mongo-watcher-demo  | {'_index': 'watcher-index', '_type': '_doc', '_id': 'mKz8e4kBOUoK6m8iDqxT', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 24, '_primary_term': 1}
mongo-watcher-demo  | ----
generate-demo-data  | now doing random change in MongoDB
mongo-watcher-demo  | {'operationType': 'update', 'clusterTime': datetime.datetime(2023, 7, 22, 5, 4, 28, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'fullDocument': {'_id': '64bb63485b8516eac0223a1d', 'name': 'mike', 'age': 14, 'createAt': datetime.datetime(2023, 7, 22, 5, 4, 8, 517000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>), 'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 28, 635000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'ns': {'db': 'demoDatabase', 'coll': 'demoCollection'}, 'documentKey': {'_id': '64bb63485b8516eac0223a1d'}, 'updateDescription': {'updatedFields': {'lastCheck': datetime.datetime(2023, 7, 22, 5, 4, 28, 635000, tzinfo=<bson.tz_util.FixedOffset object at 0x7f28be9ade80>)}, 'removedFields': [], 'truncatedArrays': []}}
mongo-watcher-demo  | {'_index': 'watcher-index', '_type': '_doc', '_id': 'maz8e4kBOUoK6m8iIazo', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 25, '_primary_term': 1}
mongo-watcher-demo  | ----
mongo-monitor-demo  | 2023-07-22 05:04:29.107304+00:00
mongo-monitor-demo  | {'_index': 'monitor-index', '_type': '_doc', '_id': 'mqz8e4kBOUoK6m8iI6y3', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 5, '_primary_term': 1}
mongo-monitor-demo  | ----
```

### check the datas in Elasticsearch

As we can see from above, `mongo-watcher-demo` and `mongo-monitor-demo` have both indexed something into ES, and we can check them simply by:

```json
# curl -XGET http://127.0.0.1:9200/watcher-index/_doc/mKz8e4kBOUoK6m8iDqxT?pretty
{
  "_index" : "watcher-index",
  "_type" : "_doc",
  "_id" : "mKz8e4kBOUoK6m8iDqxT",
  "_version" : 1,
  "_seq_no" : 24,
  "_primary_term" : 1,
  "found" : true,
  "_source" : {
    "operationType" : "update",
    "clusterTime" : "2023-07-22T05:04:23+00:00",
    "fullDocument" : {
      "_id" : "64bb63485b8516eac0223a1d",
      "name" : "mike",
      "age" : 14,
      "createAt" : "2023-07-22T05:04:08.517000+00:00",
      "lastCheck" : "2023-07-22T05:04:23.622000+00:00"
    },
    "ns" : {
      "db" : "demoDatabase",
      "coll" : "demoCollection"
    },
    "documentKey" : {
      "_id" : "64bb63485b8516eac0223a1d"
    },
    "updateDescription" : {
      "updatedFields" : {
        "lastCheck" : "2023-07-22T05:04:23.622000+00:00"
      },
      "removedFields" : [ ],
      "truncatedArrays" : [ ]
    }
  }
}

# curl -XGET http://127.0.0.1:9200/monitor-index/_doc/mqz8e4kBOUoK6m8iI6y3?pretty
{
  "_index" : "monitor-index",
  "_type" : "_doc",
  "_id" : "mqz8e4kBOUoK6m8iI6y3",
  "_version" : 1,
  "_seq_no" : 5,
  "_primary_term" : 1,
  "found" : true,
  "_source" : {
    "name" : "rondo",
    "age" : 15,
    "createAt" : "2023-07-22T05:04:08.517000+00:00",
    "mongo_id" : "64bb63485b8516eac0223a1b",
    "timestamp" : "2023-07-22T05:04:29.107304+00:00"
  }
}
```

As the results shown above, the documents in MongoDB can storage in Elasticsearch, depending on your needs. Then you can do some other tricks in kibana, like visualizing your data.

# Manual

So, when you decide to run this project at your environment, here is the steps:

1. use `pip3` to install the python modules.

2. use `export` command to export the environment variables.

3. start the script `main.py`.

4. If anything goes wrong like failing to connect to database or lacking environment variables, the stdout will tell you.

## Environment variables

| name | defination | sample | remark |
| --- |  --- | --- | --- |
| run_mode | choose the mode you wan to run | `monitor` or `watcher` | watcher mode requires a MongoDB cluster | 
| mongodb_url | connection string of a MongoDB | `mongodb://demo:demo12345@192.168.0.1:27017,192.168.0.2:27017,192.168.0.3:27017/?replicaSet=yourReplicaSet` | [MongoClient](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient) |
| es_url | connection string of a ElasticSearch | `http://elastic:password@http://192.168.1.2:9200/` | - |
| mongodb_database_name | name of the mongodb database you want to scan | - | - |
| mongodb_collection_name | name of the mongodb collection you want to scan | - | - |
| es_index_name | the index name of Elasticsearch | - | suggest to prepare a proper index template before using it |
| check_interval | sleep seconds between every two scaning | `30` | optional, defaul is `60`, effects only in monitor mode |
| my_query | the query when scanning the documents in MongoDB | optional, `{"name":"rondo"}` | default is `{}`, effects only in monitor mode |

## Runing in Docker

Every detail infos are all in the file `sample-docker-compose.yml` and `dockerfile`.

# Backgroup(why I did this)

I am currently working in a mobile game company as server engineer.

We have come datas in MongoDB need to be collected and analysised which I planned to make some visualization in Kibana. I had try searching in Github, there were a few `mongo2es` project, but none of them meet my need, so this project came.

I have not done such complicated work before, hopefully this can help you.
