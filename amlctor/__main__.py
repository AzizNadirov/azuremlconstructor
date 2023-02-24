from argparse import ArgumentParser
import os






def main():
    parser = ArgumentParser(description="Parse arguments for amlctor.", prog='amlctor')

    commands = parser.add_subparsers(title='main commands')

    run_command = commands.add_parser('run', 
                                      help='Run applyed pipeline.')
    
    run_command.add_argument('-p','--path', type=str,required=True, 
                             help="path of pipeline. '.' for specify current directory")
    

    init_command = commands.add_parser('init', 
                                       help='Initialise pipeline. ')
    
    init_command.add_argument('-n', '--name', type=str, required=True,
                              help="Name of pipeline. Also, will be used as project directory name")
    init_command.add_argument('-p', '--path', type=str, required=True,
                              help="Path where pipeline will be initialised. '.' for specify cwd.")
    init_command.add_argument('-e', '--env', type=str, required=False,
                              help="Env file name for this pipeline. You will have to enter password for decrypt the env")


    apply_command = commands.add_parser('apply', 
                                       help='Apply configs from the settings file and build pipeline.') 
    
    apply_command.add_argument('-p', '--path', type=str, required=True,
                              help="Path to the pipeline. '.' for choose cwd.")
    

    rename_command = commands.add_parser('rename', 
                                       help='Rename step or pipeline.') 
    rename_command.add_argument('-p', '--path', type=str, required=True,
                              help="Path to the pipeline.")
    rename_command.add_argument('-o', '--old_name', type=str, required=True,
                              help="Old pipeline step name.")
    rename_command.add_argument('-n', '--new_name', type=str, required=True,
                              help="New pipeline step name.")
    rename_command.add_argument('-x', '--pipe', required=False, action='store_true',
                              help="pass this flag if it's name of pipeline.")

    args = parser.parse_args()
    print(args)













if __name__ == '__main__':
    main()