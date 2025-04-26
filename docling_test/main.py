from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True

# pipeline_options.generate_picture_images = True
# pipeline_options.images_scale = 2
# pipeline_options.do_picture_classification = True
# pipeline_options.do_picture_description = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("./pdf/docling_test_pdf.pdf")
doc = result.document

print(doc.export_to_dict())
