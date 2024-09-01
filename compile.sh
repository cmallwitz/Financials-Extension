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
cp -f "${PWD}"/src/jsonParser.py "${PWD}"/build/
cp -f "${PWD}"/src/naivehtmlparser.py "${PWD}"/build/
cp -f "${PWD}"/src/tz.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_ft.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_yahoo.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_coinbase.py "${PWD}"/build/

# this copies python modules dateutil, pytz, pyparsing to extension so it doesn't have to be installed by user

TMPFILE=`mktemp`

wget "https://files.pythonhosted.org/packages/ec/57/56b9bcc3c9c6a792fcbaf139543cee77261f3651ca9da0c93f5c1221264b/python_dateutil-2.9.0.post0-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE dateutil/\* -d "${PWD}"/build/
rm $TMPFILE

wget "https://files.pythonhosted.org/packages/9c/3d/a121f284241f08268b21359bd425f7d4825cffc5ac5cd0e1b3d82ffd2b10/pytz-2024.1-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE pytz/\* -d "${PWD}"/build/
rm $TMPFILE

wget "https://files.pythonhosted.org/packages/8a/bb/488841f56197b13700afd5658fc279a2025a39e22449b7cf29864669b15d/pyparsing-2.4.7-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE pyparsing.py -d "${PWD}"/build/
rm $TMPFILE

# Windows LibreOffice 7.1 Python is missing this...
wget "https://files.pythonhosted.org/packages/d9/5a/e7c31adbe875f2abbb91bd84cf2dc52d792b5a01506781dbcf25c91daf11/six-1.16.0-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE six.py -d "${PWD}"/build/
rm $TMPFILE

echo "Package into oxt file..."
pushd "${PWD}"/build/
zip -r "${PWD}"/Financials-Extension.zip ./*
popd

mv "${PWD}"/build/Financials-Extension.zip "${PWD}"/Financials-Extension.oxt
