import asyncio
import concurrent.futures
import logging
import time

from pyasn1.codec.ber import encoder, decoder
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.proto import api
from pysnmp.proto.api import v2c

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class SysDescr:
    name = (1, 3, 6, 1, 2, 1, 1, 1, 0)

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __lt__(self, other):
        return self.name < other

    def __le__(self, other):
        return self.name <= other

    def __gt__(self, other):
        return self.name > other

    def __ge__(self, other):
        return self.name >= other

    def __call__(self, protoVer):
        return api.protoModules[protoVer].OctetString(
            "PySNMP example command responder"
        )


class Uptime:
    name = (1, 3, 6, 1, 2, 1, 1, 3, 0)
    birthday = time.time()

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __lt__(self, other):
        return self.name < other

    def __le__(self, other):
        return self.name <= other

    def __gt__(self, other):
        return self.name > other

    def __ge__(self, other):
        return self.name >= other

    def __call__(self, protoVer):
        # return api.protoModules[protoVer].TimeTicks((time.time() - self.birthday) * 100)

        # module 'pysnmp.proto.api.v1' has no attribute 'Bits'
        return api.protoModules[protoVer].Bits(
            "xxxxx"
        )


async def task01():
    while True:
        logging.info("Task01 is running...")
        await asyncio.sleep(10)


def run_transport_dispatcher(transportDispatcher):
    transportDispatcher.jobStarted(1)
    try:
        transportDispatcher.runDispatcher()
    except Exception as e:
        transportDispatcher.closeDispatcher()
        logging.error(f"Exception: {e}")


async def task02():
    logging.info("Task02 is running...")

    mibInstr = (SysDescr(), Uptime())  # sorted by object name

    mibInstrIdx = {}
    for mibVar in mibInstr:
        mibInstrIdx[mibVar.name] = mibVar

    def cbFun(transport_dispatcher, transportDomain, transportAddress, wholeMsg):
        while wholeMsg:
            msgVer = api.decodeMessageVersion(wholeMsg)
            if msgVer in api.protoModules:
                pMod = api.protoModules[msgVer]
            else:
                print("Unsupported SNMP version %s" % msgVer)
                return
            reqMsg, wholeMsg = decoder.decode(
                wholeMsg,
                asn1Spec=pMod.Message(),
            )

            # print(f"reqMsg: {reqMsg}")

            print(f"-------------------")

            rspMsg = pMod.apiMessage.getResponse(reqMsg)
            rspPDU = pMod.apiMessage.getPDU(rspMsg)
            reqPDU = pMod.apiMessage.getPDU(reqMsg)

            requestId = v2c.apiPDU.getRequestID(rspPDU)
            print(f"requestId: {requestId} ---------------")

            print(f"-------------------")

            varBinds = []
            pendingErrors = []
            errorIndex = 0

            if reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
                for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                    if oid in mibInstrIdx:
                        varBinds.append((oid, mibInstrIdx[oid](msgVer)))
                    else:
                        # No such instance

                        print(f"No such instance: {oid} {val}")
                        varBinds.append((oid, val))
                        pendingErrors.append(
                            (pMod.apiPDU.setNoSuchInstanceError, errorIndex)
                        )
                        break
            else:
                # Report unsupported request type
                pMod.apiPDU.setErrorStatus(rspPDU, "genErr")
            pMod.apiPDU.setVarBinds(rspPDU, varBinds)
            # Commit possible error indices to response PDU
            for f, i in pendingErrors:
                f(rspPDU, i)

            for varBind in varBinds:  # SNMP response contents
                oid = varBind[0]
                val = varBind[1]

                print(f"oid type: {type(oid)}, val type: {type(val)}")

                print(f"oid: {oid}, val: {str(val)}")

            print(f"-------------------")

            # print(f"rspMsg: {rspMsg}")

            transport_dispatcher.sendMessage(
                encoder.encode(rspMsg), transportDomain, transportAddress
            )
        return wholeMsg

    transportDispatcher = AsyncoreDispatcher()
    transportDispatcher.registerRecvCbFun(cbFun)
    transportDispatcher.registerTransport(
        udp.domainName, udp.UdpSocketTransport().openServerMode(("0.0.0.0", 4161))
    )

    # 使用 ThreadPoolExecutor 将 SNMP 引擎运行在一个单独的线程中
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, run_transport_dispatcher, transportDispatcher)


async def main():
    task_01 = asyncio.create_task(task01())
    task_02 = asyncio.create_task(task02())

    await asyncio.gather(task_01, task_02)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted and exiting...")
