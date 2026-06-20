from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv
from pydantic import BaseModel
from io import StringIO
import traceback
import sys
import re


app1 = FastAPI()

app1.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5
class CodeRequest(BaseModel):
    code: str

def execute_python_code(code: str):
    old_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        exec(code)

        return {
            "success": True,
            "output": captured_output.getvalue()
        }

    except Exception:
        return {
            "success": False,
            "output": traceback.format_exc()
        }

    finally:
        sys.stdout = old_stdout

@app1.post("/code-interpreter")
async def code_interpreter(request: CodeRequest):

    result = execute_python_code(request.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    tb = result["output"]

    
    matches = re.findall(r'File "<string>", line (\d+)', tb)

    if matches:
        error_lines = [int(matches[-1])]
    else:
        error_lines = []

    return {
        "error": error_lines,
        "result": tb
    }
    


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