from fastapi import FastAPI
import torch
import torch.nn as nn
import numpy as np

app = FastAPI()

class SimpleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(16, 3)

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.layer2(x)
        return x

model = None

@app.on_event("startup")
def load_model():
    global model
    model = SimpleClassifier()
    model.load_state_dict(torch.load("model.pth", map_location="cpu"))
    model.eval()

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}

@app.post("/predict")
def predict(data: dict):

    features = np.array(data["features"], dtype=np.float32)
    x = torch.tensor(features).unsqueeze(0)

    with torch.no_grad():
        output = model(x)
        prediction = torch.argmax(output, dim=1).item()

    class_names = ["setosa", "versicolor", "virginica"]

    return {
        "prediction": class_names[prediction],
        "raw_prediction": prediction
    }