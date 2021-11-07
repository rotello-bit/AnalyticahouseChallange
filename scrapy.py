from bs4 import BeautifulSoup
from queue import Queue
import pandas as pd
import requests
import threading
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

result = []
base_url = 'https://www.markastok.com'
q = Queue()


def create_product_list(url):
    products = []
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    product_list = soup.find_all('div', class_='catalogWrapper')

    for item in product_list:
        for i in item.find_all('a', class_='product-item-inner', href=True):
            r = requests.get(f'{base_url}{i["href"]}')
            soup = BeautifulSoup(r.content, 'lxml')
            try:
                name = soup.find('h1', class_='product-name').text.strip()
                name = re.sub(r"[\n]*", '', name)
            except:
                name = 'no name'

            try:
                sale_price = soup.find('span', class_='product-price').text.strip()
                sale_price = re.sub(r"[\n]", '', sale_price)
            except:
                sale_price = 'no sale price'

            try:
                product_price = soup.find('span', class_='currencyPrice').text.strip()
                product_price = re.sub(r"[\n]*", '', product_price)
            except:
                product_price = ' no product price'

            try:
                offer = soup.find('div', class_='detay-indirim').text.strip()
                offer = re.sub(r"[\n]*", '', offer)
            except:
                offer = 'no offer'

            try:
                availability_total = len(soup.find('div', class_='new-size-variant').find_all('a'))
                availability_passive = len(soup.find('div', class_='new-size-variant').find_all('a', class_='passive'))
                availability_value = (availability_total - availability_passive) / availability_total * 100
                availability = "{:.2f}".format(availability_value) + "%"
            except:
                availability = 'no info'
            try:
                value = soup.find("input", {'id': "urun-sezon"}).attrs['value']
            except:
                value = 'no info'

            product = {
                'Link': url,
                'Product Name': name,
                'Sale Price': sale_price,
                'Product Price': product_price,
                'Offer': offer,
                'Availability': availability,
                'value': value
            }
            result.append(product)


class Worker(threading.Thread):

    def __init__(self, qu):
        threading.Thread.__init__(self)
        self.que = qu

    def run(self):
        for item in iter(self.que.get, None):
            create_product_list(item)
            self.que.task_done()
        self.que.task_done()


def create_workers():
    for j in range(50):
        work = Worker(q)
        work.setDaemon(True)
        work.start()


def create_jobs():
    urls = pd.read_excel(r'URLs.xlsx')
    count = 0
    for link in (base_url + urls).iloc[:, 0]:
        count += 1
        if count > 50:
            break
        q.put(link)
    q.join()


create_workers()
create_jobs()
df = pd.DataFrame(result)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
service_account_file = '../AnalyticahouseChallange/stok.json'
creds = None
creds = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=SCOPES)


SAMPLE_SPREADSHEET_ID = '1wCW2Bgjzom9PXcil3hwW62HxbUX9LAuxouzCql8DV70'


service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()


final = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="Sayfa1!A1",valueInputOption="RAW",
                               body=dict(majorDimension='ROWS',
                                         values=df.T.reset_index(

                                         ).T.values.tolist())).execute()
print(df)
