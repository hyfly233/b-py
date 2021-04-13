#!/usr/bin/env python3
"""
Dify 长上下文合同审核工作流
"""

import json
import requests
from typing import List, Dict, Any
from contract_processor import LongContextContractProcessor

class DifyLongContextContractReviewer:
    """Dify 长上下文合同审核器"""
    
    def __init__(self, dify_api_base: str, api_key: str):
        self.dify_api_base = dify_api_base
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.processor = LongContextContractProcessor()
    
    def create_contract_review_prompt(self, contract_content: str) -> str:
        """创建合同审核提示词"""
        return f"""
你是一名专业的法律顾问，请对以下合同进行全面审核。请按照以下结构提供详细分析：

## 合同基本信息分析
- 合同类型和性质
- 合同当事方信息
- 合同期限和生效条件

## 关键条款审核
- 权利义务条款分析
- 违约责任条款
- 争议解决机制
- 终止和解除条款

## 风险识别
- 法律风险点
- 商业风险点
- 操作风险点

## 合规性检查
- 法律法规符合性
- 行业标准符合性
- 内部政策符合性

## 修改建议
- 条款优化建议
- 风险防范措施
- 补充条款建议

## 总体评估
- 合同整体评级（1-10分）
- 主要优势
- 主要风险
- 是否建议签署

请基于以下合同内容进行审核：

{contract_content}
"""
    
    def review_single_contract(self, file_path: str, workflow_id: str) -> Dict[str, Any]:
        """审核单个合同"""
        # 处理合同文档
        contract = self.processor.process_contract(file_path)
        
        # 检查是否适合长上下文处理
        if not contract.metadata['can_fit_in_context']:
            return self._review_large_contract_in_chunks(contract, workflow_id)
        
        # 创建审核提示
        prompt = self.create_contract_review_prompt(contract.content)
        
        # 调用 Dify API
        response = self._call_dify_workflow(workflow_id, {
            "inputs": {
                "contract_content": contract.content,
                "review_prompt": prompt,
                "file_name": file_path.split('/')[-1]
            }
        })
        
        return {
            "file_path": file_path,
            "metadata": contract.metadata,
            "review_result": response,
            "processing_mode": "single_context"
        }
    
    def review_multiple_contracts(self, file_paths: List[str], workflow_id: str) -> Dict[str, Any]:
        """批量审核多个合同"""
        # 合并多个合同
        combined_contract = self.processor.combine_multiple_contracts(file_paths)
        
        if not combined_contract.metadata['can_fit_in_context']:
            # 如果合并后仍然超出上下文，分别处理
            results = []
            for file_path in file_paths:
                result = self.review_single_contract(file_path, workflow_id)
                results.append(result)
            
            # 生成综合分析
            summary_prompt = self._create_batch_summary_prompt(results)
            summary_response = self._call_dify_workflow(workflow_id, {
                "inputs": {
                    "contract_content": summary_prompt,
                    "review_type": "batch_summary"
                }
            })
            
            return {
                "individual_reviews": results,
                "batch_summary": summary_response,
                "processing_mode": "chunked_processing"
            }
        
        # 如果可以在单个上下文中处理
        prompt = self.create_contract_review_prompt(combined_contract.content)
        prompt += "\n\n特别说明：这是多个合同的合并审核，请在分析中明确区分各个合同的特点和风险。"
        
        response = self._call_dify_workflow(workflow_id, {
            "inputs": {
                "contract_content": combined_contract.content,
                "review_prompt": prompt,
                "file_count": len(file_paths)
            }
        })
        
        return {
            "file_paths": file_paths,
            "combined_metadata": combined_contract.metadata,
            "review_result": response,
            "processing_mode": "combined_context"
        }
    
    def _review_large_contract_in_chunks(self, contract, workflow_id: str) -> Dict[str, Any]:
        """分块处理大型合同"""
        chunk_reviews = []
        
        for i, section in enumerate(contract.sections):
            section_prompt = f"""
请审核合同的第{i+1}部分：{section['title']}

{section['content']}

请重点关注：
1. 本部分的核心内容
2. 潜在的法律风险
3. 需要注意的条款
4. 与其他部分的关联性
"""
            
            response = self._call_dify_workflow(workflow_id, {
                "inputs": {
                    "contract_content": section['content'],
                    "review_prompt": section_prompt,
                    "section_title": section['title']
                }
            })
            
            chunk_reviews.append({
                "section": section['title'],
                "review": response
            })
        
        # 生成整体总结
        summary_prompt = self._create_chunk_summary_prompt(chunk_reviews)
        summary_response = self._call_dify_workflow(workflow_id, {
            "inputs": {
                "contract_content": summary_prompt,
                "review_type": "chunk_summary"
            }
        })
        
        return {
            "chunk_reviews": chunk_reviews,
            "overall_summary": summary_response,
            "processing_mode": "chunked_sections"
        }
    
    def _call_dify_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用 Dify 工作流 API"""
        url = f"{self.dify_api_base}/workflows/{workflow_id}/run"
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}
    
    def _create_batch_summary_prompt(self, individual_results: List[Dict]) -> str:
        """创建批量审核总结提示"""
        summary_content = "以下是多个合同的个别审核结果，请提供综合分析：\n\n"
        
        for i, result in enumerate(individual_results):
            summary_content += f"=== 合同 {i+1} ===\n"
            summary_content += f"文件：{result['file_path']}\n"
            summary_content += f"审核结果：{result['review_result']}\n\n"
        
        summary_content += """
请提供以下综合分析：
1. 整体风险评估
2. 合同间的关联性分析
3. 统一的合规建议
4. 优先处理建议
"""
        return summary_content
    
    def _create_chunk_summary_prompt(self, chunk_reviews: List[Dict]) -> str:
        """创建分块审核总结提示"""
        summary_content = "以下是合同各部分的详细审核结果，请提供整体总结：\n\n"
        
        for chunk in chunk_reviews:
            summary_content += f"=== {chunk['section']} ===\n"
            summary_content += f"{chunk['review']}\n\n"
        
        summary_content += """
请基于以上分块审核结果，提供：
1. 合同整体风险评估
2. 关键问题汇总
3. 优化建议
4. 最终建议
"""
        return summary_content

# 使用示例
if __name__ == "__main__":
    # 初始化审核器
    reviewer = DifyLongContextContractReviewer(
        dify_api_base="https://api.dify.ai/v1",
        api_key="your-dify-api-key"
    )
    
    # 审核单个合同
    result = reviewer.review_single_contract(
        "sample_contract.pdf",
        "your-workflow-id"
    )
    
    # 批量审核
    batch_result = reviewer.review_multiple_contracts(
        ["contract1.pdf", "contract2.docx", "contract3.txt"],
        "your-workflow-id"
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
