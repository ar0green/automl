# backend/app.py

import os
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.pipeline import run_pipeline
import uuid

app = FastAPI(title="AutoML Service")


class PipelineParams(BaseModel):
    target_column: str
    task_type: str = 'classification'
    sep: str = ','
    dataset_name: str = 'dataset'


tasks_status = {}


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
    background_tasks: BackgroundTasks
):
    data_files = os.listdir('data/')
    matched_files = [f for f in data_files if f.startswith(f"{file_id}_")]
    if not matched_files:
        return {"error": "File not found"}

    data_path = f"data/{matched_files[0]}"

    task_id = str(uuid.uuid4())
    report_id = str(uuid.uuid4())
    tasks_status[task_id] = "Running"

    background_tasks.add_task(
        run_pipeline_task,
        data_path,
        params,
        task_id,
        report_id
    )

    return {"task_id": task_id, "status": "Pipeline started", "report_id": report_id}


def run_pipeline_task(data_path, params, task_id, report_id):
    try:
        run_pipeline(
            data_path=data_path,
            column_names=None,
            target_column=params.target_column,
            task_type=params.task_type,
            sep=params.sep,
            dataset_name=params.dataset_name,
            report_id=report_id
        )
        tasks_status[task_id] = "Completed"
    except Exception as e:
        tasks_status[task_id] = f"Error: {str(e)}"


@app.get("/task_status/{task_id}")
def get_task_status(task_id: str):
    status = tasks_status.get(task_id, "Task not found")
    return {"task_id": task_id, "status": status}


@app.get("/download_report/{report_id}/{report_filename}")
def download_report(report_id: str, report_filename: str):
    report_path = os.path.join('src', 'reports', report_id, report_filename)
    if os.path.exists(report_path):
        return FileResponse(report_path, media_type='application/json', filename=report_filename)
    else:
        return {"error": "Report not found"}
