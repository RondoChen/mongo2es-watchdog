# -*- coding: utf-8 -*-
import mongo2es
from os import getenv


def check_env(needed_env):
	if getenv(needed_env) is None:
		print("environment variable ${%s} is needed!" %needed_env)
		exit()

if __name__ == '__main__':
	list_of_needed_env=['run_mode','mongodb_url','mongodb_database_name','mongodb_collection_name','es_url','es_index_name']
	for item in list_of_needed_env:
		check_env(item)
	if getenv('run_mode') == 'monitor':
		if getenv('my_query') is None:
			my_query = "{}"
		else:
			my_query = getenv('my_query')
		if getenv('check_interval') is None:
			check_interval = 60
		else:
			check_interval = int(getenv('check_interval'))
		job = mongo2es.MongoMonitor(mongodb_url = getenv('mongodb_url'), \
			mongodb_database_name = getenv('mongodb_database_name'), \
			mongodb_collection_name = getenv('mongodb_collection_name'), \
			es_url = getenv('es_url'), \
			es_index_name = getenv('es_index_name'), \
			check_interval = check_interval, \
			my_query = my_query \
			)
		job.monitor_collection()
	elif getenv('run_mode') == 'watcher':
		job = mongo2es.MongoWatcher(mongodb_url = getenv('mongodb_url'), \
			mongodb_database_name = getenv('mongodb_database_name'), \
			mongodb_collection_name = getenv('mongodb_collection_name'), \
			es_url = getenv('es_url'), \
			es_index_name = getenv('es_index_name'))
		job.watch_collection()
	else:
		print("environment variable ${run_mode} must be either 'monitor' or 'watcher'!")
		exit()
