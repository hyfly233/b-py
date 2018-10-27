import base64
import time

from openai import OpenAI


#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# 将xxxx/eagle.png替换为你本地图像的绝对路径
# base64_image = encode_image("data/images/test.png")
base_path = r'/Users/flyhy/Desktop/snippet'
base64_image_1 = encode_image(f'{base_path}/13.png')

#  zh
api_key = 'sk-0ae4bfe9251b4667be1372d4f6d8a2e7'


def offical_run():
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    st = time.time()
    completion = client.chat.completions.create(
        # model="qwen-vl-max-latest",
        model='qwen2.5-vl-7b-instruct',
        # model='qwen2.5-vl-32b-instruct',

        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "将表格数据逐行将二维数据转为1维描述，不要输出二维表格结构"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image_1}"},
                },
                # {
                #     "type": "image_url",
                #     "image_url": {"url": f"data:image/png;base64,{base64_image_2}"},
                # },
                # {
                #     "type": "image_url",
                #     "image_url": {"url": f"data:image/png;base64,{base64_image_3}"},
                # },
                # {
                #     "type": "image_url",
                #     "image_url": {"url": f"data:image/png;base64,{base64_image_4}"},
                # },
            ],
        }
        ],
    )
    ed = time.time()
    print('识别图像文件耗时: [s]', (ed - st))
    print(completion.choices[0].message.content)


offical_run()
