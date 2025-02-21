from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from core.config import logger
from models.model import MonitorPayload
from monitoring.monitor import monitor_task

api_router = APIRouter()


@api_router.get("/application.json")
def get_integration_json(request: Request, status_code: int = status.HTTP_200_OK):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "date": {"created_at": "2025-02-20", "updated_at": "2025-02-20"},
            "descriptions": {
                "app_name": "Twitter NG Trends Monitor",
                "app_description": "Retrieves the 5 latest tweets from the top 10 trending tweets on Twitter Ng",
                "app_url": base_url,
                "app_logo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzqnmyNlygtds5hKfmdUIXfzlFkqzQDuack_Y0ekPJpqaJO-R1JgbgszHZEApPN9oNPpw&usqp=CAU",
            },
            "key_features": [
                "Fetches the 5 latest tweets from the top 10 trending tweets on Twitter Ng",
                "Runs every hour",
                "Logs the tweets",
            ],
            "integration_category": "Monitoring & Logging",
            "integration_type": "interval",
            "is_active": True,
            "settings": [
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "0 * * * *",
                }
            ],
            "tick_url": f"{base_url}/tick",
            "target_url": "",
        }
    }


@api_router.post("/tick", status_code=202)
def monitor(payload: MonitorPayload, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(monitor_task, payload)
        return {"status": "accepted"}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
