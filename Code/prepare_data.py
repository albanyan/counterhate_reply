import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer
import torch
from torch.utils.data import TensorDataset
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
import os

# Constant seed for reproducibility.
SEED = 42
BATCH_SIZE = 16
EXP = [
    "counter_hate",
    "reply",
]  # choose any combination of: hateful_tweet, counter_hate, reply


def preprocess_dataframe_tweets(df, col):
    # remove URL
    df[col + "_proc"] = df[col].str.replace(r"http(\S)+", r"", regex=True)
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"http ...", r"", regex=True)
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"http", r"", regex=True)
    # remove RT, @
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"(RT|rt)[ ]*@[ ]*[\S]+", r"", regex=True)
    df[df[col + "_proc"].str.contains(r"RT[ ]?@")]
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"@[\S]+", r"", regex=True)
    # remove non-ascii words and characters
    df[col + "_proc"] = [
        "".join([i if ord(i) < 128 else "" for i in text]) for text in df[col + "_proc"]
    ]
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"_[\S]?", r"", regex=True)
    # remove &, < and >
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"&amp;?", r"and", regex=True)
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"&lt;", r"<", regex=True)
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"&gt;", r">", regex=True)
    # remove extra space
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"[ ]{2, }", r" ", regex=True)
    # insert space between punctuation marks
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"([\w\d]+)([^\w\d ]+)", r"\1 \2", regex=True)
    df[col + "_proc"] = df[col + "_proc"].str.replace(r"([^\w\d ]+)([\w\d]+)", r"\1 \2", regex=True)
    # lower case and strip white spaces at both ends
    df[col + "_proc"] = df[col + "_proc"].str.lower()
    df[col + "_proc"] = df[col + "_proc"].str.strip()


def encode_sentence(s, tokenizer):
    return tokenizer.encode_plus(
        s,  # Sentence to encode.
        add_special_tokens=True,  # Add separation tokens
        max_length=128,  # Pad & truncate all sentences.
        pad_to_max_length=True,
        return_attention_mask=True,  # Construct attn. masks.
        return_tensors="pt",  # Return pytorch tensors.
    )


def bert_encode(df, tokenizer, exp, max_seq_length=128):
    input_ids = []
    attention_masks = []
    seprator = " </s> "
    for s in df[exp].values:
        sent = seprator.join(filter(None, s))
        encoded_dict = tokenizer.encode_plus(
            sent,  # Sentence to encode.
            add_special_tokens=True,  # Add <s> and </s> at the beginning and the end
            max_length=max_seq_length,  # Pad & truncate all sentences.
            pad_to_max_length=True,
            return_attention_mask=True,  # Construct attn. masks.
            return_tensors="pt",  # Return pytorch tensors.
        )

        # Add the encoded sentence to the list.
        input_ids.append(encoded_dict["input_ids"])

        # And its attention mask (simply differentiates padding from non-padding).
        attention_masks.append(encoded_dict["attention_mask"])
    input_ids = torch.cat(input_ids, dim=0)
    attention_masks = torch.cat(attention_masks, dim=0)

    inputs = {"input_word_ids": input_ids, "input_mask": attention_masks}

    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv-file", required=True, help="Location of the data file in a .csv format."
    )
    parser.add_argument(
        "--question",
        required=True,
        help="A number from 1 to 4 indicating the question number.",
    )
    parser.add_argument(
        "--output-dir",
        required=False,
        default="./Dataloaders",
        help="A directory to save the output files in.",
    )
    args = parser.parse_args()
    csv_file = args.csv_file

    if int(args.question) not in [1, 2, 3, 4]:
        raise Exception("Question number must be in [1, 2, 3, 4].")
    else:
        Q = "Q" + args.question

    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        dataset = df[~df[Q].isnull()]
    else:
        raise Exception(f'CSV file "{csv_file}" not found.')

    output_dir = args.output_dir
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    X_train, X_test, y_train, y_test = train_test_split(
        dataset[EXP], dataset[Q], test_size=0.2, stratify=dataset[Q], random_state=SEED
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.1, stratify=y_train, random_state=SEED
    )

    df_train = X_train.join(y_train)
    df_val = X_val.join(y_val)
    df_test = X_test.join(y_test)

    for exp in EXP:
        preprocess_dataframe_tweets(df_train, col=exp)
        preprocess_dataframe_tweets(df_val, col=exp)
        preprocess_dataframe_tweets(df_test, col=exp)

    tokenizer = AutoTokenizer.from_pretrained(
        "vinai/bertweet-base", use_fast=True, normalization=True
    )

    tweet_train = bert_encode(df_train, tokenizer, EXP)
    tweet_train_labels = df_train[Q].astype(int)
    tweet_valid = bert_encode(df_val, tokenizer, EXP)
    tweet_valid_labels = df_val[Q].astype(int)
    tweet_test = bert_encode(df_test, tokenizer, EXP)
    tweet_test_labels = df_test[Q].astype(int)

    input_ids, attention_masks = tweet_train.values()
    labels = tweet_train_labels

    # Combine the training inputs into a TensorDataset.
    input_ids, attention_masks = tweet_train.values()
    labels = torch.tensor(tweet_train_labels.values, dtype=torch.long)
    train_dataset = TensorDataset(input_ids, attention_masks, labels)

    # Create a 90-10 train-validation split.
    input_ids, attention_masks = tweet_valid.values()
    labels = torch.tensor(tweet_valid_labels.values, dtype=torch.long)
    val_dataset = TensorDataset(input_ids, attention_masks, labels)

    # Create a 90-10 train-validation split.
    input_ids, attention_masks = tweet_test.values()
    labels = torch.tensor(tweet_test_labels.values, dtype=torch.long)
    test_dataset = TensorDataset(input_ids, attention_masks, labels)

    # The DataLoader needs to know our batch size for training, so we specify it
    # here. For fine-tuning BERT on a specific task, the authors recommend a batch size of 16 or 32.

    # Create the DataLoaders for our training and validation sets.
    # We'll take training samples in random order.
    train_dataloader = DataLoader(
        train_dataset,  # The training samples.
        sampler=RandomSampler(train_dataset),  # Select batches randomly
        batch_size=BATCH_SIZE,  # Trains with this batch size.
    )

    # For validation the order doesn't matter, so we'll just read them sequentially.
    validation_dataloader = DataLoader(
        val_dataset,  # The validation samples.
        sampler=SequentialSampler(val_dataset),  # Pull out batches sequentially.
        batch_size=BATCH_SIZE,  # Evaluate with this batch size.
    )

    # For testing the order doesn't matter, so we'll just read them sequentially.
    testing_dataloader = DataLoader(
        test_dataset,  # The validation samples.
        sampler=SequentialSampler(test_dataset),  # Pull out batches sequentially.
        batch_size=BATCH_SIZE,  # Evaluate with this batch size.
    )

    torch.save(train_dataloader, os.path.join(output_dir, "train.pth"))
    torch.save(validation_dataloader, os.path.join(output_dir, "valid.pth"))
    torch.save(testing_dataloader, os.path.join(output_dir, "test.pth"))


if __name__ == "__main__":
    main()
