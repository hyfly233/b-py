from transformers import pipeline

pipe = pipeline("object-detection", model="microsoft/table-transformer-detection")