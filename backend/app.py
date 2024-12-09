# backend/app.py

import os
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
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


app = FastAPI(title="AutoML Service")

Base.metadata.create_all(bind=engine)

class PipelineParams(BaseModel):
    target_column: str
    task_type: str = 'classification'
    sep: str = ','
    dataset_name: str = 'dataset'


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
