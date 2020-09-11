# Financials-Extension

Extension for LibreOffice Calc to make stock market, index and FX data available in a Calc spread 
sheet - currently supports Yahoo's, Financial Times' and Google's (without FX data) finance web sites using web scraping.

### System dependencies:

Requires the following Python 3 (used by LibreOffice) packages (on top of standard libs): dateutil, pytz, pyparsing 

The following steps have worked for me on a fresh Debian installation (as root)
- apt install python3-pip
- pip3 install python-dateutil
- pip3 install pytz
- pip3 install pyparsing

### Usage:

Have a look at the 'releases' tab above: download a prebuild **Financials-Extension.oxt** file and load it into Calc 
under menu item: Tools, Extension Manager...

There is a file **examples.ods** there too with usage examples and possible arguments to functions.

You have to check the respective web sites to work out what symbol is the right one for you. If a web site doesn't have 
the symbol/asset you want, this extension can't help you either. Having said that, I mostly look at US and West European 
equities, ETFs and mutual funds and major FX rates - if you have issues with the data available for other assets or 
assets in other regions, drop me a line (best to include full URLs and possibly the same asset listed on more than one 
site for comparison). While data for last price is most likely consistent across sites, they may differ for other data 
points.     

### List of supported data points

You can either specify numbers or names (lower or upper case) - not all bits are available from all sources and they are not necessarily consistent across sources either.

|Name|Number|Yahoo|FT|Google|
| :--- | :--- | :---: | :---: | :---: |
|PREV_CLOSE|5|Yes|Yes|Yes|
|OPEN|6|Yes|Yes|Yes|
|CHANGE|7|Yes|Yes|Yes|
|LAST_PRICE_DATE|8|Yes|Yes|Yes|
|LAST_PRICE_TIME|10|Yes|Yes|Yes|
|CHANGE_IN_PERCENT|11|Yes|Yes|Yes|
|LOW|14|Yes|Yes|Yes|
|HIGH|16|Yes|Yes|Yes|
|LAST_PRICE|21|Yes|Yes|Yes|
|HIGH_52_WEEK|24|Yes|Yes|Yes|
|LOW_52_WEEK|26|Yes|Yes|Yes|
|MARKET_CAP|27|Yes|Yes|Yes|
|VOLUME|35|Yes|Yes|No|
|AVG_DAILY_VOL_3MONTH|39|Yes|Yes|No|
|BETA|67|Yes|Yes|No|
|EPS|68|Yes|Yes|No|
|PE_RATIO|69|Yes|Yes|No|
|DIV|70|Yes|Yes|No|
|DIV_YIELD|71|Yes|Yes|No|
|EX_DIV_DATE|72|Yes|Yes|No|
|PAYOUT_RATIO|73|Yes|No|No|
|CLOSE|90|(historic)|No|No|
|ADJ_CLOSE|91|(historic)|No|No|
|SECTOR|98|Yes|Yes|No|
|INDUSTRY|99|Yes|Yes|No|
|TICKER|101|Yes|Yes|Yes|
|EXCHANGE|102|Yes|No|Yes|
|CURRENCY|103|Yes|Yes|Yes|
|NAME|104|Yes|Yes|Yes|
|TIMEZONE|105|Yes|Yes|Yes|

### Dealing with missing data:

First of all, a hint for using LibreCalc: if you want to refresh data you can press SHIFT-CTRL-F9 - this will force a 
recalculation of all formulas in all sheets. 

Secondly the extension saves some debug information under your user directory in a directory ".financials-extension": 
the HTML for each stock symbol is saved in a separate file (depending on source and ticker symbol). You can open it 
your favorite web browser (or other tools) to check if the page actually contained the information you are looking for. 
If it does the file trace.log has a record of all calls to the extension and the value returned to LibreOffice.  

### Build:

You will need the LibreOffice SDK installed. 

On my system I installed packages: libreoffice-dev libreoffice-java-common libreoffice-script-provider-python

\# depending on your location...

cd ~/tech/IdeaProjects/Financials-Extension/

python3 src/test_yahoo.py

python3 src/test_google.py

\# This builds file **Financials-Extension.oxt**

./compile.sh

### Tested with:
- Debian 10.3  / LibreOffice Calc 6.1.5.2 / Python 3.7.3
- Ubuntu 20.04 / LibreOffice Calc 6.4.3.2 / Python 3.8.2
- Ubuntu 19.10 / LibreOffice Calc 6.3.5.2 / Python 3.7.6
- Ubuntu 19.04 / LibreOffice Calc 6.2 / Python 3.7.3
- Ubuntu 18.04 / LibreOffice Calc 6 / Python 3.6.7
- Ubuntu 16.04 / LibreOffice Calc 5 (previous versions)
