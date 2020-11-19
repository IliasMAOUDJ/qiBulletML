import threading
from src.laser import Laser
from src.camera import Camera
import math
import time
import src.chatBotGUI
import re
import nltk
import numpy as np
orders = src.chatBotGUI.orders
tasks_done = src.chatBotGUI.tasks_done
talk = src.chatBotGUI.talk

class Robot(threading.Thread):
    def __init__(self, simulation_manager, client_id):
        threading.Thread.__init__(self)
        self.x = 0
        self.y = 0
        self.theta = 0

        self.pepper = simulation_manager.spawnPepper(client_id, spawn_ground_plane=True)
        self.pepper.showLaser(True)
        self.pepper.subscribeLaser()
        self.threads = [
            Camera(self.pepper, "top"),
            Camera(self.pepper, "bottom"),
            Camera(self.pepper, "depth"),
            Laser(self.pepper, "front"),
            Laser(self.pepper, "left"),
            Laser(self.pepper, "right")
        ]
        self.pepper.goToPosture("Stand", 0.6)
        for thread in self.threads:
            thread.start()
        self.killed = False

    def kill(self):
        self.killed = True

    def move(self, x=0.0, y=0.0, theta=0.0, sync=False, facedirection = True):
        self.x = x
        self.y = y
        self.pepper.moveTo(x, y, theta, frame=1, _async= sync)
        #print("Local position: \n{} | {}".format(self.x, self.y))
    

    def findWholeWord(self,w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def isnumber(self, word): #handles negative numbers as well because isdigit() only works for without the minus sign
        for char in word:
            isnum = char.isdigit()
            if(isnum==True):
                return True
        return False

    def order(self, content):
        if (self.findWholeWord('go')(content)):          
            sentence_words = nltk.word_tokenize(content)
            position = [float(word) for word in sentence_words if self.isnumber(word)]
            if(len(position)==2):              
                self.move(x=position[0],y=position[1],sync=True)
                content = "Going to: x= "+ str(position[0]) + ", y= "+ str(position[1]) 
            else:
                content = "I couldn't move to this position, make sure you asked correctly."
        elif (self.findWholeWord('find')(content)):
            pass
        elif (self.findWholeWord('come')(content)):
            pass
        elif (self.findWholeWord('stop')(content)):
            self.move(x=0,y=0, sync=True)
        tasks_done.put(content)


    def perform_action(self, tag):
        if(tag=="greeting"):
            self.pepper.setAngles('LShoulderPitch', -0.5, 0.6)
            time.sleep(2)
            self.pepper.goToPosture("Stand", 0.6)
        elif(tag=="thanks"):
            pass
        else:
            pass
    
    def run(self):
        while True:
            for obj in self.threads:
                if isinstance(obj,Camera):
                    if obj.circle_found == True:
                        pass
                        #self.move(x=0.1)
                        #print("circle found")
            
            global orders
            if(orders.empty() is False):
                self.order(orders.get())
            global talk
            if(talk.empty() is False):
                self.perform_action(talk.get())
        #self.threads[1].save_img()