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

```

pip install --ignore-installed pywin32
python C:\Users\User\miniconda3\envs\LInEnv\Scripts\pywin32_postinstall.py -install
```

To create an executable, run the following command:
```
pyinstaller LinkedIn_Data_Scraper.py
```
