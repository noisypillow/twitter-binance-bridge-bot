from PyInquirer import Separator, prompt
from BinanceTwitterBridge import BinanceTwitterBridge
from ConfigManager import Config
import colorama
from colorama import Fore, Style
from art import tprint
import json


class CLI:
    def __init__(self):
        colorama.init()
        self.config = Config()
        self.bridge = BinanceTwitterBridge()
        self.binance_client = self.bridge.binance_client
        print('\n')
        tprint("T-B  Bridge", font="random")
        print("----------------------------------------------------------")
        print(f"Current {self.config.ASSET} value: ")
        print(
            " \u001b[33m    ❯ " +
            f"{self.binance_client.get_price(self.config.ASSET + self.config.BASE_ASSET)} {self.config.BASE_ASSET}\033[0m"
        )
        print(f"Current {self.config.BASE_ASSET} balance: ")
        print(
            " \u001b[33m    ❯ " +
            f"{self.binance_client.get_asset_blance(self.config.BASE_ASSET)} {self.config.BASE_ASSET}\033[0m"
        )
        print(f"Gain summary: ")
        print(" \u001b[33m    ❯ " +
              f"{self.get_gain_summary()} {self.config.BASE_ASSET}\033[0m")
        print("----------------------------------------------------------")
        self.main_menu()

    def get_gain_summary(self):
        bought = 0.0
        sold = 0.0
        with open('trades.log', 'r') as log_file:
            trades = log_file.readlines()
            for trade in trades:
                details = json.loads(trade.split(' ', 3)[3])
                if 'BUY' in trade:
                    bought += float(details['price']) * float(
                        details['qty']) - float(details['commission'])
                elif 'SELL' in trade:
                    sold += float(details['price']) * float(
                        details['qty']) - float(details['commission'])
        return sold - bought

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
                'type':
                'input',
                'name':
                'asset_input',
                'message':
                f'What asset do you want to buy ? (currently {self.config.get_asset()})'
            }
            asset = prompt(set_asset_prompt)['asset_input']
            self.config.update_asset(asset)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Set BASE_ASSET':
            set_base_asset_prompt = {
                'type':
                'input',
                'name':
                'base_asset_input',
                'message':
                f'What base asset do you want to buy with ? (currently {self.config.get_base_asset()})'
            }
            base_asset = prompt(set_base_asset_prompt)['base_asset_input']
            self.config.update_base_asset(base_asset)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Set BASE_ASSET_QUANTITY':
            set_base_asset_quantity_prompt = {
                'type':
                'input',
                'name':
                'base_asset_quantity_input',
                'message':
                f'What base asset quantity do you want to use ? (currently {self.config.get_base_asset_quantity()} {self.config.get_base_asset()})'
            }
            base_asset_quantity = prompt(
                set_base_asset_quantity_prompt)['base_asset_quantity_input']
            self.config.update_base_asset_quantity(base_asset_quantity)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Set INTERVAL':
            interval_prompt = {
                'type':
                'input',
                'name':
                'interval_input',
                'message':
                f'How many time between buy and sell ? (currently {self.config.get_interval()} seconds)'
            }
            interval = prompt(interval_prompt)['interval_input']
            self.config.update_interval(interval)
            self.bridge.reload_config()
            self.settings_menu()
        elif answer == 'Return':
            self.main_menu()
