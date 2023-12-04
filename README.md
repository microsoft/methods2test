# Unit Test Generation Task
The task of Automated Unit Test Case generation has been the focus of extensive research in software engineering community. Existing approaches are usually guided by test coverage criteria and generate synthetic test cases that are often difficult to read or understand even for developers familiar with the code base.

# Dataset Description

We introduce `methods2test`: a supervised dataset consisting of Test Cases and their corresponding Focal Methods from a large set of Java software repositories. To extract `methods2test`, we first parsed the Java projects to obtain classes and methods with their associated metadata. Next we identified each Test Class and its corresponding Focal Class. Finally, for each Test Case within a Test Class, we mapped it to the related Focal Method and obtain a set of Mapped Test Cases.

## Accessing via Git LFS
The repository makes use of the Git large file storage (LFS) service. Git LFS does replacing large files in the repository with tiny pointer files. To pull the actual files do:
```bash
# first, clone the repo
git clone git@github.com:microsoft/methods2test.git
# next, change to the methods2test folder
cd methods2test
# finally, pull the files
git lfs pull
```

Please refer to this [web page](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-large-files?view=azure-devops) for more details about Git LFS and working with large files.

## What is Unit Test Case?
Unit testing is a level of software testing where individual software components are tested with a purpose of validating that each software component performs as designed. A unit is the smallest testable part of any software. In this work, we are focusing on testing Java methods.

We identify all the Test Classes, which are classes that contain a test case. To do so, we mark a class as a Test Class if it contains at least one method with the `@Test` annotation. This annotation informs JUnit that the method to which it is attached can be run as a test case.

## What is a Focal Method?
Focal methods are the methods under test. For each Test Case (that is, method within a Test Class with the `@Test`annotation) we attempt to identify the corresponding Focal Method within the focal class. To this aim, we employ the following heuristics:

1. Name Matching: similarly to the best practices related to the class names, Test Cases names are often similar to the corresponding Focal Methods. Thus, the first heuristic attempts to match the Test Cases with a Focal Method having a name that matches, after removing possible `Test` prefix/suffix. 

1. Unique Method Call: if the previous heuristic did not identify any focal method, we compute the intersection between:
    1. the list of method invocations within the test case and 
    1. the list of method defined within the focal class. If the intersection results in a unique method, then we select the method as the focal method. 

The rationale behind this approach is the following: since we have already matched the test class with the focal class (with very high confidence heuristics), if the test case invokes a single method within that focal class, it is very likely testing that single method.


## Data Format
The data is organized as `dataset` and `corpus`.

### Dataset
The `dataset` contains test cases mapped to their corresponding focal methods, along with a rich set of metadata.
The dataset is stored as JSON files of the following format:
```yaml
repository: repository info
    repo_id: int, unique identifier of the repository in the dataset
    url: string, repository URL
    language: string, programming languages of the repository
    is_fork: Boolean, whether repository is a fork
    fork_count: int, number of forks
    stargazer_count: int, cumulative number of start on GitHub

focal_class: properties of the focal class
    identifier: string, class name
    superclass: string, superclass definition
    interfaces: string, interface definition
    fields: list, class fields
    methods: list, class methods
    file: string, relative path (inside the repository) to file containing the focal class

focal_method: properties of the focal method
    identifier: string, focal method name 
    parameters: string, parameter list of the focal method
    modifiers: string, method modifiers
    return: string, return type
    body: string, source code of the focal method
    signature: string, focal method signature (return type + name + parameters)
    full_signature: string, focal method signature (modified + return type + name + parameters)
    class_method_signature: string, focal method signature (class + name + parameters)
    testcase: boolean, whether the method is a test case
    constructor: boolean, whether the method is a constructor
    invocations: list of strings of all methods invoked in the file scope

test_class:  properties of the test class containing the test case
    identifier: string, class name
    superclass: string, superclass definition
    interfaces: string, interface definition
    fields: list, class fields
    file: string, relative path (inside the repository) to file containing the test class

test_case: properties of the unit test case
    identifier: string, unit test case method name
    parameters: string, parameter list of the unit test case method
    modifiers: string, method modifiers
    return: string, return type
    body: string, source code of the unit test case method
    signature: string, test case signature (return type + name + parameters)
    full_signature: string, test case signature (modified + return type + name + parameters)
    class_method_signature: string, test case signature (class + name + parameters)
    testcase: boolean, whether the method is a test case
    constructor: boolean, whether the method is a constructor
    invocations: list of strings of all methods invoked in the file scope
```

### Corpus
The `corpus` folder contains the parallel corpus of focal methods and test cases, as json, raw, tokenized, and preprocessed, suitable for training and evaluation of the model.
The corpus is organized in different levels of focal context, incorporating information from the focal method and class within the *input sentence*, which can inform the model when generating test cases. The different levels of focal contexts are the following: 

- *FM*: focal method
- *FM_FC*: focal method + focal class name
- *FM_FC_CO*: focal method + focal class name + constructor signatures
- *FM_FC_MS*: focal method + focal class name + constructor signatures + public method signatures
- *FM_FC_MS_FF*: focal method + focal class name + constructor signatures + public method signatures + public fields

### Methods2Test v1.0
The `methods2test-v1.0` folder contains the previous version of this dataset. More information are availble in the README within the folder.


# Statistics
The dataset contains 780,944 test cases mapped to their corresponding focal methods, extracted from 9,410 unique repositories (91,385 original repositories analyzed).

**Total**
- Repositories: 9,410
- Instances: 780,944

We split the dataset in training (80%), validaiton (10%), and test (10%) sets. The split is performed avoiding data leakage at repository-level, that is, all instances from a given repository will appears in a single set (e.g., in training but not in test). Duplicate pairs with same code representation have been removed.

**Training**
- Repositories: 7,440
- Instances:    624,022

**Validation**
- Repositories: 953
- Instances:    78,534

**Test**
- Repositories: 1,017
- Instances:    78,388




# Citation

```latex
@misc{tufano2020unit,
    title={Unit Test Case Generation with Transformers and Focal Context},
    author={Michele Tufano and Dawn Drain and Alexey Svyatkovskiy and Shao Kun Deng and Neel Sundaresan},
    year={2020},
    eprint={2009.05617},
    archivePrefix={arXiv},
    primaryClass={cs.SE}
}
```

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Dataset Metadata
The following table is necessary for this dataset to be indexed by search
engines such as <a href="https://g.co/datasetsearch">Google Dataset Search</a>.
<div itemscope itemtype="http://schema.org/Dataset">
<table>
  <tr>
    <th>property</th>
    <th>value</th>
  </tr>
  <tr>
    <td>name</td>
    <td><code itemprop="name">methods2test</code></td>
  </tr>
  <tr>
    <td>url</td>
    <td><code itemprop="url">https://github.com/microsoft/methods2test</code></td>
  </tr>
  <tr>
    <td>sameAs</td>
    <td><code itemprop="sameAs">https://github.com/microsoft/methods2test</code></td>
  </tr>
  <tr>
    <td>description</td>
    <td><code itemprop="description">The task of Automated Unit Test Case generation has been the focus of extensive research in software engineering community. Existing approaches are usually guided by test coverage criteria and generate synthetic test cases that are often difficult to read or understand even for developers familiar with the code base.

We introduce `methods2test`: a supervised dataset consisting of Test Cases and their corresponding Focal Methods from a large set of Java software repositories. To extract `methods2test`, we first parsed the Java projects to obtain classes and methods with their associated metadata. Next we identified each Test Class and its corresponding Focal Class. Finally, for each Test Case within a Test Class, we mapped it to the related Focal Method and obtain a set of Mapped Test Cases.
</code></td>
  </tr>
  <tr>
    <td>provider</td>
    <td>
      <div itemscope itemtype="http://schema.org/Organization" itemprop="provider">
        <table>
          <tr>
            <th>property</th>
            <th>value</th>
          </tr>
          <tr>
            <td>name</td>
            <td><code itemprop="name">Microsoft</code></td>
          </tr>
          <tr>
            <td>sameAs</td>
            <td><code itemprop="sameAs">https://en.wikipedia.org/wiki/Microsoft</code></td>
          </tr>
        </table>
      </div>
    </td>
  </tr>
  <tr>
    <td>citation</td>
    <td><code itemprop="citation">https://identifiers.org/arxiv:2009.05617</code></td>
  </tr>
</table>
</div>


