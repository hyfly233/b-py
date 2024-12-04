import asyncio
import concurrent.futures
import logging
import signal

from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import context, cmdrsp

'''
查看 https://github.com/pysnmp/pysnmp/blob/main/examples/v3arch/asyncio/agent/cmdrsp/multiple-usm-users.py
'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# 全局变量
exit_event = asyncio.Event()

async def task01():
    while not exit_event.is_set():
        logging.info("Task01 is running...")
        await asyncio.sleep(10)

async def task02():
    logging.info("Task02 is running...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    snmpEngine = engine.SnmpEngine()
    config.addTransport(snmpEngine, udp.domainName, udp.UdpTransport().openServerMode(('0.0.0.0', 4161)))
    config.addV1System(snmpEngine, "my-area", "public")
    config.addVacmUser(snmpEngine, 1, "my-area", "noAuthNoPriv", (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))

    snmpContext = context.SnmpContext(snmpEngine)

    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    try:
        loop.run_forever()
    finally:
        snmpEngine.transportDispatcher.closeDispatcher()
        logging.info("SNMP engine stopped.")

def run_task02():
    asyncio.run(task02())

async def main():
    task_01 = asyncio.create_task(task01())

    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        get_task = loop.run_in_executor(pool, run_task02)

        # 等待所有任务完成
        await asyncio.gather(task_01, get_task)

def handle_signal(loop, signal):
    logging.info(f"Received exit signal {signal.name}...")
    exit_event.set()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # 注册信号处理程序
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_signal, loop, sig)

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Program interrupted and exiting...")
    finally:
        loop.run_until_complete(exit_event.wait())
        loop.close()