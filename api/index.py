import secrets
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

API_KEY = "ak_hxm4p85s2grdwl8176yj3ae5"
EMAIL = "24f1000256@ds.study.iitm.ac.in"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def unauthorized():
    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})


@app.post("/analytics")
@app.post("/api/analytics")
@app.post("/api/index/analytics")
@app.post("/api/index")
async def analytics(request: Request):
    key = request.headers.get("x-api-key")
    if not key or not secrets.compare_digest(key, API_KEY):
        return unauthorized()

    try:
        body = await request.json()
        events = body.get("events", [])
        if not isinstance(events, list):
            events = []
    except Exception:
        events = []

    users = set()
    positive_totals = defaultdict(float)
    revenue = 0.0

    for event in events:
        if not isinstance(event, dict):
            continue
        user = event.get("user")
        users.add(user)
        try:
            amount = float(event.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0.0
        if amount > 0:
            revenue += amount
            positive_totals[user] += amount

    top_user = max(positive_totals, key=positive_totals.get) if positive_totals else None

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(users),
        "revenue": round(revenue, 6),
        "top_user": top_user,
    }


@app.get("/{full_path:path}")
def health(full_path: str, request: Request):
    return {"status": "ok", "path_seen": request.url.path}
