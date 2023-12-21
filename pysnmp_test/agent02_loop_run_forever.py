import asyncio
import logging

from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import context, cmdrsp

"""
查看 https://github.com/pysnmp/pysnmp/blob/main/examples/v3arch/asyncio/agent/cmdrsp/multiple-usm-users.py
"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

# 全局变量
exit_event = asyncio.Event()


async def task01():
    while not exit_event.is_set():
        logging.info("Task01 is running...")
        await asyncio.sleep(10)


async def task02():
    loop = asyncio.new_event_loop()

    snmpEngine = engine.SnmpEngine()

    config.addTransport(
        snmpEngine, udp.domainName, udp.UdpTransport().openServerMode(("0.0.0.0", 4161))
    )

    communityIndex = "my-area"
    communityName = "public"

    config.addV1System(snmpEngine, communityIndex, communityName)

    logging.info(
        f"Get V1System communityIndex: {communityIndex} communityName: {communityName} ---"
    )

    securityName = "my-area"
    securityLevel = "noAuthNoPriv"

    config.addVacmUser(
        snmpEngine,
        1,
        securityName,
        securityLevel,
        (1, 3, 6, 1, 2, 1),
        (1, 3, 6, 1, 2, 1),
    )

    snmpContext = context.SnmpContext(snmpEngine)

    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    loop.run_forever()


async def main():
    task_01 = asyncio.create_task(task01())
    task_02 = asyncio.create_task(task02())

    await asyncio.gather(task_01, task_02)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted and exiting...")
