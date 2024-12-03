from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import context

from snmp_tool.entity import ow_cmdrsp

snmpEngine = engine.SnmpEngine()

config.addTransport(
    snmpEngine, udp.domainName, udp.UdpTransport().openServerMode(("127.0.0.1", 4161))
)

config.addV1System(snmpEngine, "my-area", "public")

config.addVacmUser(
    snmpEngine, 2, "my-area", "noAuthNoPriv", (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1)
)

snmpContext = context.SnmpContext(snmpEngine)

ow_cmdrsp.GetOwCommandResponder(snmpEngine, snmpContext)
# ow_cmdrsp.SetOwCommandResponder(snmpEngine, snmpContext)
# ow_cmdrsp.NextOwCommandResponder(snmpEngine, snmpContext)
# ow_cmdrsp.BulkOwCommandResponder(snmpEngine, snmpContext)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise
