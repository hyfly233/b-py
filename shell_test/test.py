import logging
import os
import threading

import uvicorn
from fastapi import FastAPI, APIRouter

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s')


def start_fast_api(httpPort: int):
    app = FastAPI(title="test", description="test", version="1.0.0")

    router = APIRouter(
        prefix="/test",
        tags=["test"],
        responses={404: {"description": "Not found"}}
    )

    @router.get("/getPort")
    def getPort():
        logging.info(f"getPort: {httpPort} pid: {os.getgid()} ppid: {os.getppid()} tid: {threading.get_ident()}")
        return httpPort

    app.include_router(router)

    config = uvicorn.Config(app, host="0.0.0.0", port=httpPort, log_level="info")
    server = uvicorn.Server(config)
    server.run()


def main():
    thread1 = threading.Thread(target=start_fast_api, args=(23333,))
    thread2 = threading.Thread(target=start_fast_api, args=(23334,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted and exiting...")
