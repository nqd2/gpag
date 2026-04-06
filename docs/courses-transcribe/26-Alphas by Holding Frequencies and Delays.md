# 26-Alphas by Holding Frequencies and Delays

Alphas by holding frequencies and delays. As a reminder, WorldQuant defines an alpha as a mathematical model that seeks to predict the future price movement of various financial instruments. I'm Nitish Meni, your partner in learning about quant finance research. I'm the Chief Strategy Officer at WorldQuant.

In my role, I help to define our firm's strategy and drive several cross-functional business initiatives, including new avenues for growth and innovation. In this video, we will focus on the role played by holding frequencies and data delays. Holding frequency is the total length of time an investor expects to hold a portfolio or security. The holding period has implications on the risk returns and transaction costs.

Data delay refers to the timestamp before which the alpha is allowed to use the data in its backtest. More recent data has up-to-date information which may benefit the alpha performance, but data delay can help ensure there are no look-ahead biases, an important idea we will explain in depth in this video. If an alpha uses data from a day before the date of backtest, I will call it a delay one alpha. And if the alpha uses today's price up to a chosen time during the day for simulation to run after that time, I will call it a delay zero alpha because it uses the same day information.

We will also put our ideas to the test on WorldQuant Brain, our cloud-based platform where we can get real-time feedback. If you would like to try this, as I explain these ideas, log into Brain now. Alphas can be classified into three categories based on the holding period. The medium to low frequency alphas.

These are alphas with holding periods that range from a few days to months and sometimes even longer. Intraday trading. These update positions much more frequently, ranging from every minute to a few hours. They are typically based on price-volume signals to capitalize on short-lived price patterns.

They can also use news data, earnings announcements or faster intraday data like sentiment or options. High frequency trading or HFT alphas. These hold positions from nanoseconds to a few seconds. HFT signals can be market-making strategies that provide market liquidity or price arbitrage strategies that capitalize on price discrepancies between related assets or markets.

They can also take short-term directional trades based on price patterns like short-term momentum. It is important to prevent biases in the data during backtesting. Look-ahead bias happens when you use future information in your analysis that wouldn't have been known or available during the period being analyzed. This bias can lead to over-optimistic performance predictions that don't hold up in reality, skewing over expectations and potentially leading to costly surprises.

To avoid the look-ahead bias, quants use delayed data in the backtest. Delay 1 alphas use yesterday's price, delay 0 uses today's price up to a chosen time during the day. Theoretically, delay 0 alphas are expected to perform better than delay 1 but have a lower trading capacity due to shorter time available to trade. We have reviewed several delay 1 alphas in our previous videos, so let's shift to a delay 0 example.

We will use volatility data focusing on at-the-money implied volatility of call options expiring within 4 months and their Parkinson's volatility. Parkinson's volatility measures realized volatility using the high and low prices within a day. It captures large intraday price variations even when the previous day close and the current day close price change is small. The strike price is where the call option starts making a profit.

And implied volatility represents the expected future stock movement highly influenced by option demand. At-the-money implied volatility aggregates implied volatilities of call options where the strike price equals the stock's current price and the option expires within 4 months. Our alpha idea captures call option demand using the implied volatility of its at-the-money call options expiring up to 4 months ahead, scaled by Parkinson's volatility over the past 4 months. If the implied volatility to Parkinson's volatility ratio is high, the hypothesis is that we expect high future stock returns and vice versa.

Now let's implement this idea on WorldQuantBrain using its proprietary expressions language. In this example, we simply take the ratio of the implied volatility of at-the-money call options to Parkinson's volatility for the stock using the data fields on the Brain Platform. These delay zero values are available by the cut-off time each day in the markets for the alpha to generate positions. The results show a consistent sharp of about 2 across years, a 14% gross returns, 1.2 returns to drawdown ratio, 29% turnover and decent coverage across the selected universe.

In this video, we learnt about 3 holding periods in quant finance, the importance of delayed data to prevent look-ahead biases and reviewed a delay zero alpha example. In the next video, we will discuss the power of diversity of alphas. Step by step, I hope that you are powering up your knowledge and testing out your ideas with me.

Let's go quant, see you in Brain.
