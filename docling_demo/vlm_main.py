import logging
import time
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

SOURCE = "./docx/Doc3.docx"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
_log = logging.getLogger(__name__)


def main():
    converter = DocumentConverter()

    _log.info(f"转换器配置完成 ..........")

    try:
        start_time = time.time()
        # 格式化时间
        _log.info(
            f"开始转换文档，开始时间 [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}] ..........")

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

        # -----------------

        _log.info("开始分块 ..........")
        doc = conv_result.document

        # 配置分块
        chunker = HybridChunker()
        chunk_iter = chunker.chunk(dl_doc=doc)

        for i, chunk in enumerate(chunk_iter):
            print(f"=== {i} ===")
            print(f"chunk.text:\n{f'{chunk.text[:300]}…'!r}")

            enriched_text = chunker.contextualize(chunk=chunk)
            print(f"chunker.contextualize(chunk):\n{f'{enriched_text[:300]}…'!r}")

            print()

    finally:
        # 清理其他可能的资源...
        pass


if __name__ == '__main__':
    main()
