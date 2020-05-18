# =============================================================================
#                         LinkedIn Post Data Scraper
# =============================================================================
# This script takes a list of PiP employee names and LinkedIn ID's and pulls
# the LinkedIn data on each employee that involves engagement with PiP's
# LinkedIn account.
# -----------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        if emp_id == "partnersinperformance":
            linkedin_activity_path = 'https://www.linkedin.com/company/'+emp_id+'/'
        else:
            linkedin_activity_path = 'https://www.linkedin.com/in/'+emp_id+'/detail/recent-activity/'
        browser.get(linkedin_activity_path)

        wait = WebDriverWait(browser, 1)
        element = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'occludable-update')))

        # Data Collection ------------------------------------------------------

        # Scroll the page down if dates are less than a week
        # or if counter is over 10
        util.handlePageScrolling(browser)

        # Get post data for employee
        pageData = util.getPageData(browser)
        textList = pageData[0]
        mentionList = pageData[1]

    except Exception as e:
        print("An error occured. Name: ", emp_name)
        print(e)
        error = True
        textList = []

    # String Parsing -----------------------------------------------------------

    latest_shared_date_arr = util.getLastSharedDate(textList)

    print(latest_shared_date_arr)

    period_dict = {"minute":1/60*1/24, "hour":1/24, "day":1, "week":7, "month":30, "year":365,
                   "minutes":1/60*1/24, "hours":1/24, "days":1, "weeks":7, "months":30, "years":365}

    emp_results = []
    count = 0
    for index, post in enumerate(textList):

        count += 1 # just a counter

        postCASE = False # initialise
        directorCase = False

        # split post text by newline character
        post = post.split("\n")

        # if user is online, this is the first element of post
        if ('Status is online' in post[0]):
            ind_off = 1
        else:
            ind_off = 0

        if ("liked" in post[ind_off] or "replied" in post[ind_off]):
            continue

        # CASE 1 - shared
        # Check for likes, comments, celebrates
        elif (not "likes" in post[ind_off] and not "commented" in post[ind_off] and
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

            #Checking for Director posts
            for i in post:
                directorCase = "Director at Partners in Performance" in i
                if directorCase:
                    postCASE = "CASE 1"
                    break

            #for mentions PIP
            if mentionList[index] == 1:
                postCASE= "CASE 1"

        else:
            # get index of "followers".
            indices_followers = [i for i, s in enumerate(post) if 'followers' in s]
            # get index of "PIP".
            indices_pip = [i for i, s in enumerate(post) if 'Partners in Performance' in s]

            for i in indices_followers:
                for j in indices_pip:
                    if j==i-1:
                        postCASE = "CASE 2"

            #Checking for Director posts
            for i in post:
                directorCase = "Director at Partners in Performance" in i
                if directorCase:
                    postCASE = "CASE 2"
                    break

            #for mentions PIP
            if mentionList[index] == 1:
                postCASE= "CASE 1"

        if (not postCASE):
            continue

        if (postCASE=="CASE 1"):
            action = "Shared"

        if (postCASE=="CASE 2"):
            action = post[0]

        # change format of action (makes all reactions 'Like')
        if "likes" in action or "celebrates" in action or "curious" in action or "loves" in action or "insightful" in action:
            action = "Like"
        elif "commented" in action:
            action = "Comment"

        postdate_indices = [i for i, s in enumerate(post) if 'minute' in s or 'day' in s or 'hour' in s or 'week' in s or 'month' in s or 'year' in s]
        postdate = post[postdate_indices[0]].strip()
        postdate_value = postdate.split(" ")[0]
        postdate_period = postdate.split(" ")[1]
        eval_postdate = int(postdate_value)*period_dict[postdate_period]

        last_shared_date = latest_shared_date_arr[index]

        # filter time to less than 1 week
        if (postCASE):
            if postCASE == "CASE 2":
                if eval_postdate > last_shared_date:
                    eval_postdate = last_shared_date

            if eval_postdate < 7:
                emp_results.append([emp_name, action, str(round(eval_postdate,1)) + " days"])

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
with open("./config.txt", "r") as read_file:
    config = json.load(read_file)

# Starts a timer to show how long the program takes to run
start_time = time.time()

print("---------------------------------------------------------------------")
print("LinkedIn Data Extractor for PiP")
print("---------------------------------------------------------------------")

print("NOTE: When the Chrome browser pops up, do not minimize it.")
print("---------------------------------------------------------------------")

# Ask user to input LinkedIn username and password
USER_EMAIL =  "christine.court.77@gmail.com"#input("Enter your LinkedIn Email: ")
USER_PASSWORD = "Wildpigs7!" #input("Enter your LinkedIn password: ")


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
        # sheet.delete()
        today = today + " " + time.strftime("%H-%M")

wb.sheets.add(name=today)
sht = wb.sheets[today]

sht.clear()

sht.range("A1").value = df

sht.autofit()

wb.save()
wb.close()

print("Finished writing results to Excel")
print("--- %s minutes ---" % round(((time.time() - start_time)/60),2))

time.sleep(3)
