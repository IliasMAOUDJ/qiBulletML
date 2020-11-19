import threading, time

class Laser(threading.Thread):

    def __init__(self, pepper, side):
        threading.Thread.__init__(self)
        self.pepper = pepper
        self.detection = False
        self.side = side
        self.killed = False
    
    def isDetection(self):
        for laser in self.detection:
            if laser:
                return True
        return False

    def kill(self):
        self.killed = True

    def run(self):
        while True:
            if not self.killed:
                if self.side == "right":
                    self.lasers = self.pepper.getRightLaserValue()
                elif self.side == "left":
                    self.lasers = self.pepper.getLeftLaserValue()
                elif self.side == "front":
                    self.lasers = self.pepper.getFrontLaserValue()
                else:
                    print("No laser found")
                    break

                self.detection = [False for l in self.lasers]

                for index, laser in enumerate(self.lasers):
                    if laser < 2.5:
                        self.detection[index] = True
                    else:
                        self.detection[index] = False
                time.sleep(1)
            else:
                break