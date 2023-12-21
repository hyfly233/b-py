from pysnmp.hlapi import *


def snmp_get(target: str, targetPort: int, community: str, snmpVersion=0):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=snmpVersion),
        UdpTransportTarget((target, targetPort)),
        ContextData(),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.1.0")),
        # ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.3.0")),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.4.0")),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.5.0")),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.6.0")),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.7.0")),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.8.0")),
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    print(f"varBinds type: {varBinds}")

    if errorIndication:  # SNMP engine errors
        print(errorIndication)
    else:
        if errorStatus:  # SNMP agent errors
            print(
                "%s at %s"
                % (
                    errorStatus.prettyPrint(),
                    varBinds[int(errorIndex) - 1] if errorIndex else "?",
                )
            )
        else:
            for varBind in varBinds:  # SNMP response contents
                print(" = ".join([x.prettyPrint() for x in varBind]))


def snmp_get_v3():
    iterator = getCmd(
        SnmpEngine(),
        UsmUserData("usr-md5-des", "authkey1", "privkey1"),
        # UdpTransportTarget(('demo.snmplabs.com', 161)),
        UdpTransportTarget(("127.0.0.1", 161)),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:  # SNMP engine errors
        print(errorIndication)
    else:
        if errorStatus:  # SNMP agent errors
            print(
                "%s at %s"
                % (
                    errorStatus.prettyPrint(),
                    varBinds[int(errorIndex) - 1] if errorIndex else "?",
                )
            )
        else:
            for varBind in varBinds:  # SNMP response contents
                print(" = ".join([x.prettyPrint() for x in varBind]))


if __name__ == "__main__":
    target = "127.0.0.1"
    # target = 'demo.snmplabs.com'
    targetPort = 4161

    community = "public"
    snmpVersion = 1  # 0 for SNMPv1, 1 for SNMPv2c

    snmp_get(target, targetPort, community, snmpVersion)
