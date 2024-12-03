import asyncio

from pysnmp.hlapi.asyncio import *


# 发送 trap 时 sendNotification 的参数
class SendTrapArg(object):
    def __init__(self, targetIp, targetPort, communityIndex="public", mpModel=0, step=0):
        self.targetIp = targetIp
        self.targetPort = targetPort
        self.communityIndex = communityIndex
        self.mpModel = mpModel
        self.step = step


class OidObj:
    def __init__(self, oid, strValue, dataType):
        self.oid = oid
        self.strValue = strValue
        self.dataType = dataType


# 发送 Trap 报文，默认使用 SNMPv1
async def sendTrap(snmpEngine, sendTrapArg, varBinds):
    send_result = await sendNotification(
        snmpEngine,
        CommunityData(sendTrapArg.communityIndex, mpModel=sendTrapArg.mpModel),
        UdpTransportTarget((sendTrapArg.targetIp, sendTrapArg.targetPort)),
        ContextData(),
        "trap",
        varBinds
    )

    print("----------------")

    # 将 varBinds 转换为字符串
    print("varBinds: ", varBinds.__dict__)

    for varBind in varBinds:
        print(" = ".join([x.prettyPrint() for x in varBind]))

    print("----------------")

    errorIndication, errorStatus, errorIndex, varBinds = send_result

    print(errorIndication, errorStatus, errorIndex, varBinds)

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print(
            "{}: at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))


async def stepSendTrap(snmpEngine, sendTrapArg, varBinds):
    if sendTrapArg.step == 0:
        await sendTrap(snmpEngine, sendTrapArg, varBinds)
    else:
        while True:
            await sendTrap(snmpEngine, sendTrapArg, varBinds)
            await asyncio.sleep(sendTrapArg.step)


async def main(ip: str, port: int):
    snmpEngine = SnmpEngine()
    targetIp = ip
    targetPort = port

    # varBinds0 -----------
    varBinds0 = NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2")).addVarBinds(
        ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
        ("1.3.6.1.2.1.1.1.0", OctetString("my system"))
    )
    # varBinds1 -----------
    varBinds1 = NotificationType(ObjectIdentity('SNMPv2-MIB', 'authenticationFailure')).addVarBinds(
        ("1.3.6.2.2.1", OctetString("xxxxxxx")))

    # varBinds2 -----------
    varBinds2 = NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.0")).addVarBinds(
        ("1.3.6.2.2.1.1.2.0", OctetString("xxxxxxx")),
        ("1.3.6.1.2.1.1.1.0", OctetString("my system"))
    )

    # varBinds3 -----------
    varBinds3 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386')

    # varBinds4 -----------
    test_list = []

    # test_list.append(("1.3.6.1.6.3.1.1.4.3.0", ObjectIdentifier("1.3.6.1.4.1.20408.4.1.1.2")))
    test_list.append(("1.3.6.2.2.1.1.2.0", OctetString("xxxxxxx")))
    test_list.append(("1.3.6.1.2.1.1.1.0", OctetString("my system")))

    varBinds4 = NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.0")).addVarBinds(
        *test_list
    )

    # varBinds5 -----------
    oid_objects = [
        OidObj("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2", "oid"),
        OidObj("1.3.6.1.2.1.1.1.0", "233", "string"),  # 设置为整数值 233
        OidObj("1.3.6.1.2.1.2.2.1.10.1", "12345", "integer"),
        OidObj("1.3.6.1.2.1.4.20.1.1.192.168.0.1", "192.168.0.1", "ipaddress"),
        OidObj("1.3.6.1.2.1.1.7.0", "1", "boolean"),  # 设置为 boolean 值 true
        OidObj("1.3.6.1.2.1.1.9.0", "2", "enum")  # 设置为 enum 值 2
    ]

    var_binds = []

    for obj in oid_objects:
        if obj.dataType == "oid":
            var_binds.append((ObjectIdentity(obj.oid), ObjectIdentifier(obj.strValue)))
        elif obj.dataType == "string":
            var_binds.append((ObjectIdentity(obj.oid), OctetString(obj.strValue)))
        elif obj.dataType == "integer":
            var_binds.append((ObjectIdentity(obj.oid), Integer(int(obj.strValue))))
        elif obj.dataType == "ipaddress":
            var_binds.append((ObjectIdentity(obj.oid), IpAddress(obj.strValue)))
        elif obj.dataType == "boolean":
            var_binds.append((ObjectIdentity(obj.oid), Integer(1 if obj.strValue == "1" else 0)))
        elif obj.dataType == "enum":
            var_binds.append((ObjectIdentity(obj.oid), Integer(int(obj.strValue))))
        else:
            raise ValueError(f"Unsupported data type: {obj.dataType}")

    varBinds5 = NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2")).addVarBinds(*var_binds)

    tasks = [
        # stepSendTrap(snmpEngine, SendTrapArg(targetIp=targetIp, targetPort=targetPort, mpModel=0), varBinds0),
        # stepSendTrap(snmpEngine, SendTrapArg(targetIp=targetIp, targetPort=targetPort, mpModel=1), varBinds1),
        # stepSendTrap(snmpEngine, SendTrapArg(targetIp=targetIp, targetPort=targetPort, mpModel=1), varBinds2),
        # stepSendTrap(snmpEngine, SendTrapArg(targetIp=targetIp, targetPort=targetPort, mpModel=0), varBinds3),
        # stepSendTrap(snmpEngine, SendTrapArg(targetIp=targetIp, targetPort=targetPort, mpModel=1), varBinds4),
        stepSendTrap(snmpEngine, SendTrapArg(targetIp=targetIp, targetPort=targetPort, mpModel=1), varBinds5),
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        snmpEngine.transportDispatcher.closeDispatcher()


if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 4162

    try:
        asyncio.run(main(ip, port))
    except KeyboardInterrupt:
        print("Program interrupted and exiting...")
