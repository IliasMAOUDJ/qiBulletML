# Imports for PyQt5 Lib and Functions to be used
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRunnable
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget,QApplication
import sys
from keras.models import load_model
import nltk
#nltk.download('punkt')
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer

import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import random
import threading
# To make it work from one session to another
import tensorflow as tf
# alignment to PyQt Widgets
setStyleQte = """QTextEdit {
    font-family: "Courier"; 
    font-size: 12pt; 
    font-weight: 600; 
    text-align: right;
    background-color: Gainsboro;
}"""

setStyletui = """QLineEdit {
    font-family: "Courier";
    font-weight: 600; 
    text-align: left;
    background-color: Gainsboro;
}"""

config = tf.compat.v1.ConfigProto(gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)

class Window(QtWidgets.QWidget):
    def __init__(self):
        '''
        Initilize all the widgets then call the GuiSetup to customize them
        '''
        QtWidgets.QWidget.__init__(self)
        self.lemmatizer = WordNetLemmatizer()
        self.intents = json.loads(open('./src/intents.json').read())
        self.words = pickle.load(open('./src/words.pkl','rb'))
        self.classes = pickle.load(open('./src/classes.pkl','rb'))
        self.model = load_model('./src/chatbot_model.h5')
        self.v = None
        self.layout = QtWidgets.QVBoxLayout(self)
        self.font = QFont()
        self.font.setPointSize(12)
        self.chatlog = QtWidgets.QTextEdit()
        self.userinput = QtWidgets.QLineEdit()
        self.userinput.returnPressed.connect(self.AddToChat)
        self.GuiSetup()
        print("end of setup GUI")

    def GuiSetup(self):
        self.chatlog.setStyleSheet(setStyleQte)
        self.userinput.setStyleSheet(setStyletui)
        self.userinput.setFont(self.font)
        self.layout.addWidget(self.chatlog)
        self.layout.addWidget(self.userinput)
        
    def AddToChat(self):
        umsg = self.userinput.text()
        self.chatlog.setAlignment(Qt.AlignLeft)
        self.chatlog.append("User: " + umsg)
        self.chatlog.setAlignment(Qt.AlignLeft)
        self.userinput.setText("")
        print(threading.active_count())
        self.chatbot_response(umsg)
        

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        #BLOQUE ICI
        #sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        #
        return sentence_words

    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def bow(self, sentence, words, show_details=True):
        # tokenize the pattern
        sentence_words = self.clean_up_sentence(sentence)
        # bag of words - matrix of N words, vocabulary matrix
        bag = [0]*len(words)
        for s in sentence_words:
            for i,w in enumerate(words):
                if w == s:
                    # assign 1 if current word is in the vocabulary position
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % w)
        return(np.array(bag))

    def predict_class(self, sentence, model):
        # filter out predictions below a threshold
        p = self.bow(sentence, self.words,show_details=False)
        res = model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.2
        results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
        # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": self.classes[r[0]], "probability": str(r[1])})
        return return_list

    def getResponse(self, ints, intents_json):
        tag = ints[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if(i['tag']== tag):
                result = random.choice(i['responses'])
                break
        return result

    def chatbot_response(self, msg):
        ints = self.predict_class(msg, self.model)
        print(ints)
        res = self.getResponse(ints, self.intents)
        self.chatlog.append("PEPPER: " + res)
        self.chatlog.setAlignment(Qt.AlignRight)
        return res

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.setGeometry(10,10,480,480)
    win.show()
    sys.exit(app.exec_())
