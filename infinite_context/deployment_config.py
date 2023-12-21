#!/usr/bin/env python3
"""
生产环境部署配置
"""

import os
from typing import Dict, Any


class LongContextConfig:
    """长上下文配置管理"""

    # 模型配置
    MODELS = {
        "gemini-1.5-pro": {
            "max_tokens": 1000000,
            "cost_per_1k_tokens": 0.0035,
            "suitable_for": ["massive_contracts", "complex_legal_documents"],
            "api_endpoint": "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro",
        },
        "claude-3-sonnet": {
            "max_tokens": 200000,
            "cost_per_1k_tokens": 0.003,
            "suitable_for": ["standard_contracts", "medium_documents"],
            "api_endpoint": "https://api.anthropic.com/v1/messages",
        },
        "gpt-4-turbo": {
            "max_tokens": 128000,
            "cost_per_1k_tokens": 0.01,
            "suitable_for": ["standard_contracts", "quick_reviews"],
            "api_endpoint": "https://api.openai.com/v1/chat/completions",
        },
    }

    # Dify 工作流配置
    DIFY_WORKFLOWS = {
        "contract_review": {
            "workflow_id": "contract-review-workflow-id",
            "description": "标准合同审核流程",
            "max_concurrent": 3,
        },
        "batch_contract_review": {
            "workflow_id": "batch-contract-review-workflow-id",
            "description": "批量合同审核流程",
            "max_concurrent": 1,
        },
        "legal_compliance_check": {
            "workflow_id": "legal-compliance-workflow-id",
            "description": "法律合规性检查",
            "max_concurrent": 5,
        },
    }

    # 文件处理配置
    FILE_PROCESSING = {
        "max_file_size_mb": 100,
        "supported_formats": [".pdf", ".docx", ".txt", ".doc"],
        "temp_storage_path": "/tmp/contract_processing",
        "output_storage_path": "/app/contract_reviews",
    }

    @classmethod
    def get_optimal_model(cls, token_count: int, complexity: str = "medium") -> str:
        """根据token数量和复杂度选择最优模型"""
        if token_count > 500000:
            return "gemini-1.5-pro"
        elif token_count > 100000:
            return "claude-3-sonnet"
        else:
            return "gpt-4-turbo"

    @classmethod
    def estimate_cost(cls, token_count: int, model_name: str) -> float:
        """估算处理成本"""
        if model_name not in cls.MODELS:
            return 0.0

        cost_per_1k = cls.MODELS[model_name]["cost_per_1k_tokens"]
        return (token_count / 1000) * cost_per_1k


# Docker Compose 配置
DOCKER_COMPOSE_CONFIG = """
version: '3.8'

services:
  contract-reviewer:
    build: .
    environment:
      - DIFY_API_KEY=${DIFY_API_KEY}
      - DIFY_API_BASE=${DIFY_API_BASE}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./contracts:/app/contracts
      - ./reviews:/app/reviews
      - ./temp:/tmp/contract_processing
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - postgres
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: contract_reviews
      POSTGRES_USER: reviewer
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""

# 环境变量模板
ENV_TEMPLATE = """
# Dify 配置
DIFY_API_KEY=your-dify-api-key
DIFY_API_BASE=https://api.dify.ai/v1

# 模型 API 密钥
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# 数据库配置
DB_PASSWORD=your-secure-password

# 应用配置
MAX_CONCURRENT_REVIEWS=5
LOG_LEVEL=INFO
STORAGE_PATH=/app/contracts
"""

if __name__ == "__main__":
    # 创建配置文件
    with open("docker-compose.yml", "w") as f:
        f.write(DOCKER_COMPOSE_CONFIG)

    with open(".env.template", "w") as f:
        f.write(ENV_TEMPLATE)

    print("配置文件已生成：")
    print("- docker-compose.yml")
    print("- .env.template")
    print("\n请复制 .env.template 为 .env 并填入实际的 API 密钥")
