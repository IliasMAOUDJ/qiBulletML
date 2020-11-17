from src.simulation import Simulation
from src.chatBotGUI import Window
import subprocess as sub
from PyQt5 import QtWidgets
import sys
import threading
if __name__ == "__main__": 
    def GUI():
        app = QtWidgets.QApplication(sys.argv)
        win =  Window()
        win.setGeometry(10,10,480,480)
        win.show()
        app.exec_()

    def Sim():
        sim = Simulation()
        sim.run()
    t = threading.Thread(target=Sim)
    t.start()

    t2 = threading.Thread(target=GUI)
    t2.start()
    #GUI()


    #filepath1= 'src/Server.py'
    #chatbotServer = sub.Popen(['start', 'cmd', '/k', '%s %s'%(sys.executable, filepath1)], shell = True)   
    #filepath2= 'src/Client.py'
    #chatbotClient = sub.Popen(['start', 'cmd', '/k', '%s %s'%(sys.executable, filepath2)], shell = True)
    #filepath3= 'src/simulation.py'
    #simulation = sub.Popen(['start', 'cmd', '/k', '%s %s'%(sys.executable, filepath3)], shell = True)
    #sim = Simulation()
    #sim.run()