import argparse

def range_type(min, max):
    try:
        min = int(min)
        max = int(max)
    except ValueError as err:
        print(f'You entered , which is not a positive number.')
        raise argparse.ArgumentTypeError("minvm and maxvm should be positive integers")

    if (min > 0 and max > 0 and max > min):
        return
    else:
        raise argparse.ArgumentTypeError("minvm shoulb be < than maxvm.")

def list_average(integers_list):
    if(len(integers_list) > 0):
        return sum([pair[1] for pair in integers_list if pair[1] is not None]) / len(integers_list)
    else:
        return 0.0
