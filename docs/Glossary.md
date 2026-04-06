# Glossary
## A
### Alpha
An Alpha is defined by WorldQuant as a mathematical model that seeks to predict the future price movements of various financial instruments. See articles on the Alphas page.

 

### Alpha list
Alpha list is a tool to compare your Alphas and check the correlation of those Alphas with each other. You can add your Alphas to a list using 'Alpha to list' and 'Alpha lists' tools available on the Alphas page and Simulate page in the right upper corner. The same tool allows comparing PnL graphs of Alphas of the same list.

### ATOM (Available for Consultants only)
An Alpha created on a single dataset with relaxed submission checks.

[ATOM webinar (Oct 2024)](https://support.worldquantbrain.com/hc/en-us/community/posts/26969724290327-Opportunity-Webinar-Oct-2024-ATOM-7-Oct-2024)

## B
### Backfill
Replace missing values in the underlying data. See Documentation/Operators to read about kth_element and group_backfill operators.

### Backtesting
Backtesting refers to the process of testing a model (or Alpha) on historical data. See Parameters in the Simulation results page to read about In-Sample and Out-of-Sample simulation.

### Background check
We use the background check to verify that a person is who he/she claims to be and to comply with various applicable laws and regulations across countries related to the engagement of consultants. See Why is background check important? What happens in the background check?

### Base payment (accrued daily)
Base payment (accrued daily) (or base fees, as more fully described in your consulting agreement) is the amount you are eligible to earn for the Alphas and/or SuperAlphas you submit each day. See What is a periodic payment? How is it calculated? and FAQ/Compensation for more details.

### Bollinger Band
Bollinger bands are composed of three lines. One of the more common calculations of Bollinger Bands uses a 20-day SMA for the middle band. The upper band is calculated by taking the middle band and adding the daily standard deviation to that amount. The lower band is calculated by taking the middle band minus the daily standard deviation.

### Booksize
Booksize refers to the amount of capital (money) used to trade during the simulation. The Booksize used on the platform is constant and is set to $20 million every day throughout the simulation. Simulated profit is not reinvested, and simulated losses are replaced by cash injection into the portfolio. See Simulation results page for details on Alpha simulation results.

## C
### Capacity
Refers to the maximum amount of capital that can be allocated to an Alpha before its marginal profitability (PnL from allocating another dollar) falls below some desired level.

### Capitalization
Daily market capitalization (commonly referred to as market cap) is the total market value of a company's outstanding shares of stock. To calculate the market cap for a given company, multiply the total number of outstanding shares by the market price of a share. Cap is a data field of Price-Volume-Dataset.

Combination expression (Available for Consultants only)
It is the expression used to combine the Alphas selected using the selection expression in a SuperAlpha. The output of the combo expression is a set of daily weights for each of the selected Alphas. 

Consultant
WQBrain consultant is an independent contractor part-time flexible position that offers individuals the ability to provide services (in the form of Alphas) to WorldQuant from anywhere within their respective country and at their own schedule. Consultants develop Alphas (as defined above) that may be used in WorldQuant's strategies deployed from licensed trading locations.

Correlation
Correlation measures the uniqueness of an Alpha. Please see Documentation/Alpha Submission and FAQ for more details.

Coverage
Coverage refers to the fraction of the total instruments present in the universe for which the given datafield has a defined value. Low coverage fields can be handled by making use of backfill operators like ts_backfill, kth element, group_backfill, etc. Make use of the visualization feature to analyze the coverage of the data fields. Read this BRAIN Forum Post to know more about coverage handling.

D
Data field
A named collection of data, which has constant type and business meaning. For example, 'open price' is of constant type (numeric), and it consistently means the price of a security at the starting time of the trading period. 'Close price' has the same type as 'open price', but it’s a different field as it differs in business meaning.

Dataset
A source of information on one or more variables of interest for the WorldQuant investment process. A collection of data fields. For example: “price volume data for US equities” or “analyst target price predictions for US equities". See Datasets. 

Dataset Value Score (available for consultants only)
Dataset Value Score is a measure which signifies underutilization of a dataset. Consultants are advised to research and make Alphas using datasets with a higher value score. Don't confuse this with Value Factor.

Decay
Sets input data equal to a linearly decreasing weighted average of that data over the last selected number of days.

Delay
An option in Alpha settings: Delay=1 Alphas trade in the morning using data from yesterday; Delay=0 Alphas trade in the evening using data from today.

Dividend
A distribution of a portion of a company’s earnings, decided by the board of directors, paid to a class of its shareholders.

Drawdown
Drawdown is the largest reduction in PnL during a given period, expressed as a percentage. It is calculated as follows: find the largest peak to trough gap in PnL, and divide its dollar amount by half of booksize (or $10 million). See Simulation results for details on Alpha simulation results.

F
Fast Expression
Fast expression or BRAIN expression is a proprietary programming language used by WorldQuant BRAIN that is designed to have ease in writing and testing financial models. It provides a clear and concise way to express complex ideas and algorithms that can be easily understood by other developers and researchers. Read the documentation on Fast Expression to know more about its syntax and usage.

Financial ratio
Financial ratios are created with the use of numerical values taken from financial statements to gain meaningful information about a company. The numbers found on a company’s financial statements – balance sheet, income statement, and cash flow statement – are used to perform quantitative analysis and assess a company’s liquidity, leverage, growth, margins, profitability, rates of return, valuation, and more. Please refer here for more details *) and watch video (4 min) about financial ratios.

Fitness
Fitness is defined in the Alpha Performance help page: Fitness = Sharpe * sqrt(abs(Returns) / Max(Turnover,0.125)).

Fundamental analysis
Fundamental analysis is a method of measuring a security's intrinsic value by examining related economic and financial factors. Fundamental analysts study anything that can affect a security's value, from macroeconomic factors such as the state of the economy and industry conditions to microeconomic factors like the effectiveness of the company's management. Please refer here for more details *).

G
Genius (Available for Consultants only)
A leveled system for WorldQuant BRAIN consultants that provides increasing access to data, tools, and opportunities based on performance and activity levels. There are four levels: Gold (default level for new BRAIN consultants), Expert, Master, and Grandmaster.

[BRAIN Genius Program](https://support.worldquantbrain.com/hc/en-us/articles/26715715449239-What-is-the-BRAIN-Genius-Program)

Group
Type of field which has information about instrument segregation into various groups. They are supposed to be used as an input to the group operator. Some grouping type fields are industry, subindustry and sector

Grouping Field
Grouping data fields are: country, exchange, currency, market, sector, industry and subindustry.
Grouping data fields are counted in genius tie breaker criteria: # data fields per alpha, # total data fields. That is, they are treated as any other data field.
They are not counted (aka not penalized) in # genius pyramids, single dataset (Atom) alphas, dataset themes or Power Pool Alphas. That is, you can use grouping fields without affecting your score or submission criteria.

I
Illiquid Universe (Available for Consultants only)
An illiquid universe refers to the collection of instruments associated with low liquidity. Such a universe is subjected to lower trading volumes and is generally associated with higher transaction costs.

Industry
An industry is a group of companies that are related based on their primary business activities. Industry classifications are typically grouped into larger categories called sectors. Please refer here for more details *).

Information ratio
Information ratio (IR) measures the potential predictive ability of a model. In the BRAIN platform, it is defined as the ratio of a simulated portfolio’s mean daily returns to the volatility of those returns. Please watch video (7 min) on simulation results and see Documentation/Alpha Performance for details.

In-sample (IS)
In-sample performance of an Alpha is the performance obtained from backtesting on historical data. This is the performance you see on the results page when simulating an Alpha. See Documentation for Alphas page and IS, Semi OS and OS for details.

Instrument
Instrument is a financial term for any tradeable security (stocks, futures, currencies, bonds, ETFs, options, etc.). Please refer to FAQ and Financial Instruments wiki for more details *).

 

Investability (Available for Consultants only)
Investability Constraints ensure that the positions taken by an Alpha are within the liquidity limits of the instruments. This helps avoid significant market impact, which can negatively affect the Alpha’s profitability. An Alpha that performs well under Investability Constraints will potentially have higher capacity and liquidity.

[Investability constrained metrics](https://platform.worldquantbrain.com/learn/documentation/advanced-topics/getting-started-investability-constrained-metrics)

IS Ladder (available for consultants only)
The IS Ladder test checks if Sharpe over the most recent years are consistently above respective minimum thresholds. It is one of the statistical significance tests to reduce the possibility of false positive random signals. Check Documentation for details.

K
Kurtosis
Kurtosis is the fourth central standardized moment of time-series vector X. For time-series vector X values distribution, kurtosis could be treated as a measure of how heavy or how thin the tails of the distribution are. Please see Operators description for more details about ts_kurtosis(x, d) operator.

L
Liquidity
Liquidity describes the ease with which an asset or security can be bought or sold in the market without affecting its price significantly. WorldQuant BRAIN provides different universes classifying instruments on the basis of their liquidity, with smaller universes being more liquid. 

Leaderboard
The Leaderboard page for WorldQuant Challenge lists out the ranks of the participants based on their overall score. Please see Documentation for more details. Consultant Leaderboard is available for BRAIN consultants only.

Labs (available for consultants only)
BRAIN Labs is a new feature accessible to only consultants which allows you to interact with the platform through coding. With the help of BRAIN Labs, you can access data field values and visualize distributions across instruments, time & groups, using popular Python libraries. You can also build models, test ideas and replicate BRAIN operators to study Alpha weights.

Long-short neutral
Long-short neutral strategy is commonly used by hedge funds globally. This involves allocating an equal dollar amount to long positions and short positions. This type of strategy can then profit from a change in the spread between stocks. You have also minimized exposure to the market in general, i.e. the ability of this strategy to make a profit is not directly tied to the direction of the market (either up or down). Please watch video (4 min) 'What is an Alpha' for more details.

M
Margin
Margin is the profit per dollar traded; calculated as PnL divided by total dollars traded for a given period. See Simulation results for details on Alpha simulation results.

Market capitalization
The total dollar market value of a company’s outstanding shares.

Matrix
Basic type of field which has just one value of every date and instrument. There is no special syntax for using this in simulation. Some examples of matrix fields are close, returns, cap.

Matrix Data field
Has one value on one day for one security. Two dimensional structure. E.g. Only one open price of ‘Google’ on 1 Jan

Max Trade (Available for Consultants only)
A feature designed to enhance the liquidity and scalability of the Alphas. It limits the daily position changes of instruments based on a fraction of their 20-day average daily volume (adv20). This ensures that the Alphas adjust positions less frequently in illiquid instruments, which can significantly reduce turnover and improve the Sharpe ratio of the sub-universe.

[Consultant features: Max Trade](https://platform.worldquantbrain.com/learn/documentation/consultant-information/consultant-features)

Mean-reversion
Refer to Reversion.

Median
The median is the middle number in a sorted, ascending or descending, list of numbers and can be more descriptive of that data set than the average. Please refer here for details *).

Momentum
In financial markets, momentum refers to the empirical observation that asset prices that have been rising recently are likely to rise further and vice versa. Within the framework of the efficient market hypothesis, momentum is one of the market anomalies based on return autocorrelations (along with reversion, seasonality, momentum reversal) that originate from the fact that investors’ immediate reactions may be improper and tend to adjust over time.

N
NaN
NaN stands for 'Not a Number'. It is used to indicate results of ‘invalid’ operations like division by zero or if some data is unavailable. Please see Documentation for NaN handling in simulation setting and FAQ for details.

Net weight (available for consultants only)
Refers to the contribution of Alphas to the strategy.

Neutralization
Neutralization helps to reduce the risk by making strategies long-short market neutral.

On the BRAIN platform, to neutralize an Alpha, the raw Alpha values are split into groups, and then neutralized within each group - the mean is subtracted from each value. In theory, there are other ways of neutralization as well (for example, orthogonalization).

Watch Video (4 min long) about long-short market neutral strategy. Check Documentation/Neutralization and FAQ for details.

O
Operator
Operator is a set of mathematical or statistical techniques required to implement your Alpha ideas. Read Learn/Operators for more details.

Out-of-sample (OS)
Out-sample performance of an Alpha is the performance after its date of submission. It is the ‘real world’ performance on Alpha. See Documentation Alphas page and IS, Semi OS and OS for details.

Outstanding shares
Company stock currently held by all shareholders. Includes shares held by institutional investors and restricted shares owned by the company’s officers and insiders.

Osmosis (available for consultants only)
Osmosis is a competition feature in the BRAIN platform where consultants tag their most unique and pure Alpha submissions using "Osmosis points" to indicate confidence levels. These points are assigned through the Properties section and are used to weight Alphas in regional combo portfolios (USA, ASI, EUR, GLB, IND), with participants judged on the combined performance of their tagged Alphas to optimize overall combo results.

Overfitting
Overfitting here refers to changing the Alpha expression slightly in a nonsensical way, just to get a good IS Sharpe; e.g.: slightly changing the constants in the expression, changing the power of a parameter from 2 to 2.5, static flip sign of some sectors etc. This shouldn’t be done since it will inevitably fail the OS test constraints. Please watch video (6.5 min long) "How to Avoid Overfitting" and see FAQ Alpha Performance for details.

P
Pasteurization
Pasteurization replaces input values with NaN (pasteurizes) for instruments not in the Alpha universe. When Pasteurize = ‘On’, inputs will be converted to NaN for instruments not in the universe selected in Simulation Settings. When Pasteurize = ‘Off’, this operation does not happen and all available inputs are used. Please see Simulation setting for details and FAQ for examples.

Periodic payment
Refer to Base payment.

Prod
Refers to production status. Only PROD Alphas, which are created and submitted only by BRAIN consultants, are available for use by WorldQuant in its investment strategies.

Prod correlation
This correlation metric is determined by the Maximum Pearson correlation coefficient from comparing a given Alpha to all other Alphas submitted by all BRAIN consultants.

Profit and Loss (PnL)
Profit and Loss (PnL) is the money that the positions and trades generate based on the simulation of an Alpha (which means it is the amount of money lost made or made lost during the year), expressed in dollars.

```
daily_PnL = sum of (size of position * daily_return) for all instruments,
where daily return per instrument = (today’s close / yesterday’s close) – 1.0
```

See Simulation results page for details on Alpha simulation results.

Power Pool Alphas (available for consultants only)
Power Pool Alphas are streamlined, high-quality Alphas in the BRAIN platform designed to excel in Genius, competitions, and thematic challenges. They must meet specific eligibility criteria including a Sharpe ratio of at least 1.0 and limited unique operators and data fields. Consultants can submit up to 10 pure Power Pool Alphas monthly after three months of initial submission.

Pyramid (available for consultants only)
A combination of region, delay, and dataset category. E.g. USA-D1-analyst. A consultant is considered to formulate a pyramid if they have submitted a minimum of 3 Alphas in it. A single Alpha can belong to multiple pyramids as it could have multiple data fields.

[What are pyramids?](https://support.worldquantbrain.com/hc/en-us/articles/26716012806295-What-are-pyramids)

Q
Quarterly payment
Quarterly payment is an additional amount consultants may earn for the submission of their Alphas and SuperAlphas in each quarter. Read this article and refer to your respective consulting or service agreement for more details.

R
Rank
Rank the values of the input X among all instruments. The return values are float numbers equally distributed between 0.0 and 1.0. Watch video (8 min long) about Rank Operator, see FAQ and Data & Operators for details.

Region
Set of instruments based on common geography, trading hours, and other attributes.

The only region currently available to all BRAIN platform users is the US market. The regions Europe and Asia are currently available only to our BRAIN consultants. Watch video (4 min long) on simulation setting and see Documentation/Simulation Setting for details.

Regression
Regression is a statistical measure to determine the strength of the relationship between two or more variables and forecast their future value. A regression idea can be tested in BRAIN by Ts_regression function.

Relative Strength Index
The relative strength index (RSI) is a momentum indicator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions in the price of stock or other asset.

The RSI is displayed as an oscillator (a line graph that moves between two extremes) and can have a reading from 0 to 100.

Returns
Returns mean the return on capital traded: Annual Return = Annualized PnL / Half of Book Size. It signifies the amount made or lost during the period observed in the simulation of an Alpha and is expressed in %. See Simulation results page for details on Alpha simulation results.

Reversion
Mean reversion is an analytical method based on the assumption that a stock's price will tend to move to its historical average price over time. See Documentation/Alpha Research Concept for more details.

Risk Factors (Available for Consultants only)
Risk factors are specific variables that systematically influence the expected return and volatility of an asset or portfolio, potentially leading to financial losses. These factors encompass a wide range of systematic (market-wide) and unsystematic (specific to an asset or issuer) elements, including market, liquidity, industry, and style risks. WorldQuant BRAIN provides risk factors neutralization in 3 modes: 1) Slow Factors, 2) Fast Factors and 3) Slow+Fast Factors. 

Risk-neutralized Alpha (Available for Consultants only)
Risk-neutralized Alphas are Alphas that show orthogonal and unique returns after accounting for market, industries and style factors. By controlling an Alpha for a broad set of common risk factors, its resulting return more accurately reflects the Alpha's intended capture, minimizing exposure to undesired risk factors. 

Robustness
Alpha performance shall be robust under different scenarios (robust performance among super/sub universe, have performance if ported to other regions, etc.)

S
Sector
A sector is an area of the economy in which businesses share the same or related business activity, product, or service. Sectors represent a large grouping of companies with similar business activities, such as the extraction of natural resources and agriculture. Please refer here for more details *).

Selection expression (for Consultants only)
Choose which Alphas to include in your SuperAlpha. The expression ranks all the Alphas according to the conditions specified in the expression and chooses the highest ranked Alphas according to the SuperAlpha settings. 

Self correlation
This correlation metric is determined by the maximum Pearson correlation coefficient from comparing a given Alpha to all other Alphas submitted by the same user.

Checks the correlation of your Alpha with the rest of your OS Alphas. If an Alpha is uncorrelated, then it passes the self-correlation test. Otherwise, only one out of a group of highly correlated Alphas passes the test. See FAQs/OS and IS Sharpe for details.

Semi Out-of-sample (semi OS)
The time period from end of IS simulation period to the date the Alpha was submitted is referred to as Semi-OS. See Documentation/IS, Semi-OS, and OS for details.

Sharpe ratio
This is a common mathematical ratio used to analyze an investment’s performance by measuring its risk-adjusted returns, and it is calculated as follows:

```
Sharpe = IR * Sqrt(252)
IR = Avg(PnL) / Std_dev(PnL)
```

See Simulation results page for details on Alpha simulation results.

Signal
Any elementary model which upon backtesting shows the potential for a possible Alpha. An informal word that does not have a rigorous definition.

Simple moving average
Simple moving average (SMA) is an arithmetic moving average calculated by adding recent closing prices and then dividing that by the number of time periods in the calculation average.

```
SMA = (A1 + A2 + ... + An) / n
```

where `An` is the price of an asset at period `n`, and `n` is the number of total periods

Simulation
Simulation means submitting your Alpha idea for backtesting. 

Skewness
Skewness is the third central standardized moment of time-series vector X. In probability theory and statistics, skewness is a measure of the asymmetry of the probability distribution of a real-valued random variable about its mean. The skewness value can be positive or negative, or even undefined. Please refer Detailed operator descriptions for details on skewness.

Standard Deviation
Standard deviation is a statistical measure that quantifies the amount of variation or dispersion in a set of data values. It indicates how much individual data points in a datafield deviate from the datafield's mean (average) value. A low standard deviation means that the data points tend to be close to the mean, while a high standard deviation indicates that the data points are spread out over a wider range of values. 

Statistical arbitrage
It's impossible to predict one stock's future return. Statistical arbitrage is an investment methodology that utilizes mean reversion to analyze a large universe of diverse stocks. This analytical approach to trading aims to reduce exposure to beta as much as possible. Hence, one stock error because of noisy data, calculation error, etc. will not hurt the whole performance.

Stochastic oscillator
Stochastic oscillator is a technical indicator to capture spikes in the price volume data. It can be used as an efficient mean reversion indicator as well.

Calculation:

```
%K = (Current close - Lowest low) / (Highest high - lowest low) * 100
%D = 3-Day SMA of %K
Lowest low = lowest low for the lookback period
Highest high = highest high for the lookback period
%K is multiplied by 100 to move the decimal point two places
```

Stock split ratio
A corporate action in which a company divides its existing shares into multiple shares to boost the liquidity of the shares.

Strategy
Investment Strategy - algorithm that computes portfolio positions based on data with the goal of gaining PNL. Investment strategies are created by Portfolio Managers in licensed trading location by combining Alphas and SuperAlphas. 

Subindustry
Sub-industry is the smallest classification bucket in the GICS system. Please refer here for details *).

Submission
The 'Submit' button is used to start Out-of-Sample (OS) testing for Alphas meeting the performance and correlation cutoffs. Read Documentation/Alpha submission for details.

Sub-universe test
The Sharpe of the Alpha in the next lower universe should follow the below criteria: 

```
Delay 1: Sqrt(252) * Max(0.065, sqrt(subuniverse_size / largest_universe_size) * 0.15)
Delay 0: Sqrt(252) * Max(0.1,   sqrt(subuniverse_size / largest_universe_size) * 0.25)
```

Watch video (8.5 min long) "OS-Tests in an Alpha" and check Documentation/Alpha Submission for more details.

SuperAlpha
SuperAlpha is a new feature in BRAIN designed to help consultants realize the power of combining many diverse signals. SuperAlpha gives you the power and flexibility to creatively manipulate and combine the Alphas you have already created and produce even stronger, more robust signals. 

Super-universe test
The Sharpe of Alpha in the next largest universe > 0.7*Sharpe of Alpha. Watch video (8.5 min long) "OS-Tests in an Alpha" for details.

T
Technical analysis
Technical analysis is a trading discipline employed to evaluate investments and identify trading opportunities by analyzing statistical trends gathered from trading activity, such as price movement and volume. Please refer here for details *).

Test Period
It is a simulation setting that lets users set the period for the Alpha idea to be tested upon. By setting the duration, the setting allows subset of PnL to be hidden as a validation period. 

Truncation
The maximum weight for each stock in the overall portfolio. When set to 0, there is no restriction. It aims to guard from being too exposed to movements in individual stocks. The recommended setting is between 0.05 and 0.1 (entailing 5-10%).

Ts-Zscore
Ts-Zscore is an operator: `Ts_Zscore(x, n) = (x - ts_mean(x, n)) / ts_std(x, n)`, where `x` is the data field and `n` is the number of days.

It is calculated by subtracting the mean input value over the past n days from today's input value, and then dividing by the expressing standard deviation of input value over the past n days. Watch video (6.5 min long) for more details.

Turnover
Average measure of daily trading activity: turnover signifies how often an Alpha simulates trades. It can be defined as the ratio of value traded to book size. `Daily Turnover = Dollar trading volume / Booksize`. Good Alphas tend to have lower turnover, since low turnover means lower transaction costs. See Simulation results page for details on Alpha simulation results.

U
Universe
Universe, within the BRAIN platform, is a set of trading instruments provided by the BRAIN platform. For example, "US: TOP3000" represents the top 3000 most liquid stocks in the US market. Please see FAQ for more details.

V
Value Factor (available for consultants only)
Value Factor captures the effect of recent Alpha submissions on the performance of a combination of your Alphas taking into account three particular elements: (a) the Alpha’s individual performance, (b) the diversity of recent Alpha submissions, and (c) the uniqueness of submissions as compared to your past submissions and those of other consultants.

Please note that value factor is related to payments for consultants while Dataset Value Score is related to the under-utilization of data.

Value Score (available for consultants only)
Value Score is a measure which signifies underutilization of a dataset. Consultants are advised to research and make Alphas using datasets with a higher value score. Don't confuse this with Value Factor.

Vector
Type of field which has more than one value for every date and instrument. Different type of reduce operators needs to be used to convert them into matrix fields.

Vector Data field
Can have any number of values on one day for one security. Number of values can vary across days. Three dimensional structure. E.g. Only 3 sentiment values on 1 Jan, but 1 value on 2 Jan

Visualization
Calculates additional, advanced metrics about Alpha performance; increases simulation time.

Volume
Volume signifies how many trades have taken place for that stock. You could google "Use of volume in stock market predictions" to understand how you can use it. There are many technical indicators based on volume that you can model your Alphas around.

VWAP
The volume-weighted average price (VWAP) is a trading benchmark calculated from price and volume by adding up the dollars traded for every transaction (price multiplied by number of shares traded) and dividing that by the total shares traded for the day.

W
Weight
BRAIN platform uses an Alpha to create a vector of weights, with each weight corresponding to one of the stocks in the selected universe. These weights may or may not be market neutralized, as per your neutralization setting (by market, industry, subindustry or none). This creates a portfolio for each day in the simulation period, which can then be used to calculate that day's Profit and Loss (PnL). Learn more about assigning weights.

Winsorize
Cross sectional operator used to limit the input values X between the lower and upper limits specified as multiples of standard deviations of the input data. Read wiki to know more.

Workday
Workday is our internal system designed for BRAIN consultant candidates to submit information and documentation related to the consultant onboarding process.

If you are eligible to become a BRAIN consultant, you will be asked to sign in to Workday to submit the documentation related to the consulting opportunity. For more details on Workday and next steps of consultant onboarding, refer to the following links: Consultant onboarding process explained in 12 images

WorldQuant
WorldQuant is a quantitative investment management firm founded in 2007 and currently has over 1,000 employees spread across 27 global offices. WorldQuant develops and deploys systematic financial strategies across a variety of asset classes in global markets, utilizing a proprietary research platform and risk management process. Discover more on WorldQuant.

WQ Brain
WQ BRAIN platform is a web-based tool for backtesting Alphas. Learn more about BRAIN.

 

*) The text on other websites can change without warning, so the external hyperlinks can get irrelevant
Z
Z-Score
A Z-score is a numerical measurement of a value’s relationship to the mean in a group of values. If a Z-score is 0, it means the score is equal to the mean.

Z-Score = (data - mean) / StdDev of x for each instrument within its group.

A Z-Score can be calculated in BRAIN by ts_zscore and group_zscore.

Zscore is a strong tool for comparing values.