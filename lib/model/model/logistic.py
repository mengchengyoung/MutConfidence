#!/annoroad/data1/bioinfo/PMO/yangmengcheng/SoftWare/Anaconda3-5.3.1/envs/ML/bin/python 
from ._base import Modelbase
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn import model_selection
from sklearn.metrics import accuracy_score
import os 
import pandas as pd

class Logistic(Modelbase):
        
    def build(self):
        return LogisticRegression(random_state=1)

    def save(self, filename=None):
        assert os.path.exists(self.fullpath), 'Model OutPath Not Exist!'
        path = self.fullpath
        if filename :
            filename = os.path.join(self.fullpath, filename)
        else:
            filename = os.path.join(path, 'original.pkl')
        joblib.dump(self.model, filename)

    def run(self):
        x_train, y_train =  self.train_data
        x_test, y_test = self.test_data
        #x_train = pd.DataFrame(x_train)
        y_train = y_train.reshape(y_train.shape[0], )
        print(x_train.shape, y_train.shape)
        print(y_train.ndim, y_train.shape)
        y=y_train
        print(y.dtype == object, not isinstance(y.flat[0], str), len(y))
        #scores = model_selection.cross_val_score(self.model, x_train, y_train, cv=10)
        self.model.fit(x_train, y_train)
        result = self.model.predict(x_test)
        self.save()
        print(accuracy_score(result, y_test))


