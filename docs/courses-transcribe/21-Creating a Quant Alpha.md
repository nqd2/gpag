# 21-Creating a Quant Alpha

Creating a Quant Alpha. I am Nitish Meni, the Chief Strategy Officer at WorldQuant. I help to define our firm's strategy as well as drive several cross-functional business initiatives including new avenues for growth and innovation. This series is designed to power up your mastery of quantitative finance research and help you to implement what you learn on WorldQuant Brain.

WorldQuant Brain is not just a platform to test your ideas, but also a community of quant researchers who collaborate and push each other to become better researchers. So far, we have provided an overview of the quant ecosystem.

Now we will go much deeper and go back to the very beginning of the research process. So get ready and log into WorldQuant Brain.

Let's start at the alpha level. At WorldQuant, we define an alpha as a mathematical model that seeks to predict the future price movement of various financial instruments. To create an alpha, we begin with an idea that seeks to capture an inefficiency in the market. That idea is then applied to a chosen group of stocks which we call our alpha universe.

For each stock, we need to decide whether to buy or sell it and how much capital to allocate. Next, we implement our idea using code, test its potential performance in the market, say over the past five years, a process we call back testing. During back testing, we set criteria to assess our idea's quality, refine its execution, which includes performing robustness tests. We will look at each of these steps and break them down together.

To recap from the previous video to WorldQuant, an alpha is a mathematical model that seeks to predict the future price movement of various financial instruments. One idea could be to buy stocks whose prices fell recently and expect the prices to revert back to the average historical price. For the stocks that experienced a rise in price in the last week, we shot them expecting their price to decline. This idea is called price reversion.

An alpha is a vector of predicted values of stocks in the universe. The universe could be a group of US stocks defined on the basis of their liquidity. Each value can change daily and has two properties.

First, the direction of the alpha and second, the magnitude of the alpha.

Direction determines whether you want to go long or short the instrument. The magnitude of the values determine what proportion of the allocated capital should be distributed amongst the instruments in the universe. In allocating capital across the stocks in our alpha universe, we aim to balance estimated returns with downside protection. For this, we create equity short market neutral alphas.

Let's delve into what that means. Taking a long position means buying a stock and making money when it increases in value. On the other hand, taking a short position in a stock means borrowing an equity that you do not own, usually from a broker, selling it and then hoping it declines in value. The hope is you can buy it back at a lower price than what you had paid for it and return the borrowed shares.

Many hedge funds may utilize an equity long short market neutral strategy. It involves equal amount of long positions in stocks expected to rise in value and short positions in stock expected to drop in value. The hope is that even if the long positions fall in value, profit from shorting may still outweigh losses benefiting the hedge fund. With an idea and the universe set, we move to the implementation.

Identifying the type of data can help capture the idea. The next step is to implement the alpha idea by writing a piece of code using a language like C++, Python, R, etc and run a simulation using historical data to test if the idea would have made money in the past. As an exercise, let's implement a price reversion idea using the expression language on WorldQuant Brain. Brain is our open access trading simulation platform.

We provide two aspiring quants to hone their ideas and get immediate feedback. To implement our alpha idea, we could choose the closing price data field and an operation from our expression language to calculate the change in today's price compared to the closing price five days ago. The alpha would look like t s delta close comma five with parameter five capturing a change in price over five days to make a long or short decision for each stock. This code will run on the past data to output the alpha vector for each day and has one value for each stock in the universe.

We won't show you the results of this back test in this video but we will go through multiple alpha ideas and back test them in future videos so definitely stay tuned for those. In this video, we have learnt about long short market neutralization and how to create alphas from idea to implementation. You can start testing out your ideas on WorldQuant Brain. See you in the next video where we will discuss back testing and performance checks.
