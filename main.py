from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import sanctioned_work_routes, station_routes, unit_routes, earning_routes, sync_routes, report_routes, health_routes
from utils import setup_logging, logger
from database import engine, Base
from fastapi.openapi.utils import get_openapi
from apscheduler.schedulers.background import BackgroundScheduler
import requests

# ───────────────────────────────
# Setup
# ───────────────────────────────
setup_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Railway Stations & Units API",
    version="1.0.0"
)

# ───────────────────────────────
# CORS (Flutter + Web + Render)
# ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # allow Flutter web, mobile, localhost, Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────
# Routers
# ───────────────────────────────
app.include_router(station_routes.router)
app.include_router(unit_routes.router)
app.include_router(earning_routes.router)
app.include_router(sync_routes.router)
app.include_router(health_routes.router)
app.include_router(sanctioned_work_routes.router)
app.include_router(report_routes.router)

# ───────────────────────────────
# Swagger branding
# ───────────────────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API for managing railway stations, units, earnings, and Google Sheet syncing",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Indian_Railways.svg/640px-Indian_Railways.svg.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ───────────────────────────────
# Background Google Sheet Sync
# ───────────────────────────────
scheduler = BackgroundScheduler()

def trigger_sync_all():
    sheet_id = "1JSlf6FOZMlSrb2wiAcb0LTk2BZYDPzvC98gNLfUDR-0"
    try:
        response = requests.post(
            "https://railway-dash-backend.onrender.com/sync/all",
            params={"sheet_id": sheet_id}
        )

        if response.status_code == 200:
            logger.info("✅ Periodic sync-all successful")
        else:
            logger.error(f"❌ Sync failed: {response.status_code} {response.text}")

    except Exception as e:
        logger.error(f"❌ Error during sync: {e}")

# Run daily at 2AM
scheduler.add_job(trigger_sync_all, "cron", hour=2, minute=0)
scheduler.start()
