from fastapi import FastAPI
from Servicio.Utils.Register import Writer,Read
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from Servicio.database import engine, Base
from datetime import datetime
import time

from Servicio.function import create_instance_startup, Exit_service

from Servicio.router.agents_router import router as agents_router
from Servicio.router.features_router import router as features_router
from Servicio.router.aditionals_router import router as aditional_router
from Servicio.router.history_router import router as history_router
from Servicio.router.manageables_router import router as manageable_router
from Servicio.router.alarms_router import router as alarms_router
from Servicio.router.traps_router import router as traps_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan function started")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_instance_startup()
    # asyncio.create_task(Ping().Exectping())
    print("Lifespan function finished")
    await Read()
    try:
        Writer(f"\ndatestartup = : {datetime.now()}\n")
        start_time = time.time()
        yield
    finally:
        end_time = time.time()
        Writer(f"datestop = : {datetime.now()}\n")
        Writer(f"totaltime = {end_time - start_time}\n\n")
        await Exit_service()


app = FastAPI(lifespan=lifespan)
app.include_router(agents_router)
app.include_router(features_router)
app.include_router(aditional_router)
app.include_router(history_router)
app.include_router(manageable_router)
app.include_router(alarms_router)
app.include_router(traps_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
