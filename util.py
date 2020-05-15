
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


def pageShouldBeScrolled(browser):
    scrollAction = browser.execute_script("""

    return (function (){

      scrollAction = true

      var posts = document.getElementsByClassName('occludable-update')

      if (posts.length == 0){
          scrollAction = false
          return scrollAction;
      }

      for (i in posts) {
          if (i == "length" || i == "item" || i == "namedItem"){
              continue;
          }
          var post = posts[i];

          if (post.children[0].children[2].tagName === "ARTICLE") {
              continue;
          }

          for (i in post.getElementsByClassName('visually-hidden')){
              if (i == "length" || i == "item" || i == "namedItem"){
                  continue;
              }
              if (post.getElementsByClassName('visually-hidden')[i].innerText.indexOf("ago")!== -1) {
                  timeStr = post.getElementsByClassName('visually-hidden')[i].innerText;
                  break;
              }
          }

          timeStr = timeStr.split(" ")

          if ((timeStr[0] >= 2 && timeStr[1] == 'weeks') || (timeStr[1] == 'month' || timeStr[1] == 'months' || timeStr[1] == 'year' || timeStr[1] == 'years')) {
              scrollAction = false;
          }
        }

        return scrollAction
    })
    ()
    """)
    return scrollAction

def scrollPage(browser):
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")

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
