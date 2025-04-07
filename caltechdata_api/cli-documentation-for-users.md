# CaltechDATA Command Line Interface (CLI) Documentation for Users

## Contents

1. [About the API](#introduction)

2. [Setup and Installation](#setup-and-installation)
   
   2.1 [For Mac OS Users](#for-mac-os-users)
   
   2.2 [For Windows Users](#for-windows-users)

   2.3 [Windows Subsystem for Linux](#windows-subsystem-for-linux-users)
   
3. [Interacting with the CaltechDATA CLI](#interacting-with-the-caltechdata-cli)

   3.1 [CaltechDATA and the Test Instance of the Repository: Which Should I Use?]()
   
   3.2 [For Mac OS Users and and Windows Subsystem for Linux Users](#for-macos-users)
   
   3.3 [For Windows Users](#for-windows-users-1)
   
4. [Additional Steps](#additional-steps)
   
5. [Troubleshooting](#troubleshooting)

   5.1 [General Troubleshooting FAQs](#general-troubleshooting-and-faqs)
   
   5.2 [Windows Subsystem for Linux](#windows-subsystem-for-linux-troubleshooting-and-faqs)
   
7. [Contact Us](#contact-us)

## Introduction
The CaltechData API repository houses the codebase for accessing, uploading, and editing research data and metadata from Caltech's collections through a program or CLI. This API provides developers with endpoints to interact with datasets and retrieve relevant information.


## Setup and Installation:
Requirements for a successful setup: you must have Python 3.6 or a later version installed on your system.

### For Mac OS Users:
#### Step 1: 
Please open the Terminal.

#### Step 2: 
Please install the Caltechdata_api Library via pip using the command shown: 

`pip install caltechdata_api`

### For Windows Users:

#### Step 1: 
Please go to https://github.com/caltechlibrary/caltechdata_api.git and click the green button that says "<> Code". Then choose the option that says "Download ZIP".

![Interface with a Download xip button](<pictures-documentation/Step 1.png>)

#### Step 2: 
Please extract the files from the downloaded zip file to a new folder (we recommend this folder be on the desktop and that you name this folder something easy to recall).

![Interface for extracting zip files](<pictures-documentation/Step 2.png>)

#### Step 3: 
In the next few steps, we shall change the directory to the folder called "caltechdata_api" inside the folder you extracted from the downloaded ZIP file. To do this, please go to the file you saved either on the file manager or on its location (this would be the desktop if you saved it there). Then, please open the folder called "caltechdata_api_main" and then right click on the folder inside it called "caltechdata_api" and choose the option that says "copy as path".

![Interface for changing directory](<pictures-documentation/Step 3(a).png>)

Above: Open the file on file manager as shown.

![Interface of the file manager](<pictures-documentation/Step 3(b).png>)

Above: Go into the folder caltechdata_api_main.

![Navigating the file manager](<pictures-documentation/Step 3(c).png>)

Above: Right click on the folder called caltechdata_api and choose the option that says copy as path.

#### Step 4: 
Next, please open a the Windows PowerShell or a code editor (we recommend using VSCode if you choose to use a code editor) and then open its Terminal.

![Visual studio code terminal](<pictures-documentation/Step 4(a).png>)
Above: Using Visual Studio Code (VSCode)

![Windows PowerShell terminal](<pictures-documentation/Step 4(b).png>)
Above: Using Windows PowerShell

#### Step 5: 
Next, please open the dropdown menu near the "+" icon on the top right hand corner of the terminal and choose the option that says "Git Bash". You can skip this step and go directly to the next step if you are using the Windows Powershell.

![Git bash selection](<pictures-documentation/Step 5.png>)

#### Step 6: 
Then, please type in the command as shown:

```cd <paste the file path you copied here>```

For example, it could look like this:

```cd "C:\Users\kshem\Desktop\Demonstration\caltechdata_api-main\caltechdata_api"```

![VSCode Path settings](<pictures-documentation/Step 6(a).png>)
Above: Using Visual Studio Code (VSCode)

![PowerShell path settings](<pictures-documentation//Step 6(b).png>)
Above: Using Windows PowerShell

### Windows Subsystem for Linux Users:
The Windows Subsystem for Linux (WSL) lets developers install a Linux distribution (such as Ubuntu) and use Linux applications, utilities, and Bash command-line tools directly on Windows. [1](https://learn.microsoft.com/en-us/windows/wsl/). In order to interact with the CaltechDATA CLI, you may use a BASH terminal on WSL.

#### Step 1:
First, please install the Windows Subsystem for Linux (WSL). To do this, please run the following command in a Windows Powershell terminal:

```wsl --install```

When prompted, please enter a password and keep a record of it ready for future reference.

#### Step 2:
If you do not already have some version of python 3 installed on your system, please run this command in the Windows Powershell terminal:

```sudo apt install python3```

Please note that the password you set while installing the Windows Subsystem for Linux (WSL) in the previous step is necessary to run this command (and any other sudo apt install commands).

#### Step 3:
Next, please install pipx. To do this please run the following command in a Windows Powershell terminal:

```sudo apt install pipx```

Please note that the password you set while installing the Windows Subsystem for Linux (WSL) in the first step is necessary to run this command (and any other sudo apt install commands).

#### Step 4:
Next, please ensure path. To do this, please run the following in a Windows Powershell terminal:

``` pipx ensurepath```

#### Step 5:
Now, we shall install caltechdata_api. To do this, please run the following command in a Windows Poweshell terminal:

```pipx install caltechdata_api```


## Interacting with the CaltechDATA CLI
The CaltechDATA Command Line Interface (CLI) helps you interact with the CaltechDATA repository to upload research data, link your data with your publications, and assign a permanent DOI to your dataset so that others can reference the dataset. You can access the datasets you create or edit at https://data.caltech.edu/.

### The Test Instance or the CaltechDATA Repository
If you would like to create and edit a test record of your datset before uploading it to the CaltechDATA Repository and generating a permanent DOI, you can also use the CaltechDATA Command Line Interface (CLI) to interact with the test instance of the CaltechDATA Repository that you can access at https://data.caltechlibrary.dev/.

We recommend using the CLI to interact with the test instance if you are not ready to generate a permanent DOI but would like to experiment to avoid creating junk records on the original CaltechDATA Repository. In general, users create and edit datasets in the same way regardless of whether the dataset exists on the original CaltechDATA Repository or the test instance.

Now we shall outline the steps to interact with the CLI.

### For MacOS Users and Windows Subsystem for Linux (WSL) Users:
Please run the command shown in order to interact with the CaltechDATA Repository:

```caltechdata_api```

Otherwise, please run the command shown to interact with the test instance of the CaltechDATA Repository:

```caltechdata_api -test```

### For Windows Users:
#### Step 1:
To interact with the CaltechDATA Repository, please type in this command as shown to open and run the CaltechDATA Command Line Interface (CLI):

```python cli.py```

![VSCode interface for cli](<pictures-documentation/Interact CLI Step 1(a).png>)
Above: Using Visual Studio Code (VSCode)

![PowerShell interface for cli](<pictures-documentation/Interact CLI Step 1(b).png>)
Above: Using Windows PowerShell

Otherwise, to interact with the test instance of the CaltechDATA Repository, please type in this command as shown to open and run the CaltechDATA Command Line Interface (CLI):

```python cli.py -test```

![VSCode test cli](<pictures-documentation/Interact CLI Step 1(c) Test Instance.png>)
Above: Using Visual Studio Code (VSCode)

![PowerShell test cli](<pictures-documentation/Interact CLI Step 1(d) Test Instance.png>)
Above: Using Windows PowerShell

#### Step 2:
Although the CLI setup is complete, there is one additional step required before you can begin interacting with the CLI. 

Note that the terminal is now present in the "caltechdata_api" folder or directory and can only access the files there. Please save the files you would like to upload in this particular folder. To check if your files are in this folder and thus, visible to the terminal you can run the following command to display the files in the current directory:

```dir```

![PowerShell attached files](<pictures-documentation/Interact CLI Step 2(a).png>)
Above: Adding your files to the directory

![VSCode attached files](<pictures-documentation/Interact CLI Step 2(b).png>)
Above: Using Visual Studio Code (VSCode)

![PowerShell cli](<pictures-documentation/Interact CLI Step 2(c).png>)
Above: Using Windows PowerShell

## Additional Steps:

### Creating A Token:
In order to create or edit datasets you'll need to create a token. In order to this, you'll need to open the platform you are uploading your dataset to (the original CaltechDATA Repository or the test instance of it) and log in. Then follow these steps:

#### Step 1: 
Please click the person icon appearing on the top right and choose "Applications" from the dropdown menu that appears.

#### Step 2: 
Next, please click the option that says "New Token" and name your token.

### What Files You'll Need to Create A New Dataset:
In order to create a new dataset, you will need a:

1) File containing your dataset (csv or json file)
2) A metadata file (json file)

We use a customised version of Datacite 4.3 Schema which you can download [here](https://github.com/datacite/schema/blob/master/source/json/kernel-4.3/datacite_4.3_schema.json). Otherwise you can use your own.

## Troubleshooting

### General Troubleshooting and FAQs:
#### My ORCID doesn't work:
Please try to input the ORCID without any hyphens.

#### What is my unique identifier/record id?
Your record id is the last part of the DOI link your dataset is linked to. It is the part that comes after the last forward slash. For example: if your DOI link is https://doi.org/10.33569/5t2wh-1e586, then your record id is 5t2wh-1e586.

### Windows Subsystem for Linux Troubleshooting and FAQs:
#### How can I open the Windows Subsystem for Linux after installation?
To do this, please run the following command in a Windows Powershell terminal:

```wsl```

## Contact Us
For further questions, email data@caltech.edu or visit the FAQs at [CaltechDATA](https://libanswers.caltech.edu/search/?t=0&adv=1&topics=CaltechDATA).
