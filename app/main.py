from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import shutil
import os

from app.pdf_utils import apply_stamp

app = FastAPI()

CONFIG_DIR = "app/config"
os.makedirs(CONFIG_DIR, exist_ok=True)

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate(
    request: Request,
    pdf: UploadFile = File(...)
):
    pdf_path = f"{UPLOAD_DIR}/{pdf.filename}"
    output_filename = f"stamped_{pdf.filename}"
    output_path = f"{UPLOAD_DIR}/{output_filename}"

    seal_path = "app/config/seal.png"
    sign_path = "app/config/signature.png"

    if not os.path.exists(seal_path) or not os.path.exists(sign_path):
        return {"error": "Seal or signature not configured. Please run setup first."}

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    apply_stamp(pdf_path, seal_path, sign_path, output_path)

    return templates.TemplateResponse(
        "preview.html",
        {
            "request": request,
            "file_url": f"/static/uploads/{output_filename}",
            "filename": output_filename
        }
    )




@app.post("/setup")
async def setup_config(
    seal: UploadFile = File(...),
    signature: UploadFile = File(...)
):
    seal_path = f"{CONFIG_DIR}/seal.png"
    sign_path = f"{CONFIG_DIR}/signature.png"

    with open(seal_path, "wb") as f:
        shutil.copyfileobj(seal.file, f)

    with open(sign_path, "wb") as f:
        shutil.copyfileobj(signature.file, f)

    return {"message": "Configuration saved successfully"}

