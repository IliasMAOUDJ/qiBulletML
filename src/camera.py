import threading, cv2, numpy as np
from qibullet import PepperVirtual

class Camera(threading.Thread):
    
    def __init__(self, pepper, id_camera):
        threading.Thread.__init__(self)
        self.pepper = pepper
        self.id_camera = id_camera
        self.killed = False
        self.circle_found = False

    def kill(self):
        self.killed = True

    def save_img(self):
        filename=self.id_camera+"_camera.png"
        img = self.pepper.getCameraFrame(self.handle)
        cv2.imwrite(filename, img)
        #print("Image saved")

    def run(self):
        if self.id_camera == "top":
            self.handle = self.pepper.subscribeCamera(PepperVirtual.ID_CAMERA_TOP)
        elif self.id_camera == "bottom":
            self.handle = self.pepper.subscribeCamera(PepperVirtual.ID_CAMERA_BOTTOM)
        elif self.id_camera == "depth":
            self.handle = self.pepper.subscribeCamera(PepperVirtual.ID_CAMERA_DEPTH)
        else:
            print("No camera found")
            return
        while True:
            if not self.killed:
                img = self.pepper.getCameraFrame(self.handle)
                if self.id_camera == "depth":
                    filename= "./ImageDepth.png"
                    cv2.imwrite(filename, img)
                    im_gray = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
                    im_color = cv2.applyColorMap(im_gray, cv2.COLORMAP_HSV)
                    cv2.imshow("colorBar depth camera", im_color)
                else:
                    #cv2.imshow(self.id_camera+" camera Frame", img)
                    self.find_circle(img)
                cv2.waitKey(1)
            else:
                break

    def find_circle(self, img):
        img_gray = img.copy()
        img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 4, 10, minRadius=0, maxRadius=50)
        if circles is not None:
            self.circle_found = True
            #print("circle_found")
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(img, (x, y), r, (0, 255, 0), 4)
        else: 
            self.circle_found = False
        cv2.imshow(self.id_camera+" camera Frame", img)
        
