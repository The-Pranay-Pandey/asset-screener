"""
Multi-Indicator Forex Screener
Author: Pranay Pandey
Description:
Vectorized technical indicator engine for systematic signal generation.
"""



# %%
import yfinance as yf
import pandas as pd
import numpy as np

# %%
tickers = ['EURUSD=X','USDJPY=X']
timeframe = '1h' #valid - 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
actions = {'sma':[20,10],'ema':[20,10],'rsi':14,'macd':[26,12,9],'bollinger_bands':[20,2],'stochastic':12,'adx':14}
period = '1mo' #valid - 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max


# %%
def download_data(tickers, period, timeframe):
    data = yf.download(tickers,
                       period = period, 
                       auto_adjust = False, 
                       interval = timeframe)
    
    data.drop(columns = ['Volume'], inplace = True) # no need for volume
    data.dropna(inplace=True)
    data.index = data.index + pd.Timedelta(hours = 5, minutes=30)# changing the time from utc to ist
    return data


# %%
def run_screener(data, actions, tickers):
    '''creating a new dataframe signals to store the signals from all the indicators
    multi_index creates a column for every ticker and creates sub columns(level 2 indicator names) within each column(level 1 - ticker or asset name) 
    '''
    multli_columns = pd.MultiIndex.from_product([tickers, list(actions.keys())], names=['ticker', 'indicator'])
    signals = pd.DataFrame(index=data.index, columns=multli_columns)

    assets = {} #list of dataframes of each asset
    for ticker in tickers:
        Close = data['Close'][ticker]
        High = data['High'][ticker]
        Low = data['Low'][ticker]
        Open  = data['Open'][ticker]
        Returns = data['Close'][ticker] / data['Close'][ticker].shift(1)
        df = pd.DataFrame(data = {'Close':Close, 'High':High, 'Low':Low, 'Open':Open, 'returns':Returns})
        assets.update({ticker:df})


    
    # calculation sma
    if 'sma' in actions:
        sma_slow = actions['sma'][0]
        sma_fast = actions['sma'][1]
        for ticker, asset in assets.items():
            asset = asset.copy()
            asset['sma_slow'] = asset.Close.rolling(sma_slow).mean()
            asset['sma_fast'] = asset.Close.rolling(sma_fast).mean()
            
            #signals[ticker] returns a view of the dataframe hence to have a real copy we need to use loc
            signals.loc[:, (ticker, 'sma')] = np.where(asset['sma_fast'] > asset['sma_slow'], 1, -1)

        
    #calculating ema
    if 'ema' in actions:
        ema_slow = actions['ema'][0]
        ema_fast = actions['ema'][1]
        for ticker, asset in assets.items():
            asset = asset.copy()
            asset['ema_slow'] = asset.Close.ewm(span = ema_slow, min_periods=ema_slow).mean()
            asset['ema_fast'] = asset.Close.ewm(span = ema_fast, min_periods=ema_fast).mean()

            signals.loc[:, (ticker, 'ema')] = np.where(asset['ema_fast'] > asset['ema_slow'], 1, -1)

        
    #calculating rsi
    if 'rsi' in actions:
        for ticker, asset in assets.items():
            asset = asset.copy()

            delta = asset['Close'].diff()
            period = actions['rsi']

            gain = delta.clip(lower = 0)
            loss = -delta.clip(upper = 0)

            avg_gain = gain.ewm(alpha = 1/period, adjust = False).mean()
            avg_loss = loss.ewm(alpha = 1/period, adjust = False).mean()

            rsi = avg_gain / (avg_gain + avg_loss) * 100
            asset['rsi'] = rsi

            signals.loc[:, (ticker, 'rsi')] = np.where(asset['rsi'] > 70, -1, 0)
            signals.loc[:, (ticker, 'rsi')] = np.where(asset['rsi'] < 30, 1, signals.loc[:, (ticker, 'rsi')])

    

    #calculating macd
    if 'macd' in actions:
        for ticker, asset in assets.items():
            asset = asset.copy()
            ema_slow = actions['macd'][0]
            ema_fast = actions['macd'][1]
            signal_line = actions['macd'][2]
            asset['ema_slow'] = asset.Close.ewm(span = ema_slow, min_periods=ema_slow).mean()
            asset['ema_fast'] = asset.Close.ewm(span = ema_fast, min_periods=ema_fast).mean()
            asset['macd'] = asset['ema_fast'] - asset['ema_slow']
            asset['macd_signal_line'] = asset.macd.ewm(span = signal_line, min_periods = signal_line).mean()

            signals.loc[:, (ticker, 'macd')] = np.where(asset['macd'] > asset['macd_signal_line'], 1, 0)
            signals.loc[:, (ticker, 'macd')] = np.where(asset['macd'] < asset['macd_signal_line'], -1, signals.loc[:, (ticker, 'macd')])

    #bollinger bands
    if 'bollinger_bands' in actions:
        for ticker, asset in assets.items():
            asset = asset.copy()
            sma = actions['bollinger_bands'][0]
            number_of_std = actions['bollinger_bands'][1]
            asset['sma'] = asset.Close.rolling(window = sma).mean()
            asset['upper_band'] = asset.sma + asset.Close.rolling(window = sma).std() * number_of_std
            asset['lower_band'] = asset.sma - asset.Close.rolling(window = sma).std() * number_of_std

            signals.loc[:, (ticker, 'bollinger_bands')] = np.where(asset.Close > asset['upper_band'], -1, 0)
            signals.loc[:, (ticker, 'bollinger_bands')] = np.where(asset.Close < asset['lower_band'], 1, signals.loc[:, (ticker, 'bollinger_bands')])
            asset.drop(columns=['sma'],inplace = True)

    #stochastic 
    if 'stochastic' in actions:
        for ticker, asset in assets.items():
            asset = asset.copy()
            asset['max'] = asset.High.rolling(window = actions['stochastic']).max()
            asset['min'] = asset.Low.rolling(window = actions['stochastic']).min()
            asset['K'] = (asset['Close'] - asset['min']) / (asset['max'] - asset['min']) * 100
            asset['D'] = asset.K.rolling(window = 3).mean()

            signals.loc[:, (ticker, 'stochastic')] = np.where(asset['K'] > asset['D'], 1, 0)
            signals.loc[:, (ticker, 'stochastic')] = np.where(asset['K'] < asset['D'], -1, signals.loc[:, (ticker, 'stochastic')])
            asset.drop(columns=['max','min'],inplace = True)

    
    #adx
    if 'adx' in actions:
        for ticker, asset in assets.items():
            asset = asset.copy()

            period = actions['adx']
            hl = asset['High'] - asset['Low']
            hc = (asset['High'] - asset['Close'].shift()).abs()
            lc = (asset['Low'] - asset['Close'].shift()).abs()

            asset['tr'] = pd.concat([hl, hc, lc], axis=1).max(axis=1)

            asset['up_move'] = asset['High'] - asset['High'].shift()
            asset['down_move'] = asset['Low'].shift() - asset['Low']

            asset['pos_DM'] = np.where((asset['up_move'] > asset['down_move']) & (asset['up_move'] > 0), asset['up_move'],0)
            asset['neg_DM'] = np.where((asset['down_move'] > asset['up_move']) & (asset['down_move'] > 0), asset['down_move'],0)

            asset['trt'] = asset['tr'].ewm(alpha=1/period, adjust = False).mean()
            asset['pos_DMt'] = asset['pos_DM'].ewm(alpha=1/period, adjust = False).mean()
            asset['neg_DMt'] = asset['neg_DM'].ewm(alpha=1/period, adjust = False).mean()

            asset['pos_DI'] = asset['pos_DMt']/asset['trt'] * 100
            asset['neg_DI'] = asset['neg_DMt']/asset['trt'] * 100

            asset['DX'] = np.abs(asset['pos_DI'] - asset['neg_DI']) / (asset['pos_DI'] + asset['neg_DI']) * 100

            asset['ADX'] = asset['DX'].ewm(alpha=1/period, adjust = False, min_periods = period * 3).mean()

            signals.loc[:,(ticker,'adx')] = np.where(asset['ADX'] < 20, 'sideways','')
            signals.loc[:,(ticker,'adx')] = np.where((asset['ADX'] > 20) & (asset['ADX'] < 25), 'Developing Trend',signals.loc[:,(ticker,'adx')])
            signals.loc[:,(ticker,'adx')] = np.where((asset['ADX'] > 25) & (asset['ADX'] < 50), 'Strong Trend',signals.loc[:,(ticker,'adx')])
            signals.loc[:,(ticker,'adx')] = np.where((asset['ADX'] > 50) & (asset['ADX'] < 75), 'Extremely Strong Trend',signals.loc[:,(ticker,'adx')])
            signals.loc[:,(ticker,'adx')] = np.where((asset['ADX'] > 75) & (asset['ADX'] < 100), 'Near Exhaustion',signals.loc[:,(ticker,'adx')])


    return signals
    

# %%
if __name__ == '__main__':
    data = download_data(tickers=tickers, period=period, timeframe=timeframe)
    signals = run_screener(data=data, actions=actions,tickers=tickers)
    signals.to_csv('signals_output.csv')
    print(signals.tail())
    print("Screener executed successfully.")


# %%



