from fastapi import FastAPI
from app.routes.mpesa_route import mpesa_router
from app.routes import vending
from app.core.database import Base, engine
from app.routes.meter_routes import router as meter_router
from app.routes.aggregate_route import router as aggregate_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="M-Pesa API Backend")

app.include_router(mpesa_router)
app.include_router(vending.router)
app.include_router(meter_router)
app.include_router(aggregate_router)


@app.get("/")
def root():
    return {"message": "Welcome to the M-Pesa API Backend"}
