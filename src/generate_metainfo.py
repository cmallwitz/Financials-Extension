#  generate_metainfo.py - Generate XML for Financials Extension
#  Based on template by jan@biochemfusion.com April 2009.
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#

import os

cur_dir = os.getcwd()

addin_id = "com.financials.getinfo"
addin_version = "3.6.1"
addin_displayname = "Financial Market Extension"
addin_publisher_link = "https://github.com/cmallwitz/Financials-Extension"
addin_publisher_name = "The Publisher"

print("Generating extension files for version", addin_version)


################################################################################
# description.xml

desc_xml = open(cur_dir + '/build/description.xml', 'w')

desc_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
desc_xml.write('<description xmlns="http://openoffice.org/extensions/description/2006" \n')
desc_xml.write('xmlns:d="http://openoffice.org/extensions/description/2006" \n')
desc_xml.write('xmlns:l="http://libreoffice.org/extensions/description/2011" \n')
desc_xml.write('xmlns:xlink="http://www.w3.org/1999/xlink"> \n' + '\n')
desc_xml.write('<dependencies> \n')
desc_xml.write('    <l:LibreOffice-minimal-version value="5.0" d:name="LibreOffice 5.0" /> \n')
desc_xml.write('</dependencies> \n')
desc_xml.write('\n')
desc_xml.write('<identifier value="' + addin_id + '" /> \n')
desc_xml.write('<version value="' + addin_version + '" />\n')
desc_xml.write('<display-name><name lang="en">' + addin_displayname + '</name></display-name>\n')
desc_xml.write(
    '<publisher><name xlink:href="' + addin_publisher_link + '" lang="en">' + addin_publisher_name + '</name></publisher>\n')
desc_xml.write('<extension-description><src xlink:href="description-en-US.txt" lang="en" /></extension-description>')
desc_xml.write('\n \n')
desc_xml.write('</description> \n')

desc_xml.close()


################################################################################
# manifest.xml
# List of files in package and their types.
#

def add_manifest_entry(xml_file, file_type, file_name):
    xml_file.write('<manifest:file-entry manifest:media-type="application/vnd.sun.star.' + file_type + '" \n')
    xml_file.write('    manifest:full-path="' + file_name + '"/> \n')


manifest_xml = open(cur_dir + '/build/META-INF/manifest.xml', 'w')

manifest_xml.write('<manifest:manifest>\n')
add_manifest_entry(manifest_xml, 'uno-typelibrary;type=RDB', 'XFinancials.rdb')
add_manifest_entry(manifest_xml, 'configuration-data', 'Financials.xcu')
add_manifest_entry(manifest_xml, 'uno-component;type=Python', 'financials.py')
manifest_xml.write('</manifest:manifest> \n')

manifest_xml.close()


################################################################################
# Financials.xcu

def define_function(xml_file, function_name, description, parameters):
    xml_file.write('  <node oor:name="' + function_name + '" oor:op="replace">\n')
    xml_file.write('    <prop oor:name="DisplayName"><value xml:lang="en">' + function_name + '</value></prop>\n')
    xml_file.write('    <prop oor:name="Description"><value xml:lang="en">' + description + '</value></prop>\n')
    xml_file.write('    <prop oor:name="Category"><value>Add-In</value></prop>\n')
    xml_file.write(
        '    <prop oor:name="CompatibilityName"><value xml:lang="en">AutoAddIn.Financials.' + function_name + '</value></prop>\n')
    xml_file.write('    <node oor:name="Parameters">\n')

    for p, desc in parameters:
        # Optional parameters will have a display name enclosed in square brackets.
        p_name = p.strip("[]")
        xml_file.write('      <node oor:name="' + p_name + '" oor:op="replace">\n')
        xml_file.write('        <prop oor:name="DisplayName"><value xml:lang="en">' + p_name + '</value></prop>\n')
        xml_file.write('        <prop oor:name="Description"><value xml:lang="en">' + desc + '</value></prop>\n')
        xml_file.write('      </node>\n')

    xml_file.write('    </node>\n')
    xml_file.write('  </node>\n')


# instance_id references the named UNO component instantiated by Python code (that is my understanding at least).
implementation_name = "com.financials.getinfo.python.FinancialsImpl"

# Name of the corresponding Excel add-in if you want to share documents across OOo and Excel.
excel_addin_name = "Financials.xlam"

financials_xml = open(cur_dir + '/build/Financials.xcu', 'w')

financials_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
financials_xml.write(
    '<oor:component-data xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" oor:name="CalcAddIns" oor:package="org.openoffice.Office">\n')
financials_xml.write('<node oor:name="AddInInfo">\n')
financials_xml.write('<node oor:name="' + implementation_name + '" oor:op="replace">\n')
financials_xml.write('<node oor:name="AddInFunctions">\n')

define_function(financials_xml,
                'getRealtime', 'Fetches Realtime Financial Data.',
                [('ticker', 'The ticker symbol.'), ('datacode', 'The data code.'), ('source', 'The source.')])
define_function(financials_xml,
                'getHistoric', 'Fetches Historic Financial Data.',
                [('ticker', 'The ticker symbol.'), ('datacode', 'The data code.'), ('date', 'The date.'),
                 ('source', 'The source.')])

financials_xml.write('</node>\n')
financials_xml.write('</node>\n')
financials_xml.write('</node>\n')
financials_xml.write('</oor:component-data>\n')

financials_xml.close()

################################################################################
# Done
