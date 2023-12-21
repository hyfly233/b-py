import asyncio
import concurrent.futures

from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine as entity_engine, config as entity_config
from pysnmp.entity.rfc3413 import context as rfc3413_context

from pysnmp_test.override_cmdrsp import GetOwCommandResponder


# Main Function --------------------------


def run_snmp_engine(snmpEngine):
    snmpEngine.transportDispatcher.jobStarted(1)
    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except Exception as e:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise e


async def getMain():
    print("getMain running --------------- ")
    snmpEngine = entity_engine.SnmpEngine()

    entity_config.addTransport(
        snmpEngine, udp.domainName, udp.UdpTransport().openServerMode(("0.0.0.0", 4161))
    )

    entity_config.addV1System(snmpEngine, "my-area", "public")

    entity_config.addVacmUser(
        snmpEngine, 2, "my-area", "noAuthNoPriv", (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1)
    )

    snmpContext = rfc3413_context.SnmpContext(snmpEngine)

    GetOwCommandResponder(snmpEngine, snmpContext)

    # 使用 ThreadPoolExecutor 将 SNMP 引擎运行在一个单独的线程中
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, run_snmp_engine, snmpEngine)


async def main():
    get_task = asyncio.create_task(getMain())

    # 等待所有任务完成
    await asyncio.gather(get_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted and exiting...")
