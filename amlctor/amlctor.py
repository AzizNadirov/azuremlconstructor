from argparse import ArgumentParser
import os






def main():
    parser = ArgumentParser(description="Parse arguments for amlctor.")

    parser.add_argument(
        '-r', '--run', type=str, required=False, help="Run pipeline constructor and send it to AML"
        )
    parser.add_argument(
        '-i', '--init', type=str, required=False, help="Initialize  pipeline structure."
        )
    parser.add_argument(
        '-a', '--apply', type=str, required=False, help="Apply settings to initialised pipeline."
        )
    parser.add_argument(
        '-e', '--env', type=str, required=False, help="Environment file for building. If empty, you will have to add it by yourself."
        )
    















if __name__ == '__main__':
    pass