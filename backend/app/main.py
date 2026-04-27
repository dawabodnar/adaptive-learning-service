from fastapi import FastAPI

app = FastAPI(title="Adaptive Learning Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}