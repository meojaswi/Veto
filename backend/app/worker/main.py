from arq.connections import RedisSettings

from app.config import settings
from app.worker.jobs import process_return


class WorkerSettings:
    functions = [process_return]

    redis_settings = RedisSettings.from_dsn(
        settings.redis_url
    )

    max_jobs = 5