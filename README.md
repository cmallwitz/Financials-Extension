# Financials-Extension

This is a Python based extension for LibreOffice Calc to make stock market, index and FX data available in Calc 
spreadsheets - currently supporting Yahoo's and Financial Times' finance websites using old-fashioned web scraping. 

Starting with version 3.1.0, we received a contribution to get crypto data directly from Coinbase

### Feedback requested:

Please provide feedback about using the extension [here](https://github.com/cmallwitz/Financials-Extension/issues/10)

### Usage:

Under 'Releases' on GitHub [there](https://github.com/cmallwitz/Financials-Extension/releases) is a downloadable **Financials-Extension.oxt** file - load it into Calc 
under menu item: Tools, Extension Manager...

Please make sure, not to rename the OXT file when downloading and before installing: LO will mess up the installation otherwise and the extension won't work.

Getting data should be as simple as having this in a cell: 
- `=GETREALTIME("IBM",21,"YAHOO")`
- `=GETREALTIME("IBM:NYQ",21,"FT")`
- `=GETREALTIME("EURUSD","LAST_PRICE","FT")`
- `=GETHISTORIC("IBM",90,"2020-12-01","YAHOO")`
- `=GETREALTIME("ETH-USD","LAST_PRICE","COINBASE")`

Codes 21 and 90 stand for "last price" and "close" (see below), respectively. 
Only Yahoo has historic data available.

There is a file **examples.ods** there too with usage examples and possible arguments to functions.

You have to check the respective websites to work out what symbol is the right one for you. If a website doesn't have 
the symbol/asset you want, this extension can't help you either. Having said that, I mostly look at US and West European 
equities, ETFs and mutual funds and major FX rates - if you have issues with the data available for other assets or 
assets in other regions, drop me a line (best to include full URLs and possibly the same asset listed on more than one 
site for comparison). While data for last price is most likely consistent across sites, they may differ for other data 
points.     

List of example URLs for checking symbols. You can start from these and search for other symbols. If you think some data
is available on the website but not from the extension, a good place to start when raising an issue is to include a similar 
URL to compare results.

| Website  | Symbol  | Example URL for Vodafone Group Plc UK                            |
|:---------|:--------|:-----------------------------------------------------------------|
| YAHOO    | VOD.L   | https://finance.yahoo.com/quote/VOD.L                            |
| FT       | VOD:LSE | https://markets.ft.com/data/equities/tearsheet/summary?s=VOD:LSE |
| COINBASE | ETH-EUR | https://api.exchange.coinbase.com/products/ETH-EUR/stats         |

### LibreOffice: using , (comma) vs ; (semicolon) to separate arguments in formula

There is a setting in "Tools" / "Options..." / "LibreOffice Calc" / "Formula" called "Functions". Here the user can specify the character used to separate arguments in formula.

Mine is set to , (comma) - when I enter ; (semicolon) in a formula (Ubuntu / UK English), no error is reported but the semicolon is converted to , (comma)

Depending on your system's language and default LibreOffice settings, you maybe better off using ; instead of , in your formulas.

### List of supported data points

You can either specify numbers or names (lower or upper case) - not all bits are available from all sources, and they are not necessarily consistent across sources either.

| Name                 | Code |      YAHOO       | FT  | YAHOO (historic) | COINBASE |   Notes    |
|:---------------------|:-----|:----------------:|:---:|:----------------:|----------|:----------:|
| PREV_CLOSE           | 5    |       Yes        | Yes |||
| OPEN                 | 6    |       Yes        | Yes |       Yes        | Yes      ||
| CHANGE               | 7    |       Yes        | Yes |||
| LAST_PRICE_DATE      | 8    |       Yes        | Yes |                  |          | yyyy-mm-dd |
| LAST_PRICE_TIME      | 10   |       Yes        | Yes |||
| CHANGE_IN_PERCENT    | 11   |       Yes        | Yes |||
| LOW                  | 14   |       Yes        | Yes |       Yes        | Yes      ||
| HIGH                 | 16   |       Yes        | Yes |       Yes        | Yes      ||
| LAST_PRICE           | 21   |       Yes        | Yes |                  | Yes      |
| BID                  | 22   |       Yes        | Yes |||
| ASK                  | 25   |       Yes        | Yes |||
| HIGH_52_WEEK         | 24   |       Yes        | Yes |||
| LOW_52_WEEK          | 26   |       Yes        | Yes |||
| MARKET_CAP           | 27   |       Yes        | Yes |||
| BIDSIZE              | 30   |       Yes        | Yes |||
| ASKSIZE              | 31   |       Yes        | Yes |||
| VOLUME               | 35   |       Yes        | Yes |       Yes        | Yes      ||
| AVG_DAILY_VOL_3MONTH | 39   |       Yes        | Yes |||
| BETA                 | 67   |       Yes        | Yes |||
| EPS                  | 68   |       Yes        | Yes |||
| PE_RATIO             | 69   |       Yes        | Yes |||
| DIV                  | 70   |       Yes        | Yes |||
| DIV_YIELD            | 71   |       Yes        | Yes |||
| EX_DIV_DATE          | 72   |       Yes        | Yes |                  |          | yyyy-mm-dd |
| PAYOUT_RATIO         | 73   |       Yes        | No  |||
| EXPIRY_DATE          | 74   | Yes (on options) | No  |                  |          | yyyy-mm-dd |
| SHARES_OUT           | 75   |       Yes        | Yes |                  |          ||
| FREE_FLOAT           | 76   |       Yes        | Yes |                  |          ||
| CLOSE                | 90   |        No        | No  |       Yes        |          ||
| ADJ_CLOSE            | 91   |        No        | No  |       Yes        |          ||
| SECTOR               | 98   |       Yes        | Yes |||
| INDUSTRY             | 99   |       Yes        | Yes |||
| TICKER               | 101  |       Yes        | Yes |                  | Yes      |
| EXCHANGE             | 102  |       Yes        | No  |||
| CURRENCY             | 103  |       Yes        | Yes |                  | Yes      |
| NAME                 | 104  |       Yes        | Yes |||
| TIMEZONE             | 105  |       Yes        | Yes |||

### Dealing with missing data:

A hint for using LibreCalc: if you want to refresh data you can press SHIFT-CTRL-F9 - this will force a 
recalculation of all formulas in all sheets. 

Secondly the extension saves some debug information under your user directory in a directory ".financials-extension": 
the HTML for each stock symbol is saved in a separate file (depending on the source and ticker symbol). You can open it 
your favorite web browser (or other tools) to check if the page actually contained the information you are looking for. 
If it does, the file trace.log has a record of all calls to the extension with the value returned to LibreOffice. 
Otherwise, the file extension.log in the same location might have more details about errors or exceptions.  

In general, web scraping can't be compared to using a stable API - the websites might have issues - from a technical or
data perspective. I have found especially on the weekend it can sometimes be "flaky" and closing/reopening LibreCalc can 
refresh things. 

### Build:

You will need the LibreOffice SDK installed. 

On my system (Ubuntu) I installed packages: libreoffice-dev libreoffice-java-common libreoffice-script-provider-python

\# depending on your location...

cd ~/tech/IdeaProjects/Financials-Extension/

python3 -m unittest discover src

\# This builds file **Financials-Extension.oxt**

./compile.sh

### Tested with:
- Windows 10 / LibreOffice Calc 7.1.2.2 / Python 3.8.8
- Ubuntu 20.04.5 / LibreOffice Calc 6.4.7.2 / Python 3.8.10
- MacOS 10.15.7 / LibreOffice Calc 7.2.0.4 / Python 3.8.10

(Previous versions)
- Debian 10.3  / LibreOffice Calc 6.1.5.2 / Python 3.7.3
- Ubuntu 20.10 / LibreOffice Calc 7.0.3.1 / Python 3.8.6
- Ubuntu 19.10 / LibreOffice Calc 6.3.5.2 / Python 3.7.6
- Ubuntu 19.04 / LibreOffice Calc 6.2 / Python 3.7.3
- Ubuntu 18.04.5 / LibreOffice Calc 6 / Python 3.6.9
- Ubuntu 18.04 / LibreOffice Calc 6 / Python 3.6.7
