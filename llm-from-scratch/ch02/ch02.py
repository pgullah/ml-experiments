
import os
import urllib.request
from tokenizer import SimpleTokenizerV1
from importlib.metadata import version
import tiktoken

def build_corpus():
    file_path = "/var/tmp/data/llm-from-scratch/ch02/the-verdict.txt"
    if not os.path.exists(file_path):
        # download the file if it doesn't exist
        url = "https://raw.githubusercontent.com/rasbt/LLMs-from-scratch/main/ch02/01_main-chapter-code/the-verdict.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        urllib.request.urlretrieve(url, file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    return raw_text


def main():
    corpus = build_corpus()
    print("Total number of characters in the text:", len(corpus))
    print("raw text at index:", corpus[:99])

    print("\n#### Building the vocabulary...")
    vocab = SimpleTokenizerV1.build_vocab(SimpleTokenizerV1.tokenize(corpus))
    print("Vocabulary size:", len(vocab))
    for i, item in enumerate(vocab.items()):
        print(item)
        if i >= 50:
            break

    print("\n#### Tokenizing the text...")
    bpe_tokenizer = SimpleTokenizerV1(vocab)
    text = """"It's the last he painted, you know,"
        Mrs. Gisburn said with pardonable pride."""
    token_ids = bpe_tokenizer.encode(text)
    print("Total number of tokens in the text:", len(token_ids))
    print("token IDs:", token_ids)
    decoded_text = bpe_tokenizer.decode(token_ids)
    print("Decoded text:", decoded_text)

    print("\n#### Showing the last 5 items in the vocabulary...")
    for i, item in enumerate(list(vocab.items())[-5:]):
        print(item)

    print("\n#### Encoding a new text...")
    text = "Hello, do you like tea?"
    print(bpe_tokenizer.encode(text))


    text1 = "Hello, do you like tea?"
    text2 = "In the sunlit terraces of the palace."
    text = " <|endoftext|> ".join((text1, text2))
    print(text)
    print(bpe_tokenizer.encode(text))
    print(bpe_tokenizer.decode(bpe_tokenizer.encode(text)))

    print("\n#### Encoding a new text with BPE Tokenizer")
    
    print("tiktoken version:", version("tiktoken"))
    bpe_tokenizer = tiktoken.get_encoding("gpt2")
    text = (
    "Hello, do you like tea? <|endoftext|> In the sunlit terraces"
    "of someunknownPlace."
    )
    integers = bpe_tokenizer.encode(text, allowed_special={"<|endoftext|>"})
    print(integers)
    strings = bpe_tokenizer.decode(integers)
    print(strings)

    print("\n### Unknown words encoding with BPE Tokenizer")
    unknow_word_text="LAKsjflks jeoijjsfl"
    unknow_word_tokens = bpe_tokenizer.encode(unknow_word_text, allowed_special={"<|endoftext|>"})
    print("Unknown word tokens:", unknow_word_tokens)
    print("Decoded unknown word tokens:", bpe_tokenizer.decode(unknow_word_tokens))

    print("\n### encode corpus with BPE Tokenizer")
    enc_text = bpe_tokenizer.encode(corpus, allowed_special={"<|endoftext|>"})
    print("Encoded corpus length:", len(enc_text))
    # print("Post 50 tokens:", enc_text[50:])
    enc_sample = enc_text[50:]
    context_size = 4
    x = enc_sample[:context_size]
    y = enc_sample[1:context_size + 1]
    print(f"x: {x} -> {bpe_tokenizer.decode(x)}")
    print(f"y: {y} -> {bpe_tokenizer.decode(y)}")

    for i in range(1, context_size+1):
        context = enc_sample[:i]
        desired = enc_sample[i]
        # print(f"{context} ----> {desired} ")
        print(f"{context} ({bpe_tokenizer.decode(context)}) ----> {desired} ({bpe_tokenizer.decode([desired])})")


if __name__ == "__main__":
    main()