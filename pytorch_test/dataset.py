from collections import Counter

import torch
from torch.nn.utils.rnn import pad_sequence
from torchtext.data.utils import get_tokenizer


class TranslationDataset:
    def __init__(self, src_sentences, trg_sentences):
        self.src_tokenizer = get_tokenizer('spacy', language='en_core_web_sm')
        self.trg_tokenizer = get_tokenizer('spacy', language='de_core_news_sm')

        # 构建词汇表
        self.src_vocab = self.build_vocab(src_sentences, self.src_tokenizer)
        self.trg_vocab = self.build_vocab(trg_sentences, self.trg_tokenizer)

        self.src_sentences = src_sentences
        self.trg_sentences = trg_sentences

    def build_vocab(self, sentences, tokenizer):
        counter = Counter()
        for sentence in sentences:
            counter.update(tokenizer(sentence))
        vocab = {'<pad>': 0, '<sos>': 1, '<eos>': 2, '<unk>': 3}
        for word, _ in counter.most_common():
            vocab[word] = len(vocab)
        return vocab

    def numericalize(self, sentence, vocab, tokenizer):
        tokens = tokenizer(sentence)
        return [vocab.get(token, vocab['<unk>']) for token in tokens]

    def __len__(self):
        return len(self.src_sentences)

    def __getitem__(self, idx):
        src = self.numericalize(self.src_sentences[idx], self.src_vocab, self.src_tokenizer)
        trg = self.numericalize(self.trg_sentences[idx], self.trg_vocab, self.trg_tokenizer)
        return torch.tensor(src), torch.tensor(trg)


def collate_fn(batch):
    src_batch, trg_batch = [], []
    for src, trg in batch:
        src_batch.append(torch.cat([torch.tensor([1]), src, torch.tensor([2])]))  # <sos>, <eos>
        trg_batch.append(torch.cat([torch.tensor([1]), trg, torch.tensor([2])]))
    src_batch = pad_sequence(src_batch, padding_value=0)
    trg_batch = pad_sequence(trg_batch, padding_value=0)
    return src_batch, trg_batch
