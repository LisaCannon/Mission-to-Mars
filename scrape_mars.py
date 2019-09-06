# import necessary libraries
from flask import Flask, render_template
from bs4 import BeautifulSoup as bs
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import pandas as pd

# create instance of Flask app
app = Flask(__name__)

#open browser
def init_browser():

    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():

    browser = init_browser()

    #scrape most recent article
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html
    soup = bs(html, "html.parser")
    title = soup.find('div', class_='content_title').get_text()
    paragraph = soup.find('div', class_='article_teaser_body').get_text()

    #scrape current mars image
    base_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(base_url)
    #click on the full button to navigate to the full size image
    browser.click_link_by_partial_text('FULL')
    browser.is_element_present_by_css('buttons', wait_time = 2)
    #click on the more info button to get infomation about the image
    browser.click_link_by_partial_text('more info')
    browser.is_element_present_by_css('figure',wait_time = 2)
    browser.click_link_by_partial_href('/spaceimages/images/largesize')
    html = browser.html
    soup = bs(html, 'html.parser')
    img_src = soup.find('img').get('src')

    #twitter
    base_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(base_url)
    html = browser.html
    soup = bs(html, 'html.parser')
    tweet = soup.find_all('p',class_ = 'TweetTextSize')
    #the most recent tweet might not contain weather information
    #we want the first tweet with weather info, whichalways starts with the string 'InSight sol'
    for twit in tweet:
        if 'InSight sol' in twit.text:
            pic_text = twit.a.text 
            #twit text also pics up the text from an a-tag.  replace is used to remove that unwanted text
            Mars_weather = twit.text.replace(pic_text,'')
            
            break
    
    
    #table of mars facts
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    #there are multiple tables on the web page.  the table we want is the second (in the 1 position)
    access_table = tables[1]
    table_df = pd.DataFrame(access_table)
    table_df = table_df.rename(columns = {0: "Description", 1:"Value"}).set_index('Description')
    mars_table = table_df.to_html().replace('\n', '')

    #hemispheres
    base_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(base_url)
    html = browser.html
    soup = bs(html, 'html.parser')
    #identify each of the hemispheres
    items = soup.find_all('div',class_ = 'item')
    hemi_dict = []
    for item in items:
        h = item.find('h3').text
        #the a-tag has a link to the page with the full size image of the hemisphere
        linka = item.find('a', class_ = 'itemLink product-item')['href']
        new_url = 'https://astrogeology.usgs.gov' + linka
        browser.visit(new_url)
        html = browser.html
        soup = bs(html, 'html.parser')
        img_url = 'https://astrogeology.usgs.gov'+ soup.find('img', class_ = "wide-image").get('src')
        dictionary = {'title':h,'img_url':img_url}
        hemi_dict.append(dictionary)

    mars_dict = {
        "title": title,
        "paragraph": paragraph,
        "img_src":img_src,
        "mars_weather": Mars_weather,
        "table_code": mars_table,
        "hemi_dict": hemi_dict
    }
    browser.quit()

    return mars_dict

