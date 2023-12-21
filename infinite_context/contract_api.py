#!/usr/bin/env python3
"""
合同审核 API 服务
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio
import uuid
import json
from datetime import datetime
import os

from dify_contract_reviewer import DifyLongContextContractReviewer
from deployment_config import LongContextConfig

app = FastAPI(title="长上下文合同审核系统", version="1.0.0")

# 全局配置
reviewer = DifyLongContextContractReviewer(
    dify_api_base=os.getenv("DIFY_API_BASE", "https://api.dify.ai/v1"),
    api_key=os.getenv("DIFY_API_KEY", "default-key"),
)

# 任务状态存储（生产环境建议使用 Redis）
task_status = {}


@app.post("/api/contracts/upload")
async def upload_contracts(files: List[UploadFile] = File(...)):
    """上传合同文件"""
    uploaded_files = []

    for file in files:
        # 验证文件类型
        if file.filename and not any(
            file.filename.endswith(ext)
            for ext in LongContextConfig.FILE_PROCESSING["supported_formats"]
        ):
            raise HTTPException(
                status_code=400, detail=f"不支持的文件格式: {file.filename}"
            )

        # 保存文件
        file_path = f"/tmp/contract_processing/{uuid.uuid4()}_{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        uploaded_files.append(
            {"filename": file.filename, "path": file_path, "size": len(content)}
        )

    return {"message": "文件上传成功", "files": uploaded_files}


@app.post("/api/contracts/review/single")
async def review_single_contract(
    background_tasks: BackgroundTasks, file_path: str, workflow_id: Optional[str] = None
):
    """审核单个合同"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 设置默认工作流
    if not workflow_id:
        workflow_id = LongContextConfig.DIFY_WORKFLOWS["contract_review"]["workflow_id"]

    # 初始化任务状态
    task_status[task_id] = {
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "file_path": file_path,
        "progress": 0,
    }

    # 启动后台任务
    background_tasks.add_task(process_single_contract, task_id, file_path, workflow_id)

    return {"task_id": task_id, "status": "started"}


@app.post("/api/contracts/review/batch")
async def review_batch_contracts(
    background_tasks: BackgroundTasks,
    file_paths: List[str],
    workflow_id: Optional[str] = None,
):
    """批量审核合同"""
    # 验证所有文件是否存在
    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")

    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 设置默认工作流
    if not workflow_id:
        workflow_id = LongContextConfig.DIFY_WORKFLOWS["batch_contract_review"][
            "workflow_id"
        ]

    # 初始化任务状态
    task_status[task_id] = {
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "file_paths": file_paths,
        "progress": 0,
        "total_files": len(file_paths),
    }

    # 启动后台任务
    background_tasks.add_task(process_batch_contracts, task_id, file_paths, workflow_id)

    return {"task_id": task_id, "status": "started", "total_files": len(file_paths)}


@app.get("/api/contracts/status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task_status[task_id]


@app.get("/api/contracts/result/{task_id}")
async def get_review_result(task_id: str):
    """获取审核结果"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")

    status = task_status[task_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    return status.get("result", {})


@app.get("/api/models/info")
async def get_model_info():
    """获取可用模型信息"""
    return {"models": LongContextConfig.MODELS}


@app.post("/api/contracts/estimate-cost")
async def estimate_processing_cost(
    file_paths: List[str], model_name: Optional[str] = None
):
    """估算处理成本"""
    total_tokens = 0
    file_info = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue

        # 简单估算（实际应该使用 tiktoken）
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            token_count = len(content) // 4  # 粗略估算

        total_tokens += token_count
        file_info.append({"file_path": file_path, "estimated_tokens": token_count})

    # 选择最优模型
    if not model_name:
        model_name = LongContextConfig.get_optimal_model(total_tokens)

    # 估算成本
    estimated_cost = LongContextConfig.estimate_cost(total_tokens, model_name)

    return {
        "total_tokens": total_tokens,
        "recommended_model": model_name,
        "estimated_cost_usd": estimated_cost,
        "file_breakdown": file_info,
    }


async def process_single_contract(task_id: str, file_path: str, workflow_id: str):
    """处理单个合同的后台任务"""
    try:
        task_status[task_id]["progress"] = 10

        # 执行审核
        result = reviewer.review_single_contract(file_path, workflow_id)

        task_status[task_id].update(
            {
                "status": "completed",
                "progress": 100,
                "result": result,
                "completed_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        task_status[task_id].update(
            {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat(),
            }
        )


async def process_batch_contracts(
    task_id: str, file_paths: List[str], workflow_id: str
):
    """处理批量合同的后台任务"""
    try:
        task_status[task_id]["progress"] = 10

        # 执行批量审核
        result = reviewer.review_multiple_contracts(file_paths, workflow_id)

        task_status[task_id].update(
            {
                "status": "completed",
                "progress": 100,
                "result": result,
                "completed_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        task_status[task_id].update(
            {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat(),
            }
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
