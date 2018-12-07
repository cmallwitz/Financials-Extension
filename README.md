# Financials-Extension

Extension for LibreOffice Calc to access stock market data. Currently supports Yahoo and Google.

Requires the following packages: python-dateutil python3-dateutil python3-pyparsing

Only tested this with
- Ubuntu 16.04 and LibreOffice 5
- Ubuntu 18.04 and LibreOffice 6

To Build:

cd ~/tech/IdeaProjects/Financials-Extension/

python3 src/test_yahoo.py

python3 src/test_google.py

./compile.sh

