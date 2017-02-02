#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import defaultdict
from grab import Grab
from pandas import read_excel, DataFrame
from json import loads
from logging import basicConfig, DEBUG

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass

def fetch_contacts(username, password):

    basicConfig(level=DEBUG)

    g = Grab()

    home_url = 'https://www.linkedin.com'
    g.go(home_url + '/uas/login')
    g.doc.set_input('session_key', username)
    g.doc.set_input('session_password', password)
    g.doc.submit()

    def get_nb_contacts():
        elem = g.doc('//li[@class="nav-item account-settings-tab"]/a')
        own_page = elem.attr('href')
        g.go(own_page)
        g.doc.save('z.html')
        html = g.doc.select('//*[@id="top_card-content"]').html()
        start = html.find('{')
        com = html[start:-10]
        content = loads(com)["content"]
        res = content["ContactInfo"]["distance"]["numberOfConnections"]
        return res

    nb_contacts = 0
    while nb_contacts == 0:
        try:
            nb_contacts = get_nb_contacts()
        except:
            pass

    contacts_url = g.doc('//*[@id="advanced-search"]/@href').text()
    g.go(contacts_url)

    def process_comments(commented_line):
        start = commented_line.find('{')
        tmp = commented_line[start:-10]
        res = loads(tmp)["content"]["page"]["voltron_unified_search_json"]["search"]
        next_page_url = res["baseData"]["resultPagination"]["nextPage"]["pageURL"]
        results = res["results"]
        contacts = [ X.itervalues().next() for X in results ]
        return contacts, home_url + next_page_url

    def process1contact(contact):
        s_dict = defaultdict(lambda: '')
        l_dict = defaultdict(lambda: [])

        s_dict["lastname"] = contact["lastName"]
        s_dict["firstname"] = contact["firstName"]
        try:
            s_dict["id"] = contact["id"]
        except:
            s_dict["id"] = ''
        try:
            s_dict["job_title"] = contact["fmt_headline"]
        except:
            s_dict["job_title"] = ''
        print(s_dict)

        links_profile = []
        for key in contact.keys():
            if 'link_nprofile_view' in key:
                links_profile.append(key)
        if len(links_profile) == 0:
            print("ERROR: No 'link_profile' provided in contact.keys()")
        link_profile = links_profile[0]
        url_contact = contact[link_profile]

        g.go(url_contact)

        # email
        try:
            s_dict["email"] = g.doc.select('//a[contains(@href,"mailto")]').text()
        except:
            s_dict["email"] = ''

        # phone number
        try:
            s_dict["phone"] = g.doc.select('//div[@id="phone-view"]/ul/li').text()
        except:
            s_dict["phone"] = ''

        # skills
        for elem in g.doc.select('//ul[@class="skills-section"]//span[contains(@class, "endorse-item-name-text")]'):
            l_dict["main_skills"].append(elem.text())
        for elem in g.doc.select('//ul[@class="skills-section compact-view"]//span[contains(@class, "endorse-item-name-text")]'):
            l_dict["other_skills"].append(elem.text())

        # companies
        tmp = g.doc.select('//div[@class="editable-item section-item current-position"]//a[contains(@href, "company-name")]')
        for elem in tmp:
            s_dict["current_company"] += elem.text()
        tmp = g.doc.select('//div[@class="editable-item section-item past-position"]//a[contains(@href, "company-name")]')
        for elem in tmp:
            if len(elem.text()) > 0:
                l_dict["former_companies"].append(elem.text())

        # summary
        try:
            s_dict["summary"] = g.doc.select('//div[@class="summary"]/p').text()
        except:
            s_dict["summary"] = ''

        # languages
        tmp = g.doc.select('//div[@id="languages"]//li[@class="section-item"]/h4/span')
        for elem in tmp:
            l_dict["languages"].append(elem.text())

        # projects
        project_names = g.doc('//div[@id="background-projects"]//span[@dir="auto"]')
        project_dates = g.doc('//div[@id="background-projects"]//span[@class="projects-date"]/time')
        for name, date in zip(project_names, project_dates):
            l_dict["projects"].append((name.text(), date.text()))

        # certifications
        certification_titles = g.doc('//div[@id="background-certifications"]//a[contains(@href,"certification_company_title")]')
        certification_orgs = g.doc('//div[@id="background-certifications"]//a[contains(@href,"certification-org_name")]')
        certification_dates = g.doc('//div[@id="background-certifications"]//span[@class="certification-date"]/time')
        for title, org, date in zip(certification_titles, certification_orgs, certification_dates):
            title_text = title.text()
            end = title_text.find('(')
            l_dict["certifications"].append((title_text[:end], org.text(), date.text()))

        # coursework
        schools = g.doc('//div[@id="background-education-container"]//a[contains(@href,"edu-school-name")]')
        dates = g.doc('//div[@id="background-education-container"]//span[@class="education-date"]')
        for school, date in zip(schools, dates):
            l_dict["coursework"].append((school.text(), date.text()))

        # graduation year
        try:
            end_schools = [ int(date.text().split(' ')[-1]) for date in dates ]
            s_dict["graduation_year"] = max(end_schools)
        except:
            s_dict["graduation_year"] = ''

        # experiences
        xp_titles = g.doc('//div[@id="background-experience"]//a[contains(@href,"profile_title")]')
        xp_comps = g.doc('//div[@id="background-experience"]//a[contains(@href,"company-name")]')
        xp_comps = filter(lambda x: len(x.text()) > 0, xp_comps)
        xp_dates = g.doc('//div[@id="background-experience"]//span[@class="experience-date-locale"]/time')
        xp_places = g.doc('//div[@id="background-experience"]//span[@class="locality"]')
        xp_summaries = g.doc('//div[@id="background-experience"]//p[@class="description summary-field-show-more"]')
        for title, company, date, place, summary in zip(xp_titles, xp_comps, xp_dates, xp_places, xp_summaries):
            l_dict["experiences"].append((title.text(), company.text(), date.text(), place.text(), summary.text()))

        def pretty_tuple(T):
            if type(T) == tuple:
                return ', '.join(t.encode('utf-8') for t in T)
            else:
                return T
        pretty_list = lambda L: '\n'.join(pretty_tuple(l) for l in L)

        s_l_dict = {k:pretty_list(v) for k, v in l_dict.items()}
        s_dict.update(s_l_dict)
        return s_dict

    import os
    path_to_desktop = os.path.expanduser('~/Desktop/')
    filename = path_to_desktop + 'contacts.xlsx'
    if os.path.isfile(filename):
        saved_df = read_excel(filename)
        saved_IDs = saved_df["id"].values
    else:
        saved_IDs = []

    contacts = []
    nb_pages = int((nb_contacts-1)/10 + 1)
    #nb_pages = 2
    for i in range(nb_pages):
        comments = g.doc.select('//*[@id="voltron_srp_main-content"]').html()
        new_contacts, next_page_url = process_comments(comments)
        if i == nb_pages - 1:
            new_contacts = filter(lambda contact: contact["distance"] == 1, new_contacts)
        new_contacts = filter(lambda contact: contact["id"] not in saved_IDs, new_contacts)
        contacts.extend(new_contacts)
        g.go(next_page_url)

    processed_contacts = [ process1contact(contact) for contact in contacts ]

    df = DataFrame(processed_contacts)
    cols_sorted = ["lastname", "firstname", "email", "phone", "job_title", "main_skills",
            "other_skills", "current_company", "former_companies", "certifications",
            "projects", "graduation_year", "coursework", "summary", "experiences",
            "languages", "id"]
    df_cols = df.columns.tolist()
    cols = [col for col in cols_sorted if col in df_cols]
    df = df[cols]

    if os.path.isfile(filename):
        df = saved_df.append(df)

    df.to_excel(filename, sheet_name='sheet1', index=False)

    return processed_contacts

if __name__ == "__main__":

    import sys

    assert len(sys.arg) == 2, "You should pass the arguments in command line.
    Example: 'python fetch_contacts.py first.last@gmail.com password'"
    
    usr = sys.arg[0]
    pwd = sys.arg[1]

    fetch_contacts(usr,pwd)


