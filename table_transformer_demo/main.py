from PIL import Image
from huggingface_hub import hf_hub_download
from transformers import DetrFeatureExtractor
from transformers import pipeline

pipe = pipeline("object-detection", model="microsoft/table-transformer-detection")

def main():
    file_path = hf_hub_download(repo_id="nielsr/example-pdf", repo_type="dataset", filename="example_pdf.png")
    image = Image.open(file_path).convert("RGB")
    width, height = image.size
    image.resize((int(width * 0.5), int(height * 0.5)))

    feature_extractor = DetrFeatureExtractor()
    encoding = feature_extractor(image, return_tensors="pt")
    encoding.keys()

    print(encoding['pixel_values'].shape)


if __name__ == '__main__':
    main()
