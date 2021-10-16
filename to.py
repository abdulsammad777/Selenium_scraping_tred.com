import datetime
import pandas as pd
data = {'Product': ['Desktop Computer','Printer','Tablet','Monitor'],
        'Price': [1200,150,300,450]
        }
df = pd.DataFrame(data, columns = ['Product', 'Price'])
current_time = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
print(type(current_time))

folder_name = r'Scraped_files/'
# folder_time = datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")
folder_to_save_files = folder_name + current_time + '.xlsx'
# df.to_excel(f'Scraped_files\\output.xlsx', index=None)
# df.to_excel(folder_to_save_files, index=None)

file_name = folder_name + 'output_{}.xlsx'.format(pd.datetime.today().strftime('%y-%m-%d %H%M%S'))

# writer = pd.ExcelWriter('output_{}.xlsx'.format(pd.datetime.today().strftime('%y-%m-%d %H:%M:%S')))
writer = pd.ExcelWriter(file_name)

df.to_excel(writer,'Sheet2')
writer.save()

date = datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
print(f"filename_{date}")