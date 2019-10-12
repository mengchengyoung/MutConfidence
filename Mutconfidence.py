#!/annoroad/data1/bioinfo/PROJECT/RD/Medical/Leukemia/software/lib/python/anaconda3/bin/python3
""" The master script of Mutconfidence """
import sys
import lib.cli as cli

if sys.version_info[0] < 3:
    raise Exception("This program requires at least python3")

def bad_args(args):
    PARSER.print_help()
    exit(0)

if __name__ == '__main__':
    PARSER = cli.FullHelpArgumentParser()    
    SUBPARSER = PARSER.add_subparsers()
    Generate = cli.GenerateArgs(
                SUBPARSER,
                "Generate",
                "Generate trainning data from vcf files"
                )
    Train = cli.TrainArgs(
            SUBPARSER,
            "Train",
            "Train the model"
            )
    Predict = cli.PredictArgs(
            SUBPARSER,
            "Predict",
            "calculate the confidence of th mutation"
            )
    PARSER.set_defaults(func=bad_args)
    ARGUMENTS = PARSER.parse_args()
    ARGUMENTS.func(ARGUMENTS)
