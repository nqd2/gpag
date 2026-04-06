# 22-How Good is Your Alpha_ A Metrics-Based Approach

How good is your alpha? A metrics-based approach. I am Nitish Meni, the Chief Strategy Officer at WorldQuant. I help to define our firm's strategy as well as drive several cross-functional business initiatives, including new avenues for growth and innovation.

In this series, we help you develop your skills and capabilities by guiding you in testing out your ideas on WorldQuant Brain, our simulation platform. Before we begin, head to WorldQuant Brain and log in now, and I'll take you through some ideas on the platform. So far, we have explored the quant research ecosystem and the process of creating and implementing an alpha, which is defined by WorldQuant as a mathematical model that seeks to predict the future price movement of various financial instruments.

Now, let's move on to understanding how to assess the quality of the alpha itself.

Quant researchers can seek to provide expectations about future performance by exposing the particular alpha to a stream of historical financial data to generate its theoretical past performance. This backtesting process can help us determine whether the proposed approach might have resulted in gains or losses, what would have been the potential exposures, the maximum drawdown the alpha could have incurred, the returns generated, and the costs involved. Be careful to avoid look-ahead bias in backtesting, a common pitfall where future information accidentally influences the historical data analysis. The bias can inflate performance predictions, skew expectations, and potentially lead to losses.

Let's turn our attention to the variety of metrics that quants use to gauge the quality of an alpha. These metrics should be analyzed so we know what changes to implement and improve the predictability of the signal. The metrics can be related to performance, novelty, diversity, etc.

Let's look at the six performance related metrics on WorldQuant brain.

Sharp is the measure of risk-adjusted returns earned by the alpha. Higher values of sharp are better. Turnover is the percentage of the capital which the alpha trades each day. More turnover may mean higher transaction costs during trading.

Drawdown represents the percentage of the largest loss incurred during any year in your backtesting. As a practice, you should target a return to drawdown ratio greater than one, the higher the ratio of returns to drawdown, the better it may be for your alpha. Correlation of the alpha to other alphas in the pool should be low unless we see much higher performance as compared to the correlated alphas. The metrics to check if the performance is contributed by diverse set of stocks include a weight test and a sub-universe test.

Weight test, a robustness check to ensure alpha weight is evenly distributed across stocks not concentrated on a few. A sub-universe test checks if the alpha's performance in the immediate smaller set of tradable stocks or sub-universe exceeds a required threshold. The process of backtesting and performance check should be repeated until you are satisfied with the implementation and the performance of the idea and believe that the signal is good enough to be used in real markets. So in this video, we have reviewed the significance of backtesting, the need to avoid look ahead bias and we have also explored how to measure an alpha's quality using different metrics.

I hope that you are ready to take your knowledge to the next level. In the next videos, we will employ the alpha creation process in deeper ways and power up your quant research skills.

Let's go quant and see you in brain.
