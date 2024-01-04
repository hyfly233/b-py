import torch
from torch.nn import Transformer


def translate_sentence(sentence, src_vocab, trg_vocab, model, device, max_len=50):
    model.eval()

    tokens = [src_vocab.get(token, src_vocab["<unk>"]) for token in sentence.split()]
    tokens = [src_vocab["<sos>"]] + tokens + [src_vocab["<eos>"]]
    src_tensor = torch.LongTensor(tokens).unsqueeze(1).to(device)

    with torch.no_grad():
        hidden, cell = model.encoder(src_tensor)

    trg_indexes = [trg_vocab["<sos>"]]

    for _ in range(max_len):
        trg_tensor = torch.LongTensor([trg_indexes[-1]]).to(device)

        with torch.no_grad():
            output, hidden, cell = model.decoder(trg_tensor, hidden, cell)

        pred_token = output.argmax(1).item()
        trg_indexes.append(pred_token)

        if pred_token == trg_vocab["<eos>"]:
            break

    trg_tokens = [list(trg_vocab.keys())[i] for i in trg_indexes]
    return trg_tokens[1:-1]  # 去掉 <sos> 和 <eos>


model = Transformer(d_model=512, nhead=8, num_encoder_layers=6, num_decoder_layers=6)
