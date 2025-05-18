#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o noclobber

if [[ $OSTYPE == "darwin"* ]]; then
  echo MacOS
  # Assuming both are installed in the applications folder
  # Required some steps to make it work for MacOS M1, mind the `find` call which could return more than one (shouldn't)
  # install_name_tool -change @__VIA_LIBRARY_PATH__/libreglo.dylib $(find /Applications -name "libreglo.dylib") /Applications/LibreOffice7.4_SDK/bin/idlc
  # install_name_tool -change @__VIA_LIBRARY_PATH__/libuno_sal.dylib.3 $(find /Applications -name "libuno_sal.dylib.3") /Applications/LibreOffice7.4_SDK/bin/idlc
  # install_name_tool -change @__VIA_LIBRARY_PATH__/libuno_salhelpergcc3.dylib.3 $(find /Applications -name "libuno_salhelpergcc3.dylib.3") /Applications/LibreOffice7.4_SDK/bin/idlc
  # codesign --force -s - $(find /Applications -name "idlc")
  export PATH=$PATH:/Applications/LibreOffice7.4_SDK/bin
  export PATH=$PATH:/Applications/LibreOffice.app/Contents/MacOS
else
  export PATH=$PATH:/usr/lib/libreoffice/sdk/bin
  export PATH=$PATH:/usr/lib/libreoffice/program
fi

# Setup build directories

rm -rf "${PWD}"/build

mkdir "${PWD}"/build
mkdir "${PWD}"/build/META-INF/

# Compile the binaries

if command -v idlc &> /dev/null
then
  echo "Calling idlc..."
  idlc -w -verbose "${PWD}"/idl/XFinancials.idl

  echo "Calling regmerge..."
  regmerge -v "${PWD}"/build/XFinancials.rdb UCR "${PWD}"/idl/XFinancials.urd

  rm "${PWD}"/idl/XFinancials.urd
else
  # LibreOffice 7.4+
  export unoTypes=/usr/lib/libreoffice/program/types.rdb
  export offTypes=/usr/lib/libreoffice/program/types/offapi.rdb

  echo "Calling unoidl-write..."
  unoidl-write $unoTypes $offTypes "${PWD}"/idl/XFinancials.idl "${PWD}"/build/XFinancials.rdb
fi

echo "Generating meta files..."
python3 "${PWD}"/src/generate_metainfo.py

cp -f "${PWD}"/src/financials.py "${PWD}"/build/
cp -f "${PWD}"/src/datacode.py "${PWD}"/build/
cp -f "${PWD}"/src/baseclient.py "${PWD}"/build/
cp -f "${PWD}"/src/naivehtmlparser.py "${PWD}"/build/
cp -f "${PWD}"/src/tz.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_ft.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_yahoo.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_coinbase.py "${PWD}"/build/

# this copies python some modules to extension so they doesn't have to be installed by user

TMPFILE=`mktemp`

# https://pypi.org/project/python-dateutil/
wget "https://files.pythonhosted.org/packages/ec/57/56b9bcc3c9c6a792fcbaf139543cee77261f3651ca9da0c93f5c1221264b/python_dateutil-2.9.0.post0-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE dateutil/\* -d "${PWD}"/build/
rm $TMPFILE

# https://pypi.org/project/pytz/
wget "https://files.pythonhosted.org/packages/81/c4/34e93fe5f5429d7570ec1fa436f1986fb1f00c3e0f43a589fe2bbcd22c3f/pytz-2025.2-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE pytz/\* -d "${PWD}"/build/
rm $TMPFILE

# https://pypi.org/project/pyparsing/
# lastest version of "single-file" pyparsing 2.x - used by Ubuntu 22.04 as python3-pyparsing
wget "https://files.pythonhosted.org/packages/8a/bb/488841f56197b13700afd5658fc279a2025a39e22449b7cf29864669b15d/pyparsing-2.4.7-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE pyparsing.py -d "${PWD}"/build/
rm $TMPFILE

# https://pypi.org/project/six/
wget "https://files.pythonhosted.org/packages/b7/ce/149a00dd41f10bc29e5921b496af8b574d8413afcd5e30dfa0ed46c2cc5e/six-1.17.0-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE six.py -d "${PWD}"/build/
rm $TMPFILE

# https://pypi.org/project/requests/
wget "https://files.pythonhosted.org/packages/f9/9b/335f9764261e915ed497fcdeb11df5dfd6f7bf257d4a6a2a686d80da4d54/requests-2.32.3-py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE requests/\* -d "${PWD}"/build/
rm $TMPFILE

# https://pypi.org/project/urllib3/
# urllib3-2.2.3 is last version supporting Python 3.8 used by LibreOffice 7.1
wget "https://files.pythonhosted.org/packages/ce/d9/5f4c13cecde62396b0d3fe530a50ccea91e7dfc1ccf0e09c228841bb5ba8/urllib3-2.2.3-py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE urllib3/\* -d "${PWD}"/build/
rm $TMPFILE

# https://pypi.org/project/certifi/
wget "https://files.pythonhosted.org/packages/4a/7e/3db2bd1b1f9e95f7cddca6d6e75e2f2bd9f51b1246e546d88addca0106bd/certifi-2025.4.26-py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE certifi/\* -d "${PWD}"/build/
rm $TMPFILE

# https://pypi.org/project/idna/
wget "https://files.pythonhosted.org/packages/76/c6/c88e154df9c4e1a2a66ccf0005a88dfb2650c1dffb6f5ce603dfbd452ce3/idna-3.10-py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE idna/\* -d "${PWD}"/build/
rm $TMPFILE

echo "Package into oxt file..."
pushd "${PWD}"/build/
zip -r "${PWD}"/Financials-Extension.zip ./*
popd

mv "${PWD}"/build/Financials-Extension.zip "${PWD}"/Financials-Extension.oxt
