import asyncio
import logging

from pysnmp.hlapi.asyncio import *


def trapSimulationValues():
    # varBinds 构建
    var_binds = []

    # oid = "1.3.6.1.6.3.1.1.4.3.0"
    oid = "1.3.6.1.2.1.1.9.0"
    dataType = "int"
    simulateValue = "1"

    if dataType == "oid":
        var_binds.append((ObjectIdentity(oid), ObjectIdentifier(simulateValue)))
    elif dataType == "string":
        var_binds.append((ObjectIdentity(oid), OctetString(simulateValue)))
    elif dataType == "int":
        var_binds.append((ObjectIdentity(oid), Integer(int(simulateValue))))
    elif dataType == "ipaddress":
        var_binds.append((ObjectIdentity(oid), IpAddress(simulateValue)))
    elif dataType == "boolean":
        var_binds.append((ObjectIdentity(oid), Integer(1 if simulateValue == "1" else 0)))
    elif dataType == "enum":
        var_binds.append((ObjectIdentity(oid), Integer(int(simulateValue))))
    else:
        raise ValueError(f"Unsupported data type: {dataType}")

    return var_binds


async def sendTrap():
    var_binds = trapSimulationValues()

    send_result = await sendNotification(
        SnmpEngine(),
        CommunityData("public", mpModel=0),
        UdpTransportTarget(("127.0.0.1", 4162)),
        ContextData(),
        "trap",
        NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.0")).addVarBinds(*var_binds)
    )

    errorIndication, errorStatus, errorIndex, sentVarBinds = send_result

    logging.debug(
        f"errorIndication: {errorIndication} , errorStatus: {errorStatus}, errorIndex: {errorIndex}, sentVarBinds: {sentVarBinds}")

    if errorIndication:
        logging.error(f"errorIndication: {errorIndication}")
    elif errorStatus:
        msg = "{}: at {}".format(
            errorStatus.prettyPrint(),
            errorIndex and sentVarBinds[int(errorIndex) - 1][0] or "?",
        )
        logging.info(f"send trap errorStatus: {msg}")
    else:
        for varBind in sentVarBinds:
            msg = " = ".join([x.prettyPrint() for x in varBind])
            logging.info(f"send trap varBind: {msg}")


async def main():
    # 开启 Trap 发送协程
    trap_task = asyncio.create_task(sendTrap())

    # 等待所有任务完成
    await asyncio.gather(trap_task)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted and exiting...")
