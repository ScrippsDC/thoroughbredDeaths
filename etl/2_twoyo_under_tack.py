"""
AF 10-2023

Counting the number of horses that undertack 

    inputs: 
    ______

        ../data/manual/undertack_meta.xlsx

    outputs: 
    _______
    
        RC: I made this this a horse-level data set
        ../data/processed/etl_2_twoyo_under_tack.csv

"""

##############
# SETTING UP #
##############

import pandas as pd
import requests
import bs4
from tabula.io import read_pdf

manual = "..//data//manual//"
undertack = "..//data//source//undertack//"
processed = "..//data//processed//"

###############################
# THE MAIN IMPORTANT FUNCTION #
###############################

def obs_status(price):
    if pd.notna(price):
        price_std = str(price).strip().upper()
        if pd.to_numeric(price_std, errors='coerce')>0:
            return "sold"
        if price_std == "NOT SOLD":
            return "rna"
        if price_std == "OUT":
            return "withdrawn"
        return "other"
    return "na"

def ft_status(purchaser):
    if pd.notna(purchaser):
        col_std = str(purchaser).strip().upper()
        if col_std == "OUT":
            return "withdrawn"
        if col_std == "NOT SOLD":
            return "rna"
        return "sold"
    return "na"

def api_status(row):
    buyer = row["Buyer"]
    price = row["SalePrice"]
    rna = row["RNA"]
    if pd.notna(buyer):
        return "sold"
    if rna:
        return "rna"
    if price == 0:
        return "withdrawn"
    return "other"


def count_undertacks(type, file_name): 
    print(type,file_name)
    if type == "OBS":
        filepath = undertack + file_name
        header2 = ["Apr22_Excel.xlsx", "Apr23_Excel.xls", "Mar23_Excel.xls", "Jun22_Excel.xls", "Jun23_Excel.xls"]
        if file_name in header2: 
            df = pd.read_excel(filepath, header = 2)
        else:
            df = pd.read_excel(filepath, header = 3)
        if 'YR' in df.columns: 
            birth_col = "YR"
        else: 
            birth_col = "Foal Date"
        df = df[~df[birth_col].isnull()]
        if 'UT Time' in df.columns: 
            ut_col = 'UT Time'
        elif 'Work Time' in df.columns:
            ut_col = 'Work Time'
        else: 
            ut_col = 'work time'

        if "Price" in df.columns:
            price_col = "Price"
        else:
            price_col = "Price "
        
        # RC: Converting to numeric instead of using is_digit
        df["ut_col_numeric"] = pd.to_numeric(df[ut_col],errors="coerce")
        df["sale_status"] = df[price_col].apply(obs_status)

        # We're not counting horses galloped as having breezed
        df["breezed"]  = (~df[ut_col].isnull()) & (df["ut_col_numeric"].notna())
    
    if type == "FT":
        filepath = undertack + file_name
        cols = pd.Series(list(pd.read_csv(filepath,nrows=1).columns) + ["time","url"])
        cols = list(cols[["Unnamed: " not in col for col in cols]])
        df = pd.read_csv(filepath, skiprows=1, header=None)
        df.columns = cols 
        df["ut_col_numeric"] = pd.to_numeric(df["time"],errors="coerce")
        df["breezed"] = (df["ut_col_numeric"].notna())
        df["sale_status"] = df["PURCHASER"].apply(ft_status)

    if type == "BH":
        with open(undertack + file_name) as f:
            soup = bs4.BeautifulSoup(f,features="lxml")
            df = pd.read_html(str(soup.find("table")))[0]
            df["status_std"] = df["Status"].str.strip().str.upper()
            df["ut_col_numeric"] = "Unknown"
            # RC: We were just counting rows and accidentally catching the RNAs. 
            # This fixes that.
            df["sale_status"] = df["status_std"].str.strip().str.lower()
            df["breezed"] = "Unknown"

    if type == "API":
        r = requests.get(file_name)
        horses = r.json()['value']
        df = pd.DataFrame(horses)
        
        df["undertack_time"] = df["BreezeTime"]
        df["ut_col_numeric"] = df["undertack_time"].apply(pd.to_numeric, errors='coerce')
        df["breezed"] = df["ut_col_numeric"]>0
        df["sale_status"] = df.apply(api_status,axis=1)

    if type == "PDF":
        tab = read_pdf(undertack + file_name, pages = 1)

        # Selects the columns with a "time" in them 
        times = tab[0].iloc[:,1::2]
        df = times.unstack().reset_index()
        df["undertack_time"] = df[0]
        df["ut_col_numeric"] = df["undertack_time"].apply(pd.to_numeric, errors='coerce')
        df["breezed"] = df["ut_col_numeric"]>0
        df["sale_status"] = "unknown"

    df["file"] = file_name
    df["type"] = type
    return df[['file','type','breezed','sale_status',"ut_col_numeric"]]

########################
# READING IN THE FILES #
########################

ut = pd.read_excel(manual + "undertack_meta.xlsx")[['sale','year', 'Type', 'files']]

###################################
# PROCESSING EVERY UNDERTACK FILE #
###################################

ut_dfs = []
for row in ut.iterrows():
    type = row[1]["Type"]
    file = row[1]["files"]
    ut_df = count_undertacks(type,file)
    ut_dfs.append(ut_df)
ut_df = pd.concat(ut_dfs)

#########################
# WRITING OUT THE FILES #
#########################

ut_df.to_csv(processed+"etl_2_twoyo_under_tack.csv")