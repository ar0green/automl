# backend/app.py

import os
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.pipeline import run_pipeline
import uuid
from src.database import engine
from src.models import Base
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import Report
import pandas as pd
import numpy as np
import mlflow

app = FastAPI(title="AutoML Service")

Base.metadata.create_all(bind=engine)


class PipelineParams(BaseModel):
    target_column: str
    task_type: str = 'classification'
    sep: str = ','
    dataset_name: str = 'dataset'

class InputData(BaseModel):
    features: list
    model_name: str = Query(..., description="Имя модели для предсказания")
    task_type: str = Query('classification', description="Тип задачи: classification или regression")


tasks_status = {}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload_data")
async def upload_data(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_location = f"data/{file_id}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"file_id": file_id, "filename": file.filename}


@app.get("/list_datasets")
def list_datasets():
    datasets = []
    data_dir = 'data'

    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            if '_' in f:
                parts = f.split('_', 1)
                if len(parts) == 2:
                    file_id, filename = parts
                    datasets.append({"file_id": file_id, "filename": filename})

    return {"datasets": datasets}


@app.get("/get_dataset_info")
def get_dataset_info(file_id: str):

    data_dir = 'data'
    if not os.path.exists(data_dir):
        raise HTTPException(status_code=404, detail="Data directory not found")
    matched_files = []
    for f in os.listdir(data_dir):
        if f.startswith(file_id + "_"):
            matched_files.append(f)

    if not matched_files:
        raise HTTPException(
            status_code=404, detail="File not found for given file_id")

    print(matched_files)
    filename = matched_files[0]

    full_path = os.path.join(data_dir, filename)
    print(filename)
    try:
        df = pd.read_csv(full_path, nrows=0)
        columns = list(df.columns)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read file: {str(e)}")

    return {"columns": columns}


@app.get("/list_pipelines")
def list_pipelines(db: Session = Depends(get_db)):
    reports = db.query(Report).all()
    pipelines = []
    for r in reports:
        pipelines.append({
            "task_id": r.task_id,
            "report_id": r.report_id,
            "status": r.status,
            "dataset_name": r.dataset_name,
            "model_name": r.model_name,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return {"pipelines": pipelines}

@app.post("/run_pipeline/{file_id}")
async def run_pipeline_endpoint(
    file_id: str,
    params: PipelineParams,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    data_files = os.listdir('data/')
    matched_files = [f for f in data_files if f.startswith(f"{file_id}_")]
    if not matched_files:
        return {"error": "File not found"}

    data_path = f"data/{matched_files[0]}"

    task_id = str(uuid.uuid4())
    report_id = str(uuid.uuid4())
    tasks_status[task_id] = "Running"

    new_report = Report(
        report_id=report_id,
        task_id=task_id,
        status='Running'
    )
    db.add(new_report)
    db.commit()

    background_tasks.add_task(
        run_pipeline_task,
        data_path,
        params,
        task_id,
        report_id,
        db
    )

    return {"task_id": task_id, "status": "Pipeline started", "report_id": report_id}


def run_pipeline_task(data_path, params, task_id, report_id, db: Session):
    try:
        report = db.query(Report).filter(Report.task_id == task_id).first()
        report.status = 'Running'
        db.commit()

        run_pipeline(
            data_path=data_path,
            column_names=None,
            target_column=params.target_column,
            task_type=params.task_type,
            sep=params.sep,
            dataset_name=params.dataset_name,
            report_id=report_id,
            db=db  # Передаём сессию БД
        )

        # Обновляем статус задачи в БД
        report.status = 'Completed'
        db.commit()
    except Exception as e:
        # Обновляем статус задачи в БД
        report.status = f"Error: {str(e)}"
        db.commit()

@app.post("/predict")
def predict(data: InputData):
    model_path = f'models/{data.model_name}'
    if not os.path.exists(model_path):
        return {"error": "Model not found."}

    model = mlflow.sklearn.load_model(model_path)

    input_array = np.array(data.features).reshape(1, -1)
    prediction = model.predict(input_array)

    if data.task_type == 'classification':
        prediction = prediction.astype(int).tolist()
    else:
        prediction = prediction.tolist()

    return {"prediction": prediction}

@app.get("/task_status/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.task_id == task_id).first()
    if report:
        return {"task_id": task_id, "status": report.status}
    else:
        return {"error": "Task not found"}


@app.get("/download_report/{report_id}")
def download_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if report:
        return {
            "report_id": report_id,
            "dataset_name": report.dataset_name,
            "model_name": report.model_name,
            "report_data": report.report_data,
            "mlflow_data": report.mlflow_data
        }
    else:
        return {"error": "Report not found"}
