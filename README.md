# Linkedin-Scraper

This aim of this project is to create an executable that can be used to scrape
LinkedIn data for a given list of employees.

## Overview

The repo consists of:

1. LinkedIn_Data_Scraper.py

The main script.

2. util.py

Contains functions used by the main script.

3. config.txt

Contains the configurations for the main script such as paths and load delay times.

4. results.xlsx

An Excel sheet that will capture the results for the scraped data.

5. chromedriver.exe

This is an executable that allows the main script to create a new Chrome window.

6. Employee_Details.csv (Not shown)

A list of the employee names and LinkedIn ID's in a csv format.

## Getting started

This program was created in Anaconda using a virual environment. To create and
install the virual environment, run the command:
```
conda env create --file environment.yml
```

Then to activate the environment, run:
```
conda activate LInEnv
```

There are some packages that do not import correctly from the environment.yml file.
To install these packages, run the following commands.

```
python C:\path_to_scripts\Scripts\pywin32_postinstall.py -install
// e.g.
python C:\Users\User\miniconda3\envs\LInEnv\Scripts\pywin32_postinstall.py -install
```

Also, for some reason, I needed to install the devlopment version of pyinstaller:

```
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz
```

To create an executable, run the following command:
```
pyinstaller LinkedIn_Data_Scraper.py
```
