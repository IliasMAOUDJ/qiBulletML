from qibullet import SimulationManager
from src.robot import Robot
import pybullet as p
import pybullet_data, signal, random, sys, threading

class Simulation(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.manager = SimulationManager()
        self.client_id = self.manager.launchSimulation(gui=True)
        p.connect(p.DIRECT)
        self.robot = Robot(self.manager, self.client_id)
        signal.signal(signal.SIGINT, self.signal_handler)
        self.createScene()
        self.initUI()

    def initUI(self):
        self.joint_parameters = list()

        """for name, joint in self.robot.pepper.joint_dict.items():
            if "Finger" not in name and "Thumb" not in name:
                self.joint_parameters.append(
                    (
                        p.addUserDebugParameter(
                            name,
                            joint.getLowerLimit(),
                            joint.getUpperLimit(),
                            self.robot.pepper.getAnglesPosition(name)
                        ),
                        name
                    )
                )"""
        print(self.joint_parameters)

    def createScene(self):
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        """p.loadURDF("./urdf/table/table.urdf", basePosition=[2,1,0], globalScaling=1)
        p.loadURDF("./urdf/chair/chair.urdf", basePosition=[3,1,0], globalScaling=1)
        p.loadURDF("./urdf/chair/chair.urdf", basePosition=[4,1,0], globalScaling=1)"""
        p.loadURDF("duck_vhacd.urdf", basePosition=[3,-2,0.5], globalScaling=10, )
        #self.createWall(3, 0.1, 2, 0, 3, 0)
        #self.createWall(3, 0.1, 2, 0, -3, 0)
        #self.createWall(0.1, 3, 2, 3, 0, 0)
        #self.createWall(0.1, 3, 2, -3, 0, 0)
        #self.createSphere(0.2, 2, 0, 0.5)
        #self.createSphere(0.2, 2.2, -0.5, 0.15, (0, 0, 255))
        for i in range(30):
            #self.createSphere(0.2, random.randint(0, 5), random.randint(-5, 5), 0.3, color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            self.createSphere(0.2, random.choice([-5, -4, -3, -2, -1, 1, 2, 4, 5]), random.choice([-5,-4, -3,-2,-1,1,2,3,4,5]), 0.3,
                              color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            #self.createCube(random.choice([0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]),random.randint(-5, 5), random.randint(-5,5),(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            #self.createCube(random.choice([0.2, 0.3, 0.4]), random.choice([-5,-4,-3,-2,-1,1, 2, 4, 5]), random.choice([-5,-4,-3, -2, -1, 1, 2, 3,4,5]),(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        #cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.5,0.5,0.5])
        #cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.75,0.75,0.75])
        #cube_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=cube_collision, baseVisualShapeIndex=cube_visual, basePosition=[2,1,0.25])
        #cube_body_1 = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=cube_collision, baseVisualShapeIndex=cube_visual, basePosition=[2,0,0.25])
        #cube_body_2 = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=cube_collision, baseVisualShapeIndex=cube_visual, basePosition=[2,2,0.25])

    def createWall(self, w, h, d, x, y, z):
        wall_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[w, h, d])
        wall_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[w, h, d])
        wall_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision, baseVisualShapeIndex=wall_visual, basePosition=[x, y, z])

    def createSphere(self, radius, x, y, z, color=(255, 0, 0)):
        sphere_visual = p.createVisualShape(p.GEOM_SPHERE, rgbaColor=[color[0]/255, color[1]/255, color[2]/255, 1], radius=radius)
        sphere_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=radius)
        sphere_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=sphere_collision,baseVisualShapeIndex=sphere_visual, basePosition=[x, y, z])

    def createCube(self, width, x, y, color=(255, 0, 0)):
        cube_visual = p.createVisualShape(p.GEOM_BOX, rgbaColor=[color[0]/255, color[1]/255, color[2]/255, 1], halfExtents=[0.5, 0.5, 0.5])
        cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[width, width, width])
        cube_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=cube_collision, baseVisualShapeIndex=cube_visual, basePosition=[x,y,width/2])

    def signal_handler(self, signal, frame):
        print("CTRL-C detected")
        for t in self.robot.threads:
            t.kill()
        self.robot.kill()
        self.manager.stopSimulation(self.client_id)
        sys.exit(0)

    def run(self):
        self.robot.start()
        """while True:
            for joint_parameter in self.joint_parameters:
                self.robot.pepper.setAngles(
                    joint_parameter[1],
                    p.readUserDebugParameter(joint_parameter[0]), 1.0
                )"""
