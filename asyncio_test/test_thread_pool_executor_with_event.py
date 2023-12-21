import asyncio
import concurrent.futures
import logging
import threading
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

# 创建一个全局的 Event 对象，用于通知线程停止 ??????????????????
stop_event = threading.Event()


async def task01():
    while not stop_event.is_set():
        logging.info("Task01 is running...")
        await asyncio.sleep(10)


def run_task02(sleep_time: int, stop_event_: threading.Event):
    while not stop_event_.is_set():
        logging.info("Task02 is running...")
        time.sleep(sleep_time)


async def task02():
    logging.info("Task02 start...")

    # 使用 ThreadPoolExecutor 将 run_task02 运行在一个单独的线程中
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, run_task02, 5, stop_event)


async def main():
    task_01 = asyncio.create_task(task01())
    task_02 = asyncio.create_task(task02())

    await asyncio.gather(task_01, task_02)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 没有打印 ??????????????????
        logging.info("Program interrupted and exiting...")
        # 设置 stop_event，通知所有任务停止
        stop_event.set()
        # 等待一段时间以确保所有任务都能优雅地停止
        time.sleep(10)
        logging.info("All tasks have been stopped.")
