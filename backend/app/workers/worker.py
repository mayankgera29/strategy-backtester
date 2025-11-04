import asyncio
import logging
import traceback
from app.db.session import async_session
from app.db import crud
from app.services.simulator import run_backtest_simulation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

async def process_job(job):
    job_id = job.id
    logger.info(f"Processing job {job_id}")
    try:
        result = await run_backtest_simulation(job.payload)
        async with async_session() as db:
            await crud.save_backtest_result(db, job_id, result)
        logger.info(f"Finished job {job_id}")
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Job {job_id} failed: {e}\\n{tb}")
        async with async_session() as db:
            await crud.mark_job_failed(db, job_id, error=str(e))

async def worker_loop(poll_interval: float = 2.0):
    logger.info("Worker loop started")
    while True:
        try:
            async with async_session() as db:
                job = await crud.fetch_next_queued_job(db)
            if job:
                await process_job(job)
            else:
                await asyncio.sleep(poll_interval)
        except Exception as e:
            logger.exception("Unexpected worker exception: %s", e)
            await asyncio.sleep(5)

def main():
    asyncio.run(worker_loop())

if __name__ == '__main__':
    main()
