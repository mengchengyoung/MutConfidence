from ._base import Modelbase
import os 
import keras
from keras import losses
from keras import backend as K
from keras.layers import Input, Dense, Dropout
from keras.models import load_model, Model
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, confusion_matrix
from keras.callbacks import ModelCheckpoint

class Dnn(Modelbase):
    """
    DNN model
    """
    
    def build(self):
        network = keras.Sequential()
        network.add(Dense(32, activation='relu', input_shape=(len(self.feature),)))
        network.add(Dropout(rate=0.2))
        network.add(Dense(16, activation='relu'))
        network.add(Dropout(rate=0.2))
        network.add(Dense(10, activation='relu'))
        network.add(Dropout(rate=0.2))
        network.add(Dense(5, activation='relu'))
        network.add(Dropout(rate=0.1))
        network.add(Dense(1, activation='sigmoid'))
        network.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy'])
        return network
    
    def validation(self, history):
        validation_file = os.path.join(self.fullpath, 'validation.jpg')
        plt.plot(history.history['acc'], label = 'train')
        plt.plot(history.history['val_acc'], label = 'test')
        plt.title('Model accuracy')
        plt.ylabel('accuracy')
        plt.xlabel('epoch')
        plt.legend(loc='lower right')
        plt.savefig(validation_file)
        
    def run(self):
        x_train, y_train =  self.train_data
        x_test, y_test = self.test_data
        filepath="/annoroad/data1/bioinfo/PMO/yangmengcheng/Work/MutConfidence-Model/data/model/weights-improvement-{epoch:02d}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
        callbacks_list = [checkpoint]
        history = self.model.fit(x_train, y_train, epochs=5000, batch_size=32, validation_split=0.10, callbacks=callbacks_list)
        if self.args.validation:
            self.validation(history)
        self.save()
