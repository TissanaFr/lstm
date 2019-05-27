from selenium import webdriver
import requests
from re import findall
import xlsxwriter
from time import sleep
import click


@click.command()
@click.option('--ex_path', help='Path to chromedriver.exe')
def retrieve(ex_path):
    if ex_path:
        driver = webdriver.Chrome(executable_path="D:/chromedriver.exe")
    else:
        driver = webdriver.Chrome()

    states = {
        'alaska': 'AK',
        'alabama': 'AL',
        'arkansas': 'AR',
        'arizona': 'AZ',
        'california': 'CA',
        'colorado': 'CO',
        'connecticut': 'CT',
        'delaware': 'DE',
        'florida': 'FL',
        'georgia': 'GA',
        'hawaii': 'HI',
        'iowa': 'IA',
        'idaho': 'ID',
        'illinois': 'IL',
        'indiana': 'IN',
        'kansas': 'KS',
        'kentucky': 'KY',
        'louisiana': 'LA',
        'massachusetts': 'MA',
        'maryland': 'MD',
        'maine': 'ME',
        'michigan': 'MI',
        'minnesota': 'MN',
        'missouri': 'MO',
        'mississippi': 'MS',
        'montana': 'MT',
        'north-carolina': 'NC',
        'north-dakota': 'ND',
        'nebraska': 'NE',
        'new-hampshire': 'NH',
        'new-jersey': 'NJ',
        'new-mexico': 'NM',
        'nevada': 'NV',
        'new-york': 'NY',
        'ohio': 'OH',
        'oklahoma': 'OK',
        'oregon': 'OR',
        'pennsylvania': 'PA',
        'rhode-island': 'RI',
        'south-carolina': 'SC',
        'south-dakota': 'SD',
        'tennessee': 'TN',
        'texas': 'TX',
        'utah': 'UT',
        'virginia': 'VA',
        'vermont': 'VT',
        'washington': 'WA',
        'wisconsin': 'WI',
        'west-virginia': 'WV',
        'wyoming': 'WY',
    }

    modes = {
        'classic': '',
        'deluxe': '/#deluxe',
        'lite': '/#lite'
    }

    start_url = 'https://projects.fivethirtyeight.com/2018-midterm-election-forecast/house/'

    for mode in modes:
        print(mode)
        workbook = xlsxwriter.Workbook(mode+'.xlsx')
        worksheet = workbook.add_worksheet()
        header = (
            ['State', 'District',
             'Republican win prob', 'Republican forecasted vote share',
             'Republican vote share (low)', 'Republican vote share (hi)',
             'Democrat win prob', 'Democrat forecasted vote share',
             'Democrat vote share (low)', 'Democrat vote share (hi)'
             ]
        )

        row = 0
        col = 0

        for item in header:
            worksheet.write(row, col, item)
            col += 1
        col = 0
        row += 1

        for state in states:
            i = 1
            while True:
                dem = {
                    'win_prob': [],
                    'forecasted_vote_share': [],
                    'low': [],
                    'high': []
                }

                resp = {
                    'win_prob': [],
                    'forecasted_vote_share': [],
                    'low': [],
                    'high': []
                }

                url = start_url+state+'/'+str(i)+modes[mode]
                if requests.get(url).status_code == 404:
                    break

                driver.get(url)
                sleep(2)
                try:
                    dem_table = driver.find_elements_by_css_selector('div.row.body-row.dem')
                    for _dem in dem_table:
                        _dem = _dem.find_element_by_css_selector('div.row-wrap')

                        win_prob = _dem.find_element_by_css_selector('div.text.odds.row-item'). \
                                                    find_element_by_css_selector('span.formatted'). \
                                                    get_attribute('innerHTML')

                        if win_prob.find('%') != -1:
                            win_prob = findall("\d+", win_prob)
                        else:
                            win_prob = _dem.find_element_by_css_selector('div.text.odds.row-item'). \
                                                    find_element_by_css_selector('span.raw'). \
                                                    get_attribute('innerHTML')
                            win_prob = findall("\d+\.\d+", win_prob)

                        dem['win_prob'].append(float(win_prob[0]))

                        voteshare = _dem.find_element_by_css_selector(
                                                            'div.text.voteshare-header.mobile.row-item'). \
                                                            find_element_by_css_selector('span.voteshare'). \
                                                            get_attribute('innerHTML')
                        voteshare = findall("\d+\.\d+", voteshare)
                        dem['forecasted_vote_share'].append(float(voteshare[0]))

                        low_high = _dem.find_element_by_css_selector('div.text.voteshare-header.mobile.row-item'). \
                                                find_element_by_css_selector('span.voteshare-range'). \
                                                get_attribute('innerHTML')
                        low_high = findall("\d+\.\d+", low_high)
                        low = float(low_high[0])
                        dem['low'].append(low)

                        high = float(low_high[1])
                        dem['high'].append(high)
                except Exception:
                    pass

                try:
                    resp_table = driver.find_elements_by_css_selector('div.row.body-row.gop')
                    for _resp in resp_table:
                        _resp = _resp.find_element_by_css_selector('div.row-wrap')

                        win_prob = _resp.find_element_by_css_selector('div.text.odds.row-item'). \
                            find_element_by_css_selector('span.formatted'). \
                            get_attribute('innerHTML')

                        if win_prob.find('%') != -1:
                            win_prob = findall("\d+", win_prob)
                        else:
                            win_prob = _resp.find_element_by_css_selector('div.text.odds.row-item'). \
                                find_element_by_css_selector('span.raw'). \
                                get_attribute('innerHTML')
                            win_prob = findall("\d+\.\d+", win_prob)

                        resp['win_prob'].append(float(win_prob[0]))

                        voteshare = _resp.find_element_by_css_selector(
                            'div.text.voteshare-header.mobile.row-item'). \
                            find_element_by_css_selector('span.voteshare'). \
                            get_attribute('innerHTML')
                        voteshare = findall("\d+\.\d+", voteshare)
                        resp['forecasted_vote_share'].append(float(voteshare[0]))

                        low_high = _resp.find_element_by_css_selector('div.text.voteshare-header.mobile.row-item'). \
                            find_element_by_css_selector('span.voteshare-range'). \
                            get_attribute('innerHTML')
                        low_high = findall("\d+\.\d+", low_high)
                        low = float(low_high[0])
                        resp['low'].append(low)

                        high = float(low_high[1])
                        resp['high'].append(high)
                except Exception:
                    pass

                for key in dem:
                    s_dem = sum(dem[key])
                    dem[key] = s_dem if s_dem < 100 else 100.0
                    s_resp = sum(resp[key])
                    resp[key] = s_resp if s_resp < 100 else 100.0
                    dem[key] = str(dem[key])
                    resp[key] = str(resp[key])

                data_to_save = (
                    [states[state], str(i),
                     resp['win_prob'], resp['forecasted_vote_share'], resp['low'], resp['high'],
                     dem['win_prob'], dem['forecasted_vote_share'], dem['low'], dem['high']
                     ]
                )

                for item in data_to_save:
                    worksheet.write(row, col, item)
                    col += 1

                col = 0
                row += 1
                i += 1
        workbook.close()

    driver.quit()


if __name__ == '__main__':
    retrieve()
