import math
import requests
import json
from datetime import datetime
import hashlib
import hmac

class BaseAssetBalanceTooLow(Exception):
    pass

class BinanceClient():
    def __init__(self, keys, config_file: str = "config.json"):
        config = json.loads(open(
            config_file, 'r').read())  #loads config file into json format

        self.PUB_KEY = keys[0]
        self.SECRET_KEY = keys[1].encode()

        self.URL = config['URL']
        self.ASSET = config['ASSET']
        self.BASE_ASSET = config['BASE_ASSET']
        self.BASE_ASSET_QUANTITY = config['BASE_ASSET_QUANTITY']

        self.PRECISION = self.get_precision()

    def get_precision(self):
        exchange_info = requests.get(self.URL + "exchangeInfo")
        exchangeInfo = exchange_info.json()
        for crypto in exchangeInfo['symbols']:
            if crypto['symbol'] == self.ASSET + self.BASE_ASSET:
                for filters in crypto['filters']:
                    if filters['filterType'] == 'LOT_SIZE':
                        step_size = float(filters['stepSize'])
        precision = 0
        while step_size < 1:
            step_size *= 10
            precision += 1
        return precision

    def get_timestamp(self):
        time_request = requests.get(self.URL + "time")
        timestamp = time_request.json()['serverTime']
        return timestamp

    def round_down(slef, n, decimals=0):
        multiplier = 10**decimals
        return math.floor(n * multiplier) / multiplier

    def get_quantity(self):
        symbol_info = requests.get(
            self.URL + f"ticker/price?symbol={self.ASSET + self.BASE_ASSET}")
        price = symbol_info.json()['price']
        quantity = self.BASE_ASSET_QUANTITY / float(price)
        quantity = float(round(quantity, self.PRECISION))
        return quantity

    def verify_base_asset_balance(self):
        TOTAL_PARAMS = f"timestamp={self.get_timestamp()}"
        TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
        signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                             hashlib.sha256).hexdigest()
        payload = TOTAL_PARAMS + "&signature=" + signature
        headers = {'X-MBX-APIKEY': self.PUB_KEY}

        account_info = requests.get(self.URL + "account?" + payload,
                                    headers=headers)

        balances = account_info.json()['balances']
        for balance in balances:
            if balance['asset'] == self.BASE_ASSET:
                if float(balance['free']) > self.BASE_ASSET_QUANTITY:
                    return True
                else:
                    return False

    def verify_balance(self):
        if self.get_asset_balance() > self.BASE_ASSET_QUANTITY:
            return True
        else:
            return False

    def get_details(self, response):
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

    def get_order_status(self, order_id):
        TOTAL_PARAMS = f"symbol={self.ASSET + self.BASE_ASSET}&orderId={order_id}&timestamp={self.get_timestamp()}"
        TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
        signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                             hashlib.sha256).hexdigest()
        payload = TOTAL_PARAMS + "&signature=" + signature
        headers = {'X-MBX-APIKEY': self.PUB_KEY}

        order_info = requests.get(self.URL + "order?" + payload,
                                  headers=headers)
        response = order_info.json()
        return response

    def buy(self, retry):
        if self.verify_base_asset_balance():
            quantity = self.get_quantity()

            TOTAL_PARAMS = f"symbol={self.ASSET + self.BASE_ASSET}&side=BUY&type=MARKET&quantity={quantity}&recvWindow=3000&timestamp={self.get_timestamp()}"
            TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
            signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                             hashlib.sha256).hexdigest()
            payload = TOTAL_PARAMS + "&signature=" + signature
            headers = {'X-MBX-APIKEY': self.PUB_KEY}

            order_created = requests.post(self.URL + "order?" + payload,
                                      headers=headers)
            response = order_created.json()
            str_to_print, commission = self.get_details(response)
            if response['status'] == 'FILLED':
                print(datetime.now().strftime(
                    "\033[92m%d-%m-%Y %H:%M:%S | \033[0m") +
                    f"\033[92m{str_to_print}\033[0m")
                return response['orderId'], commission
            elif retry > 0:
                print(datetime.now().strftime(
                    "\033[91m%d-%m-%Y %H:%M:%S | \033[0m") +
                    "\033[91mOrder error\033[0m")
                print(order_created.content.decode())
                print("\033[91mRetrying...\033[0m")
                retry -= 1
                self.buy(retry)
            else:
                print("guess we'll pass for this time...")
                retry = 0
        else:
            raise BaseAssetBalanceTooLow

    def sell(self, order_id, retry, commission):
        response = self.get_order_status(order_id)
        quantity = float(response['executedQty']) - commission
        quantity = self.round_down(quantity, self.PRECISION)

        TOTAL_PARAMS = f"symbol={self.ASSET + self.BASE_ASSET}&side=SELL&type=MARKET&quantity={quantity}&recvWindow=4000&timestamp={self.get_timestamp()}"
        TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
        signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                             hashlib.sha256).hexdigest()
        payload = TOTAL_PARAMS + "&signature=" + signature
        headers = {'X-MBX-APIKEY': self.PUB_KEY}

        order_created = requests.post(self.URL + "order?" + payload,
                                      headers=headers)
        response = order_created.json()
        str_to_print, commission = self.get_details(response)
        if response['status'] == 'FILLED':
            print(datetime.now().strftime(
                "\033[94m%d-%m-%Y %H:%M:%S | \033[0m") +
                  f"\033[94m{str_to_print}\033[0m")
        elif retry > 0:
            print(datetime.now().strftime(
                "\033[91m%d-%m-%Y %H:%M:%S | \033[0m") +
                  "\033[91mOrder error\033[0m")
            print(order_created.content.decode())
            print("\033[91mRetrying...\033[0m")
            retry -= 1
            self.sell(retry)
        else:
            print("guess we'll pass for this time...")
            retry = 0
