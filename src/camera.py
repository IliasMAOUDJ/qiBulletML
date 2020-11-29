import threading, cv2, numpy as np, time
from qibullet import PepperVirtual


def pyramid(image, scale=1.5, minSize=(30, 30)):
    # yield the original image
    yield image

    # keep looping over the pyramid
    while True:
        # compute the new dimensions of the image and resize it
        w = int(image.shape[1] / scale)
        image = imutils.resize(image, width=w)

        # if the resized image does not meet the supplied minimum
        # size, then stop constructing the pyramid
        if image.shape[0] < minSize[1] or image.shape[1] < minSize[0]:
            break

        # yield the next image in the pyramid
        yield image

def sliding_window(image, stepSize, windowSize):
    # slide a window across the image
    for y in range(0, image.shape[0], stepSize):
        for x in range(0, image.shape[1], stepSize):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

class Camera(threading.Thread):
    
    def __init__(self, parent, pepper, id_camera, classifier):
        threading.Thread.__init__(self)
        self.parent = parent
        self.pepper = pepper
        self.classifier = classifier
        self.id_camera = id_camera
        self.killed = False
        self.duck_found = False
        self.search_duck = False

    def kill(self):
        self.killed = True

    def save_img(self):
        filename=self.id_camera+"_camera.png"
        img = self.pepper.getCameraFrame(self.handle)
        cv2.imwrite(filename, img)
        #print("Image saved")

    def find_duck_in_big_image(self):
        #get current image from camera and put it in an array
        img_array = [self.pepper.getCameraFrame(self.handle)]
        img_array = np.array(img_array)
        prediction = self.classifier.predict(img_array)[0]
        print(prediction)
        #prediction[0] is "not duck" and prediction[1] is "there is a duck"
        if prediction[1] > 0.95:
            print("Youpi, canard trouvé")
            self.duck_found = True
            self.parent.stop = True
            self.parent.point_finger()
            self.find_duck_accurately(img_array[0])

    def find_duck_accurately(self, img):
        (winW, winH) = (128,128)
        find = False
        for resized in pyramid(img, scale=1.5):
            for (x, y, window) in sliding_window(resized, stepSize=32, windowSize=(winW, winH)):
                if window.shape[0] != winH or window.shape[1] != winW:
                    continue

                image = window.copy()
                image = cv2.resize(image, (320,240), interpolation=cv2.INTER_AREA)
                img_array = np.array([image])
                prediction = self.classifier.predict(img_array)[0]
                if prediction[1] > 0.95:
                    find = True

                if find:
                    clone = resized.copy()
                    cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 0, 255), 2)
                    cv2.putText(clone, 'A Duck is here', (x, y + winH + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)
                    cv2.imshow("Window", clone)
                    cv2.waitKey(1)
                    break
            if find:
                break
        
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
            if not self.killed and self.search_duck:
                img = self.pepper.getCameraFrame(self.handle)
                if self.id_camera == "depth":
                    filename= "./ImageDepth.png"
                    cv2.imwrite(filename, img)
                    im_gray = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
                    im_color = cv2.applyColorMap(im_gray, cv2.COLORMAP_HSV)
                    cv2.imshow("colorBar depth camera", im_color)
                else:
                    if self.classifier != None and not self.duck_found:
                        self.find_duck_in_big_image()
                    cv2.imshow(self.id_camera+" camera Frame", img)
                    #self.find_circle(img)
            if self.killed:
                break
            time.sleep(0.01)
        
