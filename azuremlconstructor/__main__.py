from azuremlconstructor.init.args_handling import parse_args, ArgsHandler



def main():
    args = parse_args()
    ArgsHandler(args).launch()

if __name__== '__main__':
    main()
