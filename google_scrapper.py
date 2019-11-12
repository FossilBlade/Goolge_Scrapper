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

log = logging.getLogger(__name__)

############### DO NOT REMOVE BELOW ####################################
import chromedriver_binary  # Adds chromedriver binary to path

page_load_timeout = 45

START_URL_TMPL = 'https://www.google.ca'
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

    def __del__(self):
        if self.close_driver == True and self.driver:
            self.driver.quit()

    def scrap(self, brand, store):
        print('Scrapping {} {}'.format(brand,store))
        data = {'brand': brand, 'store': store, 'fb_link': None, 'g_link': None}
        search_query = '{} {}'.format(brand, store)


        self.driver.get(START_URL_TMPL)
        search = self.driver.find_element_by_name('q')
        search.send_keys(search_query)
        search.send_keys(Keys.RETURN)  # hit return after you enter search text

        try:
            rhs_block = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'rhs_block')))
        except:
            print('Google Store Box not found')
        else:
            try:
                fb_a = rhs_block.find_element_by_xpath('//span[@title="Facebook"]/..')
            except:
                print('FB Link not found')
            else:
                fb_link = fb_a.get_attribute('href')
                data.update({'fb_link': fb_link})

            try:
                a = rhs_block.find_element_by_xpath('//a/span[contains(text(),"Google review")]/..')
            except:
                print('Google Review Link not found')
            else:
                a.click()
                sleep(.5)
                gr_link = self.driver.current_url

                data.update({'g_link': gr_link})

        return data


if __name__ == '__main__':
    import csv
    from random import randint
    scrapper = GScrapper(headless=True, close_driver=True)
    result =[]
    for store in ['Mayfair',
'Woodgrove',
'Cherry Lane',
'Hillside',
'Guildford Town Centre',
'Aberdeen',
'Tsawwassen',
'Village Green',
'Orchard Park',
'Lougheed',
'Seven Oaks',
'Metrotown Centre',
'Willowbrook Shopping Centre',
'Cottonwood',
'Richmond Centre',
'Pine Centre',
'Park Royal',
'Brentwood',
'McAthur Glen Outlet',
'Fairview Park',
'Pen Centre',
'Masonville',
'White Oaks',
'Cambridge',
'Devonshire',
'Stone Road',
'Niagara',
'Oakville Place',
'Limeridge',
'Lynden Park',
'Halifax',
'Conestoga Mall',
'McAllister Place',
'Regent Mall',
'Charlottetown',
'Maple View',
'Burlington Centre',
'Pickering',
'Oshawa',
'Scarborough Town Centre',
'Markville',
'St Laurent',
'Hillcrest',
'Bayshore',
'Place D`Orleans',
'Yorkdale',
'Cataraqui',
'Carlingwood',
'Cadillac Fairview Mall',
'Rideau Centre',
'Quinte Mall',
'Kildonan',
'Polo Park',
'St Vital',
'Brandon',
'Winnipeg Outlet',
'Kingsway Garden Mall',
'West Edmonton Mall',
'Prairie Mall',
'Edmonton City Centre',
'Peter Pond',
'Sherwood Park',
'Londonderry Mall',
'St Albert',
'Edmonton Outlet',
'Sunridge Mall',
'Marlborough',
'South Centre',
'Crossiron Mills',
'Bower Place',
'Chinook',
'Midtown Plaza',
'Market Mall',
'Medicine Hat Mall',
'Park Place',
'Bramalea',
'Upper Canada Mall',
'Georgian Mall',
'Dufferin',
'Yonge Eglinton',
'Inter City',
'Erin Mills',
'Sherway',
'Square One',
'Vaughan Mills',
'North Bay',
'New Sudbury',


                  ]:
        data = scrapper.scrap('michael hill', store)
        result.append(data)
        print(data)



        # sleep(randint(1,))



    csv_columns = ['brand', 'store', 'fb_link','g_link']
    dict_data = result
    csv_file = "mh_store_ca.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")