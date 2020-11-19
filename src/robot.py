import threading, time, math, pickle
from src.laser import Laser
from src.camera import Camera

<<<<<<< Updated upstream
=======
from tensorflow import keras

>>>>>>> Stashed changes

class Robot(threading.Thread):
    def __init__(self, simulation_manager, client_id):
        threading.Thread.__init__(self)
        self.x = 0
        self.y = 0
<<<<<<< Updated upstream
=======
        self.stop = False
>>>>>>> Stashed changes
        self.pepper = simulation_manager.spawnPepper(client_id, spawn_ground_plane=True)
        #self.pepper.showLaser(True)
        #self.pepper.subscribeLaser()
        #with open("classifier_v3.super", "rb") as file:
        #    self.duck_finder = pickle.load(file)
        self.duck_finder = keras.models.load_model("./model/classifier.h5")
        self.threads = [
            Camera(self,self.pepper, "top", self.duck_finder),
            #Camera(self, self.pepper, "bottom"),
            #Camera(self, self.pepper, "depth"),
            #Laser(self.pepper, "front"),
            #Laser(self.pepper, "left"),
            #Laser(self.pepper, "right")
        ]
        self.pepper.goToPosture("Stand", 0.6)
        self.pepper.setAngles("HeadPitch", 0.361, 1.0)
        for thread in self.threads:
            thread.start()
        self.killed = False

    def kill(self):
        self.killed = True

<<<<<<< Updated upstream
    def move(self, x=0.0, y=0.0, theta=0.0):
        self.x += x
        self.y += y
        self.pepper.moveTo(x, y, theta, frame=2, _async=False)
        print("Local position: \n{} | {}".format(self.x, self.y))

    def run(self):
        self.move(y=-0.7)
        self.move(y=1.4)
        #self.move(x=0.5)
        #self.threads[1].save_img()
=======
    def point_finger(self):
        self.pepper.setAngles("RShoulderPitch", 0.088, 1.0)
        self.pepper.setAngles("RShoulderRoll", -0.377, 1.0)
        self.pepper.setAngles("RElbowYaw", 0.044, 1.0)
        self.pepper.setAngles("RElbowRoll", 0.401, 1.0)
        self.pepper.setAngles("RWristYaw", 0.768, 1.0)
        self.pepper.setAngles("RHand", 0.975, 1.0)

    def move(self, x=0.0, y=0.0, theta=0.0, env=2, speed=1.0):
        self.x += x
        self.y += y
        self.pepper.moveTo(x, y, theta, speed=speed, frame=env, _async=False)

    def run(self):
        while True:
            self.move(theta=math.pi/6, speed=0.6)
            time.sleep(0.001)
            if self.stop:
                break
        #self.move(x=0.5)
        #self.threads[1].save_img()
        #shoulderpitch=0.088
        #shoulderroll=-0.377
        #elbowyaw=0.044
        #elbowroll=0.401
        #wristyaw=0.768
        #rhand=0.975
>>>>>>> Stashed changes
