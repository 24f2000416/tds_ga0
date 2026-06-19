from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

students_data = []

with open("q-fastapi.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        students_data.append({
            "studentId": int(row["studentId"]),
            "class": row["class"]
        })

@app.get("/api")
async def get_students(class_: list[str] = Query(default=None, alias="class")):

    if class_ is None:
        return {"students": students_data}

    return {
        "students": [
            s for s in students_data
            if s["class"] in class_
        ]
    }