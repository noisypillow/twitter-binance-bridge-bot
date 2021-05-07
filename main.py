import json
from datetime import datetime
from time import sleep
from urllib3 import exceptions

from TradingCore import BinanceClient, BaseAssetBalanceTooLow
from requests.models import ProtocolError
from TweeterCore import TweetListener

keys = json.loads(open('keys.json', 'r').read())
TWITTER_KEYS = [
    keys['API_KEY'], keys['API_SECRET_KEY'], keys['ACCESS_TOKEN'],
    keys['SECRET_ACCESS_TOKEN']
]

BINANCE_KEYS = [keys['LIVE_PUB_KEY'], keys['LIVE_SECRET_KEY']]


def got_tweet(status):
    try:
        print(datetime.now().strftime(f"%d-%m-%Y %H:%M:%S | ") +
              f"Elon just tweeted about ${binance_client.ASSET}:")
        print("    " + status.text)
        order_id, commission = binance_client.buy(3)
        sleep(5)
        binance_client.sell(order_id, 5, commission)
        print("----------------------------------------------------------")
    except BaseAssetBalanceTooLow:
        print("Not enough liquidity.")


if __name__ == "__main__":
    while True:
        try:
            print('Start streaming.')
            binance_client = BinanceClient(BINANCE_KEYS)
            TweetListener(TWITTER_KEYS, '884457459183738880', 'doge',
                          got_tweet)
        except KeyboardInterrupt:
            print("Stream stopped.")
            break
        except ProtocolError:
            print("ProtocolError, retying..")
            pass
        except exceptions.ReadTimeoutError:
            print("ReadTimoutError, retrying..")
