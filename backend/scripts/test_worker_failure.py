
import asyncio
from unittest.mock import patch

from sqlalchemy import select

from app.db.models import Return
from app.db.session import SessionLocal
from app.worker.jobs import process_return

RETURN_ID = "56e84fa3-231d-476a-bd61-777ea1c85296"


async def main():
    print("TEST STARTED", flush=True)

    with patch(
        "app.worker.jobs.return_graph.ainvoke",
        side_effect=RuntimeError("Simulated pipeline failure"),
    ) as mocked_graph:
        try:
            await process_return({}, RETURN_ID)
        except RuntimeError as exc:
            assert str(exc) == "Simulated pipeline failure"
            print("EXPECTED TEST ERROR:", exc, flush=True)
        else:
            raise AssertionError("Expected pipeline failure, but none occurred")

        assert mocked_graph.called, "Pipeline graph was not called"

    async with SessionLocal() as db:
        result = await db.execute(
            select(Return).where(Return.id == RETURN_ID)
        )
        item = result.scalar_one()

        assert item.status == "failed", (
            f"Expected status 'failed', got {item.status!r}"
        )

    print("GRAPH CALLED: True", flush=True)
    print("DATABASE STATUS: failed", flush=True)
    print("TEST PASSED", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
