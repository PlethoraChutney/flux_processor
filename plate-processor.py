import re
import os
import argparse
import pandas as pd

well_pattern = re.compile('[A-Z][0-9]{2}')

def read_plate_csv(filename, conditions_key, plate_swap):
    with open(filename, 'r') as f:
        # un-read cells are filled with '-'
        #
        # separate plate reads are separated by a line with no entries in it
        # with our processing this becomes [''], which we'll replace with 'end_plate'
        lines = [[y.strip() for y in x.split(':')] for x in f]

    reads = []
    current_time = 0
    current_cycle = 0
    for line in lines:
        try:
            if line[1] == '-':
                continue
        except IndexError:
            pass
        if re.search(well_pattern, line[0]):
            row = line[0][0]
            column = int(line[0][1:])
            flr = float(line[1])
            sample = conditions_key[row][column-1]
            plate_condition = 'Equilibration'

            time = current_time
            for plate in plate_swap:
                if current_cycle > plate[0]:
                    time += plate[1]
                    plate_condition = plate[2]

            reads.append({
                'Time': time,
                'Plate': plate_condition,
                'Row': row,
                'Column': column,
                'Condition': sample,
                'Fluorescence': flr
            })
        elif line[0] == 'Time [s]':
            current_time = int(line[1])
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
        plate_swap = [(int(x[0]), int(x[1]), x[2].replace('_', ' ')) for x in args.plate_swap]
    else:
        plate_swap = []

    with open(args.conditions_key, 'r') as f:
        conditions_list = [x.rstrip().split(',') for x in f]

    conditions_key = {}
    for row in conditions_list[1:]:
        conditions_key[row[0]] = row[1:]

    data = read_plate_csv(args.plate_data, conditions_key, plate_swap)
    output_name = f"processed_{os.path.split(args.plate_data)[1]}"
    data.to_csv(output_name, index = False)

if __name__ == '__main__':
    main()