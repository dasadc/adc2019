# coding: utf-8

import os

os.environ['DATASTORE_DATASET']='test813'
os.environ['DATASTORE_EMULATOR_HOST']='localhost:8081'
os.environ['DATASTORE_EMULATOR_HOST_PATH']='localhost:8081/datastore'
os.environ['DATASTORE_HOST']='http://localhost:8081'
os.environ['DATASTORE_PROJECT_ID']='test813'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser('~/keyfile.json')
