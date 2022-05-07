# Flux processor

I am writing these scripts to process data from the 4th floor plate reader
for use in developing a Na+ flux assay. plate-processor.py may be more
generally useful, as it converts the data-as-a-plate layout to a more
useful long format.

## Installation/usage
 1. Download required packages (`pip3 install -r requirements.txt`)
 2. `python plate-processor.py [-s sampling_rate] data.csv conditions.csv`
 3. Run the script:

 ```python plate-processor.py {data.csv} {conditions.csv}```

## Plate processor
Unfortunately,
the time between plates (i.e., the sampling rate) is not output as part
of the data, so it must be recorded and input by the user. Format is as follows:

```-p {cycle removed} {removal duration (s)} {name of reagent added}```

You must include the A-H and 1-12 column/row in the `conditions.csv` template
file so that the csv is the correct size and shape.

## Plotter
Automated plot production using R and tidyverse. The python script should
run this automatically, but you can open and modify as you see fit.