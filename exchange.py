import configparser
import datetime
import time
import logging
from dateutil import tz

import ccxt


class ExchData():

    def __init__(self, symbol):
        self.symbol = symbol
        logging.info('Symbol: {}'.format(self.symbol))

        if (symbol in '.BXBT'):
            self.exchange = ccxt.bitmex({
                                            'rateLimit': 10000,
                                            'enableRateLimit': True
                                            })
        else:
            self.exchange = ccxt.bitmex({
                                            'rateLimit': 10000,
                                            'enableRateLimit': True
                                            })
        
        logging.info('{0} instantialized...'.format(self.exchange.describe()['name']))
        
        self.candles = []
        self.apilimit = 10
        self.sleeptimer = 10
            

    def get_books(self, symbol, ):
        book = self.exchange.fetch_order_book(self.symbol)


    def clear_candles(self):
        self.candles = []
        logging.info('Candles cleared...')
            
    def fetch_candles(self, timeframe=None, start=None, limit=None):
        apitry = 0
        logging.info('Attempting to fetch candles...')
        if timeframe == None:
            timeframe = '1h'
        logging.info('Timeframe: {}'.format(timeframe))

        if start == None:
            start = int(self.exchange.milliseconds()) - 86400000 * 1 #last 1 * 24hours
        else:
            start = int(self.exchange.milliseconds()) - 86400000 * start
        logging.info('Start date: {}'.format(self.exchange.iso8601(start)))

        if limit == None:
            limit = 100
        logging.info('Limit: {}'.format(limit))
        condition = True
        while (apitry < self.apilimit) and (condition):
            try:
                results = self.exchange.fetch_ohlcv(self.symbol, timeframe=timeframe, since=start, limit=limit)
                condition = False
            except:
                logging.error('Could not fetch candles. Trying again...')
                apitry += 1
                time.sleep(self.sleeptimer)

        for element in results:
            candle = {
                'timestamp':element[0],
                'open':element[1],
                'high':element[2],
                'low':element[3],
                'close':element[4],
                'volume':element[5]}

            self.candles.insert(0, candle)


    def fetch_candles_long(self, timeframe, start, limit):
        results = []
        results2 = []
        logging.info('Attempting to fetch candles...')
        logging.info('Timeframe: {}'.format(timeframe))

        since = int(self.exchange.milliseconds()) - 86400000 * start
        logging.info('Start date: {}'.format(self.exchange.iso8601(since)))

        if limit == None:
            limit = 1000
        logging.info('Limit: {}'.format(limit))

        condition = True
        apitry = 0
        while (apitry < self.apilimit) and (condition):
            try:
                results = self.exchange.fetch_ohlcv(self.symbol, timeframe=timeframe, since=since, limit=limit)
                condition = False
            except:
                logging.error('Could not fetch candles. Trying again...')
                apitry += 1
                time.sleep(self.sleeptimer)

        logging.info('Fetching second part of candles...')
        since = int(self.exchange.milliseconds()) - 86400000 * int(start // 2)
        logging.info('Start date: {}'.format(self.exchange.iso8601(since)))
        
        condition = True
        apitry = 0
        while (apitry < self.apilimit) and (condition):
            try:
                results2 = results = self.exchange.fetch_ohlcv(self.symbol, timeframe=timeframe, since=since, limit=limit)
                condition = False
            except:
                logging.error('Could not fetch candles. Trying again...')
                apitry += 1
                time.sleep(self.sleeptimer)

        for element in results:
            candle = {
                'timestamp':element[0],
                'open':element[1],
                'high':element[2],
                'low':element[3],
                'close':element[4],
                'volume':element[5]}

            self.candles.insert(0, candle)
        for element in results2:
            candle = {
                'timestamp':element[0],
                'open':element[1],
                'high':element[2],
                'low':element[3],
                'close':element[4],
                'volume':element[5]
                }

            self.candles.insert(0, candle)


    def get_candles(self):
        return self.candles


    def get_hour(self, timestamp):
        hour = datetime.datetime.utcfromtimestamp(timestamp / 1000).strftime('%H')        #take timestamp and remove miliseconds

        return hour


    def convert_candles(self, candle_data, timeframe):
        new_candles = []
        condition = True
        logging.info('Converting candles to {}h candles...'.format(timeframe))
        #remove open candles
        logging.info('Original length: {}'.format(len(candle_data)))        #debugging
        while (condition):         
            if ( int(self.get_hour(candle_data[0]['timestamp'])) % timeframe == timeframe-1 ):
                condition = False
            else:
                del candle_data[0]
        logging.info('New length: {}'.format(len(candle_data)))        #debugging
        
        #create custom candles
        i = 0
        for i in range(i, len(candle_data) - len(candle_data)%timeframe, timeframe):
            candle_timestamp = candle_data[i]['timestamp']
            candle_open = candle_data[i+3]['open']

            candle_high = max(
                            candle_data[i]['high'],
                            candle_data[i+1]['high'],
                            candle_data[i+2]['high'],
                            candle_data[i+3]['high']
                            )

            candle_low = min(
                            candle_data[i]['low'],
                            candle_data[i+1]['low'],
                            candle_data[i+2]['low'],
                            candle_data[i+3]['low']
                            )

            candle_close = candle_data[i]['close']

            candle_volume = int(candle_data[i]['volume']) \
                            + int(candle_data[i+1]['volume']) \
                            + int(candle_data[i+2]['volume']) \
                            + int(candle_data[i+3]['volume']) 

            candle = {
                'timestamp':candle_timestamp,
                'open':candle_open,
                'high':candle_high,
                'low':candle_low,
                'close':candle_close,
                'volume':candle_volume
                }

            new_candles.append(candle)

        return new_candles
