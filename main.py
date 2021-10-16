from automation_script import get_user_input, get_urls_to_be_scraped, save_to_xlsx, get_scraped_data, close_driver
import logging
from Exceptions.custom_exceptions import *
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',filename='app.log')



if __name__ == "__main__":

    while True:

        Area_in_miles, ZipCode = get_user_input()
        try:
            urls_list = get_urls_to_be_scraped(Area_in_miles, ZipCode)
        except ConnectionError:
            print('--Please check your internet and try again')
            logging.warning(f'--Please check your internet and try again')
            prompt = input("Do you want to search again. Y/N").lower()
            if prompt == 'y':
                continue
            else:
                close_driver()
                break
        results = len(urls_list)

        if "not found" in urls_list:
            print("We have not found any result against your data.")
            prompt = input("Do you want to search again. Y/N").lower()
            if prompt == 'y':
                continue
            else:
                close_driver()
                break
        elif results > 0:
            print(f"We have find {results} results, Going to scrape these results.")
        try:
            scraped_data_list = get_scraped_data(urls_list)
        except ConnectionError:
            print('--Please check your internet and try again')
            logging.warning(f'--Please check your internet and try again')
            prompt = input("Do you want to search again. Y/N").lower()
            if prompt == 'y':
                continue
            else:
                close_driver()
                break



        print(f"Succesfully scrapped {len(scraped_data_list)} results")
        print(f"Going to save the scraped data in to a file")

        time_to_save, file_name = save_to_xlsx(scraped_data_list)

        print(f"We have saved {len(scraped_data_list)} rows into file {file_name} ,against your search area {Area_in_miles} and zipcode {ZipCode}")

        logging.warning(f"We have saved {len(scraped_data_list)} rows into file {file_name} ,against your search area {Area_in_miles} and zipcode {ZipCode}")

        prompting_again = input("Do you want to search again. Y/N").lower()

        if prompting_again == 'y':
            continue
        else:
            close_driver()
            break



