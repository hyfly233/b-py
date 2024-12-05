import asyncio
import concurrent.futures
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


async def task01():
    while True:
        logging.info("Task01 is running...")
        await asyncio.sleep(10)


def run_task02(sleep_time: int):
    while True:
        logging.info("Task02 is running...")
        time.sleep(sleep_time)


async def task02():
    logging.info("Task02 start...")

    # 使用 ThreadPoolExecutor 将 SNMP 引擎运行在一个单独的线程中
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, run_task02, 5)


async def main():
    task_01 = asyncio.create_task(task01())
    task_02 = asyncio.create_task(task02())

    await asyncio.gather(task_01, task_02)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted and exiting...")
