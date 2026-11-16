from contextlib import asynccontextmanager
from typing import Annotated
import joblib
import pandas as pd
from fastapi import FastAPI, Query
from sqlmodel import select
import shap
from app.db import create_db_and_tables, SessionDep, DiamondLog, DiamondLogPublic
from app.schemas import Diamond, PredictionOutput

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Diamond-Cut-Api", lifespan=lifespan)

def get_eng_body(body):
    body['price_per_carat'] = body['price'] / body['carat']
    body['x/y'] = body['x'] / body['y']
    body['z/x'] = body['z'] / body['x']
    body['volume_per_carat'] = body['carat'] / (body['x'] * body['y'] * body['z'])
    return {k:v for k,v in body.items() if k not in ['x','y','z','price']}

@app.get("/")
def root():
    return {"message":"Hello World!"}

@app.post("/predict_cut", response_model=PredictionOutput)
def predict_cut(diamond:Diamond, session: SessionDep):
    body = diamond.model_dump()
    body_df = pd.DataFrame([get_eng_body(body)])

    pipe = joblib.load('pipeline/model_pipeline.joblib')
    y_enc = joblib.load('pipeline/y_encoder.joblib')

    pred_probs = pipe.predict_proba(body_df)
    pred = pipe.predict(body_df)
    prob = round(float(pred_probs[0][pred]),2)
    cut = y_enc.inverse_transform([pred])[0,0]

    db_row = DiamondLog(query=body, cut=cut, probability=prob)
    session.add(db_row)
    session.commit()
    session.refresh(db_row)

    return PredictionOutput(cut=cut, probability=prob)


@app.get("/get_cut_prediction_logs", response_model=list[DiamondLogPublic])
def get_cut_prediction_logs(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    predictions = session.exec(select(DiamondLog).offset(offset).limit(limit)).all()
    return predictions

@app.post("/get_cut_prediction_explanation")
def get_cut_prediction_explanation(diamond:Diamond):
    body = diamond.model_dump()
    body = pd.DataFrame([get_eng_body(body)])
    pipe = joblib.load('pipeline/model_pipeline.joblib')
    model = pipe['model']
    preprocessor = pipe['prep']
    features = [col.split("__")[1] for col in list(preprocessor.get_feature_names_out())]

    body_t = preprocessor.transform(body)

    y_enc = joblib.load('pipeline/y_encoder.joblib')

    pred = pipe.predict(body)
    cut = y_enc.inverse_transform([pred])[0, 0]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(body_t)
    print(shap_values[0,:,pred][0])
    combined =sorted(zip(features,shap_values[0,:,pred][0]), key=lambda x: abs(x[1]),reverse=True)[:5]
    return {
        'score': round(float(sum(shap_values[0,:,pred][0])), 2),
        'cut_class': cut,
        'Top 5 most impactful features':
            [
                {
                    'feature': feat,
                    'value': float(value),
                }
                for feat, value in combined
            ]}