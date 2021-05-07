from PyInquirer import Separator, prompt
from BinanceTwitterBridge import BinanceTwitterBridge


class CLI():
    def __init__(self):
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
            BinanceTwitterBridge().start()
        elif answer == 'Exit':
            exit()
        elif answer == 'Settings':
            pass

    def settings(self):
        pass


if __name__ == '__main__':
    CLI()