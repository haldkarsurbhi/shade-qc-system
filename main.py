from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Fabric Shade Matching and Grouping",
    description="Backend API for fabric shade analysis and grouping",
    version="1.0"
)

# Allow frontend (React / UI) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later we can restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Backend running successfully"}

@app.get("/health")
def health_check():
    return {"status": "OK"}
