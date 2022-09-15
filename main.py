import datetime as dt
import os
from pprint import pprint

import requests
from dotenv import load_dotenv
from newscatcherapi import NewsCatcherApiClient

load_dotenv()

Alpha_Vantage_API= os.environ.get("Alpha_Vantage_API")
NewsCatcherApi = os.environ.get("NewsCatcherApi")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
TG_TOKEN =os.environ.get("TG_TOKEN") 
TG_CHAT_ID =os.environ.get("TG_CHAT_ID") 

stock_url = "https://www.alphavantage.co/query"


def date_to_str(date):
    date_str = date.strftime("%Y-%m-%d")
    return(date_str)

def get_stock_data(stock_url,stock_symbol,Alpha_Vantage_API):

    parameters = {
        "function":"TIME_SERIES_DAILY",
        "symbol":stock_symbol,
        'apikey':Alpha_Vantage_API
    }

    response_data = requests.get(url=stock_url,params=parameters)
    response_data.raise_for_status()

    raw_stock_data = (response_data.json())
    
    # pprint(raw_stock_data)

    return raw_stock_data

stock_data = get_stock_data(stock_url,STOCK,Alpha_Vantage_API)

stock_data_daily = (stock_data['Time Series (Daily)'])

# get yesterday
yesterday = dt.date.today() - dt.timedelta(days = 1 )
yesterday_str = date_to_str(yesterday)
# print(yesterday_str)


day_before_yesterday = yesterday-dt.timedelta(days = 1 )
day_before_yesterday_str = date_to_str(day_before_yesterday)
# print(day_before_yesterday_str)


yesterday_stock_price_close=  stock_data_daily[yesterday_str]['4. close']
day_before_yesterday_stock_price_close =stock_data_daily[day_before_yesterday_str]['4. close'] 



def compare_stock_price(yesterday_stock_price_close,day_before_yesterday_stock_price_close):
    
    changed_percentage = (float(yesterday_stock_price_close) - float(day_before_yesterday_stock_price_close) )/float(day_before_yesterday_stock_price_close)

    # print(changed_percentage)

    if abs(changed_percentage) > 0.05:
        print("more then 5%")
    else :
        print("least then 5 %")

    return changed_percentage


# print(compare_stock_price(yesterday_stock_price_close,day_before_yesterday_stock_price_close))

changed_percentage =compare_stock_price(yesterday_stock_price_close,day_before_yesterday_stock_price_close) 



# Getting the new  
newscatcherapi = NewsCatcherApiClient(x_api_key=NewsCatcherApi)

all_articles = newscatcherapi.get_search(q=COMPANY_NAME,
                                         lang='en',
                                         countries='us',
                                         page_size=3)

# print(all_articles)     

news_dict = {}

def generate_message (stock_symbol,all_articles , changed_percentage):

    message_arr = []

    changed_percentage = round(changed_percentage *100,2) 


    for article in all_articles['articles']:
        title = (article["title"])
        summary = article["summary"]
        
        if changed_percentage > 0 :
            message = f"{stock_symbol} 🔺{changed_percentage}% \n\nHeadline : {title} \n\nBrief : {summary}"
        else:
           message = f"{stock_symbol} 🔻{changed_percentage}% \n\nHeadline : {title} \n\nBrief : {summary}" 

        message_arr.append(message)

    return message_arr

message_list = generate_message(STOCK,all_articles,changed_percentage)


# Sending message 

def tgGetUpdates():
    tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates"
    return (requests.get(tg_url).json())

# print(tgGetUpdates())

def tgSendMessage(message):
    tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&text={message}"
    send_message = (requests.get(tg_url))
    send_message.raise_for_status()
   
    # print("even thing good ")


for message in message_list:
    tgSendMessage(message)



