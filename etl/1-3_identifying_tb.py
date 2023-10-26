"""
AF 10-2023

identifying which horses in horseracing wrongs are actually thoroughbreds

See etl/notebooks/8_matching_horses.ipynb for scratch work

    inputs: 
    ______

        data/source/etl_1-1_horseracing_wrongs.csv

        data/source/equibase_QH.csv

        data/source/equibase_TB.csv

        data/source/pedigree_query.csv

        data/manual/racetrack_types.xlsx

        (after manual lookup) data/manual/etl_1-4_manual.xlsx


    outputs: 
    _______

        data/processed/etl_1-4_for_manual_review.csv

        data/processed/etl_1-4_hw_identifying_tb.csv


"""

##############
# SETTING UP #
##############

import pandas as pd
import os

source = "..//data//source//"
processed = "..//data//processed//"
manual = "..//data//manual//"

########################
# READING IN THE FILES #
########################

tb = pd.read_csv(source + "equibase_TB.csv")[['horseName', 'fy']].drop_duplicates()
qh = pd.read_csv(source + "equibase_QH.csv")[['horseName', 'fy']].drop_duplicates()

pq = pd.read_csv(source + "pedigree_query.csv").drop_duplicates()
pq.columns = ['name', 'year', 'fy_pq']

types = pd.read_excel(manual + "racetrack_types.xlsx")[['State', 'Search Name', 'Types']]
types['Types'] = types.Types.str.replace(u"\xa0", "")
types['State'] = types['State'].str.strip()

hw = pd.read_csv(processed + "etl_1-2_parse_hw.csv")
hw = hw[(hw["year"]==2023)]

hw = hw[hw["race_train_stall"].isin(["R","T","R/T"])]


##############
# PROCESSING #
##############

# separate named horses from non-named horses
NON_NAMES = ['unidentified', 'yet-to-be-named', 'yet-to-be-named 2-year-old', '[illegible name]', 'unidentified filly', 'yet-to-be-named filly']

noname = hw[hw.name.isin(NON_NAMES)]
named = hw[~hw.name.isin(NON_NAMES)]

print(f"horses with no name: {len(noname)}")
print(f"horses with names: {len(named)}")

DYEAR = 2023

#
# Assumption: Very young horses don't race, nor do they train like older horses do.
# We're assuming a horse won't die the year it is born or the year afterwards. 
# We're assuming the same for very old horses (horses over the age of 10).
#
# We're keeping the latest fy for each horse, within the age window described above. 
# If a horse has the exact same name as an older horse, the older horse has died.
#
tb_year = tb[(tb.fy<DYEAR) & (tb.fy>=DYEAR-10)].sort_values("fy").drop_duplicates("horseName")
qh_year = qh[(qh.fy<DYEAR) & (qh.fy>=DYEAR-10)].sort_values("fy").drop_duplicates("horseName")
namedtb_year = pd.merge(named, tb_year, left_on = 'name', right_on = 'horseName', how = 'left')

namedtbqh_year = pd.merge(namedtb_year, qh_year, left_on = 'name', right_on = 'horseName', how = 'left', suffixes=['_TB', '_QH'])

# merge in pedigree query data
dyear = pd.merge(namedtbqh_year, pq, on = ['name', 'year'], how = 'left', validate= '1:1').drop(['horseName_TB', 'horseName_QH'], axis=1)

# add not named horses back in
dyear = pd.concat([dyear, noname])

# matching horses to racetracks
deaths_w_reg_fy = dyear.join(types.set_index("Search Name"),on="track")


######################
# CLASSIFYING HORSES #
######################

deaths_w_reg_fy['TB'] = "unclear"

#
## Horses that can be matched by their name only being in the QH registry, or only in the TB registries
# (equibase and/or pedigree query)
#
# only matched in the TB database is definitely TB
deaths_w_reg_fy.loc[(~deaths_w_reg_fy.fy_TB.isnull()) & (deaths_w_reg_fy.fy_QH.isnull()), 'TB'] = "T"

# only matched in the QH database is definitely just a QH 
deaths_w_reg_fy.loc[(deaths_w_reg_fy.fy_TB.isnull()) & (~deaths_w_reg_fy.fy_QH.isnull()) & (deaths_w_reg_fy.fy_pq.isnull()), 'TB'] = "Q"

# if still unmatched, not in the QH database, and matched in PQ, then it's a TB 
deaths_w_reg_fy.loc[(deaths_w_reg_fy['TB']=="unclear") & (deaths_w_reg_fy['fy_QH'].isnull()) & (~deaths_w_reg_fy['fy_pq'].isnull()), 'TB'] = "T"

#
## After this stage, we manually reviewed horses that only matched either QH or TB registries, and  died at tracks 
# that didn't match their registered type. In 100% of these cases, the name was correct and the track type was not,
# so we manually corrected the track type in racetrack_types.xlsx and re-ran the script.
#
# If the horse died at a track that only races quarter or harness horses, then we assume it's that kind of horse. 
deaths_w_reg_fy.loc[(deaths_w_reg_fy.Types.isin(['Q', 'H'])), 'TB'] = deaths_w_reg_fy.loc[(deaths_w_reg_fy.Types.isin(['Q', 'H'])), 'Types']

# Some horses race as both quarter horses and thoroughbreds. If the foaling year is the same in all three databases, 
# then all records refer to the same horse, and we we label the horse as both
deaths_w_reg_fy.loc[(deaths_w_reg_fy['TB']=="unclear") & (deaths_w_reg_fy['fy_QH'] == deaths_w_reg_fy['fy_pq']) & (deaths_w_reg_fy['fy_pq'] == deaths_w_reg_fy['fy_TB']), 'TB'] = "T and Q"


###################
# IDENTIFY MANUAL #
###################

man = deaths_w_reg_fy[(deaths_w_reg_fy.TB == 'unclear')]

man[['name', 'date', "Types", 'notes']].to_csv(processed + "etl_1-4_for_manual_review.csv", index=None, encoding='utf-8-sig')
print(f"Number to be manually looked up for 2023: {len(man)}")

#########################
# AFTER MANUAL CHECKING #
#########################

def replace_manually(final_row, manual_file):
    if (final_row['name'] in list(manual_file['name'])): 
        print(f"manually replacing {final_row['name']}")
        return str(manual_file[manual_file['name'] == final_row['name']]['type'].iloc[0])
    else: 
        return str(final_row['TB'])

m_file_str = manual + "etl_1-3_manual.xlsx"

if os.path.exists(m_file_str):
    print("Doing manual replacement!")
    m = pd.read_excel(m_file_str)[['name', 'type']]
    print(f"Number to be replaced: {len(m)}")
    deaths_w_reg_fy['TB'] = deaths_w_reg_fy.apply(lambda row: replace_manually(row, m), axis=1)

final = deaths_w_reg_fy

####################
# WRITING OUT FILE #
####################

final.to_csv(processed + "etl_1-4_hw_identifying_tb.csv", index=None, encoding='utf-8-sig')

print("NEIGHHHHHHHH")
