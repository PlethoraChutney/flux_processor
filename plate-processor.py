from string import ascii_uppercase
import os
import argparse
import pandas as pd


def read_plate_csv(filename, sampling_rate, conditions_key, plate_swap):
    with open(filename, 'r') as f:
        # un-read cells are filled with '-'
        #
        # separate plate reads are separated by a line with no entries in it
        # with our processing this becomes [''], which we'll replace with 'end_plate'
        lines = [x.rstrip().split(',') for x in f]
        lines = [[int(y.strip()) for y in x if y.strip() != '-'] if x != [''] else 'end_plate' for x in lines]

    row = 0
    time_index = 0
    current_plate = []
    data = pd.DataFrame(columns = ['Row', 'Column', 'Condition', 'Time', 'Plate', 'Fluorescence'])
    for line in lines:
        if line == 'end_plate':
            # reset every time we end a plate
            row = 0
            data = pd.concat([data, pd.DataFrame(current_plate)])
            current_plate = []
            time_index += 1
            continue
        
        time = time_index * sampling_rate
        offset = 0
        plate = 'Equilibration'
        for swap in plate_swap:
            if swap[0] <= time_index * sampling_rate:
                time += swap[1]
                plate = swap[2]
        time += offset

        for col_index in range(len(line)):
            # add an entry to our eventual dataframe
            # 
            # this is faster than directly modifying a pd dataframe, apparently

            current_plate.append({
                'Row': ascii_uppercase[row],
                'Column': col_index + 1,
                'Time': time,
                'Fluorescence': line[col_index],
                'Condition': conditions_key[col_index][row],
                'Plate': plate
            })
        row += 1
    
    # our file doesn't end with an empty line, so we need to add the
    # last plate manually since it's not caught in the loop
    data = pd.concat([data, pd.DataFrame(current_plate)])
    return data

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
        'sampling_rate',
        type = int,
        help = 'Sampling rate for plates, in seconds. Default 4'
    )
    parser.add_argument(
        '-p',
        '--plate-swap',
        type = str,
        nargs = 3,
        action = 'append',
        help = 'Record plate removals. Provide the following arguments, separated with spaces: time plate removed (seconds, do not add earlier plate swap durations), duration of plate removal (seconds), new plate name. This option can be added multiple times.'
    )

    args = parser.parse_args()

    if args.plate_swap:
        plate_swap = [(int(x[0]), int(x[1]), x[2]) for x in args.plate_swap]
    conditions_key = pd.read_csv(args.conditions_key, header = None)

    data = read_plate_csv(args.plate_data, args.sampling_rate, conditions_key, plate_swap)
    output_name = f"processed_{os.path.split(args.plate_data)[1]}"
    data.to_csv(output_name, index = False)

if __name__ == '__main__':
    main()