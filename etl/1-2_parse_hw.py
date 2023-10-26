"""
RC 10-2023

Parsing horseracing wrongs data into a more useful csv

    inputs: 
    ______

        data/source/etl_1-1_horseracing_wrongs.csv

    outputs: 
    _______

        data/processed/etl_1-2_parse_hw.csv


"""

##############
# SETTING UP #
##############

import pandas as pd
import re

source = "..//data//source//"
processed = "..//data//processed//"
manual = "..//data//manual//"

REASON_FOR_DEATH_CODE = ['R/T/S','R/T','R', 'S', 'T']

########################
# READING IN THE FILES #
########################

hw = pd.read_csv(source + "etl_1-1_horseracing_wrongs.csv")

##############
# PROCESSING #
##############

def get_reason_for_death_index(notes):
    for r in REASON_FOR_DEATH_CODE:
        reg_r = r"\b" + r + r"\b"
        search = re.search(reg_r, notes)
        if search:
            return (search.span()[0],search.span()[1])
    return (-1,-1)

hw['date'] = hw['date'].str.strip()
hw["notes"] = hw["notes"].str.strip().str.replace("R or T","R/T")
hw['split_index'] = hw["notes"].apply(get_reason_for_death_index)
hw["race_train_stall"] = hw.apply(lambda x: x["notes"][x["split_index"][0]:x["split_index"][1]] if x["split_index"][0]>=0 else "",axis=1)
hw["details"] = hw.apply(lambda x: x["notes"][x["split_index"][1]:][1:].replace("–","").strip(),axis=1)
hw['track'] = hw.apply(lambda x: x["notes"][:x["split_index"][0]].strip(),axis=1)
hw["date_dt"] = hw.apply(lambda x: pd.to_datetime(str(x["date"])+", "+str(x["year"]), errors="coerce").date(),axis=1)

####################
# WRITING OUT FILE #
####################

hw.to_csv(processed + "etl_1-2_parse_hw.csv", index=False, encoding='utf-8-sig')
