import logging
import multiprocessing
import time
from pathlib import Path

import torch
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

SOURCE = "./pdf/OpsGuide-Network-Troubleshooting.pdf"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
_log = logging.getLogger(__name__)


def main():
    # 获取CPU核心数
    cpu_cores = multiprocessing.cpu_count()
    _log.info(f"CPU核心数: {cpu_cores} --------")

    # 配置分块
    # chunker = HybridChunker()


    # 配置 pipeline
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    ## 加速配置
    # pipeline_options.accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.MPS
    # )

    cuda_version = torch.version.cuda
    if cuda_version:
        pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=cpu_cores,
            device=AcceleratorDevice.CUDA,
            cuda_use_flash_attention2=True,
        )
    else:
        pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=cpu_cores,
            device=AcceleratorDevice.MPS
        )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    _log.info(f"转换器配置完成 ..........")

    start_time = time.time()
    # 格式化时间
    _log.info(f"开始转换文档，开始时间 [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}] ..........")

    # 转换文档
    input_doc_path = Path(SOURCE)
    conv_result = converter.convert(input_doc_path)

    end_time = time.time()
    _log.info(f"转换文档结束，完成时间 [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}] ..........")
    _log.info(f"转换文档耗时 [{end_time - start_time}] ..........")

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
