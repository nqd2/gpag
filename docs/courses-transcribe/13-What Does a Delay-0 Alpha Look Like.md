# 13-What Does a Delay-0 Alpha Look Like

use volatility data, focusing on add-the-money implied volatility of call options expiring within 4 months and their Parkinson's volatility. Parkinson's volatility measures realized volatility using the high and low prices within a day. It captures large intraday price variations even when the previous day close and the current day close price change is small.

However, Alpha Idea captures call option demand using the implied volatility of its add-the-money call options expiring up to 4 months ahead, scaled by Parkinson's volatility over the past 4 months.

If the implied volatility to Parkinson's volatility ratio is high, the hypothesis is that we expect high future stock returns and vice versa.
