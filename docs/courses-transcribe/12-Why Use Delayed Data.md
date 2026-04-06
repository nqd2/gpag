# 12-Why Use Delayed Data

Data delay refers to the timestamp before which the alpha is allowed to use the data in its backtest. More recent data has up to date information which may benefit the alpha performance but data delay can help ensure there are no look ahead biases, an important idea we will explain in depth in this video. If an alpha uses data from a day before the date of backtest, I will call it a delay one alpha. And if the alpha uses today's price up to a chosen time during the day for simulation to run after that time, I will call it a delay zero alpha because it uses the same day information.

It is important to prevent biases in the data during backtesting. Look ahead bias happens when you use future information in your analysis that wouldn't have been known or available during the period being analyzed. This bias can lead to overoptimistic performance predictions that don't hold up in reality, skewing over expectations and potentially leading to costly surprises. To avoid the look ahead bias, quants use delayed data in the backtest.

Delay one alphas use yesterday's price, delay zero uses today's price up to a chosen time during the day, theoretically delay zero alphas are expected to perform better than delay one, but have a lower trading capacity due to shorter time available to trade.
