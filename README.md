# qiBulletML
Project using qiBullet (python)

This project is part of the MSc of Computer Science (SIIA) at the University of Western Brittany. 
It was developped by Pierre LE DEZ and Ilias MAOUDJ between october and december 2020. 
It includes Computer Vision via Object Detection and Human/Robot Interaction via Chat.

PiLDIM (named after the developers) is a Pepper robot that interacts with humans and can recognize ducks.

## Installation

```console
# clone the repo
$ git clone https://github.com/IliasMAOUDJ/qiBulletML.git

# change the working directory to qiBulletML
$ cd qiBulletML

# install the requirements
$ pip install -r requirements.txt

```

## Usage

```console
# for main application
$ python main.py

# for CNN
$ python src/DL.py [-s] [-im path_folder] [-h]
  optional arguments:
    -h, --help                                    Show this help message and exit
    -s, --save                                    Save trained model into a "h5" file
    -im path_folder, --import_image path_folder   Get new images from path_folder
    
# for chatBot
$ python src/train_chatbot.py

*It is possible to add more dialogue options by filling "src/data/intents.json"
```


Screenshots and demonstration video below:
https://www.youtube.com/watch?v=UVsZ72RsFcs&feature=youtu.be
![alt text](https://github.com/IliasMAOUDJ/qiBulletML/blob/master/Screenshots/Hello.png)
![alt text](https://github.com/IliasMAOUDJ/qiBulletML/blob/master/Screenshots/MoveTo.png)
![alt text](https://github.com/IliasMAOUDJ/qiBulletML/blob/master/Screenshots/FindDuck.png)
![alt text](https://github.com/IliasMAOUDJ/qiBulletML/blob/master/Screenshots/DuckHere.png)
