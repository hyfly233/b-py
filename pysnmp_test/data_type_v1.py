from pysnmp.hlapi import *
from pysnmp.proto import rfc1902

# 创建一个 SNMP v1 对象
snmp_v1 = SnmpEngine()

# 定义 SNMP v1 支持的数据类型
integer_value = rfc1902.Integer(123)
octet_string_value = rfc1902.OctetString('hello')
null_value = rfc1902.Null('')
object_identifier_value = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')
ip_address_value = rfc1902.IpAddress('192.168.1.1')
counter_value = rfc1902.Counter32(12345)
gauge_value = rfc1902.Gauge32(67890)
time_ticks_value = rfc1902.TimeTicks(123456)

# 打印这些值
print(f'Integer: {integer_value}')
print(f'OctetString: {octet_string_value}')
print(f'Null: {null_value.prettyPrint()}')
print(f'ObjectIdentifier: {object_identifier_value}')
print(f'IpAddress: {ip_address_value.prettyPrint()}')
print(f'Counter32: {counter_value}')
print(f'Gauge32: {gauge_value}')
print(f'TimeTicks: {time_ticks_value}')
