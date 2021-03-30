#!/usr/env/python
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

#
# Adds prefix (can be os name) to each test report.
#

import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser(description='Tag test names in a JUnit report')
for arg in ['tag', 'xml_report_file']:
	parser.add_argument(arg)
args = parser.parse_args()

tree = ET.parse(args.xml_report_file)
root = tree.getroot()
for i in root.findall(".//Test/Name"):
	i.text = "%s | %s" % (args.tag, i.text)
tree.write(args.xml_report_file)
