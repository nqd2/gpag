# 25-Alpha Examples by Idea Type

Alpha Examples by IdeaType Welcome to WorldQuant's Learn to Quant. We have created this series to develop your skills in quant finance research. I am Nitesh Meni, Chief Strategy Officer at WorldQuant. Every day at WorldQuant, we aim to study and deploy sophisticated quant research.

And through this video series, we hope to share our experiences with you, empowering you to test your ideas. We will leverage our platform, WorldQuant Brain, a simulation platform to demonstrate these research ideas and see how they perform. Each day, a growing number of quant researchers are leveraging the data fields and tools on WorldQuant Brain to power up their quant skills and get real-time feedback on their ideas. So, let's give it a go now.

In our previous set of videos, we explored alphas by data categories and now we will cover alpha examples by different idea categories. As a reminder, WorldQuant defines an alpha as a mathematical model that seeks to predict the future price movement of various financial instruments. Alphas are fueled by a variety of ideas, each distinct in the pattern it can identify and the results it forecasts. Some ideas include reversion.

The hypothesis is that if something increases today, it will fall tomorrow. And if something decreases today, it will increase tomorrow. This something can be anything, price, volume, correlation between two things or the other indicators or variables that you think of while developing your alpha. Another idea category is momentum.

Assume that stocks which have performed well in the past will continue to perform well, while the stocks that have performed poorly will continue to do so. Seasonality is based on the idea that certain months, quarters or years may influence the price of a security. Lead-lag relationships assume that the prices of certain stocks lead and other lag behind. For example, an improvement in an industrial company might later lead to an improvement in its suppliers.

Index rebalancing is another idea category. When a stock is added to an index like the S&P 500, indexed funds purchased by the funds tracking the index can increase its price and can be predicted.

Now let's build some alphas based on a few of these ideas using Brain. We've already explored a mean reversion alpha in the previous video on price volume data.

If today's price is greater than the price 5 days ago, the hypothesis was that tomorrow the price will fall. So we would short this stock. Similarly, if today's price is less than the price 5 days ago, the price might increase tomorrow, therefore we might want to long the stock. We noted a similar pattern in the sentiment data set example where above average sentiment suggested an upcoming price drop.

Next, let's create an alpha example that builds on the momentum idea. That is based on the assumption that stocks which have performed well in the past will continue to perform well, while the stocks that have performed poorly will continue to do so. One way to create momentum alphas is by tracking the momentum in the stock's volume of shares traded. Larger volumes may imply increased liquidity and a bullish sentiment, which can be a positive predictor for the future stock returns.

Our hypothesis is that a large volume last week compared with an average volume over the past year implies higher liquidity. Therefore, a trader may want to go long on that stock.

Now let's implement this idea on Worldcoin Brain, a cloud-based simulation platform with proprietary expression language. This idea has a simple implementation using a rank and time series mean operator.

Time series mean calculates a stock's average volume over the last 5 trading days and 240 trading days. We compute a ratio of these metrics and then rank them from 0 to 1. The results show a sharp of 1.5, 6% returns, 1.25 ratio of returns to drawdown, 20% turnover with decent coverage across the selected universe. There are multiple times during a year when one could notice seasonal patterns.

The January Effect. Stocks often rise in January as investors repurchase stocks after selling them in December for tax harvesting. The End of Quarter Effect. Funds may rebalance their portfolios during the last week of a quarter, possibly creating predictable price patterns.

There is a pre-holiday effect or the Santa Claus rally. Markets have been known to rise around the year-end holidays. Then there is sell in May and go away until Halloween. This trend suggests investors may sell stocks on May 1st and return at October's end.

Seasonality can also occur around events like earnings announcements. You should now have a stronger understanding of how you too can come up with alpha idea categories from mean reversion, momentum, to seasonality. I hope you feel inspired to think through some of your own alpha ideas. In our next video, we will move on to building alphas by holding frequencies and delays.

Let's go quant.
