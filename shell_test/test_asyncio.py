import asyncio
import logging

import uvicorn
from fastapi import FastAPI, APIRouter


async def start_fast_api(httpPort: int):
    app = FastAPI(title="test", description="test", version="1.0.0")

    router = APIRouter(
        prefix="/test",
        tags=["test"],
        responses={404: {"description": "Not found"}}
    )

    @router.get("/getPort")
    async def getPort():
        logging.info(f"getPort: {httpPort}")
        return httpPort

    app.include_router(router)

    config = uvicorn.Config(app, host="0.0.0.0", port=httpPort, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        start_fast_api(23333),
        start_fast_api(23334)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted and exiting...")
