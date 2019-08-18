import json


def check_dataset_size(dataset_path):
    """检查数据集的实际大小"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"数据集路径: {dataset_path}")
    print(f"总条数: {len(data)}")
    print(f"样本格式: {type(data[0]) if data else 'Empty'}")

    # 显示前几条的基本信息
    for i, item in enumerate(data[:3]):
        if isinstance(item, dict):
            print(f"样本 {i + 1}: {list(item.keys())}")

    return len(data)


# 使用示例
dataset_size = check_dataset_size("/path/ShareGPT_V3_unfiltered_cleaned_split.json")
print(f"\n建议 --num-prompts 设置: {min(dataset_size, 5000)}")