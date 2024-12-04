"""
Implementing scalar MIB objects
+++++++++++++++++++++++++++++++

Listen and respond to SNMP GET/GETNEXT queries with the following options:

* SNMPv1 or SNMPv2c
* with SNMP community "public"
* over IPv4/UDP, listening at 127.0.0.1:161
* over IPv6/UDP, listening at [::1]:161
* serving two Managed Objects Instances (sysDescr.0 and sysUptime.0)

Either of the following Net-SNMP commands will walk this Agent:

| $ snmpwalk -v2c -c public 127.0.0.1 .1.3.6
| $ snmpwalk -v2c -c public udp6:[::1] .1.3.6

The Command Receiver below uses two distinct transports for communication 
with Command Generators - UDP over IPv4 and UDP over IPv6.


https://github.com/pysnmp/pysnmp/blob/main/examples/v1arch/asyncore/agent/cmdrsp/implementing-scalar-mib-objects-over-ipv4-and-ipv6.py

snmpget -v2c -c public 127.0.0.1:4161 .1.3.6.1.2.1.1.3.0
snmpget -v2c -c public 127.0.0.1:4161 .1.3.6.1.2.1.1.3.0 .1.3.6.1.2.1.1.1.0
snmpget -v1 -c public 127.0.0.1:4161 .1.3.6.1.2.1.1.3.0 .1.3.6.1.2.1.1.1.0
"""  #
import bisect
import time

from pyasn1.codec.ber import encoder, decoder
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.proto import api
from pysnmp.proto.api import v2c


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

        # return api.protoModules[protoVer].Integer(
        #     -123
        # )

        # module 'pysnmp.proto.api.v1' has no attribute 'Integer32'
        # return api.protoModules[protoVer].Integer32(
        #     123
        # )

        # module 'pysnmp.proto.api.v1' has no attribute 'Unsigned32'
        # return api.protoModules[protoVer].Unsigned32(
        #     32131
        # )

        # return api.protoModules[protoVer].OctetString(
        #     "xxxxx"
        # )

        # return api.protoModules[protoVer].ObjectIdentifier(
        #     ".1.3.6.33.33.2.1"
        # )

        # module 'pysnmp.proto.api.v1' has no attribute 'Bits'
        return api.protoModules[protoVer].Bits(
            "xxxxx"
        )

        # return api.protoModules[protoVer].IpAddress(
        #     "127.0.0.1"
        # )

        # module 'pysnmp.proto.api.v1' has no attribute 'Counter32'
        # return api.protoModules[protoVer].Counter32(
        #     12345
        # )

        # module 'pysnmp.proto.api.v1' has no attribute 'Counter64'
        # return api.protoModules[protoVer].Counter64(
        #     123222
        # )

        # module 'pysnmp.proto.api.v1' has no attribute 'Gauge32'
        # return api.protoModules[protoVer].Gauge32(
        #     67890
        # )

        # return api.protoModules[protoVer].Opaque(
        #     '123'
        # )

        # return api.protoModules[protoVer].Null(
        #     ''
        # )


mibInstr = (SysDescr(), Uptime())  # sorted by object name

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


transportDispatcher = AsyncoreDispatcher()
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