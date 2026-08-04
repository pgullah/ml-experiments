
import os
import urllib.request
from tokenizer import SimpleTokenizerV1
from importlib.metadata import version
import tiktoken
from dataset import GPTDatasetV1, create_dataloader_v1
import torch
from torch.utils.data import DataLoader

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


def run_naive_encoder():
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
    

def run_bpe_encoder():
    corpus = build_corpus()
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


def run_gpt_encoder(batch_size=1, max_length=4, stride=1, suffle=False):
    corpus = build_corpus()
    print("\n#### Encoding a new text with GPT Tokenizer")
    dataloader = create_dataloader_v1(
        corpus, batch_size=batch_size, max_length=max_length, stride=stride, shuffle=suffle
    )
    data_iter = iter(dataloader)
    first_batch = next(data_iter)
    print("first_batch:\n", first_batch)
    print("input_ids shape:\n", type(first_batch[0][0]).shape)
    
    second_batch = next(data_iter)
    print("second_batch:\n", second_batch)


def toy_example():
    input_ids = torch.tensor([2, 3, 5, 1])
    vocab_size = 6
    output_dim = 3
    
    torch.manual_seed(123)
    embedding_layer = torch.nn.Embedding(vocab_size, output_dim)
    # returns 6 X 3 Matrix ie., 6 possible tokens (vocab_size) with 3 values (output_dim)
    print("embedding layer weight: ", embedding_layer.weight)
    
    # sample tensor with a single token ID
    sample_tensor = torch.tensor([3])
    print("Sample tensor: ", sample_tensor)
    print("Sample tensor shape: ", sample_tensor.shape)
    lookup_result = embedding_layer(sample_tensor)
    print("Lookup result: ", lookup_result)
    print("Lookup shape:", lookup_result.shape)
    
    print("\n### Lookup with multiple token IDs")
    # since the vocab_size is 6, we can use token IDs from 0 to 5 
    # other than 6 or more which will throw an error
    # But with in this possible vocab_size, 
    # we can use any combination  or any number of token IDs to lookup the embedding values
    multiple_tokens = torch.tensor([2, 3, 5, 1, 0,])
    print("Multiple tokens: ", multiple_tokens)
    lookup_result_multiple = embedding_layer(multiple_tokens)
    print("Lookup result: ", lookup_result_multiple)
    print("Lookup shape:", lookup_result_multiple.shape)
    

def positional_embedding_example():
    vocab_size = 50257
    output_dim = 256
    token_embedding_layer = torch.nn.Embedding(vocab_size, output_dim)
    raw_text = build_corpus()
    max_length = 4
    dataloader = create_dataloader_v1(
    raw_text, batch_size=8, max_length=max_length,
    stride=max_length, shuffle=False
    )
    data_iter = iter(dataloader)
    inputs, targets = next(data_iter)
    print("Token IDs:\n", inputs)
    print("\nInputs shape:\n", inputs.shape)

if __name__ == "__main__":
    # run_naive_encoder()
    # run_bpe_encoder()
    # run_gpt_encoder(
    #     batch_size=1,
    #     max_length=4, stride=1
    # )
    
    # run_gpt_encoder(
    #     batch_size=2,
    #     max_length=2, stride=2
    # )
    
    # run_gpt_encoder(
    #     batch_size=8,
    #     max_length=4, stride=4
    # )
    
    # toy_example()
    positional_embedding_example()
    
    