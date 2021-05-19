# Corpus
This folder contains the corpus extracted from the dataset of mapped test cases.
The corpus is organized in different levels of focal context, incorporating information from the focal method and class within the *input sentence*, which can inform the model when generating test cases. The different levels of focal contexts are the following: 

- *FM*: focal method
- *FM_FC*: focal method + focal class name
- *FM_FC_CO*: focal method + focal class name + constructor signatures
- *FM_FC_MS*: focal method + focal class name + constructor signatures + public method signatures
- *FM_FC_MS_FF*: focal method + focal class name + constructor signatures + public method signatures + public fields

## JSON
The `json/` folder contains the target test case as well as all the five variations of focal context input. 

```yaml
target: <TEST_CASE>
src_fm: <FOCAL_METHOD>
src_fm_fc: <FOCAL_CLASS_NAME> <FOCAL_METHOD>
src_fm_fc_co: <FOCAL_CLASS_NAME> <FOCAL_METHOD> <CONTRSUCTORS>
src_fm_fc_ms: <FOCAL_CLASS_NAME> <FOCAL_METHOD> <CONTRSUCTORS> <METHOD_SIGNATURES>
src_fm_fc_ms_ff: <FOCAL_CLASS_NAME> <FOCAL_METHOD> <CONTRSUCTORS> <METHOD_SIGNATURES> <FIELDS>
```


## Raw
The `raw/` folder contains the raw text parallel corpus of focal methods and test cases.
The corpus does not contain duplicate pairs, and is organized in train, validation, and test set.

## Tokenized
The `tokenized/` folder contains the parallel corpus tokenized using a Byte-Level BPE Tokenizer. Specifically, we use the ByteLevelBPETokenizer from [huggingface/tokenizers](https://github.com/huggingface/tokenizers "text") with a Roberta-based vocabulary available in `preprocessed/dict.tar.bz2`


## Preprocessed
The `preprocessed/` folder contains the corpus preprocessed using fairseq as well as the dictionary.  Specifically, we use the [fairseq-preprocess](https://fairseq.readthedocs.io/en/latest/command_line_tools.html#fairseq-preprocess "fairseq-preprocess") command that build vocabularies and binarize the data, to be used during training.
