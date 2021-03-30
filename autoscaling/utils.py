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
