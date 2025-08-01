from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Coordinate(BaseModel):
    latitude: float
    longitude: float

@app.get("/coordinates", response_model=List[Coordinate])
async def get_coordinates():
    coords = [
        {"latitude": 37.7749, "longitude": -122.4194},  # San Francisco
        {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles
        {"latitude": 40.7128, "longitude": -74.0060},   # New York
        {"latitude": 51.5074, "longitude": -0.1278},    # London
        {"latitude": 35.6895, "longitude": 139.6917},   # Tokyo
    ]
    return coords

