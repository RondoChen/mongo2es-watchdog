from pymongo import MongoClient
from pymongo import ReturnDocument
from datetime import datetime as dt
import pytz
from time import sleep
import random
import os

class demoJob():
    def __init__(self, mongodb_url):
        self.mongodb_url = mongodb_url
        self.mongodb_client = MongoClient(host=self.mongodb_url, tz_aware=True, timeoutMS=5000)
        try:
            self.mongodb_client.server_info()
        except Exception as e:
            print(e)
            exit()

    def insert_demo_data(self):
        self.mongodb_client['demoDatabase']['demoCollection'].drop()
        demo_data_list=[{"name":"rondo", "age":15, "createAt": dt.utcnow().replace(tzinfo=pytz.UTC)},\
            {"name":"john", "age":16, "createAt": dt.utcnow().replace(tzinfo=pytz.UTC)}, \
            {"name":"mike", "age":14, "createAt": dt.utcnow().replace(tzinfo=pytz.UTC)}]
        for items in demo_data_list:
            try:
                self.mongodb_client['demoDatabase']['demoCollection'].insert_one(items)
            except Exception as e:
                print(e)
    def update_demo_data(self):
        self.mongodb_client['demoDatabase']['demoCollection'].find_one_and_update(
                {'age': random.randint(14,16)},{'$set': {'lastCheck':dt.utcnow().replace(tzinfo=pytz.UTC)}},
            return_document=ReturnDocument.AFTER)

if __name__ == '__main__':
    job = demoJob(os.getenv('mongodb_url'))
    job.insert_demo_data()
    while True:
        print('now doing random change in MongoDB')
        job.update_demo_data()
        sleep(5)
