import time

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from sqladmin import Admin

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.hotels.rooms.router import router as router_rooms
from app.hotels.router import router as router_hotels
from app.images.router import router as router_images
from app.logger import logger
from app.pages.router import router as router_pages
from app.prometheus.router import router as router_prometheus
from app.users.router import router_auth, router_users

app = FastAPI(
    title="Booking Hotels",
    version="0.1.0",
    root_path="/api",
)


if settings.MODE != 'TEST':
    # Sentry connection for error monitoring. It is better to turn it off for the period of local testing
    sentry_sdk.init(
        dsn='https://4e010531b2b04e5e45e5aca17aa09825@o4505772443172864.ingest.sentry.io/4505772444942336',
        traces_sample_rate=1.0,
    )

# Connection the main router
app.include_router(router_users)
app.include_router(router_auth)
app.include_router(router_bookings)
app.include_router(router_hotels)

# Connection the extra router
app.include_router(router_rooms)
app.include_router(router_pages)
app.include_router(router_images)
app.include_router(router_prometheus)


# Connecting CORS so API requests can come from the browser
origins = [
    # 3000 is the port on which the React.js frontend is running
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)

app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}')

app.include_router(router_pages)

if settings.MODE == "TEST":
    # When testing with pytest, Redis must be enabled for caching to work.
    # Otherwise, the @cache decorator from the fastapi-cache library breaks cached endpoints.
    # From this follows the conclusion that third-party solutions sometimes break our code, and this can be problematic to fix.
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


@app.on_event("startup")
def startup():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=['.*admin.*', '/metrics'],
)

instrumentator.instrument(app).expose(app)


# Connecting the admin panel
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(HotelsAdmin)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # When connecting Prometheus + Grafana, signal registration is not required
    logger.info('Request handling time', extra={
        'process_time': round(process_time, 4)
    })
    return response

app.mount('/static', StaticFiles(directory='app/static'), 'static')


@app.on_event("startup")
async def _startup():
    instrumentator.expose(app)






