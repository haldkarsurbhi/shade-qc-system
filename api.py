from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil, os
import numpy as np

from color_engine import preprocess_roi, extract_lab_stats
from grouping import assign_shade_group
from data_store import save_results

app = FastAPI()
@app.get("/")
def root():
    return {"status": "Shade QC backend running"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "IMAGES"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MASTER_LAB = None

@app.post("/set-master")
async def set_master(image: UploadFile):
    global MASTER_LAB
    path = f"{UPLOAD_DIR}/master.jpg"
    with open(path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    roi = preprocess_roi(path)
    MASTER_LAB, _ = extract_lab_stats(roi)

    return {"status": "Master shade set"}

@app.post("/analyze")
async def analyze_roll(
    roll_no: str = Form(...),
    quantity: float = Form(...),
    image: UploadFile = Form(...)
):
    path = f"{UPLOAD_DIR}/{roll_no}.jpg"
    with open(path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    roi = preprocess_roi(path)
    mean_lab, _ = extract_lab_stats(roi)

    from color_engine import delta_e_2000
    delta_e = delta_e_2000(mean_lab, MASTER_LAB)

    shade, decision = assign_shade_group(delta_e)

    result = [{
        "roll_no": roll_no,
        "lab": mean_lab,
        "delta_e": delta_e,
        "shade_group": shade,
        "decision": decision,
        "quantity": quantity,
        "image": path
    }]

    save_results([{
        "roll_no": roll_no,
        "L*": mean_lab[0],
        "a*": mean_lab[1],
        "b*": mean_lab[2],
        "delta_e": round(delta_e,2),
        "shade_group": shade,
        "decision": decision
    }])

    return result[0]
