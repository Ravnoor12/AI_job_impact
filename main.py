from jobImpact.components.data_ingestion import DataIngestion
from jobImpact.entity.config_entity import DataIngestionConfig
from jobImpact.entity.config_entity import TrainingPipelineConfig
from jobImpact.logging.logger import logging
from jobImpact.exception.exception import JobImpactException
import sys

if __name__=="__main__":
    try:
        training_pipeline_config=TrainingPipelineConfig()


        data_ingestion_config=DataIngestionConfig(training_pipeline_config)
        data_ingestion=DataIngestion(data_ingestion_config)
        logging.info("initiating data ingestion")
        data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
        print(data_ingestion_artifact)
    except Exception as e:
        raise JobImpactException(e,sys)