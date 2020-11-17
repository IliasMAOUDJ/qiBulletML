import threading
from src.laser import Laser
from src.camera import Camera
import math

class Robot(threading.Thread):
    def __init__(self, simulation_manager, client_id):
        threading.Thread.__init__(self)
        self.x = 0
        self.y = 0

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

    def move(self, x=0.0, y=0.0, theta=0.0):
        self.x += x
        self.y += y
        self.pepper.moveTo(x, y, theta, frame=2, _async=False)
        #print("Local position: \n{} | {}".format(self.x, self.y))
    


        
    def run(self):
        while True:
            for obj in self.threads:
                if isinstance(obj,Camera):
                    if obj.circle_found == True:
                        self.move(x=0.1)
                        print("circle found")
            self.move(theta=math.pi/4)
            
        #self.threads[1].save_img()