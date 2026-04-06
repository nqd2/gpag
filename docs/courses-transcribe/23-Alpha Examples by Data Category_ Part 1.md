# 23-Alpha Examples by Data Category_ Part 1

Alpha Examples by Data Category, Part 1 Welcome to WorldQuant's Learn to Quant, where we hope to demystify quantitative finance research and make it accessible to you, guiding you through different ideas and their implementation on WorldQuant Brain. WorldQuant Brain is a simulation platform that provides data sets and tools to test your own ideas and gain feedback in real time. I'm Nitish Meni, the Chief Strategy Officer at WorldQuant. This series is your gateway to powering up your approach to quant research.

So let's learn to quant. Quant researchers tap into a variety of data to build predictive signals or alphas which are defined by WorldQuant as mathematical models that seek to predict future price movements of various financial instruments. The data categories include price fundamental, analyst, sentiment, options, model, insider transactions, short interest and more. Over the next few videos, we will introduce four data categories and illustrate each with an alpha example from idea to result.

So log into WorldQuant Brain. We are going to start with the price volume data category. It includes data like stock prices, the open price of a stock, high price, low price, close and other trading related information like volume of shares traded and market capitalization. The change in a stock's price between the open and the close of a trading session can be a potential idea.

Let's see how this information can be used as a signal to generate an alpha. Here is one hypothesis. If a stock's close price is lower than its open price, we may anticipate a reversion, expecting the stock to bounce back and outperform others in the near future. We take a long position, profiting if the price of the stock rises.

Conversely, if the close price is higher than the open price, we may expect a reversion to a lower price, prompting us to take a short position. Shorting an instrument usually involves borrowing it from a broker, then selling it in the market and later we buy it back from the market and return it to the broker. We profit if the price falls after we have shorted.

Now let's implement this idea on WorldQuant Brain using the proprietary expression language.

You can access all data categories discussed in this series on Brain. The group rank function takes the close and open price difference as the first input and sub-industry as the second. It ranks this difference among all stocks in the same sub-industry and assigns value between 0 and 1. Higher values get better ranks closer to 1 and lower values get rank closer to 0.

Stocks with negative alpha values are shorted, positive ones are bought. Next, decide the data timing to use in an alpha which we refer to as delay. Delay 1 uses yesterday's price while delay 0 uses today's price until a chosen time. Also decide if you want to use decay for your alpha.

Decay considers a weighted sum of the past alpha values to smooth out fluctuations or outliers. Decay helps if we want to use previous day's alpha value or to reduce the turnover. In this simulation, we use delay 1 data to prevent look-ahead bias, neutralize alpha over sub-industry, apply a decay of 10 for signal smoothing and restrict the maximum capital on any single stock to 1%. The back testing simulation runs for the previous five years generating an alpha vector for each day.

The results show a consistent sharp of 1.7 across years with decent coverage across the selected universe of top 3000 US stocks on the basis of liquidity.

Let's determine how to improve this alpha. This performance could be improved by controlling the turnover to trade only in the conditions which are more conducive to reversion. Trading only in higher volatility conditions and holding during low volatility.

Next up, the fundamental data category. Fundamentals capture the underlying business, financial and operational health of a company usually reported every quarter. While the data fields are many, they can be summarized into three financial statements. Balance sheet, income statement and cash flow statement.

The balance sheet provides a snapshot of the company's financial health, detailing its assets, liabilities and equity. The income statement illustrates the company's profitability showing how revenue is transformed into income after accounting for various expenses. And last, the cash flow statement reveals the company's liquidity by tracking the inflow and the outflow of cash from activities like operations, investments and financing.

Now, let's discuss an idea based on the changes in the cash flow from operations and market cap of the firm.

Cash flow from operations is the cash earned through core business activities. Market capitalization represents the firm's worth calculated as the current market price of one share multiplied by the total number of the company's outstanding shares. The ratio of cash flow from operations to market cap indicates if a company is fairly valued in the market with respect to its cash generating abilities. One theory is high ratio suggests an undervalued firm which could provide higher future returns and vice versa.

The hypothesis of the alpha is that if this ratio is improving over time, then the company's stock will outperform others. Hence, we will take a long position in this firm. Similarly, if this ratio declines, we expect underperformance and take a short position.

Now, let's examine how our idea gets implemented using brain's expression language.

The time series z-score function shows how the cash flow to market cap ratio has changed over the last 60 trading days. In statistics, the z-score describes how far a value is from the mean of a group in terms of standard deviations. We simulate the alpha expression over the top 3000 most liquid US stocks and neutralize over the market to make the alpha long shot neutral. The results show a consistent sharp of about two across years, 9% return, 29% turnover, and decent coverage across the selected universe.

To improve the alpha's performance, consider analyst predictions for each stock's operational cash flow rather than the last actual value. Analyst's estimates provide insights into expected company performance before the actual quarterly earnings reports are released. Using these estimates may enhance the accuracy of fundamental signals. In this video, we explored price volume and fundamental data with alpha examples.

Next, we will discuss options and sentiment data categories. Hopefully, you can grow your knowledge and further your journey into quant finance research as we explore alpha examples with other data categories. See you there.
