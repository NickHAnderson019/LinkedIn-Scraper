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


def handlePageScrolling(browser, sleep_time):

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
            if len(post.find_elements_by_class_name("feed-shared-update-v2__content feed-shared-article ember-view"))>0:
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
            time.sleep(sleep_time)

def getPageData(browser):
    # Execute Javascript code on webpage
    textList = browser.execute_script("""
    return (function(){
        textList = [];
        var posts = document.getElementsByClassName('occludable-update')
        try{
            if (posts.length != 0){
                for (i in posts) {
                    if (i == "length" || i == "item" || i == "namedItem"){
                        continue;
                    }
                    var post = posts[i];
                    textList.push(post.innerText)
                }
                return textList;
            }
            else {
                textList = []
                return textList;
            }
        }
        catch(e){
            return 'ERROR';
        }
    })
    ()
    """)
    return textList

def isPageReady(browser):
    state = browser.execute_script("""
    return (function(){
        return document.readyState
    })
    ()
    """)

    if state == "complete":
        return True
    else:
        return False


#
#
#
# button = document.getElementsByClassName('sort-dropdown__dropdown-trigger display-flex t-12 t-black--light t-normal artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view')[0]
# recent = document.getElementsByClassName("flex-grow-1 justify-flex-start ph4 artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view")[0]
#
