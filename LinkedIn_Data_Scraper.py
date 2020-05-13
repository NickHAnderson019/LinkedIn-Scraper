# =============================================================================
#                         LinkedIn Post Data Scraper
# =============================================================================
# This script takes a list of PiP employee names and LinkedIn ID's and pulls
# the LinkedIn data on each employee that involves engagement with PiP's
# LinkedIn account.
# -----------------------------------------------------------------------------
from selenium import webdriver
import time, csv
import json
from pandas import DataFrame as pdDataFrame
import xlwings as xw
import util

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

def getEmployeeData(browser, employee, emp_count, emp_total):

    emp_name = employee['name']
    emp_id = employee['linkedin_id']

    global textList
    global config

    error = False

    try:
        # Load the page on the browser
        linkedin_activity_path = 'https://www.linkedin.com/in/'+emp_id+'/detail/recent-activity/'
        browser.get(linkedin_activity_path)

        while(not util.isPageReady(browser)):
            # Wait 1 second
            time.sleep(config["CONSTANTS"]["PAGE_LOAD_TIME"])

        # Data Collection ------------------------------------------------------


        # Scroll the page down if dates aren't equal to or over a month
        # or if counter is over 15
        counter = 1
        while (util.pageShouldBeScrolled(browser) and counter<=10):
            util.scrollPage(browser)
            counter += 1
            # Wait 3 seconds for scrolling to do its thing
            time.sleep(config["CONSTANTS"]["SCROLL_PAUSE_TIME"])

        # Get post data for employee
        textList = util.getPageData(browser)

    except Exception as e:
        print("An error occured. Name: ", emp_name)
        print(e)
        error = True
        textList = []

    # String Parsing -----------------------------------------------------------

    emp_results = []
    count = 0
    for post in textList:

        count += 1 # just a counter

        postCASE = False # initialise

        # split post text by newline character
        post = post.split("\n")

        # if user is online, this is the first element of post
        if ('Status is online' in post[0]):
            ind_off = 1
        else:
            ind_off = 0

        # CASE 1 - shared
        # Check for likes, comments, celebrates
        if (not "likes" in post[ind_off] and not "commented" in post[ind_off] and
            not "celebrates" in post[ind_off] and not "insightful" in post[ind_off] and
            not "loves" in post[ind_off] and not "curious" in post[ind_off]):
            # check for PIP
            # get index of "followers".
            indices_followers = [i for i, s in enumerate(post) if 'followers' in s]
            # get index of "PIP".
            indices_pip = [i for i, s in enumerate(post) if 'Partners in Performance' in s]

            for i in indices_followers:
                for j in indices_pip:
                    if j==i-1:
                        postCASE = "CASE 1"

        # CASE 2 - liked, comment, celebrate PiP post
        elif ("Partners in Performance" in post[1]):
            postCASE = "CASE 2"

        # CASE 3 - liked, comment, celebrate shared PiP post
        else:
            # get index of "followers".
            indices_followers = [i for i, s in enumerate(post) if 'followers' in s]
            # get index of "PIP".
            indices_pip = [i for i, s in enumerate(post) if 'Partners in Performance' in s]

            for i in indices_followers:
                for j in indices_pip:
                    if j==i-1:
                        postCASE = "CASE 3"

        if (not postCASE):
            continue

        if (postCASE=="CASE 1"):
            action = "Shared"
            postdate_indices = [i for i, s in enumerate(post) if 'day' in s or 'hour' in s or 'week' in s or 'month' in s or 'year' in s]
            postdate = post[postdate_indices[0]]

        if (postCASE=="CASE 2"):
            action = post[0]
            postdate_indices = [i for i, s in enumerate(post) if 'day' in s or 'hour' in s or 'week' in s or 'month' in s or 'year' in s]
            postdate = post[postdate_indices[0]]

        if (postCASE=="CASE 3"):
            action = post[0]
            postdate_indices = [i for i, s in enumerate(post) if 'day' in s or 'hour' in s or 'week' in s or 'month' in s or 'year' in s]
            postdate = post[postdate_indices[0]]

        # change format of action (makes all reactions 'Like')
        if "likes" in action or "celebrates" in action or "curious" in action or "loves" in action or "insightful" in action:
            action = "Like"
        elif "commented" in action:
            action = "Comment"

        # filter time to less than 1 week
        if (postCASE):
            if not ("week" in postdate or "weeks" in postdate or "month" in postdate or "months" in postdate or "year" in postdate):
                emp_results.append([emp_name, action, postdate])

    if (error):
        emp_results.append([emp_name, "error", "error"])

    if len(emp_results) == 0:
        emp_results.append([emp_name, "No Data", "No Data"])

    if (not error):
        percent_done = round((emp_count/emp_total)*100)
        print("Data extracted for {0:30} {1:5}".format(emp_name, str(percent_done)+"%"))

    return emp_results

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

# import constants from config.txt
with open("config.txt", "r") as read_file:
    config = json.load(read_file)

# Starts a timer to show how long the program takes to run
start_time = time.time()

print("---------------------------------------------------------------------")
print("LinkedIn Data Extractor for PiP")
print("---------------------------------------------------------------------")

# Maybe ask user to input LinkedIn username and password
# username = 'christine.court.77@gmail.com'
# password = 'Wildpigs7!'
USER_EMAIL = input("Enter your LinkedIn Email: ")
USER_PASSWORD = input("Enter your LinkedIn password: ")

# PiP employee LinkedIn Details ------------------------------------------------

with open(config["CONSTANTS"]["EMPLOYEE_DETAILS_PATH"]) as csv_file:
    pipEmployeeDict = csv.DictReader(csv_file, fieldnames=['name', 'linkedin_id'])

    print("List of employees and LinkedIn ID")
    print("---------------------------------------------------------------------")

    emp_total = 0
    for employee in pipEmployeeDict:
        print("- {0:30}{1:30}".format(employee['name'], employee['linkedin_id']))
        emp_total += 1

print("---------------------------------------------------------------------")

# Chrome Driver ----------------------------------------------------------------

# Creation of a new instance of Google Chrome
browser = webdriver.Chrome(executable_path=config["CONSTANTS"]["CHROME_DRIVER_PATH"])

# Login to LinkedIn
util.linkedin_login(browser, USER_EMAIL, USER_PASSWORD)
print("Logged in to LinkedIn as " + USER_EMAIL)

# sleep for 5 seconds so the page can load
time.sleep(5)

with open(config["CONSTANTS"]["EMPLOYEE_DETAILS_PATH"]) as csv_file:
    pipEmployeeDict = csv.DictReader(csv_file, fieldnames=['name', 'linkedin_id'])

    print("Starting data extraction")
    print("---------------------------------------------------------------------")

    results = []
    emp_count = 0
    for employee in pipEmployeeDict:
        emp_count += 1
        # filter out employees with no known LinkedIn account
        if employee['linkedin_id']:
            # get all post data from LinkedIn on employee
            emp_results = getEmployeeData(browser, employee, emp_count, emp_total)
            for result in emp_results:
                results.append(result)
            # printing
            percent_done = round((emp_count/emp_total)*100,2)
            # context.bot.send_message(chat_id=update.effective_chat.id, text="Data Extracted for {0:20} {1:3}".format(employee['name'], str(percent_done)+'%'))
        else:
            results.append([employee['name'], "No LinkedIn", "No LinkedIn"])


# close browser to finish off
browser.close()
print("Browser Closed")

print("---------------------------------------------------------------------")
print("Finished data extraction")

# context.bot.send_message(chat_id=update.effective_chat.id, text="Finished data extraction")

print("Results")
print("---------------------------------------------------------------------")
df = pdDataFrame(results, columns=['Name', 'Action', 'Time'])
print(df)
print("---------------------------------------------------------------------")

# Write data to Excel --------------------------------------------------------
print("Writing results to Excel file: " + config["CONSTANTS"]["EXCEL_RESULTS_PATH"])

# current date
today = time.strftime("%d-%m-%Y")

app = xw.App(visible=False)
wb = xw.Book(config["CONSTANTS"]["EXCEL_RESULTS_PATH"])

# if a sheet with today's date already exists
for sheet in wb.sheets:
    if sheet.name == today:
        sheet.delete()

wb.sheets.add(name=today)
sht = wb.sheets[today]

sht.clear()

sht.range("A1").value = df

sht.autofit()

wb.save()
wb.close()

print("Finished writing results to Excel")
print("--- %s minutes ---" % round(((time.time() - start_time)/60),2))
