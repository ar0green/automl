from fastapi import FastAPI, Query
from pydantic import BaseModel
import mlflow.sklearn
import numpy as np
import uvicorn
import os

app = FastAPI(title="AutoML API")

class InputData(BaseModel):
    features: list
    model_name: str = Query(..., description="Имя модели для предсказания")
    task_type: str = Query('classification', description="Тип задачи: classification или regression")

@app.get("/")
def read_root():
    return {"message": "AutoML API is up and running!"}

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
