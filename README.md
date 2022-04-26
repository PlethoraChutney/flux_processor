# Flux processor

I am writing these scripts to process data from the 4th floor plate reader
for use in developing a Na+ flux assay. plate-processor.py may be more
generally useful, as it converts the data-as-a-plate layout to a more
useful long format.

## Installation/usage
 1. Download required packages (`pip3 install -r requirements.txt`)
 2. `python plate-processor.py [-s sampling_rate] data.csv conditions.csv`

## Plate processor
Process the data-as-a-plate layout to more useable format. Unfortunately,
the time between plates (i.e., the sampling rate) is not output as part
of the data, so it must be recorded and input by the user.

A simple .csv file with conditions for each well laid out as a plate
will fill those conditions into the appropriate column. That is, a
`conditions.csv` file can be up to 8 rows tall and 12 columns wide,
each containing a string representing the condition of that "well".