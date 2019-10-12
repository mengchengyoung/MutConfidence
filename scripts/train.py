import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from importlib import import_module
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import roc_auc_score, confusion_matrix


class Train():
    """
    Class for command line Train to train model.
    """
    def __init__(self, args):
        self.args = args
        self.input = self.args.input_dir
        self.output = self.args.output_dir
        self.feature = ['strand_bias', 'insert_average', 'mapping_quality', 'base_quality', 
                        'GC', 'frequency', 'depth', 'FOXOG', 'NORMAL', 'Tlodfstar', 'PONFilter',]
        self.model = self.args.model
        
    def prepare_data(self):
        assert os.path.exists(self.input), 'Input data is not found'
        df = pd.read_csv(self.input)
        filter_df = df[ df.FOXOG != '.' ]
        rus = RandomUnderSampler(random_state=42)
        resample_x, resample_y = rus.fit_resample(filter_df[self.feature], filter_df['confidence'])
        resample_y = resample_y.reshape(resample_y.shape[0], 1)
        resample_array = np.append(resample_x, resample_y, axis=1)
        train, test = train_test_split(resample_array, test_size=0.2)  
        x_train, y_train = train[:,:-1], train[:,-1]
        x_test, y_test = test[:,:-1], test[:,-1]

        return (x_train, y_train), (x_test, y_test)

    def load_model(self):
        mod = "lib.model.model.{}".format(self.model)
        module = import_module(mod)
        model = getattr(module, self.model.title())
        return model

    def process(self):
        train, test = self.prepare_data()
        model = self.load_model()
        process = model(train, test, self.feature, self.args)
        process.run()
        
