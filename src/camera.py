import threading, cv2, numpy as np
import time
from qibullet import PepperVirtual

class Camera(threading.Thread):
    
    def __init__(self, parent, pepper, id_camera, classifier=None):
        threading.Thread.__init__(self)
        self.parent = parent
        self.pepper = pepper
        self.classifier = classifier
        self.id_camera = id_camera
        self.duck_found = False
        self.killed = False
        self.photo = [i for i in range(100)]

    def kill(self):
        self.killed = True

    def save_img(self):
        filename="./img_mix/"+str(int(time.time()*1000))+".png"
        img = self.pepper.getCameraFrame(self.handle)
        cv2.imwrite(filename, img)
        print("Image saved")

    def find_duck(self):
        img_array = [self.pepper.getCameraFrame(self.handle)]
        img_array = np.array(img_array)
        #img_array = np.asarray([(img-img.mean())/img.std() for img in img_array])
        #img = img_array.reshape((img_array.shape[0], -1))
        prediction = self.classifier.predict(img_array)[0]
        print(prediction)
        if prediction[1] > 0.95:
            print("Youpi, canard trouvé")
            self.duck_found = True
            self.parent.stop = True
            self.parent.point_finger()

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
                    filename= "../ImageDepth.png"
                    cv2.imwrite(filename, img)
                    im_gray = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
                    im_color = cv2.applyColorMap(im_gray, cv2.COLORMAP_HSV)
                    cv2.imshow("colorBar depth camera", im_color)
                else:
                    if self.classifier != None and not self.duck_found:
                        self.find_duck()
                    if self.id_camera == "top":
                        pass#self.save_img()
                    cv2.imshow(self.id_camera+" camera Frame", img)
                    #self.find_cirle(img)
                cv2.waitKey(1)
            else:
                break

    def find_cirle(self, img):
        img_gray = img.copy()
        img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 4, 10, minRadius=0, maxRadius=50)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(img, (x, y), r, (0, 255, 0), 4)
        cv2.imshow(self.id_camera+" camera Frame", img)
