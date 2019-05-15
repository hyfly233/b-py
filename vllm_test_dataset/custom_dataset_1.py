import json
import random

# 预定义的测试问题和场景
test_prompts = [
    # 数学计算
    "计算 123 * 456 的结果",
    "求解方程 2x + 5 = 15",
    "什么是斐波那契数列的前10项？",

    # 编程问题
    "用Python写一个快速排序算法",
    "解释什么是递归，并给出一个例子",
    "如何在JavaScript中创建一个数组？",

    # 常识问答
    "地球上最高的山峰是什么？",
    "太阳系有几个行星？",
    "什么是光合作用？",

    # 文本处理
    "总结一下机器学习的基本概念",
    "写一首关于春天的短诗",
    "解释什么是区块链技术",

    # 推理分析
    "如果今天是星期三，那么三天后是星期几？",
    "比较Python和Java的优缺点",
    "分析人工智能对未来工作的影响",
]

# 扩展问题模板
question_templates = [
    "请详细解释{}的概念和应用",
    "如何解决{}相关的问题？",
    "{}有什么优势和劣势？",
    "能否举例说明{}的实际应用？",
    "{}的工作原理是什么？",
]

topics = [
    "机器学习", "深度学习", "云计算", "大数据", "物联网",
    "区块链", "人工智能", "网络安全", "数据分析", "微服务架构"
]

def create_custom_dataset(output_file="custom_test_dataset.json", num_samples=200):
    """创建自定义测试数据集"""

    dataset = []

    for i in range(num_samples):
        if i < len(test_prompts):
            # 使用预定义问题
            user_message = test_prompts[i]
        else:
            # 使用模板生成问题
            template = random.choice(question_templates)
            topic = random.choice(topics)
            user_message = template.format(topic)

        # 创建对话格式
        conversation = {
            "conversations": [
                {
                    "from": "human",
                    "value": user_message
                },
                {
                    "from": "gpt",
                    "value": f"这是对问题 '{user_message}' 的回答。"  # 占位符回答
                }
            ]
        }

        dataset.append(conversation)

    # 保存数据集
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ 已创建包含 {num_samples} 条记录的数据集: {output_file}")
    return output_file


if __name__ == "__main__":
    create_custom_dataset("custom_benchmark_dataset.json", 500)
