#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o noclobber

export PATH=$PATH:/usr/lib/libreoffice/sdk/bin
export PATH=$PATH:/usr/lib/libreoffice/program

# Setup build directories

rm -rf "${PWD}"/build

mkdir "${PWD}"/build
mkdir "${PWD}"/build/META-INF/

# Compile the binaries

echo "Calling idlc..."
idlc -w -verbose "${PWD}"/idl/XFinancials.idl

echo "Calling regmerge..."
regmerge -v "${PWD}"/build/XFinancials.rdb UCR "${PWD}"/idl/XFinancials.urd

rm "${PWD}"/idl/XFinancials.urd

echo "Generating meta files..."
python3 "${PWD}"/src/generate_metainfo.py

cp -f "${PWD}"/src/financials.py "${PWD}"/build/
cp -f "${PWD}"/src/datacode.py "${PWD}"/build/
cp -f "${PWD}"/src/baseclient.py "${PWD}"/build/
cp -f "${PWD}"/src/jsonParser.py "${PWD}"/build/
cp -f "${PWD}"/src/naivehtmlparser.py "${PWD}"/build/
cp -f "${PWD}"/src/tz.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_ft.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_google.py "${PWD}"/build/
cp -f "${PWD}"/src/financials_yahoo.py "${PWD}"/build/

# this copies python modules dateutil, pytz, pyparsing to extension so it doesn't have to be installed by user

TMPFILE=`mktemp`

wget "https://files.pythonhosted.org/packages/d4/70/d60450c3dd48ef87586924207ae8907090de0b306af2bce5d134d78615cb/python_dateutil-2.8.1-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE dateutil/\* -d "${PWD}"/build/
rm $TMPFILE

wget "https://files.pythonhosted.org/packages/70/94/784178ca5dd892a98f113cdd923372024dc04b8d40abe77ca76b5fb90ca6/pytz-2021.1-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE pytz/\* -d "${PWD}"/build/
rm $TMPFILE

wget "https://files.pythonhosted.org/packages/8a/bb/488841f56197b13700afd5658fc279a2025a39e22449b7cf29864669b15d/pyparsing-2.4.7-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE pyparsing.py -d "${PWD}"/build/
rm $TMPFILE

# Windows LibreOffice 7.1 Python is missing this...
wget "https://files.pythonhosted.org/packages/ee/ff/48bde5c0f013094d729fe4b0316ba2a24774b3ff1c52d924a8a4cb04078a/six-1.15.0-py2.py3-none-any.whl" -O $TMPFILE
unzip $TMPFILE six.py -d "${PWD}"/build/
rm $TMPFILE

echo "Package into oxt file..."
pushd "${PWD}"/build/
zip -r "${PWD}"/Financials-Extension.zip ./*
popd

mv "${PWD}"/build/Financials-Extension.zip "${PWD}"/Financials-Extension.oxt
