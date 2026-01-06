from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import sanctioned_work_routes, station_routes, unit_routes, earning_routes, sync_routes
from utils import setup_logging, logger
from database import engine, Base
from fastapi.openapi.utils import get_openapi
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from api import station_routes, unit_routes, earning_routes, sync_routes, report_routes
from api import health_routes
from api import report_routes
setup_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Railway Stations & Units API", version="1.0.0")

# Enable CORS so that Next.js (port 3000) can talk to FastAPI (port 8000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # you can add more origins if needed (e.g. if deployed somewhere else)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(station_routes.router)
app.include_router(unit_routes.router)
app.include_router(earning_routes.router)
app.include_router(sync_routes.router)
app.include_router(health_routes.router)


app.include_router(sanctioned_work_routes.router)
app.include_router(report_routes.router)
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

# 🕑 APScheduler setup
scheduler = BackgroundScheduler()

def trigger_sync_all():
    sheet_id = '1JSlf6FOZMlSrb2wiAcb0LTk2BZYDPzvC98gNLfUDR-0'
    try:
        response = requests.post(
            "http://localhost:8000/sync/all",
            params={"sheet_id": sheet_id}
        )
        if response.status_code == 200:
            logger.info("✅ Periodic sync-all successful")
        else:
            logger.error(f"❌ Periodic sync-all failed: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"❌ Error during periodic sync-all: {e}")

# Schedule the sync to run every day at 2 AM
scheduler.add_job(trigger_sync_all, 'cron', hour=2, minute=0)
scheduler.start()

# main.py (or app.py)



# … existing setup …


