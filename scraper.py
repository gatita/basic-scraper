# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
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


def extract_data_listings(html):
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


def has_two_tds(element):
    verdict = False
    if element.name == 'tr':
        children = element.findChildren('td')
        if len(children) == 2:
            verdict = True
    return verdict


def clean_data(cell):
    cell = cell.text
    return cell.strip(' \n:-')


def extract_restaurant_metadata(listing):
    metadata_rows = listing.find('tbody').find_all(
        has_two_tds, recursive=False
    )
    rdata = {}
    current_label = ''
    for row in metadata_rows:
        key_cell, val_cell = row.find_all('td', recursive=False)
        new_label = clean_data(key_cell)
        current_label = new_label if new_label else current_label
        rdata.setdefault(current_label, []).append(clean_data(val_cell))
    return rdata


def is_inspection_row(element):
    verdict = False
    if element.name == 'tr':
        children = element.findChildren('td')
        if len(children) == 4:
            firstchild = clean_data(children[0]).lower()
            if ('inspection' in firstchild
               and firstchild.split()[0] != 'inspection'):
                verdict = True
    return verdict


def extract_score_data(listing):
    inspection_rows = listing.find_all(is_inspection_row)
    samples = len(inspection_rows)
    total = high_score = average = 0
    for row in inspection_rows:
        strval = clean_data(row.find_all('td')[2])
        try:
            intval = int(strval)
        except (ValueError, TypeError):
            samples -= 1
        else:
            total += intval
            high_score = intval if intval > high_score else high_score
    if samples:
        average = total/float(samples)
    data = {
        u'Average Score': average,
        u'High Score': high_score,
        u'Total Inspections': samples
    }
    return data


def generate_results(test=False):
    kwargs = {
        Zip_Code: '98112',
        Inspection_Start: '01/01/2015',
        Inspection_End: '07/01/2015'
    }

    if test:
        html = load_inspection_page('inspection_page.html')

    else:

    document = parse_source(content, 'utf-8')
    listings = extract_data_listings(document)

    knitted = {}
    for listing in listings[:10]:
        metadata = extract_restaurant_metadata(listing)
        score_data = extract_score_data(listing)
        score_data.update(metadata)
        yield score_data


if __name__ == '__main__':
    test = len(sys.argv_) > 1 and sys.argv[1] == 'test'
    for result in generate_results(test):
        print result
