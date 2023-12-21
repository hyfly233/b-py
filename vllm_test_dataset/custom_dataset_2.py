#!/usr/bin/env python3
"""
创建更真实的基准测试数据集
"""

import json
import random
from typing import List, Dict


class BenchmarkDatasetGenerator:
    def __init__(self):
        # 不同类型和长度的测试用例
        self.short_questions = [
            "1+1等于多少？",
            "今天天气如何？",
            "Python是什么？",
            "你好，你是谁？",
            "什么是AI？",
        ]

        self.medium_questions = [
            "请解释机器学习和深度学习的区别，并举例说明它们的应用场景。",
            "如何设计一个高并发的Web服务架构？请详细说明各个组件的作用。",
            "分析当前人工智能技术的发展趋势，以及对各行业可能产生的影响。",
            "请编写一个Python函数来实现二分搜索算法，并分析其时间复杂度。",
        ]

        self.long_questions = [
            """请详细分析以下代码的性能瓶颈，并提供优化建议：

def process_data(data_list):
    result = []
    for item in data_list:
        if item > 0:
            for i in range(len(data_list)):
                if data_list[i] == item:
                    result.append(item * 2)
    return result

同时请解释为什么这样的优化能够提升性能，以及在什么情况下这种优化最有效。""",
            """在分布式系统设计中，CAP定理是一个重要的概念。请详细解释：
1. CAP定理的具体内容和含义
2. 为什么不能同时满足所有三个特性
3. 在实际系统设计中如何根据业务需求进行取舍
4. 举例说明不同类型的分布式系统是如何处理CAP权衡的
5. 现代分布式系统如何通过技术手段尽可能地平衡这三个特性

请结合具体的技术实现和真实案例来说明。""",
        ]

    def generate_dataset(
        self,
        total_samples: int = 300,
        short_ratio: float = 0.3,
        medium_ratio: float = 0.5,
        long_ratio: float = 0.2,
    ) -> List[Dict]:
        """生成基准测试数据集"""

        dataset = []

        # 计算各类型问题的数量
        short_count = int(total_samples * short_ratio)
        medium_count = int(total_samples * medium_ratio)
        long_count = total_samples - short_count - medium_count

        # 生成短问题
        for _ in range(short_count):
            question = random.choice(self.short_questions)
            dataset.append(self._create_conversation(question))

        # 生成中等长度问题
        for _ in range(medium_count):
            question = random.choice(self.medium_questions)
            dataset.append(self._create_conversation(question))

        # 生成长问题
        for _ in range(long_count):
            question = random.choice(self.long_questions)
            dataset.append(self._create_conversation(question))

        # 打乱顺序
        random.shuffle(dataset)

        return dataset

    def _create_conversation(self, question: str) -> Dict:
        """创建对话格式"""
        return {
            "conversations": [
                {"from": "human", "value": question},
                {"from": "gpt", "value": "这是一个测试回答。"},  # 占位符
            ]
        }

    def save_dataset(self, dataset: List[Dict], filename: str):
        """保存数据集到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        print(f"✅ 数据集已保存到: {filename}")
        print(f"📊 总计 {len(dataset)} 条记录")


def main():
    generator = BenchmarkDatasetGenerator()

    # 生成不同规模的数据集
    datasets = [
        # (100, "small_benchmark_dataset.json"),
        # (500, "medium_benchmark_dataset.json"),
        (1000, "large_benchmark_dataset.json")
    ]

    for size, filename in datasets:
        print(f"\n🔄 生成 {filename}...")
        dataset = generator.generate_dataset(total_samples=size)
        generator.save_dataset(dataset, filename)


if __name__ == "__main__":
    main()
