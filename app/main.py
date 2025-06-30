from fastapi import FastAPI
from app.routers import production_plan

app = FastAPI()

app.include_router(production_plan.router)
