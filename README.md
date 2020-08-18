# Unit Test Generation Task
The task of Automated Unit Test Case generation has been the focus of extensive research in software engineering community. Existing approaches are usually guided by test coverage criteria and generate synthetic test cases that are often difficult to read or understand even for developers familiar with the code base.

# Dataset Description

We introduce `methods2test`: a supervised dataset consisting of Test Cases and their corresponding Focal Methods from a large set of Java software repositories. To extract `methods2test`, we first parsed the Java projects to obtain classes and methods with their associated metadata. Next we identified each Test Class and its corresponding Focal Class. Finally, for each Test Case within a Test Class, we mapped it to the related Focal Method and obtain a set of Mapped Test Cases.

## Accessing via Git LSF
The repository makes use of the Git large file storage (LFS) service. Git LFS does replacing large files in the repository with tiny pointer files. To pull the actual files do:
```bash
# first, clone the repo
git clone git@github.com:microsoft/methods2test.git
# next, change to the methods2test folder
cd methods2test
# finally, pull the files
git lfs pull
```

Please refer to this [web page](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-large-files?view=azure-devops) for more details about Gut LFS and working with large files.

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

The dataset is stored as JSON files of the following format:
```yaml
Repository (repository info)
    repo_id: int, unique identifier of the repository in the dataset
    url: string, repository URL
    stars: int, cumulative number of start on GitHub
    updates: string, time stamp of the most recent update made to the repository
    created: string, time stamp of the repository creation
    fork: Boolean, whether repository is a fork
MappedTestCase (list, an entry for each mapped Test Case)
    focal_class: string, relative path (inside the repository) to file containing the focal method
    focal_method: properties of the focal method
        body: string, source code of the focal method
        invocations: list of strings of all methods invoked in the file scope
        testcase: boolean, whether the method is a test case
        signature: string, focal method signature (including the class name)
        parameters: string, parameter list of the focal method
        identifier: string, focal method name 
        class: string, a class name containing the focal method  
    test_class: string, relative path (inside the repository) to file containing the unit test case
    test_case: properties of the unit test case
        body: string, source code of the unit test case method
        invocations: list of strings of all methods invoked in the file scope
        testcase: boolean, whether the method is a test case (always True for test cases)
        signature: string, unit test case method signature (including the class name)
        parameters: string, parameter list of the unit test case method
        identifier: string, unit test case method name
        class: string, a class name containing the unit test case method   
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
