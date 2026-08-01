import re

EOT="<|endoftext|>"
UNKNOWN="<|unk|>"



class SimpleTokenizerV1:
    def __init__(self, vocab):
        self.vocab = vocab
        self.token_to_id = {token: idx for idx, token in enumerate(vocab)}
        self.id_to_token = {idx: token for idx, token in enumerate(vocab)}

    def encode(self, text):
        preprocessed = SimpleTokenizerV1.tokenize(text)
        preprocessed = [ self.token_to_id[token] if token in self.token_to_id else self.token_to_id[UNKNOWN] for token in preprocessed if token.strip()]
        return preprocessed

    def decode(self, token_ids):
        text =  " ".join([self.id_to_token[token_id] for token_id in token_ids if token_id in self.id_to_token])
        text = re.sub(r'\s+([,.?!"()\'])', r'\1', text)
        return text

    @staticmethod
    def tokenize(text):
        preprocessed = re.split(r'([,.?_!"()\']|--|\s)', text)
        preprocessed = [token.strip() for token in preprocessed if token.strip()]
        return preprocessed

    @staticmethod
    def build_vocab(tokens):
        all_words = sorted(set(tokens))
        all_words.extend([EOT, UNKNOWN])
        vocab = {word: i for i, word in enumerate(all_words)}
        return vocab