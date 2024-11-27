from fastapi import FastAPI
from pydantic import BaseModel
import mlflow.sklearn
import numpy as np
import uvicorn

model = mlflow.sklearn.load_model('models/best_model')

app = FastAPI(title="AutoML API")


class InputData(BaseModel):
    features: list


@app.get("/")
def read_root():
    return {"message": "AutoML API is up and running!"}


@app.post("/predict")
def predict(data: InputData):
    input_array = np.array(data.features).reshape(1, -1)
    prediction = model.predict(input_array)
    return {"prediction": prediction.tolist()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
