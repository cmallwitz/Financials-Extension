# Financials-Extension

Extension for LibreOffice Calc to make stock, index and FX (Yahoo only) market data available in a Calc spread sheet - currently supports Yahoo and Google using web scraping.

### System dependencies:

Requires the following Python 3 packages (on top of standard libs): python3-dateutil python3-pyparsing pytz

### Usage:

Have a look at the 'releases' tab above: download a prebuild **Financials-Extension.oxt** file and load it into Calc under menu item: Tools, Extension Manager...

There is a file **examples.ods** there too with usage examples and possible arguments to functions.

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
- Ubuntu 18.04 / LibreOffice Calc 6 / Python 3.6.7 (most recent version)
- Ubuntu 16.04 / LibreOffice Calc 5 (previous versions)
