from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import shutil
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
import sys

from time import sleep, time
from bs4 import BeautifulSoup
from traceback import print_exc

import json
import datetime

import random

import logging
import fnmatch

from googlesearch import search

log = logging.getLogger(__name__)

############### DO NOT REMOVE BELOW ####################################
import chromedriver_binary  # Adds chromedriver binary to path

page_load_timeout = 45


GOOLGE_TLD = 'com.au'
GOOLGE_URL = 'https://www.google.{}'.format(GOOLGE_TLD)
user_agent_list = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',

    # Firefox
    # 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/70.0',
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/70.0',
    # 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/70.0'
]

def get_json_files_from_dir(folder_path):
    result =[os.path.abspath(os.path.join(folder_path,f )) for f in fnmatch.filter(os.listdir(folder_path), '*.json')]
    return result


def read_json_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)

    return data

class GScrapper:

    def __init__(self, close_driver=True, headless=True):
        self.driver = None
        self.headless = headless
        self.close_driver = close_driver
        self.__setup_driver()

    def __setup_driver(self):

        options = webdriver.ChromeOptions()
        options.add_argument('--profile-directory=Default')
        options.add_argument("--user-data-dir=chrome-profile/profile")

        options.add_argument("disable-infobars")
        options.add_argument("disable-extensions")
        options.add_argument("disable-cache")
        options.add_argument("disk-cache-size=1")

        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)

        options.add_argument(f'user-agent={random.choice(user_agent_list)}')
        options.add_argument('start-maximized')

        prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 1,
                                                            'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                            'notifications': 2, 'auto_select_certificate': 2,
                                                            'fullscreen': 2,
                                                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                            'media_stream_mic': 2, 'media_stream_camera': 2,
                                                            'protocol_handlers': 2,
                                                            'ppapi_broker': 2, 'automatic_downloads': 2,
                                                            'midi_sysex': 2,
                                                            'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                            'metro_switch_to_desktop': 2,
                                                            'protected_media_identifier': 2, 'app_banner': 2,
                                                            'site_engagement': 2,
                                                            'durable_storage': 2}}
        # prefs ={}
        options.add_experimental_option("prefs", prefs)

        if self.headless:

            options.headless = True
            # options.add_argument("remote-debugging-port={}".format(get_free_tcp_port()))
            options.add_argument('start-maximized')

            self.driver = webdriver.Chrome(options=options, desired_capabilities=None)

        else:
            self.driver = webdriver.Chrome(options=options, desired_capabilities=None)

        self.driver.set_page_load_timeout(page_load_timeout)

    def scrap_fb_link(self, brand, store):
        print('Scrapping FB link {} {}'.format(brand, store))
        # data = {'brand': brand, 'store': store, 'fb_link': None, 'g_link': None}
        search_query = 'site:facebook.com AND {} {}'.format(brand, store)

        self.driver.get(GOOLGE_URL)
        search_box = self.driver.find_element_by_name('q')
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        sleep(1)

        try:
            fb_link_a = self.driver.find_element_by_xpath('//*[@id="rso"]//a')
        except:
            print('FB link not found')
            return None
        else:
            link = fb_link_a.get_attribute('href')
            return link



    def scrap(self, brand, store):
        print('Scrapping {} {}'.format(brand,store))
        data = {'brand': brand, 'store': store, 'fb_link': None, 'g_link': None}
        search_query = '{} {}'.format(brand, store)


        self.driver.get(GOOLGE_URL)
        search_box = self.driver.find_element_by_name('q')
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)  # hit return after you enter search text

        try:
            rhs_block = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'rhs_block')))
        except:
            print('Google Store Box not found')
        else:
            fb_link_found = False
            try:
                fb_a = rhs_block.find_element_by_xpath('//span[@title="Facebook"]/..')
                fb_link_found =True
            except:
                print('FB Link not found in google box')
            else:
                fb_link = fb_a.get_attribute('href')
                data.update({'fb_link': fb_link})

            try:
                a = rhs_block.find_element_by_xpath('//a/span[contains(text(),"Google review")]/..')
            except:
                print('Google Review Link not found')
            else:
                a.click()
                sleep(1)
                gr_link = self.driver.current_url

                data.update({'g_link': gr_link})


            if fb_link_found == False:
                data.update({'fb_link': 'NOT FOUND'})
                # for url in search('site:facebook.com AND {}'.format(search_query), stop=1,tld=GOOLGE_TLD):
                #
                #     break


        return data


if __name__ == '__main__':
    import csv
    import store_names
    from random import randint
    brand = 'michael hill'
    stores = store_names.mh_au
    csv_file = "mh_store_au.csv"
    scrapper = GScrapper(headless=True, close_driver=True)
    result =[]

    for idx,store in enumerate(stores):
        print('Processing {}/{} store'.format(idx+1,len(stores)))
        data = scrapper.scrap(brand, store)
        result.append(data)
        print(data)

    for idx,data in  enumerate(result):
        print('Processing {}/{} FB Link'.format(idx + 1, len(result)))
        if data.get('fb_link')=='NOT FOUND':
            fb_link = scrapper.scrap_fb_link(data.get('brand'), data.get('store'))
            data.update({'fb_link':fb_link})

    csv_columns = ['brand', 'store', 'fb_link','g_link']
    dict_data = result

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")