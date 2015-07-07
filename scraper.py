# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import sys
from bs4 import BeautifulSoup

INSPECTION_DOMAIN = 'http://info.kingcounty.gov'
INSPECTION_PATH = '/health/ehs/foodsafety/inspections/Results.aspx?'
INSPECTION_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H'
}


def get_inspection_page(**kwargs):
    inspection_params = INSPECTION_PARAMS.copy()

    for k, v in kwargs.iteritems():
        if k in INSPECTION_PARAMS:
            inspection_params[k] = v

    search = INSPECTION_DOMAIN + INSPECTION_PATH
    response = requests.get(search, params=inspection_params)
    response.raise_for_status()

    return response.content, response.encoding


def write_inspection_page(search_results):
    with open('inspection_page.html', 'w') as page:
        page.write(search_results)


def load_inspection_page(filename):
    with open(filename, 'r') as page:
        return page.read()


def parse_source(source_content, source_encoding):
    soup = BeautifulSoup(
        source_content,
        'html5lib',
        from_encoding=source_encoding
    )

    return soup


if __name__ == '__main__':
    if len(sys.argv) < 2:
        content, encoding = get_inspection_page(
            Zip_Code='98115',
            Inspection_Start='7/1/2015',
            Inspection_End='7/6/2015'
        )

        write_inspection_page(content)

    elif sys.argv[1] == 'test':
        import pdb; pdb.set_trace()
        content = load_inspection_page('inspection_page.html')

    document = parse_source(content, 'utf-8')
    print document.prettify(encoding='utf-8')
