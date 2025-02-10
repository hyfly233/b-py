import json

from pyhocon import ConfigFactory

hocon_file_path = './test.conf'
json_file_path = './test.json'

# 读取 HOCON 文件
config = ConfigFactory.parse_file(hocon_file_path)

# 转换为 JSON 格式
json_data = json.dumps(config, indent=2)

# 保存为 JSON 文件
with open(json_file_path, 'w') as json_file:
    json_file.write(json_data)

print("HOCON 文件已成功转换为 JSON 格式")
