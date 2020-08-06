Automated Unit Test Case generation has been the focus of extensive research in software engineering community. Existing approaches are usually guided by test coverage criteria and generate synthetic test cases that are often difficult to read or understand even for developers familiar with the code base. 

We introduce `methods2test`: a supervised dataset consisting of Test Cases and their corresponding Focal Methods from a large set of Java software repositories. To extract `methods2test`, we first parsed the Java projects to obtain classes and methods with their associated metadata. Next we identified each Test Class and its corresponding Focal Class. Finally, for each Test Case within a Test Class, we mapped it to the related Focal Method and obtain a set of Mapped Test Cases.

# Data Format

The dataset is stored as JSON files of the following format:
```
Repository Info
 repo_id
 url
 stars
MappedTestCase (list, an entry for each Test Case)
 Test class
 Test Case Properties (body, signature, etc.)
 Focal Class
 Focal Method Properties (body, signature, etc.)
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
