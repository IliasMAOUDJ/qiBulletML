# Imports for PyQt5 Lib and Functions to be used
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRunnable
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget,QApplication
import sys
from keras.models import load_model
import nltk
import time
import json
import pickle
import numpy as np
import random
import threading, queue
import re
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

orders = queue.Queue()
tasks_done = queue.Queue()
talk = queue.Queue()

class Window(QtWidgets.QWidget):
    def __init__(self):
        '''
        Initilize all the widgets then call the GuiSetup to customize them
        '''
        QtWidgets.QWidget.__init__(self)
        self.intents = json.loads(open('./src/intents.json').read())
        self.words = pickle.load(open('./src/words.pkl','rb'))
        self.classes = pickle.load(open('./src/classes.pkl','rb'))
        self.model = load_model('./src/chatbot_model.h5')
        self.layout = QtWidgets.QVBoxLayout(self)
        self.font = QFont()
        self.font.setPointSize(12)
        self.chatlog = QtWidgets.QTextEdit()
        self.chatlog.setReadOnly(True)
        self.userinput = QtWidgets.QLineEdit()
        self.userinput.returnPressed.connect(self.AddToChat)
        self.GuiSetup()
        threading.Thread(target=self.run).start()

    def GuiSetup(self):
        self.chatlog.setStyleSheet(setStyleQte)
        self.userinput.setStyleSheet(setStyletui)
        self.userinput.setFont(self.font)
        self.layout.addWidget(self.chatlog)
        self.layout.addWidget(self.userinput)
        
    def AddToChat(self):
        umsg = self.userinput.text()   
        self.chatlog.append("User: " + umsg)
        self.chatlog.setAlignment(Qt.AlignLeft)
        self.userinput.setText("~wait for answer~")
        self.userinput.setReadOnly(True)
        threading.Thread(target=self.chatbot_response, args=(umsg,)).start()        
        

    def clean_up_sentence(self,sentence): #Remove "useless" words
        sentence_words = nltk.word_tokenize(sentence)
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
        ERROR_THRESHOLD = 0.4
        results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
        # sort by strength of probability
        if(len(results)==0):
            return_list = []
            return_list.append({"intent": "no_result"})
        else:
            results.sort(key=lambda x: x[1], reverse=True)
            return_list = []
            for r in results:
                return_list.append({"intent": self.classes[r[0]], "probability": str(r[1])})
        return return_list

    def getResponse(self, ints, msg, intents_json):
        tag = ints[0]['intent']
        if(tag=="order"):
            self.order(msg)
        else:
            self.talk(tag)
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if(i['tag']== tag):
                result = random.choice(i['responses'])
                break
        return result

    def chatbot_response(self, msg):
        ints = self.predict_class(msg, self.model)
        res = self.getResponse(ints, msg, self.intents)
        self.chatlog.append("PiLDIM: " + res)
        self.chatlog.setAlignment(Qt.AlignRight)
        self.userinput.setReadOnly(False)      
        self.userinput.setText("")
        return res

    def order(self, content):
        global orders
        orders.put(content)

    def talk(self, tag):
        global talk
        talk.put(tag)
        
    def order_done(self, msg):
        self.chatlog.setAlignment(Qt.AlignRight)
        self.chatlog.append(msg)

    def run(self):
        while True:
            global tasks_done
            if(tasks_done.empty() is False):
                msg = tasks_done.get()                            
                self.order_done(msg) 

                


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.setGeometry(10,10,480,480)
    win.show()
    sys.exit(app.exec_())
