import sys
import os
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from jobImpact.constants.training_pipeline import TARGET_COLUMN
from jobImpact.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)
from jobImpact.entity.config_entity import DataTransformationConfig
from jobImpact.exception.exception import JobImpactException 
from jobImpact.logging.logger import logging
from jobImpact.utils.main_utils.utils import save_numpy_array_data, save_object

class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            raise JobImpactException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise JobImpactException(e, sys)
        
    def get_data_transformer_object(self) -> ColumnTransformer:
        """
        Creates a ColumnTransformer that applies OneHotEncoding to categorical columns 
        and StandardScaling to numerical columns.
        """
        logging.info("Entered get_data_transformer_object method of DataTransformation class")
        try:
            # Define categorical columns
            numerical_columns = ['year', 'salary', 'ai_risk_score', 'skill_demand_score', 'job_openings']
            categorical_columns = ['job_title', 'country', 'experience_level', 'education_level', 'primary_skill', 'salary_bucket', 'ai_risk_category']

            # Build the Numerical Pipeline
            num_pipeline = Pipeline(steps=[
                ("scaler", StandardScaler())
            ])

            # Build the Categorical Pipeline
            cat_pipeline = Pipeline(steps=[
                # sparse_output=False is REQUIRED here so np.c_ works later in the script
                ("one_hot_encoder", OneHotEncoder(sparse_output=False, handle_unknown="ignore")),
                ("scaler", StandardScaler(with_mean=False)) 
            ])

            logging.info(f"Categorical columns encoded: {categorical_columns}")
            logging.info(f"Numerical columns scaled: {numerical_columns}")

            # Combined into a single ColumnTransformer
            preprocessor = ColumnTransformer([
                ("num_pipeline", num_pipeline, numerical_columns),
                ("cat_pipeline", cat_pipeline, categorical_columns)
            ])

            return preprocessor

        except Exception as e:
            raise JobImpactException(e, sys)

        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Entered initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting data transformation")
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            ## training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN])
            target_feature_train_df = train_df[TARGET_COLUMN]

            # testing dataframe
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN])
            target_feature_test_df = test_df[TARGET_COLUMN]

            # Get the preprocessor object
            preprocessor = self.get_data_transformer_object()

            # Fit on training data, transform both train and test data
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)
             
            # Combine transformed inputs with their targets into final numpy arrays
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # Save numpy arrays and the preprocessor pickle file
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)
            
            # Optional: Save a duplicate for easy access later
            save_object("final_model/preprocessor.pkl", preprocessor_object)

            # Prepare artifacts to pass to Model Trainer
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact
            
        except Exception as e:
            raise JobImpactException(e, sys)