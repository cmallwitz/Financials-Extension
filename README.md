# Financials-Extension

Extension for LibreOffice Calc to make stock, index and FX (Yahoo only) market data available in a Calc spread sheet - currently supports Yahoo and Google using web scraping.

### System dependencies:

Requires the following Python 3 (used by LibreOffice) packages (on top of standard libs): dateutil, pytz, pyparsing 

The following steps have worked for me on a fresh Debian installation (as root)
- apt install python3-pip
- pip3 install python-dateutil
- pip3 install pytz
- pip3 install pyparsing

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
- Debian 10.3  / LibreOffice Calc 6.1.5.2 / Python 3.7.3
- Ubuntu 19.10 / LibreOffice Calc 6.3.5.2 / Python 3.7.6
- Ubuntu 19.04 / LibreOffice Calc 6.2 / Python 3.7.3
- Ubuntu 18.04 / LibreOffice Calc 6 / Python 3.6.7
- Ubuntu 16.04 / LibreOffice Calc 5 (previous versions)
