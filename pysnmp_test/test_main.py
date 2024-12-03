import asyncio
import concurrent.futures
import logging

from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import context, cmdrsp

'''
使用 kill 无法完全退出进程，只能使用 kill -9 强制退出
'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


async def task01():
    while True:
        logging.info("Task01 is running...")
        await asyncio.sleep(10)


def run_snmp_engine(snmpEngine):
    snmpEngine.transportDispatcher.jobStarted(1)
    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except Exception as e:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise e


async def task02():
    snmpEngine = engine.SnmpEngine()

    config.addTransport(
        snmpEngine, udp.domainName, udp.UdpTransport().openServerMode(('0.0.0.0', 4161))
    )

    communityIndex = "my-area"
    communityName = "public"

    config.addV1System(snmpEngine, communityIndex, communityName)

    logging.info(f"Get V1System communityIndex: {communityIndex} communityName: {communityName} ---")

    securityName = "my-area"
    securityLevel = "noAuthNoPriv"

    config.addVacmUser(
        snmpEngine, 1, securityName, securityLevel, (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1)
    )

    snmpContext = context.SnmpContext(snmpEngine)

    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)

    # 使用 ThreadPoolExecutor 将 SNMP 引擎运行在一个单独的线程中
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, run_snmp_engine, snmpEngine)


async def main():
    task_01 = asyncio.create_task(task01())
    task_02 = asyncio.create_task(task02())

    await asyncio.gather(task_01, task_02)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted and exiting...")
