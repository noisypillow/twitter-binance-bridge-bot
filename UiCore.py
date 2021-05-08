from PyInquirer import Separator, prompt
from BinanceTwitterBridge import BinanceTwitterBridge
from ConfigManager import Config


class CLI:
    def __init__(self):
        self.config = Config()
        self.bridge = BinanceTwitterBridge()
        self.main_menu()

    def main_menu(self):
        main_menu_prompt = {
            'type': 'list',
            'name': 'main-menu',
            'message': 'Twitter-Binance bridge bot',
            'choices': ['Start bot', 'Exit',
                        Separator(), 'Settings']
        }
        answer = prompt(main_menu_prompt)['main-menu']

        if answer == 'Start bot':
            self.bridge.start()
        elif answer == 'Exit':
            exit()
        elif answer == 'Settings':
            self.settings_menu()

    def settings_menu(self):
        settings_menu_prompt = {
            'type':
            'list',
            'name':
            'settings_menu',
            'message':
            'Settings',
            'choices': [
                'Set ASSET', 'Set BASE_ASSET', 'Set BASE_ASSET_QUANTITY',
                'Set INTERVAL',
                Separator(), 'Return'
            ]
        }
        answer = prompt(settings_menu_prompt)['settings_menu']

        if answer == 'Set ASSET':
            set_asset_prompt = {
                'type': 'input',
                'name': 'asset_input',
                'message': 'What asset do you want to buy ? (in CAPS)'
            }
            asset = prompt(set_asset_prompt)['asset_input']
            self.config.update_asset(asset)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Set BASE_ASSET':
            set_base_asset_prompt = {
                'type': 'input',
                'name': 'base_asset_input',
                'message':
                'What base asset do you want to buy with ? (in CAPS)'
            }
            base_asset = prompt(set_base_asset_prompt)['base_asset_input']
            self.config.update_base_asset(base_asset)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Set BASE_ASSET_QUANTITY':
            set_base_asset_quantity_prompt = {
                'type': 'input',
                'name': 'base_asset_quantity_input',
                'message': 'What base asset quantity do you want to use ?'
            }
            base_asset_quantity = prompt(
                set_base_asset_quantity_prompt)['base_asset_quantity_input']
            self.config.update_base_asset_quantity(base_asset_quantity)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Set INTERVAL':
            interval_prompt = {
                'type': 'input',
                'name': 'interval_input',
                'message': 'How many time between buy and sell ? (in seconds)'
            }
            interval = prompt(interval_prompt)['interval_input']
            self.config.update_interval(interval)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Return':
            self.main_menu()


if __name__ == '__main__':
    CLI()