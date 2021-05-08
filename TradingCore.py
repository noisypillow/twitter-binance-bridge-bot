import math
import requests
import json
from datetime import datetime
import hashlib
import hmac
from time import sleep
from ConfigManager import Config


class BaseAssetBalanceTooLow(Exception):
    pass


class BinanceClient:
    def __init__(self, keys, config_file: str = "config.json"):
        self.config = Config()

        self.PUB_KEY = keys[0]
        self.SECRET_KEY = keys[1].encode()

        self.PRECISION = self.get_precision()

        self.log_file = open('trades.log', 'a+')

    def reload_config(self):
        self.config = Config()

    def on_tweet(self, status):
        try:
            print("----------------------------------------------------------")
            print(datetime.now().strftime("[%d-%m-%Y %H:%M:%S] ") +
                  f"Just got tweet about ${self.config.ASSET}:")
            print("    " + status.text)
            total_bought, order_id, commission = self.buy(3)
            sleep(self.config.INTERVAL)
            total_sold = self.sell(order_id, 5, commission)
            print("Profit = " + str(total_sold - total_bought))
        except BaseAssetBalanceTooLow:
            print("Not enough liquidity.")

    def get_precision(self):
        exchange_info = requests.get(self.config.URL + "exchangeInfo")
        exchangeInfo = exchange_info.json()
        for crypto in exchangeInfo['symbols']:
            if crypto['symbol'] == self.config.ASSET + self.config.BASE_ASSET:
                for filters in crypto['filters']:
                    if filters['filterType'] == 'LOT_SIZE':
                        step_size = float(filters['stepSize'])
        precision = 0
        while step_size < 1:
            step_size *= 10
            precision += 1
        return precision

    def get_timestamp(self):
        time_request = requests.get(self.config.URL + "time")
        timestamp = time_request.json()['serverTime']
        return timestamp

    def round_down(self, n, decimals=0):
        multiplier = 10**decimals
        return math.floor(n * multiplier) / multiplier

    def get_quantity(self):
        symbol_info = requests.get(
            self.config.URL +
            f"ticker/price?symbol={self.config.ASSET + self.config.BASE_ASSET}"
        )
        price = symbol_info.json()['price']
        quantity = self.config.BASE_ASSET_QUANTITY / float(price)
        quantity = float(round(quantity, self.PRECISION))
        return quantity

    def verify_base_asset_balance(self):
        TOTAL_PARAMS = f"timestamp={self.get_timestamp()}"
        TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
        signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                             hashlib.sha256).hexdigest()
        payload = TOTAL_PARAMS + "&signature=" + signature
        headers = {'X-MBX-APIKEY': self.PUB_KEY}

        account_info = requests.get(self.config.URL + "account?" + payload,
                                    headers=headers)

        balances = account_info.json()['balances']
        for balance in balances:
            if balance['asset'] == self.config.BASE_ASSET:
                if float(balance['free']) > self.config.BASE_ASSET_QUANTITY:
                    return True
                else:
                    return False

    def get_order_status(self, order_id):
        TOTAL_PARAMS = f"symbol={self.config.ASSET + self.config.BASE_ASSET}&orderId={order_id}&timestamp={self.get_timestamp()}"
        TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
        signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                             hashlib.sha256).hexdigest()
        payload = TOTAL_PARAMS + "&signature=" + signature
        headers = {'X-MBX-APIKEY': self.PUB_KEY}

        order_info = requests.get(self.config.URL + "order?" + payload,
                                  headers=headers)
        response = order_info.json()
        return response

    def buy(self, retry):
        if self.verify_base_asset_balance():
            quantity = self.get_quantity()

            TOTAL_PARAMS = f"symbol={self.config.ASSET + self.config.BASE_ASSET}&side=BUY&type=MARKET&quantity={quantity}&recvWindow=3000&timestamp={self.get_timestamp()}"
            TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
            signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                                 hashlib.sha256).hexdigest()
            payload = TOTAL_PARAMS + "&signature=" + signature
            headers = {'X-MBX-APIKEY': self.PUB_KEY}

            order_created = requests.post(self.config.URL + "order?" + payload,
                                          headers=headers)
            response = order_created.json()
            if response['status'] == 'FILLED':
                total_bought, commission = self.log(response)
                return total_bought, response['orderId'], commission
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

        TOTAL_PARAMS = f"symbol={self.config.ASSET + self.config.BASE_ASSET}&side=SELL&type=MARKET&quantity={quantity}&recvWindow=4000&timestamp={self.get_timestamp()}"
        TOTAL_PARAMS_b = TOTAL_PARAMS.encode('ASCII')
        signature = hmac.new(self.SECRET_KEY, TOTAL_PARAMS_b,
                             hashlib.sha256).hexdigest()
        payload = TOTAL_PARAMS + "&signature=" + signature
        headers = {'X-MBX-APIKEY': self.PUB_KEY}

        order_created = requests.post(self.config.URL + "order?" + payload,
                                      headers=headers)
        response = order_created.json()
        if response['status'] == 'FILLED':
            total_sold, commission = self.log(response)
            return total_sold
        elif retry > 0:
            print(datetime.now().strftime(
                "\033[91m%d-%m-%Y %H:%M:%S | \033[0m") +
                  "\033[91mOrder error\033[0m")
            print(order_created.content.decode())
            print("\033[91mRetrying...\033[0m")
            retry -= 1
            self.sell(order_id, retry, commission)
        else:
            print("guess we'll pass for this time...")
            retry = 0

    def log(self, response):
        commission = 0
        for filled in response['fills']:
            commission += float(filled['commission'])
            trade_time = datetime.now().strftime(" [%d-%m-%Y %H:%M:%S] ")
            log = response['side'] + trade_time + str(filled) + "\n"
            self.log_file.write(log)

            total = float(filled['price']) * float(filled['qty'])
            if response['side'] == 'BUY':
                formated_log = '\033[92mBUY' + trade_time + f"total: {total}\033[0m"
            elif response['side'] == 'SELL':
                formated_log = '\033[94mSELL' + trade_time + f"total: {total}\033[0m"
            print(formated_log)
        self.log_file.flush()
        return total, commission
