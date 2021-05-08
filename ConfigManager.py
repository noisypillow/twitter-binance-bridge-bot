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

    def update_url(self, url):
        self.config['URL'] = url
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def update_asset(self, asset):
        self.config['ASSET'] = asset
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def update_base_asset(self, base_asset):
        self.config['BASE_ASSET'] = base_asset
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def update_base_asset_quantity(self, base_asset_quantity):
        self.config['BASE_ASSET_QUANTITY'] = base_asset_quantity
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def update_interval(self, interval):
        self.config['INTERVAL'] = interval
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)


Config().update_interval(8)