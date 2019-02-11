# Financials-Extension

Extension for LibreOffice Calc to make stock/FX market data available in spread sheet. Currently supports Yahoo and Google using web scraping.

Requires the following packages: python3-dateutil python3-pyparsing

Tested this with
- Ubuntu 16.04 and LibreOffice Calc 5
- Ubuntu 18.04 and LibreOffice Calc 6

To Build:

cd ~/tech/IdeaProjects/Financials-Extension/

python3 src/test_yahoo.py

python3 src/test_google.py

./compile.sh

