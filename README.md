# Horse Deaths

This repository contains data and code to reproduce the data findings in [A new push to protect racehorses is leaving behind young thoroughbreds](https://scrippsnews.com/stories/a-new-push-to-protect-racehorses-is-leaving-behind-young-thoroughbreds/), published on October 25, 2023.

**From the video piece:**

> SO FAR THIS YEAR, NATIONWIDE DATA WE ANALYZED FROM HORSE SAFETY ADVOCATES, SHOW AT LEAST 298 THOROUGHBRED RACEHORSE DEATHS LINKED TO TRAINING OR RACING.

**From the digital piece:**

> But a Scripps News analysis of national data from the animal rights group Horseracing Wrongs showed at least 298 thoroughbred racehorse deaths so far this year linked to training or racing.

and

> We found that 2-year-old horses have sprinted over 17,000 times in auctions since 2018. 

## Data

### **1. Horse deaths** 

The story focuses on thoroughbred racing, which is the only federally regulated horse racing in the United States. As such, our analysis focuses on the deaths of thoroughbreds. The main data source for our findings is a list of deaths of many kinds of racehorses from an advocacy organization called Horseracing Wrongs. We cross-reference this dataset with various external sources to determine if the horse was a thoroughbred -- as opposed to a quarter horse, standardbred, or any other kind of race horse.

To check the validity of the data, we also used it to calculate the same statistics found in [this report](https://www.arci.com/2023/10/test-post/) from the Association of Racing Commissioners International (ARCI) and by reaching out to individual state racing comissions. Our derived numbers were very close to those reported by ARCI.

#### **Horseracing Wrongs**

##### **Deaths**

We are using data from [Horseracing Wrongs](https://horseracingwrongs.org/) with horse names to identify race horses that died. The data is authored and maintained by Patrick Battuello, compiled from a variety of sources, including regular open records requests to state horse racing commissions, and from media reports. Not all horses in the database are named, either because they weren't yet named when they died, or because their names weren't part of the necropsy reports. Horseracing Wrongs classifies each death as related to racing ("R"), training ("T"), or if it occurred in the horse's stall ("S".)

##### **Racetrack types**

Battuello also provided us with information on what kinds of horses raced at each racetrack. We reformatted that data and added information on additional tracks that had closed down. That information is saved at [manual/racetrack_types.xlsx](data/manual/racetrack_types.xlsx). (Key: T = Thoroughbred, Q = Quarter Horse, H = Harness) In some cases, we found Quarterhorses that had died at tracks that were labelled as Thoroughbred-only. In those cases, we manually adjusted the database. We also manually added and looked up tracks that were not part of this list. 

#### **Equibase**

The horseracing site Equibase publishes [leaderboards](https://www.equibase.com/stats/View.cfm?tf=year&tb=horse) of horses by foaling year. We used data pulled from the leaderboards to help identify horses as thoroughbreds or quarter horses.

These files are saved at [source/equibase_QH.csv](data/source/equibase_QH.csv) and [source/equibase_TB.csv](data/source/equibase_TB.csv)

#### **Pedigree Query**

As a secondary data source on horse breed, we searched for the horses in Horseracing Wrongs in [Pedigree Query](https://www.pedigreequery.com/). This helps us classify thoroughbred horses that aren't present in Equibase's leaderboards, some of whom never raced.

This data is saved at:
[source/pedigree_query.csv](data/source/pedigree_query.csv)

### **2. Under tack shows**

To count the number of completed sprints at under tack shows in 2023, we pulled together a list of auctions of two-year-old horses, and then sought out the records from each of the auctions.

#### **Auction house data**
The trade publication Bloodhorse publishes lists of throroughbred [sales results and auctions](https://www.bloodhorse.com/horse-racing/thoroughbred-sales/results). We took the lists of two-year-old auctions and manually identified the auctions that took place in the United States. We also manually added some auctions from Ocala Breeder Sales that weren't on the Bloodhorse site.

Then, we went through and found the auction houses's records for each auction. These files are saved in [source/undertack](data/source/undertack). Metadata on each auction file, is at [manual/undertack_meta.xlsx](data/manual/undertack_meta.xlsx).

If a horse didn't have a recorded time in the auction records -- as may be the case when horses are withdrawn from the auction before the under tack show, break down on the course, or when they are "galloped" instead of being "breezed" -- we did not count the horse as having sprinted in the undertack.

When talking about under tacks in the piece, we mostly focus on horses than sprinted one furlong (1/8th of a mile). This analysis includes horses that sprinted all distances. 

#### **Bloodhorse auction records**
In cases where we couldn't find the catalog for the auction, Bloodhorse maintains a record of horses that completed individual auctions -- i.e. they enrolled, and were not withdrawn before being auctioned off. This includes horses that were sold and horses that did not attain their reserve price (RNA). These files are also saved as html snapshots in [source/undertack](data/source/undertack), and the file is tracked in [manual/undertack_meta.xlsx](data/manual/undertack_meta.xlsx).

For the auctions where we're relying on Bloodhorse data, we count horses sold. Based on the auction data we do have, we found that this reliably undercounts the number of horses that sprinted in an under tack show. (The number of horses that sprint and then are either withdrawn or RNA is always larger than the number of horses that are sold at auction but did not sprint.)

#### **[manual/undertack_meta.xlsx](data/manual/undertack_meta.xlsx)**
A spreadsheet with all the metadata on the auctions in the US, including the location of the file for that auction. 

* **OBS**: An [Ocala Breeders' Sales](https://obssales.com/) auction
* **FT**: A [Fasig Tipton](fasigtipton.com/) auction
* **BH**: An auction that didn't have a publicly available catalog with under tack show times, so we used the Bloodhorse catalog
* **PDF**: Auctions that released their under tack show time information in PDF format. Used for the earlier [Texas Thoroughbred Association](ttasales.com/) auctions.
* **API**: Auctions where an API was the best way to access their auction data. Used for the later [Texas Thoroughbred Association](ttasales.com/) auctions.

## ETL 

All ETL is in the [etl](etl/) folder: 

### **1. Horse deaths**

**[1-1_horseracing_wrongs.py](etl/1-1_horseracing_wrongs.py)** 

This is a web scraper for the ["Killed in Action"](https://horseracingwrongs.org/killed-in-action/) pages on Horseracing Wrongs to get a list of horses that have been killed. 

Output saved at [data/source/etl_1-1_horseracing_wrongs.csv](data/source/etl_1-1_horseracing_wrongs.csv)

**[1-2_parse_hw.py](etl/1-2_parse_hw.csv)**

This script parses the data from [data/source/etl_1-1_horseracing_wrongs.csv](data/source/etl_1-1_horseracing_wrongs.csv), splitting the "notes" column into separate columns in a well-formed csv.

Output saved at [data/source/etl_1-2_parse_hw.csv](data/processed/etl_1-2_parse_hw.csv)

**[1-3_identifying_tb.py](etl/1-3_identifying_tb.py)**

This file is where we identify what horses are thoroughbreds.

1. Read in `etl_1-2_parse_hw.csv`, limit to 2023 deaths related to Racing and Training ("R" and "T" in the *race_train_stall* column). Split the data into horses that are named and unnamed. (**named**,**no_name**)

2. Merge **named** to `equibase_QH.csv` (**qh**) and `equibase_TB.csv` (**tb**), limited to horses that were born before 2023, and within the past 10 years, and with name duplicates dropped to keep the youngest horse (the older horse would have had to have already died for the name to be reregistered). -- Adds columns *fy_tb* and *fy_qh*.

3. Merge to `pedigree_query.csv` (**pq**) and `racetrack_types.xlsx` (**types**). -- Adds columns *fy_pq* and *type*.

4. To identify thoroughbreds do the following. -- Adds column *TB*: 

    * If the horse only has a *fy_tb* and not a *fy_qh*, then we label it a thoroughbred. If it has a *fy_qh*, and neither a *fy_tb* nor a *fy_pq*, we label it a quarter horse.

    * If the horse died at a track that only races non-thoroughbreds (*type* is "Q" or "H"), we assume it is a horse of that type.

    * If a horse wasn't classifiable by either method above, has no *fy_qh*, and has a *fy_pq* then we label it a thoroughbred.

    * If the horse matched in all three data sources with the same foaling year (*fy_tb*==*fy_qh*==*fy_pq*), it is both a quarter horse and a thoroughbred. We labelled it as "T and Q". 

5. Export the horses that were not classified by the above methods (either because of insufficient information, or because they matched to *qh* in addition to a thoroughbred data set) to [etl/processed/etl_1-3_for_manual_review.csv](etl/processed/etl_1-3_for_manual_review.csv), saving them in [etl/manual/etl_1-3_manual.xlsx](etl/manual/etl_1-3_manual.xlsx) and manually reviewing them. Rerun this script to read these back in and overwrite the "TB" column with the manual values.

Output saved at [data/processed/etl_1-3_hw_identifying_tb.csv](data/processed/etl_1-3_hw_identifying_tb.csv)

### **2. Under tack shows**

**[2_twoyo_under_tack.py](etl/2_twoyo_under_tack.py)**

This file reads in all of the auction records specified in [undertack_meta.xlsx](data/manual/undertack_meta.xlsx) (**ut**). We create standardized columns for whether the horse sprinted in the undertack ("breezed"), whether the horse sold ("sale_status"), and -- if available -- the numeric undertack time ("ut_col_numeric").

We compile this into a single large data set, where every row represents a horse within an auction.

Output saved at [data/processed/etl_2_twoyo_under_tack.csv](data/processed/etl_2_twoyo_under_tack.csv).

## Analysis

The analysis for this piece is in the notebook [analysis.ipynb](analysis.ipynb).

For our deaths finding, we load [etl_1-3_hw_identifying_tb.csv](data/processed/etl_1-3_hw_identifying_tb.csv), limit it to thoroughbreds, and count the rows. We found 298 thoroughbred deaths this year related to racing or training. Those horses are saved at [data/processed/analysis_1_tb_2023_racing_training.csv](data/processed/analysis_1_tb_2023_racing_training.csv)

We also calculated this as grouped by state (and broken out by racing and training deaths), and state and track, saved at [data/processed/analysis_1_state_counts_2023.csv](data/processed/analysis_1_state_counts_2023.csv) and [data/processed/analysis_1_deaths_by_state_racetrack_2023.csv](data/processed/analysis_1_deaths_by_state_racetrack_2023.csv) respectively.

For our finding about under tack shows, we load [etl_2_twoyo_under_tack.csv](data/processed/etl_2_twoyo_under_tack.csv). We demonstrate that the number of horses that sprinted in an under tack show is larger than the number of horses that sold at auction, in all the auctions for which we have data, allowing us to assume that horses sold underestimates the number of under tack sprints. We then calculate the number of sprints we know occurred at the auctions for which we have data (16,990), and then, for the remaining auctions, the number of horses that sold (223) as an under estimate of the number of sprints.

We find at least 17,213 sprints in under tack shows since 2018, none of which would have fallen under HISA regulation. The counts for individual auctions are saved at [data/processed/analysis_undertack_counts.csv]([data/processed/analysis_undertack_counts.csv])


## Graphics 

The web piece contains a table with the horse deaths aggregated by state and broken out by training and racing deaths. The data from that table is at [data/processed/analysis_state_counts_2023.csv](data/processed/analysis_state_counts_2023.csv).

## Other data elements

### **Horses foaled but never raced**

Though it was not as involved as the above analyses, the following paragraph from the web piece also constitutes a data finding:

> A Scripps News analysis of data from the Jockey Club found about a third of all thoroughbreds that are born and registered never go on to race in the U.S. or Canada. However, we couldn’t find data to give the full picture of what happened to them, like whether they suffered an injury in training, were exported to race abroad, were used for breeding, or just weren’t fast enough. 

The [Jockey Club Fact Book](https://www.jockeyclub.com/default.asp?section=FB&area=psft) publishes data on the percentage of horses in each birth cohort that start racing at different ages. If we sum by year, we get the percentage of horses that have ever raced by their birth cohort. 

The Jockey Club is the breed registry for thoroughbred horses in the United States and Canada. These statistics include all horses that were foaled in the United States or Canada, and the percentage that have ever raced is based off races in the United States and Canada. 

At the time the piece was published, these were the values in the fact book. For crop year 2019, there are 0 horses in the "5YO+" category because all horses born in 2019 were younger than 5 at the time. The "Total" column has the total percentage of horses that had raced that we calculated, the "Never Raced" column is its complement: 

| Crop Year | 2YO | 3YO | 4YO | 5YO+ | Total | Never Raced |
| --------- | --- | --- | --- | ---- | ----- | ----------- |
| 2003 | 31.36 | 28.53 | 5.29 | 1.18 | 66.36 | **33.64** |
| 2004 | 31.83 | 28.22 | 5.53 | 1.16 | 66.74 | **33.26** |
| 2005 | 31.63 | 27.89 | 5.13 | 1.09 | 65.74 | **34.26** |
| 2006 | 31.04 | 27.14 | 5.05 | 1.18 | 64.41 | **35.59** |
| 2007 | 31.03 | 26.41 | 5.3 | 1.3 | 64.04 | **35.96** |
| 2008 | 30.11 | 26.69 | 5.72 | 1.3 | 63.82 | **36.18** |
| 2009 | 30.67 | 27.79 | 5.57 | 1.35 | 65.38 | **34.62** |
| 2010 | 32.29 | 27.71 | 5.22 | 1.3 | 66.52 | **33.48** |
| 2011 | 33.37 | 27.66 | 5.45 | 1.15 | 67.63 | **32.37** |
| 2012 | 35.34 | 28 | 5.25 | 0.98 | 69.57 | **30.43** |
| 2013 | 35.93 | 28.3 | 4.72 | 0.86 | 69.81 | **30.19** |
| 2014 | 36.85 | 28.05 | 4.54 | 0.9 | 70.34 | **29.66** |
| 2015 | 36.16 | 27.91 | 4.37 | 0.69 | 69.13 | **30.87** |
| 2016 | 35.96 | 28.01 | 3.95 | 0.69 | 68.61 | **31.39** |
| 2017 | 36.54 | 25.43 | 4.93 | 0.92 | 67.82 | **32.18** |
| 2018 | 34.55 | 28.46 | 4.56 | 0.6 | 68.17 | **31.83** |
| 2019 | 38.01 | 28.06 | 0.74 | 0 | 66.81 | **33.19** |

Since each of the individual years was between 29.66% and 36.18%, with a median of 33.19%, we interpreted this as approximately one third of horses. We also checked this number with other analyses and data from the Jockey Club and found similar values. 