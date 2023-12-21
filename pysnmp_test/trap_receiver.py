from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv

"""
https://github.com/pysnmp/pysnmp/blob/mains/examples/v3arch/asyncio/manager/ntfrcv/multiple-interfaces.py

https://github.com/pysnmp/pysnmp/blob/main/examples/v3arch/asyncore/manager/ntfrcv/determine-peer-network-address.py

https://github.com/pysnmp/pysnmp/blob/main/examples/v3arch/asyncore/manager/ntfrcv/multiple-network-interfaces.py
"""
# 创建SNMP引擎实例
snmpEngine = engine.SnmpEngine()

# 配置SNMPv2c
config.addV1System(snmpEngine, "my-area", "public")

# 配置监听地址和端口
config.addSocketTransport(
    snmpEngine, udp.domainName, udp.UdpTransport().openServerMode(("0.0.0.0", 4162))
)


# 回调函数，用于处理接收到的Trap消息
def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    print("Received new Trap message")
    for var_bind in varBinds:
        oid, value = var_bind
        print(f"{oid.prettyPrint()} = {value.prettyPrint()}")


# 注册Trap接收回调函数
ntfrcv.NotificationReceiver(snmpEngine, cbFun)

# 运行SNMP引擎
print("SNMP Trap Receiver is running...")
try:
    snmpEngine.transportDispatcher.jobStarted(1)  # 启动调度器
    snmpEngine.transportDispatcher.runDispatcher()
except Exception as e:
    print(f"Error: {e}")
finally:
    snmpEngine.transportDispatcher.closeDispatcher()
