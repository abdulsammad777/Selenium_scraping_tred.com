from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
chromeOptions = Options()
from Exceptions.custom_exceptions import *
chromeOptions.add_argument("--start-maximized")

# chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_argument('--disable-dev-shm-usage')
import json
import os
import time
import logging
import datetime

# driver = webdriver.Chrome(options=chromeOptions)
# driver = webdriver.Chrome(options=chromeOptions, executable_path='C:/Program Files (x86)/chromedriver.exe')
driver = webdriver.Chrome(options=chromeOptions, executable_path='/snap/chromium/1753/usr/lib/chromium-browser/chromedriver')
# export PATH=$PATH:/snap/chromium/1753/usr/lib/chromium-browser/chromedriver

# start = 25
# allowed_areas = []
# for i in range(20):
#     allowed_areas.append(str(start))
#     start += 25
# allowed_areas.append('500+')
# print(allowed_areas)



def check_internet():
    counter = 2
    time.sleep(counter)
    url = 'http://www.google.com/'
    while True:
        try:
            request = requests.get(url, timeout=5)
            return True
        except requests.ConnectionError:
            counter *= 2
            time.sleep(counter)
            if counter == 4:
                driver.refresh()
                return False

def get_user_input():

    while True:

        Area_in_miles = input("Enter the area in miles")

        allowed_areas = ['25', '50', '75', '100', '125', '150', '175', '200', '225', '250', '275', '300', '325', '350', '375', '400', '425', '450', '475', '500', '500+']

        if Area_in_miles not in allowed_areas:
            print("Area should be one of the following.")
            for area in allowed_areas:
                print(area, end="   ")
            continue

        ZipCode = input("Enter the ZipCode")
        break
    return Area_in_miles, ZipCode


def get_urls_to_be_scraped(Area_in_miles, ZipCode):

    location = 'https://www.tred.com/buy?body_style=&distance=50&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip='
    try:
        driver.get(location)
    except Exception as e:
        if "ERR_NAME_NOT_RESOLVED" in e.args[0]:
            logging.warning(f'--Found Page down for search of area {Area_in_miles} and zipcode {ZipCode}')
            check_for_connection = check_internet()
            if check_for_connection is False:
                logging.warning(f'--Still Page down for search of area {Area_in_miles} and zipcode {ZipCode}')
                raise ConnectionError
    except TimeoutException:
        driver.implicitly_wait(0.5)
        driver.get(location)
    driver.implicitly_wait(0.5)
    driver.find_element(By.XPATH, './/div//select[@class="form-control"]/option[@value="' + Area_in_miles + '"]').click()
    search_box = driver.find_element_by_xpath("//div//input[@type='number']")
    search_box.clear()
    search_box.send_keys(ZipCode)
    time.sleep(2)
    try:
        containers = driver.find_elements_by_xpath('//div[@class="grid-car col-md-4 col-sm-6 col-xs-6"]')
    except NoSuchElementException:
        # driver.quit()
        logging.warning(f'--We have not found any result against the area {Area_in_miles} and zipcode {ZipCode}')
        return "We have not found any result against your data."

    len_ = len(containers)
    if len_ == 0:
        # driver.quit()
        logging.warning(f'--We have not found any result against the area {Area_in_miles} and zipcode {ZipCode}')
        return "We have not found any result against your data."
    urls_list = []
    for index in range(len_):
        try:
            corresponding_url = containers[index].find_element_by_tag_name("a").get_attribute("href")
            # corresponding_url = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        except NoSuchElementException:
            continue
        urls_list.append(corresponding_url)

    return urls_list



def get_summary():
"""This function will returns the summary of the car on the current page."""
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="col-md-12"]')))
    except TimeoutException:
        return "None"
    Summary_Table = driver.find_elements_by_xpath('//div//table[@id="summary-table"]')

    TableRows = Summary_Table[1].find_elements_by_xpath(".//tbody//tr")

    Summary_data = []

    for i in range(len(TableRows)):
        try:
            name = TableRows[i].find_element_by_xpath(".//th").text
            value = TableRows[i].find_element_by_xpath(".//td").text
        except NoSuchElementException:
            continue


        Summary_data.append(str(name)+str(value))

    return Summary_data



def get_options():
"""This function will returns the options that car have as properties of car on the current page."""
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div//table[@id="options-table"]')))
    except TimeoutException:
        return "None"

    # Options_Table = driver.find_element(By.XPATH, '//div//table[@id="options-table"]')

    # Options_row = Options_Table.find_element(By.XPATH, 'tbody//tr//th[@class="main-head"]/..')

    # Options_Table = driver.find_element_by_xpath('//tr[contains(th, "Options")]')
    # Options_Table.find_element_by_xpath('.//following-sibling::tr/td').text

    TableRows = driver.find_elements_by_xpath('//tr[contains(th, "Options")]/following-sibling::tr')
    if TableRows == []:
        return None

    Options_data = []

    for i in range(len(TableRows)):
        value = TableRows[i].find_element_by_xpath(".//td").text
        Options_data.append(value)
    return Options_data


def close_driver():
    driver.quit()


def save_to_xlsx(scraped_data_list):
"""This function will take all scraped data in form of list and save it in .xlsx format."""
    if not os.path.exists('Scraped_files'):
        os.makedirs('Scraped_files')
    column_list = ['Name', 'Price', 'Vehicle Summary', 'Vehicle Options']
    df = pd.DataFrame(scraped_data_list, columns=column_list)
    folder_name = r'Scraped_files/'
    current_time = datetime.datetime.today().strftime('%y-%m-%d %H%M%S')
    file_name = 'output_{}.xlsx'.format(current_time)
    path = folder_name + 'output_{}.xlsx'.format(current_time)
    writer = pd.ExcelWriter(path)

    df.to_excel(writer, 'Sheet1', index=None)

    writer.save()

    return current_time, file_name


def get_currect_name(name):
"""This function will take the name of the car from the current page, and format the name."""
    name = name.split("For Sale")[0]
    for i, c in enumerate(name):
        if c.isdigit():
            format_name = name[i::]
            return format_name
        else:
            pass
    return "No digit Found"




def get_scraped_data(search_results_URI):
"""This function will take all the urls on the search page and returns the scrapped data in form of list."""

    # search_results_URI = ['https://www.tred.com/buy/bmw/3-series/2017/WBA8B3G36HNA92874?body_style=&distance=50&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/infiniti/qx56/2008/5N3AA08C08N903461?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/bmw/3-series/2001/WBAAV53411FJ71790?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/bmw/4-series/2015/WBA3N3C57FK232290?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/kia/sorento/2005/KNDJD733655438247?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/ford/f-150/2002/1FTRX07L62KB90395?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/kia/optima/2015/5XXGM4A78FG396448?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/mazda/3/2012/JM1BL1L77C1610894?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/ford/escape/2017/1FMCU9GDXHUB45190?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/porsche/718-boxster/2017/WP0CA2A85HS222267?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/land-rover/range-rover-sport/2016/SALWR2EF1GA564858?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/land-rover/discovery-sport/2018/SALCP2RX4JH765678?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/nissan/maxima/2006/1N4BA41E16C818499?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/lexus/is-250/2009/JTHCK262795034124?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/chevrolet/suburban/2012/1GNSCJE0XCR107241?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/bmw/m3/2016/WBS8M9C53G5E68803?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/mercedes-benz/c-class/2018/55SWF4KBXJU242505?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/mazda/3/2005/JM1BK343551245497?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/lexus/ct-200h/2015/JTHKD5BH5F2246843?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/tesla/model-y/2021/5YJYGDEEXMF094888?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/lexus/rx-450h/2013/JTJZB1BA1D2009391?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/mazda/cx-9/2018/JM3TCBEY1J0206080?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500', 'https://www.tred.com/buy/buick/regal/1999/2G4WF5214X1541512?body_style=&distance=25&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=54500']

    scraped_data_list = []
    for url in search_results_URI:
        data_list = []
        try:
            driver.get(url)
        except Exception as e:
            if "ERR_NAME_NOT_RESOLVED" in e.args[0]:
                logging.warning(f'--Found Page down for search of area {Area_in_miles} and zipcode {ZipCode}')
                check_for_connection = check_internet()
                if check_for_connection is False:
                    logging.warning(f'--Still Page down for search of area {Area_in_miles} and zipcode {ZipCode}')
                    raise ConnectionError
        except TimeoutException:
            driver.implicitly_wait(0.5)
            driver.get(url)
            driver.implicitly_wait(0.5)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='price-box no-arrow']/h2")))
        except TimeoutException:
            continue
        except:
            continue

        Name_Find = driver.find_element_by_xpath("//div//h1[@class='bigger no-top-margin hidden-xs']").text

        """getting formatted name"""

        Name = get_currect_name(Name_Find)
        if Name == "No digit Found":
            Name = Name_Find

        try:
            Price = driver.find_element_by_xpath("//div[@class='price-box no-arrow']/h2").text
        except NoSuchElementException:
            Price = 'Sold'

        Summary_List = get_summary()

        options_list = get_options()

        data_list.extend([Name, Price, Summary_List, options_list])

        scraped_data_list.append(data_list)

    return scraped_data_list















