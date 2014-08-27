#! /usr/bin/python
import usb.core as usbdev
#from legopi.lib.Adafruit_PWM_Servo_Driver import PWM
#from legopi.lib import xbox_read
import time, thread
#from InverseKinematics import goTo
import numpy as np
import math

# Product information for the arm
#pwm = PWM(0x40, debug=True)



#ALL OF THIS IS IN RADIANS. DO NOT USE DEGREES FOR ANYTHING. EVER. AT ALL. 



class Joint:
	def __init__(self,channel,name,minVal,maxVal,defRad = 0, minAng = 0, maxAng = 0,angleOff = 0):
		self.channel = channel;
		self.name = name;
		self.minVal = minVal;
		self.maxVal = maxVal;
		self.currentVal = defRad;
		self.minAng = minAng;
		self.maxAng = maxAng;
		self.defVal = defRad
		self.angleOff = angleOff;
		self.speed = 0;
		self.changed = True;
	def setSpeed(self,speed):
		self.speed = speed;
	def toString(self):
		return "Joint('%s')=%d @ %d" % (self.name, self.currentVal,self.speed);
	def set(self,value):
		if value > self.maxVal:
			value = self.maxVal;
		if value < self.minVal:
			value = self.minVal;
		self.currentVal = value;
		self.changed = True;
	def reset(self):
		self.set(self.defVal);
	def delta(self,inc):
		if inc != 0:
			self.set(self.currentVal + inc);
	def write(self,val):
		if self.changed:
			#print 'Writing',val,'to',self.name
#			pwm.setPWM(self.channel,0,self.currentVal);
			self.changed=False
	def update(self):
		#print 'updating',self.name;
		self.delta(self.speed);
		self.write(self.currentVal);
	def getRadians(self):
		rads = self.minAng + (self.maxAng - self.minAng) * ((self.currentVal - self.minVal) / (self.maxVal - self.minVal))
		return rads
	def getMotorVals(self,radVal):
		newVal = self.minVal + (self.maxVal - self.minVal) * ((radVal - self.minAng) / (self.maxAng - self.minAng))
		return int(newVal)

class RobotArm:
	def __init__(self,delay = 0.05):
		self.joints = [];
		thread.start_new_thread(self.run, (delay,));
		self.running = True;
	def addJoint(self,joint):
		self.joints.append(joint);
		return self.joints.index(joint);
	def setJoint(self,joint,value):
		self.joints.get(joint).set(value);

	def getJoint(self,name):
		try:
			index = int(name)
			if name <len(self.joints):
				return self.joints[index];
			return None
		except ValueError:
			for joint in self.joints:
				if joint.name == name:
					return joint;
			return None; #check for null
	def setChanged(self):
		self.changed = True;
	def update(self):
		for joints in self.joints:
			joints.update();
	def run (self, delay):
		self.running = True;
		while self.running:
			time.sleep(delay);
			self.update();
	def getCurrentPose(self): #returns current positions of all motors in radians
		currentPose = []
		for joint in self.joints:
			if joint.name is not 'gripper':
				currentPose.append(joint.getRadians())
		return currentPose
	def goToXYZ(self,newPos):
		currentPose = []
		for i in range (0,len(self.joints)):
			if self.joints[i].name is not 'gripper':
				currentPose.append(self.joints[i].getMotorVals(newPos[i]))
			self.joints[i].set(currentPose[i])
		return currentPose