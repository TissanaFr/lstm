from selenium import webdriver
import re
import os
import csv


url = 'https://www.pbump.net/files/post/history/'
driver = webdriver.Chrome()
driver.get(url)

script = driver.find_elements_by_tag_name('script')[2]
a = script.get_attribute('innerHTML')

with open('2.txt', 'w') as f:
    f.write(a)

states = {}

actual = {}
relative = {}

years = ['state', 'country', '1960', '1964', '1968', '1972', '1976', '1980', '1984', '1988',
         '1992', '1996',  '2000', '2004', '2008', '2012',
         '1960', '1964', '1968', '1972', '1976', '1980', '1984', '1988',
         '1992', '1996', '2000', '2004', '2008', '2012'
         ]

with open('2.txt', 'r') as f:
    content = f.readlines()
    content = [x.strip() for x in content]

    for line in content:
        if 'cty[' in line and '[]' not in line:
            z = line.split("'")
            state = z[1]
            country = z[3] if len(z) == 5 else z[4]
            code = re.findall(r'[0-9]+', z[4] if len(z) == 5 else z[5], re.I)

            code = code[0] if isinstance(code, list) else code
            try:
                c = states[state]
            except KeyError:
                states[state] = dict()
                states[state][country] = code
                continue

            states[state][country] = code

        elif 'actual[' in line:
            for state in states:
                for el in states[state]:
                    if str(states[state][el]) in line:
                        line = line.replace("''", '0')
                        values = [float(x) for x in re.findall('[-+]?[0-9]*\.?[0-9]+', line.split(' = ')[1])]
                        try:
                            c = actual[state]
                        except KeyError:
                            actual[state] = dict()
                            actual[state][el] = values
                            break
                        actual[state][el] = values
                        break

        elif 'relative[' in line:
            for state in states:
                for el in states[state]:
                    if str(states[state][el]) in line:
                        line = line.replace("''", '0')
                        values = [float(x) for x in re.findall('[-+]?[0-9]*\.?[0-9]+', line.split(' = ')[1])]
                        try:
                            c = relative[state]
                        except KeyError:
                            relative[state] = dict()
                            relative[state][el] = values
                            break
                        relative[state][el] = values
                        break

actual_new = actual

with open('all.csv', 'w', newline='') as outcsv:
    writer = csv.writer(outcsv)
    act_rel = ['', '', 'actual', 'actual',  'actual',  'actual',  'actual',  'actual',  'actual',  'actual',
               'actual', 'actual', 'actual', 'actual', 'actual', 'actual',
               'relative', 'relative', 'relative', 'relative', 'relative', 'relative', 'relative', 'relative',
               'relative', 'relative', 'relative', 'relative', 'relative', 'relative']
    writer.writerow(act_rel)
    writer.writerow(years)
    for state in relative:
        for country in relative[state]:
            l = list()
            l.append(state)

            l.append(country)
            for el in actual[state][country]:
                l.append(el)

            for el in relative[state][country]:
                l.append(el)

            writer.writerow(l)
        break

os.remove('2.txt')
driver.close()
