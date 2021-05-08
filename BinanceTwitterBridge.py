import json
from urllib3 import exceptions

from TradingCore import BinanceClient
from requests.models import ProtocolError

from TweeterCore import TweetListener


class BinanceTwitterBridge:
    def __init__(self):

        keys = json.loads(open('keys.json', 'r').read())

        TWITTER_KEYS = [
            keys['API_KEY'], keys['API_SECRET_KEY'], keys['ACCESS_TOKEN'],
            keys['SECRET_ACCESS_TOKEN']
        ]

        BINANCE_KEYS = [keys['LIVE_PUB_KEY'], keys['LIVE_SECRET_KEY']]

        self.binance_client = BinanceClient(BINANCE_KEYS)
        self.tweet_listener = TweetListener(TWITTER_KEYS, '44196397',
                                            'doge',
                                            self.binance_client.on_tweet)

    def start(self):
        while True:
            try:
                print('Start streaming.')
                self.tweet_listener.start()
            except KeyboardInterrupt:
                print("Stream stopped.")
                break
            except ProtocolError:
                print("ProtocolError, retying..")
                pass
            except exceptions.ReadTimeoutError:
                print("ReadTimoutError, retrying..")
            except Exception as e:
                print(e)

    def reload_config(self):
        self.binance_client.reload_config()


if __name__ == "__main__":
    BinanceTwitterBridge().start()
