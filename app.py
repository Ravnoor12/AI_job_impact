import sys
import os 

import certifi
from flask import request

ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongodb_url = os.getenv("MONGO_DB_URL")


import pymongo
from jobImpact.exception.exception import JobImpactException
from jobImpact.logging.logger import logging
from jobImpact.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request, Form
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from jobImpact.utils.main_utils.utils import load_object

from jobImpact.utils.ml_utils.model.estimator import jobImpactModel


client = pymongo.MongoClient(mongodb_url, tlsCAFile=ca)

from jobImpact.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from jobImpact.constants.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index(request: Request):
    # return RedirectResponse(url="/docs")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise JobImpactException(e,sys)

@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        #print(df)
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        jobImpact_Model = jobImpactModel(preprocessor=preprocesor,model=final_model)
        print(df.iloc[0])
        y_pred = jobImpact_Model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise JobImpactException(e,sys)

@app.post("/predict_form")
async def predict_form_route(
    request: Request,
    job_title: str = Form(...),
    country: str = Form(...),
    experience_level: str = Form(...),
    education_level: str = Form(...),
    year: int = Form(...),
    salary: float = Form(...),
    ai_risk_score: float = Form(...),
    primary_skill: str = Form(...),
    skill_demand_score: int = Form(...),
    job_openings: int = Form(...)
):
    try:
        # --- 1. AUTO-CALCULATE DERIVED FEATURES ---
        # Calculate AI Risk Category
        if ai_risk_score < 0.3:
            ai_risk_category = "Low Risk"
        elif ai_risk_score <= 0.7:
            ai_risk_category = "Medium Risk"
        else:
            ai_risk_category = "High Risk"
            
        # Calculate Salary Bucket (Adjust these numbers based on your dataset!)
        if salary < 30000:
            salary_bucket = "Low"
        elif salary < 60000:
            salary_bucket = "Medium"
        else:
            salary_bucket = "High"

        # --- 2. PREPARE DATAFRAME ---
        input_data = {
            "job_title": [job_title],
            "country": [country],
            "experience_level": [experience_level],
            "education_level": [education_level],
            "year": [year],
            "salary": [salary],
            "ai_risk_score": [ai_risk_score],
            "primary_skill": [primary_skill],
            "skill_demand_score": [skill_demand_score],
            "job_openings": [job_openings],
            "salary_bucket": [salary_bucket],       
            "ai_risk_category": [ai_risk_category] 
        }
        
        df = pd.DataFrame(input_data)
        
     
        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        jobImpact_Model = jobImpactModel(preprocessor=preprocessor, model=final_model)
        
        y_pred = jobImpact_Model.predict(df)
        predicted_class = int(y_pred[0])
        
        
        survival_mapping = {
            0: "High Risk (Unlikely to survive without adaptation)",
            1: "Evolving (Role will survive, but daily tasks will change heavily)",
            2: "Safe (Highly likely to survive as-is)"
        }
        
        human_readable_prediction = survival_mapping.get(predicted_class, "Unknown Risk Level")
        
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "prediction": human_readable_prediction}
        )
        
    except Exception as e:
        raise JobImpactException(e, sys)

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)
