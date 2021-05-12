# Twitter Binance bridge bot

### 🛑 This script is still in active developement, use at your own risk 🛑

This bot is able to buy and sell $DOGE on Binance whenever Elon Musk tweets about it. (but you can completely configure it !)

## TO-DO

- [x] Tracking tweets
- [x] Binance integration
- [x] *config.json* setup
- [x] Gain summary
- [ ] Code clean-up
- [ ] Complete CLI
- [ ] Docs

## 📖 User guide
### 🖥 Installation
##### **1. With Git**
Run the following commands in a terminal:
```
git clone https://github.com/NoisyPillow/twitter-binance-bridge-bot.git
cd twitter-binance-bridge-bot
python -m pip install -r requirements.txt
```
##### **2. Without Git**
* [Download](https://github.com/NoisyPillow/twitter-binance-bridge-bot/archive/refs/heads/master.zip) the .zip folder and unzip it
* `cd` into it
* Run `python -m pip install -r requirements.txt`

### ✏ Usage
* `cd` into the *twitter-binance-bridge-bot* folder
* Run `python BinanceTwitterBridge.py`

## What you can configure (in `config.json` or directly from CLI)

```json
{
    "URL": "https://api.binance.com",
    "ASSET": "DOGE",
    "BASE_ASSET": "USDT",
    "BASE_ASSET_QUANTITY": 100,
    "INTERVAL": 300,
    "TWITTER_ID": "44196397",
    "KEYWORD": "doge"
}
```

* `URL` Binance API endpoint (see https://binance-docs.github.io/apidocs/spot/en/#general-info)
* `ASSET` The asset you're buying
* `BASE_ASSET` The base asset you're buying with
* `BASE_ASSET_QUANTITY` The base asset amount you want to spend
* `INTERVAL` The time between buying order and selling order
* `TWITTER_ID` The user's id you want to listen tweets from (see https://tweeterid.com/)
* `KEYWORD` The keyword you're tracking

## Miscellaneous
If you find this bot usefull, a small tip would be really cool 🥰  
DOGE: *DNQNffakrL79cpzNBjB54kCSPhYEdUUAJ7*
