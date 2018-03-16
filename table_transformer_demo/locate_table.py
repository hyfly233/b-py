import matplotlib.pyplot as plt
import torch
from PIL import Image
from huggingface_hub import hf_hub_download
from transformers import TableTransformerForObjectDetection, DetrImageProcessor

model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-detection")

# colors for visualization
COLORS = [[0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125],
          [0.494, 0.184, 0.556], [0.466, 0.674, 0.188], [0.301, 0.745, 0.933]]


def plot_results(pil_img, scores, labels, boxes):
    plt.figure(figsize=(16, 10))
    plt.imshow(pil_img)
    ax = plt.gca()
    colors = COLORS * 100
    for score, label, (xmin, ymin, xmax, ymax), c in zip(scores.tolist(), labels.tolist(), boxes.tolist(), colors):
        ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                   fill=False, color=c, linewidth=3))
        text = f'{model.config.id2label[label]}: {score:0.2f}'
        ax.text(xmin, ymin, text, fontsize=15,
                bbox=dict(facecolor='yellow', alpha=0.5))
    plt.axis('on') # on 开启坐标轴 off 关闭坐标轴
    plt.show()

def main():
    file_path = hf_hub_download(repo_id="nielsr/example-pdf", repo_type="dataset", filename="example_pdf.png")
    image = Image.open(file_path).convert("RGB")
    width, height = image.size
    image.resize((int(width * 0.5), int(height * 0.5)))

    detr_image_processor = DetrImageProcessor()
    encoding = detr_image_processor(image, return_tensors="pt")
    encoding.keys()

    print(encoding['pixel_values'].shape)

    with torch.no_grad():
        outputs = model(**encoding)

    width, height = image.size
    print(f"图片大小: {width} x {height}")
    results = \
        detr_image_processor.post_process_object_detection(outputs, threshold=0.7, target_sizes=[(height, width)])[0]

    scores = results['scores']
    labels = results['labels']
    boxes = results['boxes']

    box = boxes[0]
    xmin, ymin, xmax, ymax = box.tolist()
    print(f"xmin: {xmin}, ymin: {ymin}, xmax: {xmax}, ymax: {ymax}")

    plot_results(image, scores, labels, boxes)


if __name__ == '__main__':
    main()
