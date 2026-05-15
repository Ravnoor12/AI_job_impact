from jobImpact.components.data_ingestion import DataIngestion
from jobImpact.components.data_validation import DataValidation
from jobImpact.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from jobImpact.entity.config_entity import DataIngestionConfig, DataValidationConfig
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
        logging.info("Data ingestion completed and artifact is created")
        
        data_validation_config=DataValidationConfig(training_pipeline_config)
        data_validation=DataValidation( data_ingestion_artifact, data_validation_config)
        logging.info("initiating data validation")
        data_validation.initiate_data_validation()
        logging.info("Data validation completed and artifact is created")
        print(data_ingestion_artifact)

    except Exception as e:
        raise JobImpactException(e,sys)