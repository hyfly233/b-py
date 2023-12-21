import bisect
import logging
import time
from asyncore import loop
from sys import exc_info
from traceback import format_exception

from pyasn1.codec.ber import encoder, decoder
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.error import PySnmpError
from pysnmp.proto import api
from pysnmp.proto.api import v2c

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)


class CustomAsyncoreDispatcher(AsyncoreDispatcher):
    def runDispatcher(self, timeout=0.0):
        while self.jobsArePending() or self.transportsAreWorking():
            try:
                loop(
                    timeout or self.getTimerResolution(),
                    use_poll=True,
                    map=super().getSocketMap(),
                    count=1,
                )
            except KeyboardInterrupt:
                raise
            except:
                # 自定义异常处理逻辑
                # raise PySnmpError('poll error: %s' % ';'.join(format_exception(*exc_info())))
                pyErr = PySnmpError(
                    "poll error: %s" % ";".join(format_exception(*exc_info()))
                )
                logging.error(pyErr)
            self.handleTimerTick(time.time())


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

        return api.protoModules[protoVer].Bits("xxxxx")


mibInstr = [Uptime()]  # sorted by object name

mibInstrIdx = {}
for mibVar in mibInstr:
    mibInstrIdx[mibVar.name] = mibVar


def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
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
        # GETNEXT PDU
        if reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
            # Produce response var-binds
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                errorIndex = errorIndex + 1
                # Search next OID to report
                nextIdx = bisect.bisect(mibInstr, oid)
                if nextIdx == len(mibInstr):
                    # Out of MIB
                    print(f"Out of MIB: {oid} {val}")
                    varBinds.append((oid, val))
                    pendingErrors.append((pMod.apiPDU.setEndOfMibError, errorIndex))
                else:
                    # Report value if OID is found
                    varBinds.append((mibInstr[nextIdx].name, mibInstr[nextIdx](msgVer)))
        elif reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                if oid in mibInstrIdx:
                    varBinds.append((oid, mibInstrIdx[oid](msgVer)))

                    # 使用下面的代码可以避免异常导致程序退出
                    # try:
                    #     varBind = mibInstrIdx[oid](msgVer)
                    #     varBinds.append((oid, varBind))
                    # except Exception as e:
                    #     print(f"Exception: {e}")
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

        transportDispatcher.sendMessage(
            encoder.encode(rspMsg), transportDomain, transportAddress
        )
    return wholeMsg


transportDispatcher = CustomAsyncoreDispatcher()
transportDispatcher.registerRecvCbFun(cbFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.domainName, udp.UdpSocketTransport().openServerMode(("0.0.0.0", 4161))
)

transportDispatcher.jobStarted(1)

try:
    # Dispatcher will never finish as job#1 never reaches zero
    transportDispatcher.runDispatcher()
except Exception as e:
    # todo
    transportDispatcher.closeDispatcher()
    raise
