#!/annoroad/data1/bioinfo/PROJECT/RD/Medical/Leukemia/software/lib/python/anaconda3/bin/python3

import argparse
import logging
from importlib import import_module
import sys
import os
logger = logging.getLogger(__name__)

class FullHelpArgumentParser(argparse.ArgumentParser):
    """ Identical to the built-in argument parser, but on error it
        prints full help message instead of just usage information """
    def error(self, message):
        self.print_help(sys.stderr)
        args = {"prog": self.prog, "message": message}
        self.exit(2, "%(prog)s: error: %(message)s\n" % args)

class ScriptExecutor():
    """ Loads the relevant script modules and executes the script.
        This class is initialised in each of the argparsers for the relevant
        command, then execute script is called within their set_default
        function. """

    def __init__(self, command, subparsers=None):
        self.command = command.lower()
        self.subparsers = subparsers

    def import_script(self):
        """ Only import a script's modules when running that script."""
        cmd = os.path.basename(sys.argv[0])
        src = "scripts"
        mod = ".".join((src, self.command.lower()))
        module = import_module(mod)
        script = getattr(module, self.command.title())
        return script
    
    def execute_script(self, arguments):
        """ Run the script for called command """
        #log_setup(arguments.loglevel, arguments.logfile, self.command, is_gui)
        logger.debug("Executing: %s. PID: %s", self.command, os.getpid())
        try:
            script = self.import_script()
            process = script(arguments)
            process.process()

        except KeyboardInterrupt:  # pylint: disable=try-except-raise
            raise
        except SystemExit:
            #pass
            raise
        

class MutArgs():
    """ Mutconfidenc model argument parser functions that are universal
        to all commands. Should be the parent function of all
        subsequent argparsers """
    def __init__(self, subparser, command,
                 description="default", subparsers=None):

        self.global_arguments = self.get_global_arguments()
        self.argument_list = self.get_argument_list()
        self.optional_arguments = self.get_optional_arguments()
        if not subparser:
            return

        self.parser = self.create_parser(subparser, command, description)
        self.add_arguments()

        script = ScriptExecutor(command, subparsers)
        self.parser.set_defaults(func=script.execute_script)

    @staticmethod
    def get_argument_list():
        """ Put the arguments in a list so that they are accessible from both
            argparse and gui override for command specific arguments """
        argument_list = []
        return argument_list

    @staticmethod
    def get_optional_arguments():
        """ Put the arguments in a list so that they are accessible from both
            argparse and gui. This is used for when there are sub-children
            Override this for custom arguments """
        argument_list = []
        return argument_list

    @staticmethod
    def get_global_arguments():
        """ Arguments that are used in ALL parts of Faceswap
            DO NOT override this """
        global_args = list()
        global_args.append({"opts": ("-L", "--loglevel"),
                    "type": str.upper,
                    "dest": "loglevel",
                    "default": "INFO",
                    "choices": ("INFO", "VERBOSE", "DEBUG", "TRACE"),
                    "help": "Log level. Stick with INFO or VERBOSE unless you need to "
                            "file an error report. Be careful with TRACE as it will "
                            "generate a lot of data"})
        return global_args
    @staticmethod
    def create_parser(subparser, command, description):
        """ Create the parser for the selected command """
        parser = subparser.add_parser(
            command,
            help=description,
            description=description,
            formatter_class=argparse.HelpFormatter)
        return parser

    def add_arguments(self):
        """ Parse the arguments passed in from argparse """
        options = self.global_arguments + self.argument_list + self.optional_arguments
        for option in options:
            args = option["opts"]
            kwargs = {key: option[key] for key in option.keys() if key != "opts"}
            self.parser.add_argument(*args, **kwargs)

class GenerateArgs(MutArgs): 
    """
    Class to parse command line arguments for Generating trainning data
    """

    @staticmethod
    def get_optional_arguments():
        argument_list = []
        argument_list.append({"opts": ("-p", "--positive-dir"),
                              "default": "/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/data/Commercial_V3",
                              "required": True,
                              "dest": "input_dir",
                              "help": "negitive dir of raw data path, default is leu path"
                                      "/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/data/Commercial_V3"
                                      "if change the path, should override the File class in ../scripts/generate.py" })
        argument_list.append({"opts": ("-n", "--negtive-dir"),
                              "default": "/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/data/Commercial_V3",
                              "required": True,
                              "dest": "negtive_dir",
                              "help": "negitive dir of raw data path, default is leu path"
                                      "/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/data/Commercial_V3"
                                      "if change the path, should override the File class in ../scripts/generate.py" })        
        argument_list.append({"opts": ("-o", "--output-dir"),
                              "required": True,
                              "dest": "output_dir",
                              "help": "Output dir Trainning data will be generated, there will be one file generated by default."
                                      "suffix is not supported so far." })

        return argument_list

class TrainArgs(MutArgs):
    """
    Class to parse command line argumnets for Trainning the model
    """

    @staticmethod
    def get_optional_arguments():
        argument_list = []
        argument_list.append({"opts": ("-i", "--input-dir"),
                              "required": True,
                              "dest": "input_dir",
                              "help": "Input dir of train data path"
                                      "if change the path, should override the File class in ../scripts/train.py" })

        argument_list.append({"opts": ("-o", "--output-dir"),
                              "required": True,
                              "dest": "output_dir",
                              "help": "Output dir that the model will be saved, suffix is not supported so far." })

        argument_list.append({"opts": ("-v", "--validation"),
                              "action": "store_true",
                              "default": True,
                              "help": "defautl to output validation"
                            })
        argument_list.append({"opts": ("-m", "--model"),
                              "required": True,
                              "default": "dnn",
                              "choices": ["dnn", "logistic"],
                              "help": "choose the model"
                            })
        return argument_list
        
class PredictArgs(MutArgs):
    @staticmethod
    def get_optional_arguments():
        argument_list = []
        argument_list.append({"opts": ("-v", "--vcf"),
                              "default": None,
                              'required': True,
                              'dest': 'vcf_file',
                              'help': 'input should be a vcf format file.'
                        })
        argument_list.append({"opts": ("-b", "--bam"),
                              "default": None,
                              "required": True,
                              "dest": "bam_file",
                              "help": "bamfile corresponded to the vcf file."
                        })
        argument_list.append({"opts": ("-m", "--model"),
                              "default": None,
                              "required": True,
                              "dest": "model_file",
                              "help": "model file you want to use."
                        })

        return argument_list
