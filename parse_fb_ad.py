from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

import time
import csv
import click


@click.command()
@click.option('--m', type=int, default=100)
@click.option('--user', type=str)
@click.option('--pwd', default='qwerty1!')
@click.option('--cand', type=str)
def fmain(m, user, pwd, cand):
    # Instantiate a chrome options object to set the size and headless preference
    ###############################################################################
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    # Path to your chrome driver
    driver = webdriver.Chrome(chrome_options=chrome_options)  # , executable_path=chrome_driver)
    ###############################################################################

    cand_list = None
    with open(cand, 'r') as f_cand:
        cand_list = f_cand.readlines()

    candidate = cand_list[0].split('\n')[0]
    candidate_for_url = candidate.replace(' ', '%20').replace("'", '%27')
    url = 'https://www.facebook.com/ads/archive/?active_status=all&ad_type=political_and_issue_ads&country=US&q={0}'. \
        format(candidate_for_url)
    driver.get(url)
    time.sleep(2)

    # Log in Routine
    # You wouldn't need this except for the first time you log in
    # Or if you use existing chrome profile, where facebook log in has already
    # been done
    ###############################################################################
    email = driver.find_element_by_css_selector("input[name='email']")
    email.send_keys(user)

    pswd = driver.find_element_by_css_selector("input[name='pass']")
    pswd.send_keys(pwd)

    driver.find_element_by_css_selector("button[name='login']").click()
    time.sleep(2)
    ###############################################################################

    # Load the page URL and give some time to fully load

    for candidate in cand_list:
        candidate = candidate.split('\n')[0]
        candidate_for_url = candidate.replace(' ', '%20').replace("'", '%27')
        url = 'https://www.facebook.com/ads/archive/?active_status=all&ad_type=political_and_issue_ads&country=US&q={0}'.\
            format(candidate_for_url)
        try:
            driver.get(url)
        except Exception:
            continue
        time.sleep(2)

        # Scroll full page, to load all the ads
        ###############################################################################
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Give page some time to load properly
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        ###############################################################################
        # Find all the "See ad perfomance" links, get their locations
        # And click them one by one, opening pop up window and
        # giving it time to load all the info
        # close the pop up window afterwards
        ###############################################################################
        ele = driver.find_elements_by_partial_link_text('See ad performance')

        ad_counter = 4
        xpath = '//*[@id="facebook"]/body/div[{0}]'
        sponsored_class = '_6jfj'
        advertiser_class = '_6jfh'
        impressions_class = '_6jfl'
        money_class = '_6jfm'
        ad_text_class = '_681i'
        active_class = '_6jgm'
        time_period_class = '_6jgp'

        file = '{0}.csv'.format(candidate)
        f = open(file, 'w', newline='')

        fieldnames = ['Candidate', 'Advertiser', 'Sponsor', 'Impressions', 'AdText', 'Date', 'MoneySpent', 'Active']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        print('--> Start writing info about {0} in {1}'.format(candidate.title(), file))

        for el in ele:
            data = {
                'Candidate': 'None',
                'Advertiser': 'None',
                'Sponsor': 'None',
                'Impressions': 'None',
                'AdText': 'None',
                'Date': 'None',
                'MoneySpent': 'None',
                'Active': 'None'
            }

            driver.execute_script("arguments[0].click()", el)
            time.sleep(2)

            ad = driver.find_element_by_xpath(xpath.format(ad_counter))

            data['Candidate'] = candidate

            try:
                adv = ad.find_element_by_class_name(advertiser_class).find_element_by_css_selector('div')
                adv = BeautifulSoup(adv.get_attribute('innerHTML'), 'lxml').text
            except NoSuchElementException:
                adv = 'None'
            data['Advertiser'] = adv

            try:
                spons = ad.find_element_by_class_name(sponsored_class).find_element_by_css_selector('div')
                spons = BeautifulSoup(spons.get_attribute('innerHTML'), 'lxml').text
                spons = spons.split('Paid for by ')[1]
            except NoSuchElementException:
                spons = 'None'
            data['Sponsor'] = spons

            try:
                impr = ad.find_element_by_class_name(impressions_class).find_element_by_css_selector('div')
                impr = BeautifulSoup(impr.get_attribute('innerHTML'), 'lxml').text
            except NoSuchElementException:
                impr = 'None'
            data['Impressions'] = impr

            try:
                money = ad.find_element_by_class_name(money_class).find_element_by_css_selector('div').\
                    find_element_by_css_selector('div')
                money = BeautifulSoup(money.get_attribute('innerHTML'), 'lxml').text
            except NoSuchElementException:
                money = 'None'
            data['MoneySpent'] = money

            try:
                active = ad.find_element_by_class_name(active_class)
                active = BeautifulSoup(active.get_attribute('innerHTML'), 'lxml').text
            except NoSuchElementException:
                active = 'None'
            data['Active'] = active

            try:
                period = ad.find_element_by_class_name(time_period_class)
                period = BeautifulSoup(period.get_attribute('innerHTML'), 'lxml').text
                if period.find('-') != -1:
                    period = period[:period.find('-')]
                else:
                    period = period[len('Started running on '):]
            except NoSuchElementException:
                period = 'None'
            data['Date'] = period

            try:
                ad_text = ad.find_element_by_class_name(ad_text_class)
                ad_text = BeautifulSoup(ad_text.get_attribute('innerHTML'), 'lxml').text
            except NoSuchElementException:
                ad_text = 'None'
            data['AdText'] = ad_text

            try:
                writer.writerows([data])
            except Exception:
                for key in data:
                    data[key] = data[key].encode('utf-8-sig')
                try:
                    writer.writerows([data])
                except Exception:
                    pass
                pass

            ad_counter += 1

            if ad_counter-4 == m:
                break

            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
        ###############################################################################
        f.close()
        print('--> Writing finished.\n')

    driver.quit()


if __name__ == '__main__':
    fmain()

