"""
AF 9-2023

Scraping all the horses that have been killed off of horseracing wrongs

    inputs: 
    ______

        https://horseracingwrongs.org/killed-in-action

    outputs: 
    _______

        ~//data//source//etl_1-1_horseracing_wrongs.csv

"""

##############
# SETTING UP #
##############

import pandas as pd
import numpy as np
import requests
import bs4
import time

source = "..//data//source//"

URL = "https://horseracingwrongs.org/killed-in-action/"

r = requests.get(URL)

soup = bs4.BeautifulSoup(r.text, features="lxml")
dropdown = soup.findAll('ul', "sub-menu")[1]
pages = [link['href'] for link in dropdown.findAll('a')]

########################
# READING IN THE FILES #
########################

pagelist = []
for page in pages:

    print(page)

    r = requests.get(page)
    soup = bs4.BeautifulSoup(r.text.replace('<em>', '').replace('</em>', ''), features="lxml")
    paragraphs = soup.findAll('p')
    type_index = np.where(['(R: Racing; T: Training; S: S' in par.text for par in paragraphs])[0][0]
    
    print(paragraphs[type_index])
    print(paragraphs[type_index+2])

    horselist = pd.DataFrame(paragraphs[type_index+1].stripped_strings)[0].str.split(",", n=2, expand = True)
    horselist.columns = ['name', 'date', 'notes']
    horselist['year'] = page[-5:-1]
    pagelist.append(horselist)
    time.sleep(2)

final = pd.concat(pagelist, ignore_index = True)

# If there is no death date, our notes are ending up in the "date" column.
# The next few lines shift them to the notes column and replace "date" with "N/A"
actual_notes = final.loc[final.notes.isnull(), 'date']
final.loc[final.notes.isnull(), 'date'] = "N/A"
final.loc[final.notes.isnull(), 'notes'] = actual_notes

# replace all weird apostrophes with the real normal ' 
final['name'] = final['name'].str.replace("’", "'")

print(final.shape)

####################
# WRITING OUT FILE #
####################

outfile_str = source + "etl_1-1_horseracing_wrongs.csv"

final.to_csv(outfile_str, index=None)

print("WOOOHOOO")