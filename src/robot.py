import threading
from src.camera import Camera
import math
import time
import src.chatBotGUI
import re
import nltk
import numpy as np
from tensorflow import keras

orders = src.chatBotGUI.orders
tasks_done = src.chatBotGUI.tasks_done
talk = src.chatBotGUI.talk

class Robot(threading.Thread):
    def __init__(self, simulation_manager, client_id):
        threading.Thread.__init__(self)
        self.pepper = simulation_manager.spawnPepper(client_id, spawn_ground_plane=True)
        self.duck_finder = keras.models.load_model("./model/classifier_V2.h5")
        self.threads = [
            Camera(self, self.pepper, "top", self.duck_finder),
        ]
        self.initialPosture()
        for thread in self.threads:
            thread.start()
        self.killed = False
        self.stop = False

    def initialPosture(self):
        self.pepper.goToPosture("Stand", 0.6)
        self.pepper.setAngles("HeadPitch", 0.361, 1.0)

    def kill(self):
        self.killed = True

    def point_finger(self):
        self.pepper.setAngles("RShoulderPitch", 0.088, 1.0)
        self.pepper.setAngles("RShoulderRoll", -0.377, 1.0)
        self.pepper.setAngles("RElbowYaw", 0.044, 1.0)
        self.pepper.setAngles("RElbowRoll", 0.401, 1.0)
        self.pepper.setAngles("RWristYaw", 0.768, 1.0)
        self.pepper.setAngles("RHand", 0.975, 1.0)
        time.sleep(4)
        self.initialPosture()
        

    def move(self, x=0.0, y=0.0, theta=0.0, asynch=False, facedirection = True):
        angle = 0
        if(facedirection):
            angle = np.angle(complex(x,y))
        self.pepper.moveTo(0, 0,theta=angle, _async= asynch)
        self.pepper.moveTo(np.linalg.norm([x,y,0]), y=0, theta=0, frame=2, _async= asynch)
        #print("Local position: \n{} | {}".format(self.x, self.y))
    

    def findWholeWord(self,w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def isnumber(self, word): #handles negative numbers as well because isdigit() only works for without the minus sign
        for char in word:
            isnum = char.isdigit()
            if(isnum==True):
                return True
        return False


    #If PiLDIM recognizes an order, he processes it here.
    def order(self, content):
        if (self.findWholeWord('go')(content) or self.findWholeWord('move')(content)):          
            sentence_words = nltk.word_tokenize(content)
            position = [float(word) for word in sentence_words if self.isnumber(word)]
            if(len(position)==2):              
                self.move(x=position[0],y=position[1])
                content = "Moving to: x= "+ str(position[0]) + ", y= "+ str(position[1]) 
            else:
                content = "I couldn't move to this position, make sure you asked correctly."
        elif (self.findWholeWord('find')(content)):
            self.find_duck()
            content = "Here it is!"
        elif (self.findWholeWord('come')(content)): #Feature not developed at the moment
            pass
        elif (self.findWholeWord('stop')(content)):
            self.pepper.stopMove()
        tasks_done.put(content)


    #PiLDIM will do a gesture according to the intent
    def perform_action(self, tag):
        if(tag=="greeting" or tag=="goodbye"):
            self.pepper.setAngles('LShoulderPitch', -0.5, 0.6)       
        elif(tag=="thanks"):
            self.pepper.setAngles('HipPitch', -0.5,0.6)
        elif(tag=="no_result"):
            self.pepper.setAngles('HeadYaw', -0.5,0.6)
            time.sleep(1)
            self.pepper.setAngles('HeadYaw', 0.5,0.6)
            time.sleep(1)
            self.pepper.setAngles('HeadYaw', 0,0.6)
        elif(tag=="who"):
            self.pepper.setAngles('RShoulderPitch',0.5,0.4)
            self.pepper.setAngles('RElbowYaw',0.35,0.4)
            self.pepper.setAngles('RElbowRoll',1.1,0.4)
            self.pepper.setAngles('RWristYaw',1.3,0.4)
        time.sleep(2)
        self.initialPosture()

    
    def find_duck(self):
        #self.threads[0].search_duck = True
        while True:
            self.pepper.moveTo(x=0.0, y=0.0, theta=math.pi/5, speed=0.6, _async=False)
            self.threads[0].find_duck_in_big_image()
            if self.stop:
                break


    def run(self):
        while True:       
            global orders
            if(orders.empty() is False):
                self.order(orders.get())
            global talk
            if(talk.empty() is False):
                self.perform_action(talk.get())
        #self.threads[1].save_img()