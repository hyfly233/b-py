# 长上下文合同审核系统

## 概述

本系统利用大模型的长上下文能力，结合 Dify 平台，实现智能化的合同审核功能。支持单个和批量合同处理，能够处理大型合同文档，提供全面的法律风险分析。

## 核心特性

### 1. 长上下文支持
- **Gemini-1.5-Pro**: 支持 1M tokens，适合超大型合同
- **Claude-3-Sonnet**: 支持 200K tokens，适合标准合同
- **GPT-4-Turbo**: 支持 128K tokens，适合快速审核

### 2. 智能文档处理
- 支持 PDF、DOCX、TXT 格式
- 自动文档分段和结构化
- 智能合并多文档处理

### 3. Dify 工作流集成
- 标准合同审核流程
- 批量处理工作流
- 法律合规性检查

## 系统架构

```
客户端上传
    ↓
FastAPI 接口层
    ↓
文档处理模块 → 长上下文分析
    ↓
Dify 工作流引擎
    ↓
多模型智能审核
    ↓
结构化审核报告
```

## 安装部署

### 1. 环境准备

```bash
# 克隆代码
git clone <repository-url>
cd contract-review-system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置文件

创建 `.env` 文件：

```env
# Dify 配置
DIFY_API_KEY=your-dify-api-key
DIFY_API_BASE=https://api.dify.ai/v1

# 模型 API 密钥
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# 数据库配置
DB_PASSWORD=your-secure-password
```

### 3. Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## API 使用指南

### 1. 上传合同文件

```bash
curl -X POST "http://localhost:8000/api/contracts/upload" \
  -F "files=@contract1.pdf" \
  -F "files=@contract2.docx"
```

### 2. 单个合同审核

```bash
curl -X POST "http://localhost:8000/api/contracts/review/single" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/contract.pdf"}'
```

### 3. 批量合同审核

```bash
curl -X POST "http://localhost:8000/api/contracts/review/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": [
      "/path/to/contract1.pdf",
      "/path/to/contract2.docx"
    ]
  }'
```

### 4. 查询任务状态

```bash
curl "http://localhost:8000/api/contracts/status/{task_id}"
```

### 5. 获取审核结果

```bash
curl "http://localhost:8000/api/contracts/result/{task_id}"
```

## Dify 工作流配置

### 1. 创建合同审核工作流

在 Dify 平台中创建以下节点：

1. **开始节点**: 接收合同内容和审核提示
2. **LLM 节点**: 配置长上下文模型进行审核
3. **代码节点**: 结构化输出处理
4. **结束节点**: 返回审核结果

### 2. 工作流提示词模板

```
你是一名专业的法律顾问，请对以下合同进行全面审核：

## 审核维度
1. 合同基本信息分析
2. 关键条款审核  
3. 风险识别
4. 合规性检查
5. 修改建议
6. 总体评估

## 输出格式
请按照 JSON 格式返回结构化的审核结果：
{
  "basic_info": {...},
  "key_clauses": {...},
  "risks": [...],
  "compliance": {...},
  "suggestions": [...],
  "overall_rating": "1-10分"
}

合同内容：
{{contract_content}}
```

## 最佳实践

### 1. 模型选择策略

```python
def select_optimal_model(token_count, complexity):
    if token_count > 500000:
        return "gemini-1.5-pro"  # 超大文档
    elif token_count > 100000:
        return "claude-3-sonnet"  # 标准文档
    elif complexity == "high":
        return "gpt-4-turbo"  # 复杂但较短的文档
    else:
        return "gpt-3.5-turbo"  # 简单文档
```

### 2. 成本控制

- 预估处理成本：使用 `/api/contracts/estimate-cost` 接口
- 分段处理：超出上下文限制时自动分段
- 缓存机制：相似合同复用审核结果

### 3. 并发处理

```python
# 配置并发限制
MAX_CONCURRENT_REVIEWS = 5
BATCH_SIZE = 10

# 使用队列管理任务
import asyncio
from asyncio import Semaphore

semaphore = Semaphore(MAX_CONCURRENT_REVIEWS)

async def process_with_limit(contract_path):
    async with semaphore:
        return await review_contract(contract_path)
```

## 监控和日志

### 1. 性能监控

```python
import time
import logging

def monitor_review_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        logging.info(f"审核耗时: {duration:.2f}秒")
        return result
    return wrapper
```

### 2. 错误处理

```python
try:
    result = reviewer.review_contract(file_path)
except TokenLimitExceeded:
    # 自动切换到分段处理
    result = reviewer.review_in_chunks(file_path)
except APIRateLimitError:
    # 延迟重试
    time.sleep(60)
    result = reviewer.review_contract(file_path)
```

## 扩展功能

### 1. 合同对比分析

```python
def compare_contracts(contract1, contract2):
    prompt = f"""
    请对比分析以下两个合同的差异：
    
    合同A：{contract1}
    合同B：{contract2}
    
    重点关注：
    1. 关键条款差异
    2. 风险点变化
    3. 有利/不利变更
    """
    return call_dify_workflow(prompt)
```

### 2. 历史版本追踪

```python
def track_contract_versions(contract_id):
    versions = get_contract_history(contract_id)
    return analyze_version_changes(versions)
```

### 3. 智能模板生成

```python
def generate_contract_template(contract_type, industry):
    prompt = f"""
    基于 {industry} 行业的 {contract_type} 合同，
    生成标准化模板，包含必要条款和风险防范措施。
    """
    return call_dify_workflow(prompt)
```

## 故障排除

### 常见问题

1. **Token 超限**: 自动分段处理
2. **API 限制**: 实现重试机制  
3. **文件格式错误**: 转换为支持格式
4. **网络超时**: 增加超时时间配置

### 性能优化

1. **并行处理**: 使用异步处理提高效率
2. **缓存策略**: 缓存常见合同类型的审核模板
3. **负载均衡**: 多个 API 密钥轮询使用

## 联系支持

如有问题，请联系技术支持团队或查看项目文档。
