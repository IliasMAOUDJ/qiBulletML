import cv2
import time
from qibullet import SimulationManager
from qibullet import PepperVirtual
import pybullet as p
import sys
import random
import pyntcloud as pc

def showCam(robot, name, handle) :
   img = robot.getCameraFrame(handle)
   cv2.imshow(name, img)
   return img



def main():
    simulation_manager = SimulationManager()
    client = simulation_manager.launchSimulation(gui=True)
    pepper = simulation_manager.spawnPepper(client,
                                            translation = [0,0,0],
                                            spawn_ground_plane=True)

    #Creation objet 3d
    p.connect(p.DIRECT)
    cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.125,0.125,0.125])
    cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.25,0.25,0.25])
    cube_body = p.createMultiBody( baseMass=0, baseCollisionShapeIndex=cube_collision,baseVisualShapeIndex=cube_visual, basePosition = [6,0, 0.725])

    #Balls
    for i in range(15):
        r = random.random()
        g = random.random()
        b = random.random()
        sphere_visual = p.createVisualShape(p.GEOM_SPHERE, radius=0.2, rgbaColor = [r,g,b,1])
        sphere_collision = p.createCollisionShape(p.GEOM_SPHERE)
        x= random.randint(0,18)
        y = random.randint(0,18)
        z = random.randint(0,2)
        sphere_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex= sphere_collision, baseVisualShapeIndex=sphere_visual, basePosition = [x-9,y-9,z+0.2])


    for i in range(15):
        r = random.random()
        g = random.random()
        b = random.random()
        cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.125,0.125,0.125], rgbaColor = [r,g,b,1])
        cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.25,0.25,0.25])
        x= random.randint(0,18)
        y = random.randint(0,18)
        z = random.randint(0,2)
        cube_body = p.createMultiBody( baseMass=0, baseCollisionShapeIndex=cube_collision,baseVisualShapeIndex=cube_visual, basePosition = [x,y,z])

    #Walls
    cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[10,0.2,2])
    cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[10,0.2,2])
    cube_body = p.createMultiBody( baseMass=0, baseCollisionShapeIndex=cube_collision,baseVisualShapeIndex=cube_visual, basePosition = [0,10, 1])

    cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[10,0.2,2])
    cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[10,0.2,2])
    cube_body = p.createMultiBody( baseMass=0, baseCollisionShapeIndex=cube_collision,baseVisualShapeIndex=cube_visual, basePosition = [0,-10,1])

    cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.2,10,2])
    cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.2,10,2])
    cube_body = p.createMultiBody( baseMass=0, baseCollisionShapeIndex=cube_collision,baseVisualShapeIndex=cube_visual, basePosition = [10,0,1])

    cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.2,10,2])
    cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.2,10,2])
    cube_body = p.createMultiBody( baseMass=0, baseCollisionShapeIndex=cube_collision,baseVisualShapeIndex=cube_visual, basePosition = [-10,0,1])

    #Spawn Objet 3D
    p.loadURDF("./table/table.urdf", basePosition = [6,0,0], globalScaling = 1)
    p.loadURDF("./chair/chair.urdf", basePosition = [7,0,0], globalScaling = 1)
    p.loadURDF("./chair/chair.urdf", basePosition = [8,0,0], globalScaling = 1)



    """
    #Modification de la posture de pepper
    pepper.goToPosture("Crouch", 0.6)
    time.sleep(1)
    pepper.goToPosture("Stand", 0.6)
    time.sleep(1)
    pepper.goToPosture("StandZero", 0.6)
    time.sleep(1)
    """

    #Subscribe to pepper camera
    handle = pepper.subscribeCamera(PepperVirtual.ID_CAMERA_BOTTOM)
    handle2 = pepper.subscribeCamera(PepperVirtual.ID_CAMERA_TOP)
    handle3 = pepper.subscribeCamera(PepperVirtual.ID_CAMERA_DEPTH)
    
    #Affichage des lasers
    pepper.showLaser(True)
    pepper.subscribeLaser()


    joint_parameters = list()
    for name, joint in pepper.joint_dict.items():
        if "Finger" not in name and "Thumb" not in name:
            joint_parameters.append((
                p.addUserDebugParameter(
                    name,
                    joint.getLowerLimit(),
                    joint.getUpperLimit(),
                    pepper.getAnglesPosition(name)),
                name))

    try:
        while True:
            for joint_parameter in joint_parameters:
                pepper.setAngles(
                    joint_parameter[1],
                    p.readUserDebugParameter(joint_parameter[0]), 1.0)

            showCam(pepper,"bottom camera", handle)
            showCam(pepper,"top camera", handle2)
            img3 = showCam(pepper,"depth camera", handle3)
            
            filename = "ImageDepth.png"
            cv2.imwrite(filename,img3)
            #im_gray = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            #im_color = cv2.applyColorMap(im_gray, cv2.COLORMAP_HSV)
            #cv2.imshow("colorBar depth camera", im_color)
            
            

            cv2.waitKey(1)
            
            laser_list_sides = pepper.getRightLaserValue()            
            laser_list_sides.extend(pepper.getLeftLaserValue())

            laser_list_front = pepper.getFrontLaserValue()


            if any(laser <= 2.0 for laser in laser_list_sides): #If there is something on his side, turn
                pepper.moveTo(0,0,90,frame =2, _async=True)
            elif all(laser >= 2.7 for laser in laser_list_front): #If there is no object close in front of it, go ahead
                pepper.moveTo(0.25,0,0,frame =2, _async=True)
            else:
                pepper.stopMove()
                pass
                
    except KeyboardInterrupt:
        simulation_manager.stopSimulation(client)
    

if __name__ == "__main__":
    main()