from collections import Counter

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from dataset import SimpleDataset, collate_fn
from translation_model import Encoder, Decoder, Seq2Seq

# 1. 扩大语料：两种方式任选其一

# 方法 A：从本地平行文本读入
# src.txt, tgt.txt 每行一条，按行一一对应
# with open("data/src.txt", encoding="utf-8") as f:
#     src_sentences = [line.strip() for line in f if line.strip()]
# with open("data/tgt.txt", encoding="utf-8") as f:
#     trg_sentences = [line.strip() for line in f if line.strip()]

# 方法 B：直接用 WMT14 数据集（示例）
raw = load_dataset("wmt14", "de-en", split="train")
src_sentences = raw["en"]
trg_sentences = raw["de"]


# 特殊符号
# 2. 重写 build_vocab，支持 min_freq / max_size
special_tokens = ["<pad>", "<bos>", "<eos>", "<unk>"]


# 构建词表
def build_vocab(sentences, tokenizer, min_freq=2, max_size=30000):
    counter = Counter()
    for sent in sentences:
        counter.update(tokenizer(sent))
    vocab = {tok: idx for idx, tok in enumerate(special_tokens)}
    for token, freq in counter.most_common():
        if freq < min_freq or len(vocab) >= max_size + len(special_tokens):
            break
        if token not in vocab:
            vocab[token] = len(vocab)
    return vocab


def simple_tokenizer(text):
    return text.lower().split()


# 真实数据集
src_vocab = build_vocab(src_sentences, simple_tokenizer, min_freq=5, max_size=20000)
trg_vocab = build_vocab(trg_sentences, simple_tokenizer, min_freq=5, max_size=20000)

INPUT_DIM = len(src_vocab)
OUTPUT_DIM = len(trg_vocab)

print("src_vocab size =", INPUT_DIM, "trg_vocab size =", OUTPUT_DIM)


ENC_EMB_DIM = 256
DEC_EMB_DIM = 256
HID_DIM = 512
N_LAYERS = 2
ENC_DROPOUT = 0.5
DEC_DROPOUT = 0.5
BATCH_SIZE = 2
N_EPOCHS = 10

device = (
    torch.accelerator.current_accelerator().type
    if torch.accelerator.is_available()
    else "cpu"
)

print(f"Using device: {device}")

# 数据集和加载器
dataset = SimpleDataset(src_sentences, trg_sentences, src_vocab, trg_vocab)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, collate_fn=collate_fn)

# 模型
enc = Encoder(INPUT_DIM, ENC_EMB_DIM, HID_DIM, N_LAYERS, ENC_DROPOUT)
dec = Decoder(OUTPUT_DIM, DEC_EMB_DIM, HID_DIM, N_LAYERS, DEC_DROPOUT)
model = Seq2Seq(enc, dec, device).to(device)

# 优化器和损失函数
optimizer = optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss(ignore_index=src_vocab["<pad>"])

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

    print(f"Epoch {epoch + 1}, Loss: {epoch_loss / len(dataloader):.4f}")

# 保存模型
torch.save(src_vocab, "src_vocab.pth")
torch.save(trg_vocab, "trg_vocab.pth")
torch.save(model.state_dict(), "translation_model.pth")
