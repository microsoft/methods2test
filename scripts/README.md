The `script` folder contains the following files:
- `find_map_test_cases.py`: the main script to find and map test cases in a repository
- `TestParser.py`: an utility class that parses test cases
- `java-grammar.so`: tree-sitter Java grammar file


## Extraction & Mapping
To extract test cases and map them to focal methods, we can run the `find_map_test_cases.py` script, which takes the following arguments:

- `--repo_url`: GitHub URL of the repo to analyze
- `--repo_id`: ID used to refer to the repo
- `--grammar`: Filepath of the tree-sitter grammar
- `--tmp`: Path to a temporary folder used for processing
- `--output`: Path to the output folder


### Example
Let us analyze the Apache Hadoop project (url: https://github.com/apache/hadoop), extract and map test cases using this command:

```
python find_map_test_cases.py 
    --repo_url https://github.com/apache/hadoop
    --repo_id 23418517  
    --grammar ./java-grammar.so 
    --tmp /tmp/tmp/ 
    --output /tmp/output/
```