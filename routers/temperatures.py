from typing import List, Optional
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import get_db


router = APIRouter(prefix="/temperatures", tags=["Temperatures"])


async def fetch_temperature(city_name: str) -> float:
    async with httpx.AsyncClient() as client:
        geo_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_name, "count": 1}
        )
        geo_data = geo_response.json()

        if "results" not in geo_data:
            raise ValueError(f"City '{city_name}' not found")

        latitude = geo_data["results"][0]["latitude"]
        longitude = geo_data["results"][0]["longitude"]

        weather_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True
            }
        )
        weather_data = weather_response.json()

        return weather_data["current_weather"]["temperature"]


@router.post("/update")
async def update_temperatures(db: Session = Depends(get_db)):
    cities = crud.get_cities(db=db)

    results = []

    for city in cities:
        try:
            temp = await fetch_temperature(city.name)

            temperature_record = crud.create_temperature(
                db=db,
                city_id=city.id,
                temperature=temp,
                date_time=datetime.utcnow()
            )

            results.append(temperature_record)

        except Exception as e:
            continue

    return {
        "message": "Temperatures updated",
        "records_created": len(results)
    }


@router.get(
    "",
    response_model=List[schemas.TemperatureRead]
)
def get_temperatures(
    city_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    if city_id is not None:
        return crud.get_temperature_by_city(db=db, city_id=city_id)

    return crud.get_temperature(db=db)
