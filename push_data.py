import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")
# print(MONGO_DB_URL)

import certifi
ca=certifi.where()

import pandas as pd
import numpy as np
import pymongo
from jobImpact.exception.exception import JobImpactException
from jobImpact.logging.logger import logging

class JobImpactDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise JobImpactException(e,sys)
        
    def csv_to_json_convertor(self,file_path):
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)
            records=list(json.loads(data.T.to_json()).values())  # converting csv to json format and then to list of dicts like csv A B C 1 2 3 to [{"A":1,"B":2,"C":3}]
            return records
        except Exception as e:
            raise JobImpactException(e,sys)
        
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.database=database
            self.collection=collection
            self.records=records

            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            
            self.collection=self.database[self.collection]
            self.collection.insert_many(self.records)
            return(len(self.records))
        except Exception as e:
            raise JobImpactException(e,sys)
        
if __name__=='__main__':
    FILE_PATH="jobImpact_data\Future of Jobs AI Dataset.csv"
    DATABASE="jobImpactDB"
    Collection="jobImpactCollection"
    jobimpactobj=JobImpactDataExtract()
    records=jobimpactobj.csv_to_json_convertor(file_path=FILE_PATH)
    print(records)
    no_of_records=jobimpactobj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)
         

# from pymongo import MongoClient
# from pymongo.server_api import ServerApi

# uri = ''

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))


# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)