from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import StringIO
import traceback
import sys
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/code-interpreter")
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