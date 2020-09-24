# Corpus
This folder contains the corpus extracted from the dataset of mapped test cases.

## Raw
The `raw/` folder contains the raw text parallel corpus of focal methods and test cases.
The corpus does not contain duplicate pairs, and is organized in train, validation, and test set.

## Tokenized
The `tokenized/` folder contains the parallel corpus tokenized using a Byte-Level BPE Tokenizer. Specifically, we use the ByteLevelBPETokenizer from [huggingface/tokenizers](https://github.com/huggingface/tokenizers "text") with a Roberta-based vocabulary available in `preprocessed/dict.tar.bz2`


## Preprocessed
The `preprocessed/` folder contains the corpus preprocessed using fairseq as well as the dictionary.  Specifically, we use the [fairseq-preprocess](https://fairseq.readthedocs.io/en/latest/command_line_tools.html#fairseq-preprocess "fairseq-preprocess") command that build vocabularies and binarize the data, to be used during training.
