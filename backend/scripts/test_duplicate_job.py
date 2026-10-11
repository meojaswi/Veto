import asyncio

from app.worker.jobs import process_return

RETURN_ID = "1ff9507c-b1b0-4bb5-a542-c144e54c43f7"


async def main():
    result = await process_return({}, RETURN_ID)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())