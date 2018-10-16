import logging
import multiprocessing
import time
from pathlib import Path

import torch.cuda
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    ApiVlmOptions,
    ResponseFormat,
    PdfPipelineOptions,
    VlmPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

# SOURCE = "./pdf/OpsGuide-Network-Troubleshooting.pdf"
SOURCE = "./pdf/d2l-zh-pytorch.pdf"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
_log = logging.getLogger(__name__)


def ollama_vlm_options(model: str, prompt: str):
    options = ApiVlmOptions(
        url="http://localhost:11434/v1/chat/completions",  # the default Ollama endpoint
        params=dict(
            model=model,
        ),
        prompt=prompt,
        timeout=1000,
        scale=1.0,
        response_format=ResponseFormat.MARKDOWN,
    )
    return options

def main():
    # 获取CPU核心数
    cpu_cores = multiprocessing.cpu_count()
    _log.info(f"CPU核心数: {cpu_cores} --------")

    # 配置分块
    # chunker = HybridChunker()

    # # 配置 PdfPipelineOptions ----------------------
    pdf_pipeline_options = PdfPipelineOptions()
    pdf_pipeline_options.do_ocr = True  # 启用OCR
    ## 表格处理
    pdf_pipeline_options.do_table_structure = True  # 启用表结构提取
    pdf_pipeline_options.table_structure_options.do_cell_matching = True  # 启用单元格匹配
    ## 代码块处理
    pdf_pipeline_options.do_code_enrichment = True  # 启用代码块提取
    ## 公式处理
    pdf_pipeline_options.do_formula_enrichment = True  # 启用公式提取
    ## 图片处理
    pdf_pipeline_options.do_picture_classification = True  # 启用对文档中的图片进行分类
    pdf_pipeline_options.do_picture_description = True  # 启用运行描述文档中的图片
    ## 加速配置
    if torch.cuda.is_available():
        ## ocr配置
        pdf_pipeline_options.ocr_options.use_gpu = True
        pdf_pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=cpu_cores,
            device=AcceleratorDevice.CUDA,
            cuda_use_flash_attention2=True,
        )
    else:
        pdf_pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=cpu_cores,
            device=AcceleratorDevice.AUTO,
        )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pdf_pipeline_options
            )
        }
    )

    # # 配置 VlmPipelineOptions ----------------------
    vlm_pipeline_options = VlmPipelineOptions(
        enable_remote_services=True  # <-- this is required!
    )

    vlm_pipeline_options.vlm_options = ollama_vlm_options(
        # model="granite3.2-vision:2b",
        model="granite3.2-vision:2b-fp16",
        prompt="OCR the full page to markdown.",
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=vlm_pipeline_options,
                pipeline_cls=VlmPipeline,
            )
        }
    )

    # # ----------------------------

    _log.info(f"转换器配置完成 ..........")

    start_time = time.time()
    # 格式化时间
    _log.info(f"开始转换文档，开始时间 [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}] ..........")

    # 转换文档
    input_doc_path = Path(SOURCE)
    conv_result = converter.convert(input_doc_path)

    end_time = time.time()
    _log.info(f"转换文档结束，完成时间 [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}] ..........")
    _log.info(f"转换文档耗时 [{end_time - start_time}] s ..........")

    # 导出
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_result.input.file.stem

    _log.info("开始导出结果到 Markdown ..........")

    # 导出到 markdown
    with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_markdown())

    _log.info("导出结果到 Markdown 完成 ..........")


if __name__ == '__main__':
    main()
