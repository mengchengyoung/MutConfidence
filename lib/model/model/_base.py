#!/usr/bin/env python3
""" Base class for Models. ALL Models should at least inherit from this class
    When inheriting model_data should be a list of NNMeta objects.
    See the class for details.
"""
import logging
import os
import sys

class Modelbase():
    def __init__(self, train, test, feature, args):
        self.feature = feature
        self.model = self.build()
        self.args = args
        self.fullpath = self.args.output_dir
        self.train_data = train
        self.test_data = test

    def build(self):
        """
        build the model  and return it
        """
        raise NotImplementedError

    def save(self, filename=None):
        """
        override this function if hte model doesn't
        build with Keras
        """
        assert os.path.exists(self.fullpath), 'Model OutPath Not Exist!'
        path = self.fullpath
        if filename :
            filename = os.path.join(self.fullpath, filename)
        else:
            filename = os.path.join(path, 'original.h5')
        self.model.save(filename)
         
    def run(self):
        """
        Override to train the model and do somthing else.
        """
        raise NotImplementedError

    def auto_save(self):
        """
        override this funciton to auto save the model
        """
        pass 
