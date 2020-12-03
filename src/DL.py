import argparse, glob, pickle, random, cv2, numpy as np
from tensorflow import keras
from tensorflow.keras import utils, models, layers
from sklearn.model_selection import train_test_split

def get_new_images(path, new_filename):
    raw_img = []
    print("Read images from " + path)
    for img in glob.glob(path):
        temp_img = cv2.imread(img)
        raw_img.append(temp_img)
    print("Write images to " + new_filename)
    with open(new_filename, "wb") as file:
        pickle.dump(raw_img, file)

def read_images(path):
    with open(path, "rb") as file:
        data = pickle.load(file)
    return data

def main(save=False):
    duck_img = read_images("../data/raw_images.pick")
    not_duck_img = read_images("../data/raw_images_not.pick")

    not_duck_img = not_duck_img[:int(len(duck_img))]

    classes_duck = [1 for i in range(len(duck_img))]
    classes_not_duck = [0 for i in range(len(not_duck_img))]

    seed = random.randint(0,255)

    X = [*duck_img, *not_duck_img]
    random.seed(seed)
    random.shuffle(X)
    y = [*classes_duck, *classes_not_duck]
    random.seed(seed)
    random.shuffle(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    
    X_train = np.array(X_train)
    X_test = np.array(X_test)
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    y_train = utils.to_categorical(y_train, 2)
    y_test = utils.to_categorical(y_test, 2)

    model = models.Sequential()

    model.add(layers.Conv2D(64, kernel_size=3, activation="relu", input_shape=(240, 320, 3)))
    model.add(layers.Conv2D(32, kernel_size=3, activation="relu"))
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.Dropout(0.25))
    model.add(layers.Flatten())
    model.add(layers.Dense(2, activation="softmax"))

    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

    model.fit(X_train, y_train, batch_size=15, epochs=3, verbose=1, validation_data=(X_test, y_test))

    if save:
        model.save("../model/classifier_V2.h5")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        prog="deepl",
        description="Deep learning script",
        add_help=True
    )

    ap.add_argument("-s", "--save", action="store_true", help="Save trained model into a file")
    ap.add_argument("-im", "--import_image", help="Get new images from img folder (-im path|filename)")

    args = vars(ap.parse_args())

    if args["import_image"] != None:
        path = args["import_image"].split("|")[0]
        filename = args["import_image"].split("|")[1]
        get_new_images(path, filename)

    main(args["save"])


