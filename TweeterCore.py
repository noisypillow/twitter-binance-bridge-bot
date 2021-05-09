from types import FunctionType
import tweepy
from ConfigManager import Config


def verify(status, keywords):
    if hasattr(status, 'retweeted_status'):
        return False
    if status.in_reply_to_status_id != None:
        return False
    elif status.in_reply_to_screen_name != None:
        return False
    elif status.in_reply_to_user_id != None:
        return False
    elif keywords in status.text.lower():
        return True
    else:
        print("False alert.")


class TweetListener(tweepy.StreamListener):
    def __init__(self, keys, exec_func):
        super().__init__()  #inits mother class
        self.config = Config()
        self.twiter_id = self.config.TWITTER_ID  #id of the tracked profile
        self.keywords = self.config.KEYWORD  #keywords wich have to be in the tweet
        self.exec_func = exec_func  #function to be executed on verifed status

        auth = tweepy.OAuthHandler(keys[0], keys[1])
        auth.set_access_token(keys[2], keys[3])

        self.stream = tweepy.Stream(auth=auth, listener=self)

    def reload_config(self):
        self.config = Config()

    def start(self):
        self.update()

    def update(self):
        self.stream.filter(follow=[self.tweeter_id])

    def set_tweeter_id(self, tweeter_id):
        self.tweeter_id = tweeter_id
        self.update()

    def set_keywords(self, keywords):
        self.keywords = keywords
        self.update()

    def on_status(self, status):
        if verify(status, self.keywords):
            self.exec_func(status)
