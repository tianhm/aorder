# encoding: UTF-8

"""
展示如何执行策略回测。
"""

from __future__ import division

from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME
import pandas as pd
from utils import plot_candles, plot_trade
import talib
import numpy as np

if __name__ == '__main__':
    from vnpy.trader.app.ctaStrategy.strategy.strategyAtrRsi import AtrRsiStrategy

    # 创建回测引擎
    engine = BacktestingEngine()

    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.BAR_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20160601')

    # 设置产品相关参数
    engine.setSlippage(0.2)  # 股指1跳
    engine.setRate(0.3 / 10000)  # 万0.3
    engine.setSize(300)  # 股指合约大小
    engine.setPriceTick(0.2)  # 股指最小价格变动

    # 设置使用的历史数据库
    engine.setDatabase(MINUTE_DB_NAME, 'rb0000')

    # 在引擎中创建策略对象
    # d = {'rsiLength': 10, 'atrLength': 10, 'rsiEntry':27}
    d = {'rsiLength': 10, 'atrLength': 10, 'rsiEntry':27}
    engine.initStrategy(AtrRsiStrategy, d)

    engine.loadHistoryData()

    # 开始跑回测

    engine.loadHistoryData()

    engine.runBacktesting()

    # 显示回测结果
    engine.showBacktestingResult(d)

    # analysis
    engine.loadHistoryData()

    orders = pd.DataFrame([i.__dict__ for i in engine.calculateBacktestingResult()['resultList']])

    pricing = pd.DataFrame(list(engine.dbCursor))

    atr = np.nan_to_num(talib.ATR(pricing.high.values, pricing.low.values, pricing.close.values, 25))

    atr_ma = np.nan_to_num(pd.DataFrame(atr).rolling(25).mean()[0].values)

    # 每个子图一个tuple: (name, type, [list of tech]), type为0则画在主图（k线图）上，1，则画在子图上。
    # [list of tech]，每个元素长度要和k线相同

    length = pricing.shape[0]
    technicals = [('rsi', 1, [talib.RSI(pricing.close.values, 4), np.full(length,50-16), np.full(length,50+16)]),
                  ('atr', 1,[np.greater(atr, atr_ma).astype(int)])]

    plot_trade(pricing, volume_bars=True, orders=orders, technicals=technicals)
