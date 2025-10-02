from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allow all domains
    allow_credentials=True,
    allow_methods=["*"],            # Allow all methods: GET, POST, etc.
    allow_headers=["*"],  
    expose_headers=["*"]
    
)

with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/api/latency-check")
async def latency_check(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        if not records:
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        breaches = sum(1 for l in latencies if l > threshold)
        region_result = {
            "avg_latency": round(np.mean(latencies), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(np.mean(uptimes) / 100, 4),
            "breaches": breaches,
        }
        result[region] = region_result

    return JSONResponse(result)
