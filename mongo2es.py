# -*- coding: utf-8 -*-
'''
storage MongoDB data into Elasticsearch
function:
- check the connection to database before running
- Monitor mode
	- query the documents in MongoDB periodically, and index the document datas into Elasticsearch
	- support customerize query, default is no query
	- convert MongoDB ObjectID into string
	- make datetime data display time zone
	- record the timestamp when the data is indexed
- Watcher mode
	- convert MongoDB ObjectID into string
	- make datetime data display time zone

by rondochen
'''

from pymongo import MongoClient
from elasticsearch import Elasticsearch
from time import sleep
from datetime import datetime as dt
import pytz
import json


class mongo2es():
	def __init__(self, mongodb_url, mongodb_database_name, mongodb_collection_name, es_url, es_index_name):
		self.mongodb_url = mongodb_url
		self.mongodb_database_name = mongodb_database_name
		self.mongodb_collection_name = mongodb_collection_name
		self.es_url = es_url
		self.es_index_name = es_index_name
		self.connection_check()
		self.run_check()

	def connection_check(self):
		# limit the timeout setting in order to validate the connection quickly
		self.mongodb_client = MongoClient(host=self.mongodb_url, tz_aware=True, timeoutMS=5000)
		self.es_client = Elasticsearch(hosts=self.es_url, timeout = 5)
		try:
			self.mongodb_client.server_info()
		except Exception as e:
			print(e)
			exit()
		try:
			self.es_client.info()
		except Exception as e:
			print(e)
			exit()

	def run_check(self):
		if self.mongodb_database_name not in self.mongodb_client.list_database_names():
			print('mongodb can not find database %s' %self.mongodb_database_name)
			exit()
		elif self.mongodb_collection_name not in self.mongodb_client[self.mongodb_database_name].list_collection_names():
			print('can not find %s in %s' %(self.mongodb_collection_name, self.mongodb_database_name))
			exit()
		else: 
			return True
		
class MongoMonitor(mongo2es):
	def __init__(self, mongodb_url, mongodb_database_name, mongodb_collection_name, es_url, es_index_name, check_interval=60, my_query="{}"):
		super().__init__(mongodb_url, mongodb_database_name, mongodb_collection_name, es_url, es_index_name)
		self.check_interval = check_interval
		self.my_query = my_query
	def test_my_query(self):
		print(self.my_query)
		print(json.loads(self.my_query))
		result = self.mongodb_client[self.mongodb_database_name][self.mongodb_collection_name].find(json.loads(self.my_query))
	def mongo_collection_to_es_index(self):
		collect_date =dt.utcnow().replace(tzinfo=pytz.UTC)
		print(collect_date)
		try:
			result = self.mongodb_client[self.mongodb_database_name][self.mongodb_collection_name].find(json.loads(self.my_query))
		except Exception as e:
			print(e)
		for item in result:
			item['mongo_id'] = str(item['_id'])
			del item['_id']
			item['timestamp'] = collect_date
			try:
				print(self.es_client.index(index=self.es_index_name, body = item))
				print('----')
			except Exception as e:
				print(e)
	def monitor_collection(self):
		while True:
			self.mongo_collection_to_es_index()
			sleep(self.check_interval)

class MongoWatcher(mongo2es):
	def __init__(self, mongodb_url, mongodb_database_name, mongodb_collection_name, es_url, es_index_name):
		super().__init__(mongodb_url, mongodb_database_name, mongodb_collection_name, es_url, es_index_name)
		

	def watch_collection(self):
		# re-define a client without timeout setting when start watching
		self.mongodb_client = MongoClient(host=self.mongodb_url, tz_aware=True)
		try:
			change_stream = self.mongodb_client[self.mongodb_database_name][self.mongodb_collection_name].watch([],"updateLookup")
		except Exception as e:
			print(e)
		for change_stream_item in change_stream:
			change_stream_item = adjust_change_stream_item(change_stream_item)
			try:
				print(self.es_client.index(index = self.es_index_name, body = change_stream_item))
				print('----')
			except Exception as e:
				print(e)		

def adjust_change_stream_item(change_stream_item):
	# do some necessary adjustment before indexing into es
	del change_stream_item['_id']
	if 'fullDocument' in change_stream_item:
		if (change_stream_item['fullDocument'] is not None ) and ('_id' in change_stream_item['fullDocument']):
			change_stream_item['fullDocument']['_id'] = str(change_stream_item['fullDocument']['_id'])
	# convert <class 'bson.timestamp.Timestamp'> into datetime
	# https://pymongo.readthedocs.io/en/stable/api/bson/timestamp.html
	change_stream_item['clusterTime'] = change_stream_item['clusterTime'].as_datetime()
	change_stream_item['documentKey']['_id'] = str(change_stream_item['documentKey']['_id'])
	print(change_stream_item)
	return change_stream_item
