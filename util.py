from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def linkedin_login(browser, username, password):
    browser.get('https://www.linkedin.com/uas/login')

    username_input = browser.find_element_by_id('username')
    username_input.send_keys(username)

    password_input = browser.find_element_by_id('password')
    password_input.send_keys(password)
    try:
        password_input.submit()
    except:
        pass


def handlePageScrolling(browser):
    # wait = WebDriverWait(browser, 1)
    # element = wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'detail-page-loader')))

    scrollAction = True
    posts_skip_index = 0
    count = 0

    while (scrollAction == True and count <= 10):
        posts = browser.find_elements_by_class_name("occludable-update")

        if len(posts) == 0:
            scrollAction = False
            break

        for index, post in enumerate(posts):
            # skip posts that we've already looked at
            if index < posts_skip_index:
                continue

            # Looking for case of article with no date
            if len(post.find_elements_by_class_name("feed-shared-actor"))==0:
                continue

            # getting date from post
            for element in post.find_elements_by_class_name('visually-hidden'):
                # getting the date element
                if "ago" in element.text:
                    timeStr = element.text;
                    break

            timeStr = timeStr.split(" ")
            if 'minute' in timeStr[1] or "hour" in timeStr[1] or "day" in timeStr[1]:
                scrollAction = True;
                break
            else:
                scrollAction = False

        posts_skip_index = len(posts)
        count += 1

        if (scrollAction):
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(0.5)


def getPageData(browser):
    textList =[]
    mentionList =[]
    posts = browser.find_elements_by_class_name("occludable-update")

    try:
        for post in posts:
            textList.append(post.text)

            linkList = post.find_elements_by_tag_name("a")

            isLink = False
            for link in linkList:
                if link.text == "Partners in Performance":
                    isLink = True
                    break

            if isLink:
                mentionList.append(1)
            else:
                mentionList.append(0)

        return [textList, mentionList]

    except Exception as e:
        print(e)
        return "ERROR"


def getLastSharedDate(textList):
    latest_shared_date_arr = []
    has_shared = False

    period_dict = {"minute":1/60*1/24, "hour":1/24, "day":1, "week":7, "month":30, "year":365,
                   "minutes":1/60*1/24, "hours":1/24, "days":1, "weeks":7, "months":30, "years":365}

    for post in textList[::-1]:
        # split post text by newline character
        post = post.split("\n")

        # if user is online, this is the first element of post
        if ('Status is online' in post[0]):
            ind_off = 1
        else:
            ind_off = 0

        if (not "likes" in post[ind_off] and not "commented" in post[ind_off] and
            not "celebrates" in post[ind_off] and not "insightful" in post[ind_off] and
            not "loves" in post[ind_off] and not "curious" in post[ind_off] and
            not "liked" in post[ind_off] and not "replied" in post[ind_off]):

            has_shared = True

            postdate_indices = [i for i, s in enumerate(post) if 'minute' in s or 'day' in s or 'hour' in s or 'week' in s or 'month' in s or 'year' in s]
            postdate = post[postdate_indices[0]].strip()
            postdate_value = postdate.split(" ")[0]
            postdate_period = postdate.split(" ")[1]

            eval_postdate = int(postdate_value)*period_dict[postdate_period]

            latest_shared_date_arr.append(eval_postdate)

        else:
            if has_shared:
                latest_shared_date_arr.append(latest_shared_date_arr[-1])
            else:
                latest_shared_date_arr.append(365)

    return latest_shared_date_arr[::-1]


#
#
#
# button = document.getElementsByClassName('sort-dropdown__dropdown-trigger display-flex t-12 t-black--light t-normal artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view')[0]
# recent = document.getElementsByClassName("flex-grow-1 justify-flex-start ph4 artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view")[0]

#link to partners in perfomrance
# <a href="https://www.linkedin.com/company/43075/" data-attribute-index="0" data-entity-hovercard-id="urn:li:fs_miniCompany:43075" data-entity-type="MINI_COMPANY">Partners in Performance</a>
