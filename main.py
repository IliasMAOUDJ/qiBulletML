from src.simulation import Simulation
from src.chatBotGUI import Window
import subprocess as sub
from PyQt5 import QtWidgets
import sys
import threading

if __name__ == "__main__": 
    global queue
    def GUI():  
        app = QtWidgets.QApplication(sys.argv)
        win =  Window()
        win.setGeometry(10,10,480,480)
        win.show()
        app.exec_()

    t = threading.Thread(target=GUI)
    t.start()

    sim = Simulation()
    sim.start()

