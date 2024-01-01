import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from dataset import TranslationDataset, collate_fn
from translation_model import Encoder, Decoder, Seq2Seq

# 超参数
INPUT_DIM = 10000
OUTPUT_DIM = 10000
ENC_EMB_DIM = 256
DEC_EMB_DIM = 256
HID_DIM = 512
N_LAYERS = 2
ENC_DROPOUT = 0.5
DEC_DROPOUT = 0.5
BATCH_SIZE = 32
N_EPOCHS = 10

device = (
    torch.accelerator.current_accelerator().type
    if torch.accelerator.is_available()
    else "cpu"
)

# 示例数据（实际使用时替换为真实数据集）
src_sentences = ["Hello, how are you?", "I love machine learning."]
trg_sentences = ["Hallo, wie geht es dir?", "Ich liebe maschinelles Lernen."]

# 数据集和加载器
dataset = TranslationDataset(src_sentences, trg_sentences)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, collate_fn=collate_fn)

# 模型
enc = Encoder(INPUT_DIM, ENC_EMB_DIM, HID_DIM, N_LAYERS, ENC_DROPOUT)
dec = Decoder(OUTPUT_DIM, DEC_EMB_DIM, HID_DIM, N_LAYERS, DEC_DROPOUT)
model = Seq2Seq(enc, dec, device).to(device)

# 优化器和损失函数
optimizer = optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss(ignore_index=0)  # 忽略 padding

# 训练循环
for epoch in range(N_EPOCHS):
    model.train()
    epoch_loss = 0

    for src, trg in dataloader:
        src, trg = src.to(device), trg.to(device)

        optimizer.zero_grad()
        output = model(src, trg)

        output_dim = output.shape[-1]
        output = output[1:].view(-1, output_dim)
        trg = trg[1:].view(-1)

        loss = criterion(output, trg)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()

    print(f'Epoch {epoch + 1}, Loss: {epoch_loss / len(dataloader):.4f}')

# 保存模型
torch.save(model.state_dict(), 'translation_model.pt')
