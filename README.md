# AutoMLPipeline

This project is an auto-ML platform for automating the training and application of ML models to user-uploaded datasets. It provides:

- Web interface (React + Material UI) for uploading data, configuring pipelines, viewing statuses and reports, and applying trained models.
- Backend (FastAPI + PostgreSQL + MLflow) for data management, pipeline execution, experiment logging, storing, and retrieving reports.
- Containerization (Docker, Docker Compose) for easy deployment and running of the project.

## **Features**

1. Data Upload:
    
    Users can upload their datasets (e.g., CSV files) through the web interface. The files are stored on the server and registered in the system.

2. Dataset Selection & Configuration:
    
    On the "Configure Pipeline" page, users can select one of the uploaded datasets from a list, retrieve its columns, and configure the pipeline parameters such as target column, task type (classification or regression), model choice (Random Forest, Logistic Regression, XGBoost, LightGBM), dataset name, and separators.

3. Pipeline Execution:
    
    After configuration, the user can run an auto-ML pipeline that trains a model based on the selected parameters. The pipeline logs experiments and results in MLflow.

4. Status Monitoring:

    The "Pipelines Status" page shows all running or completed pipelines, including their task_id, report_id, status, dataset name, and model name. Users can also view the corresponding reports directly from this page.

5. Report Viewing:  
    
    Once training is complete, users can retrieve a report (in JSON format) that includes performance metrics, model parameters, and experiment logs.

6. Model Application:
    
    A dedicated page allows users to upload new data and apply a previously trained model to generate predictions.

## **Project Structure**
```grapql
AutoMLPipeline/
├─ backend/
│  ├─ Dockerfile
│  ├─ requirements.txt
│  ├─ app.py                  # FastAPI entry point
│  ├─ src/
│  │  ├─ pipeline.py          # Pipeline launch and training logic
│  │  ├─ utils.py             # Utility functions
│  │  ├─ models.py            # SQLAlchemy models
│  │  ├─ database.py          # DB connection
│  │  ├─ reports/             # directory for reports if needed
│  ├─ data/                   # Directory for uploaded datasets
│  ├─ models/                 # Directory for saved models if needed
│  ├─ mlruns/                 # MLflow artifacts
│  ├─ mlflow.db               # SQLite database for MLflow
│  └─ ...
├─ frontend/
│  ├─ Dockerfile
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ UploadData.js
│  │  │  ├─ PipelineForm.js
│  │  │  ├─ TaskStatus.js
│  │  │  ├─ DownloadReport.js
│  │  │  ├─ ApplyModel.js
│  │  │  ├─ StatusPipeline.js
│  │  ├─ App.js
│  │  ├─ index.js
│  ├─ public/
│  ├─ package.json
│  └─ ...
├─ docker-compose.yml
└─ README.md

```

## **Prerequisites**

- Docker and Docker Compose installed on your machine.
- Sufficient memory and CPU for building and running the containers (recommended at least 4GB RAM).

## **Installation and Launch**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ar0green/AutoMLPipeline.git
    cd AutoMLPipeline
   ```

2. **Build and start containers:**

    ```bash
    docker-compose up --build 
    ```

    This will start the following services:

        backend on port 8000
        frontend on port 3000
        mlflow on port 5000
        db (PostgreSQL) on port 5432

3. **Open the web interface:**
    
    Go to http://localhost:3000 in your browser.

## **UI Pages**

- Upload Data: Upload a new dataset.
- Configure Pipeline: Select a dataset, choose target column, model, etc., and run the pipeline.
- View Reports: View previously generated reports (JSON format).
- Models → Apply Model: Apply a trained model to new data.
- Pipelines Status: Monitor the status of all pipelines and view their reports.

## **UI Pages**

- **/api/upload_data(POST)**: Upload a dataset.
- **/api/list_datasets (GET)**: List all uploaded datasets.
- **/api/get_dataset_info?file_id={file_id} (GET)**: Retrieve dataset columns.
- **/api/run_pipeline/{file_id} (POST)**: Run the pipeline for the specified dataset.
- **/api/task_status/{task_id} (GET)**: Get the status of a specific pipeline.
- **/api/download_report/{report_id} (GET)**: Retrieve the report for a completed pipeline.
- **/api/list_pipelines (GET)**: List all pipelines and their statuses.

## **Database**

- PostgreSQL is used for storing pipeline metadata and reports.
- SQLAlchemy and Alembic for schema management and migrations.
- Reports and statuses are stored in the database for easy retrieval.

## **Example Workflow**

1. Upload Data: Go to "Upload Data" and upload a CSV file.
2. Configure Pipeline: Go to "Configure Pipeline," select the uploaded dataset, choose the target column and model, and run the pipeline.
3. Monitor Status: Go to "Pipelines Status" to see if the pipeline has completed. View the report once it’s done.
4. Apply Model: If you need to apply the trained model to new data, go to "Apply Model" and upload another dataset.

## **MLflow Integration**

- MLflow UI is available at http://localhost:5000.
- MLflow logs parameters, metrics, and models for each pipeline run.
- You can view, compare, and track experiments and model versions.

