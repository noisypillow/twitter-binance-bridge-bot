import json


class Config:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        with open(self.config_file) as config_file:
            self.config = json.loads(
                config_file.read())  #loads config file into json format

        self.URL = self.config['URL']
        self.ASSET = self.config['ASSET']
        self.BASE_ASSET = self.config['BASE_ASSET']
        self.BASE_ASSET_QUANTITY = self.config['BASE_ASSET_QUANTITY']
        self.INTERVAL = self.config['INTERVAL']
        self.TWITTER_ID = self.config['TWITTER_ID']
        self.KEYWORD = self.config['KEYWORD']

    def update_asset(self, asset):
        try:
            int(asset)
            print("Please input a valid crypto asset")
        except:
            self.config['ASSET'] = asset.upper()
            with open(self.config_file, 'w') as config_file:
                json.dump(self.config, config_file, indent=4)

    def update_base_asset(self, base_asset):
        try:
            int(base_asset)
            print("Please input a valid base asset")
        except:
            self.config['BASE_ASSET'] = base_asset.upper()
            with open(self.config_file, 'w') as config_file:
                json.dump(self.config, config_file, indent=4)

    def update_base_asset_quantity(self, base_asset_quantity):
        try:
            self.config['BASE_ASSET_QUANTITY'] = int(base_asset_quantity)
        except:
            print("Please input an integer value")
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def update_interval(self, interval):
        try:
            self.config['INTERVAL'] = int(interval)
        except:
            print("Please input an integer value")
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def update_twitter_id(self, twitter_id):
        try:
            self.config['TWITTER_ID'] = int(twitter_id)
        except:
            print("Please input a valid twitter id")
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def update_keyword(self, keyword):
        self.config['KEYWORD'] = keyword
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def get_url(self):
        return self.config['URL']

    def get_asset(self):
        return self.config['ASSET']

    def get_base_asset(self):
        return self.config['BASE_ASSET']

    def get_base_asset_quantity(self):
        return self.config['BASE_ASSET_QUANTITY']

    def get_interval(self):
        return self.config['INTERVAL']


Config().update_interval(8)