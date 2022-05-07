import re
import os
import argparse
import pandas as pd
import subprocess

well_pattern = re.compile('[A-Z][0-9]{2}')

def read_plate_csv(filename, conditions_key, plate_swap):
    with open(filename, 'r') as f:
        # Most lines are either Time: time or Well: Flr
        lines = [[y.strip() for y in x.split(':')] for x in f]

    reads = []
    current_time = 0
    current_cycle = 0
    for line in lines:
        try:
            # Unread wells are still in the file, with a fluorescence
            # value of '-'
            if line[1] == '-':
                continue
        except IndexError:
            pass

        if re.search(well_pattern, line[0]):
            # rows are always one letter
            row = line[0][0]

            # remaining characters are the column
            column = int(line[0][1:])

            # we separated on the colon, so FLR is stored in the second element
            flr = float(line[1])

            # This `sample` is "What's in the well"
            sample = conditions_key[row][column-1]

            # start out with the plate reader time and equilibration plate
            plate_condition = 'Equilibration'
            time = current_time
            for plate in plate_swap:
                # then if we find a plate swap that occurred before this
                # cycle
                if current_cycle > plate[0]:
                    # add the duration of the plate swap to our time
                    time += plate[1]
                    # and update our current plate condition
                    plate_condition = plate[2]

            # list of dicts is faster than appending to a pd dataframe
            # or at least it used to be:
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.append.html
            reads.append({
                'Time': time,
                'Plate': plate_condition,
                'Row': row,
                'Column': column,
                'Condition': sample,
                'Fluorescence': flr
            })
        # if it's a time line, update our pre-plate-swap time
        elif line[0] == 'Time [s]':
            current_time = int(line[1])

        # if it's a new cycle, update our cycle
        #
        # technically, we only read time once per cycle, so
        # these could be combined. But we read the line anyway,
        # so it doesn't cost much to make sure we're staying in sync
        # with the plate reader.
        elif line[0] == 'Cycle':
            current_cycle = int(line[1])


    return pd.DataFrame(reads)

def main():
    parser = argparse.ArgumentParser(
        'Flux reader',
        description= 'Process plate data from the 4th floor plate reader.'
    )
    parser.add_argument(
        'plate_data',
        type = str,
        help = 'Filename for plate data csv.'
    )
    parser.add_argument(
        'conditions_key',
        type = str,
        help = 'Filename for conditions key csv.'
    )
    parser.add_argument(
        '-p',
        '--plate-swap',
        type = str,
        nargs = 3,
        action = 'append',
        help = 'Record plate removals. Provide the following arguments, separated with spaces: time plate removed (samples), duration of plate removal (seconds), new plate name. This option can be added multiple times.'
    )

    args = parser.parse_args()

    if args.plate_swap:
        # (cycle, duration, plate condition)
        plate_swap = [(int(x[0]), int(x[1]), x[2].replace('_', ' ')) for x in args.plate_swap]
    else:
        plate_swap = []

    with open(args.conditions_key, 'r') as f:
        # conditions list is a list of the rows of our csv
        conditions_list = [x.rstrip().split(',') for x in f]

    conditions_key = {}
    # skip the first row, which is just column numbers
    for row in conditions_list[1:]:
        # first element is the row letter, which will be our key
        # the remaining elements are the samples.
        conditions_key[row[0]] = row[1:]

    data = read_plate_csv(args.plate_data, conditions_key, plate_swap)
    output_name = f"processed_{os.path.split(args.plate_data)[1]}"
    data.to_csv(output_name, index = False)
    subprocess.run(['Rscript', 'flux_plotter.R'])

if __name__ == '__main__':
    main()