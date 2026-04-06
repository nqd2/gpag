# 24-Alpha Examples by Data Category_ Part 2

Alpha Examples by Data Category Part 2. I'm Nitish Meni, your partner in learning more about Quant Finance Research. By day, I am the Chief Strategy Officer at World Quant. In my role, I help to define the firm's strategy, as well as drive several cross-functional business initiatives, including new avenues for growth and innovation.

Quant, in our last video, we explored Alpha Examples by Data Categories.

Let's continue with the next set of categories. The next category is Sentiment Data. Sentiment data quantifies the emotions of the masses towards the stock or market in general.

The data are captured from various mediums like social media channels, news and blogs. Quant researchers monitor popular opinion in an effort to seek to predict the direction of the movement in the stock price and the conviction or the intensity underlying these sentiments. Quant researchers also analyze the sentiment buzz, that is the degree of activity of the investors in a particular stock.

Let's review an example for such an Alpha on Brain, our simulation platform.

Remember, at World Quant, we define an Alpha as a mathematical model that seeks to predict the future price movement of various financial instruments. The hypothesis for this Alpha idea is if a stock's sentiment buzz is rising compared to the historical average, that means the stock is attracting higher investor attention lately, and is possibly overpriced so we expect lower future returns and short the stock. Conversely, we go long on stocks with falling buzz anticipating higher future returns.

Now let's implement this idea on World Quant Brain with the proprietary expression language.

By the way, you can access all data categories discussed in this series on Brain. We compute the ratio of today's sentiment buzz for a stock to the mean over the last 10 trading days or two calendar weeks using the time series mean function. Values greater than one indicate an increasing trend in the sentiment buzz. We apply a negative sign before the expression to express our bearish outlook for the stocks with increasing recent buzz.

The back testing simulation runs for the previous five years to generate an Alpha vector for each day in the simulation. If the value for the stock is negative, it shorts the stock and goes long on the stocks with positive values. We simulate the expression on the top 200 US stocks on the basis of the liquidity and on delay one data to prevent any look ahead bias. We neutralize the Alpha over the industry, apply a decay of 10 to smoothen any noise in the buzz data and restrict the maximum capital on a single stock to 1%.

The results show a consistent sharp of 1.6 across years, returns over 9% with a decent coverage across the selected universe. The last data category that we will explore is options. Options are contracts within the derivatives market which give the right but not the obligation to buy or sell an underlying security at a specific strike price. While the world of options can be complex, in this example we will focus on extracting information from equity options by particularly focusing on a metric called implied volatility.

Implied volatility is the expected future fluctuation in the price of the underlying stock. Implied volatility is computed using multiple variables like price of options, time to expiry of options, interest rates, strike prices, etc. Higher option prices generally lead to higher implied volatility, reflecting the demand for the option. When the price of the stock moves above the strike price, the holder of the call option makes a profit.

When the price of the stock goes below the strike price, the holder of the put option makes a profit. For our analysis, we use implied volatility derived from the add the money call and put options. An add the money option is an option whose underlying asset price is very close to the strike price of the option. The idea of our alpha is based on capturing the difference in the demands of add the money call and put options as measured by their implied volatility over long horizon to capture longer term trends in the stock prices.

This leads us to a hypothesis. If implied volatility derived from call options expiring up to two years in the future is higher than the implied volatility derived from put options expiring up to two years in the future, then the demand for a stock exceeds its supply and we expect the stock prices to appreciate in the future. We shall go long on such stocks. For the stocks where the difference in the implied volatility is negative, we have a bearish outlook and we shall go short on them.

Now let's discuss how our idea is implemented using brain's expression language. We store our call and put options in two variables, IV call and IV put respectively. Our alpha captures the net demand of the stock as the difference in the implied volatilities. We simulate the expression on the top 3000 US stocks on the basis of liquidity and on delay one data to prevent any look ahead bias.

We neutralize alpha over the industry, apply a decay of seven to smoothen the signal and restrict the maximum capital on any single stock to one percent. The results show a consistent sharp of around two across years, returns of 14 percent, return to drawdown ratio of three, turnover of 25 percent and with decent coverage across the selected universe. To improve the alpha performance, we can consider trends in other variables from options trading like open interest and options volume which are indicative of the demand of the underlying stock. In this video, we explored sentiment and options data category with corresponding alpha examples.

In our next video, we are going to explore alphas categorized by idea type.

Let's continue our quant research journey together. Quant on with me.
