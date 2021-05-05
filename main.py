import math
import requests
from time import sleep
import json
from datetime import datetime
import hashlib
import hmac
from requests.models import ProtocolError
from utilities import TweetListener

ASSET = ["USDT", 11]
SYMBOL = "DOGE"

f = open("keys.txt", 'r')
keys = json.loads(f.read())

LIVE_URL = "https://api3.binance.com/api/v3/"
LIVE_PUB_KEY = keys['LIVE_PUB_KEY']
LIVE_SECRET_KEY = keys['LIVE_SECRET_KEY'].encode()

TESTNET_URL = "https://testnet.binance.vision/api/v3/"
TESTNET_PUB_KEY = keys['TESTNET_PUB_KEY']
TESTNET_SECRET_KEY = keys['TESTNET_SECRET_KEY'].encode()

FREE = True
URL = LIVE_URL
SECRET_KEY = LIVE_SECRET_KEY
PUB_KEY = LIVE_PUB_KEY


def get_precision():
    exchange_info = requests.get(URL + "exchangeInfo")
    exchangeInfo = exchange_info.json()
    for crypto in exchangeInfo['symbols']:
        if crypto['symbol'] == SYMBOL + ASSET[0]:
            for filters in crypto['filters']:
                if filters['filterType'] == 'LOT_SIZE':
                    step_size = float(filters['stepSize'])
    precision = 0
    while step_size < 1:
        step_size *= 10
        precision += 1
    return precision


PRECISION = get_precision()


def get_timestamp():
    time_request = requests.get(URL + "time")
    timestamp = time_request.json()['serverTime']
    return timestamp


def round_down(n, decimals=0):
    multiplier = 10**decimals
    return math.floor(n * multiplier) / multiplier


def get_quantity():
    symbol_info = requests.get(URL +
                               f"ticker/price?symbol={SYMBOL + ASSET[0]}")
    price = symbol_info.json()['price']
    quantity = ASSET[1] / float(price)
    quantity = float(round(quantity, PRECISION))
    return quantity


def get_asset_balance():
    TOTAL_PARAMS = f"timestamp={get_timestamp()}"
    TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
    signature = hmac.new(SECRET_KEY, TOTAL_PARAMS_b,
                         hashlib.sha256).hexdigest()
    payload = TOTAL_PARAMS + "&signature=" + signature
    headers = {'X-MBX-APIKEY': PUB_KEY}

    account_info = requests.get(URL + "account?" + payload, headers=headers)
    balances = account_info.json()['balances']
    for balance in balances:
        if balance['asset'] == ASSET[0]:
            return float(balance['free'])


def get_details(response):
    sides = {'SELL': "Sold", 'BUY': "Bought"}
    orders = 0
    commission = 0
    for filled in response['fills']:
        commission += float(filled['commission'])
        if orders == 0:
            str_to_print = f"{sides[response['side']]} {filled['qty']} at {filled['price']}"
        else:
            str_to_print = str_to_print + f", then {filled['qty']} at {filled['price']}"
        orders += 1
    return str_to_print, commission


def get_order_status(order_id):
    TOTAL_PARAMS = f"symbol={SYMBOL + ASSET[0]}&orderId={order_id}&timestamp={get_timestamp()}"
    TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
    signature = hmac.new(SECRET_KEY, TOTAL_PARAMS_b,
                         hashlib.sha256).hexdigest()
    payload = TOTAL_PARAMS + "&signature=" + signature
    headers = {'X-MBX-APIKEY': PUB_KEY}

    order_info = requests.get(URL + "order?" + payload, headers=headers)
    response = order_info.json()
    return response


def buy(retry):
    quantity = get_quantity()

    TOTAL_PARAMS = f"symbol={SYMBOL + ASSET[0]}&side=BUY&type=MARKET&quantity={quantity}&recvWindow=3000&timestamp={get_timestamp()}"
    TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
    signature = hmac.new(SECRET_KEY, TOTAL_PARAMS_b,
                         hashlib.sha256).hexdigest()
    payload = TOTAL_PARAMS + "&signature=" + signature
    headers = {'X-MBX-APIKEY': PUB_KEY}

    order_created = requests.post(URL + "order?" + payload, headers=headers)
    response = order_created.json()
    str_to_print, commission = get_details(response)
    if response['status'] == 'FILLED':
        print(datetime.now().strftime("\033[92m%d-%m-%Y %H:%M:%S | \033[0m") +
              f"\033[92m{str_to_print}\033[0m")
        return response['orderId'], commission
    elif retry > 0:
        print(datetime.now().strftime("\033[91m%d-%m-%Y %H:%M:%S | \033[0m") +
              "\033[91mOrder error\033[0m")
        print(order_created.content.decode())
        print("\033[91mRetrying...\033[0m")
        retry -= 1
        buy(retry)
    else:
        print("guess we'll pass for this time...")
        retry = 0


def sell(order_id, retry, commission):
    response = get_order_status(order_id)
    quantity = float(response['executedQty']) - commission
    quantity = round_down(quantity, PRECISION)

    TOTAL_PARAMS = f"symbol={SYMBOL + ASSET[0]}&side=SELL&type=MARKET&quantity={quantity}&recvWindow=4000&timestamp={get_timestamp()}"
    TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
    signature = hmac.new(SECRET_KEY, TOTAL_PARAMS_b,
                         hashlib.sha256).hexdigest()
    payload = TOTAL_PARAMS + "&signature=" + signature
    headers = {'X-MBX-APIKEY': PUB_KEY}

    order_created = requests.post(URL + "order?" + payload, headers=headers)
    response = order_created.json()
    str_to_print, commission = get_details(response)
    if response['status'] == 'FILLED':
        print(datetime.now().strftime("\033[94m%d-%m-%Y %H:%M:%S | \033[0m") +
              f"\033[94m{str_to_print}\033[0m")
    elif retry > 0:
        print(datetime.now().strftime("\033[91m%d-%m-%Y %H:%M:%S | \033[0m") +
              "\033[91mOrder error\033[0m")
        print(order_created.content.decode())
        print("\033[91mRetrying...\033[0m")
        retry -= 1
        sell(retry)
    else:
        print("guess we'll pass for this time...")
        retry = 0


def got_tweet(status):
    if get_asset_balance() > ASSET[1]:
        print(datetime.now().strftime(f"%d-%m-%Y %H:%M:%S | ") +
              f"Elon just tweeted about ${SYMBOL}:")
        print("    " + status.text)
        order_id, commission = buy(3)
        sleep(5)
        sell(order_id, 5, commission)
        print("----------------------------------------------------------")
    else:
        print("Not enough liquidity.")


if __name__ == "__main__":
    while True:
        try:
            print('Start streaming.')
            TweetListener('44196397', 'doge', got_tweet)
        except KeyboardInterrupt:
            print("Stream stopped.")
            break
        except ProtocolError:
            print("ProtocolError, retying..")
            pass
