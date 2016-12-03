from pandas_datareader import data
import pandas as pd
from datetime import datetime

from ftca import FTCA


def get_yahoo_finance_data(assets_list, start,
                           end=datetime.now().strftime('%Y-%m-%d')):

    prices = {}
    for asset in assets_list:
        prices[asset] = data.DataReader(asset, 'yahoo', start, end)[
            'Adj Close'].values.tolist()
    df = pd.DataFrame(prices)
    return df


def main():

    assets_list = [
        'GE', 'CAT', 'BA', 'LMT',  # Industrials
        'AIG', 'AXP', 'GS', 'JPM',  # Financials
        'AMZN', 'CSCO', 'EBAY', 'AAPL',  # Information Technology
        'APC', 'APA', 'BHI', 'SLB',  # Energy
        'ABT', 'AGN', 'BDX', 'BMY'  # Health Care
    ]

    ftca_obj = FTCA(threshold=0.5, period=1)
    prices = get_yahoo_finance_data(assets_list, '2015-01-01')
    ftca_obj.apply_ftca(prices)

    for k, v in ftca_obj.clusters.iteritems():
        print (k, v)


if __name__ == '__main__':
    main()


