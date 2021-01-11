#!/usr/bin/env python

from __future__ import print_function

import threading
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy
import math

from sensor_msgs.msg import Imu

from echobot_driving.msg import MsgDriving
from geometry_msgs.msg import Twist
import time 
import sys, select, termios, tty

msg = """
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

w : go 
s : back 

CTRL-C to quit
"""

moveBindings = {
        0:0,
        45:45,
        90:90,
        135:135,
        180:180,
        225:225,
        270:270,
        315:315
    }
goback = {
        'w':(1,0,0,0),
        's':(-1,0,0,0)
    }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
    }



class PublishThread(threading.Thread):
    def __init__(self, rate):
        super(PublishThread, self).__init__() 
        self.publisher = rospy.Publisher('cmd_vel', Twist, queue_size = 1) 
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.th = 0.0
        self.speed = 0.0
        self.turn = 0.0
        self.condition = threading.Condition() 
        self.done = False

        # Set timeout to None if rate is 0 (causes new_message to wait forever
        # for new data to publish)
        if rate != 0.0:
            self.timeout = 1.0 / rate
        else:
            self.timeout = None

        self.start() 

    def wait_for_subscribers(self): 
        i = 0
        while not rospy.is_shutdown() and self.publisher.get_num_connections() == 0:  
        
            if i == 4: 
                print("Waiting for subscriber to connect to {}".format(self.publisher.name))
            rospy.sleep(0.5)
            i += 1
            i = i % 5
        if rospy.is_shutdown():
            raise Exception("Got shutdown request before subscribers connected")

    def update(self, x, y, z, th, speed, turn):
        self.condition.acquire()# thread lock 
        self.x = x
        self.y = y
        self.z = z
        self.th = th
        self.speed = speed
        self.turn = turn
        # Notify publish thread that we have a new message.
        self.condition.notify() # thread wait 
        self.condition.release() # Thread unlock

    def stop(self): #  
        self.done = True
        self.update(0, 0, 0, 0, 0, 0)
        self.join()

    def run(self): #  
        twist = Twist() # Twist msg 
        while not self.done: # done  stop message 
            self.condition.acquire() # thread lock 
            # Wait for a new message or timeout.
            self.condition.wait(self.timeout) # thread wait 

            # Copy state into twist message.

            twist.linear.x = self.x * self.speed
            twist.linear.y = self.y * self.speed
            twist.linear.z = self.z * self.speed
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = self.th * self.turn ##  

            self.condition.release() # thread unlock 

            # Publish.
            self.publisher.publish(twist)

        # Publish stop message when thread exits.
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        self.publisher.publish(twist)



def vels(speed, turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

class Quaternion_to_euler_angle:
    def __init__(self,imu):
        '''Initialize ros publisher, ros subscriber'''
        # subscribed Topic
        self.sub = rospy.Subscriber(imu, Imu, self.callback) # imu data 
        self.euler_X = 0.0
        self.euler_Y = 0.0
        self.euler_Z = 0.0

    def quaternion_to_euler_angle(self,msg):
        quaternion_x = msg.x
        quaternion_y = msg.y
        quaternion_z = msg.z
        quaternion_w = msg.w

        ysqr = quaternion_y * quaternion_y

        t0 = +2.0 * (quaternion_w * quaternion_x + quaternion_y * quaternion_z)
        t1 = +1.0 - 2.0 * (quaternion_x * quaternion_x + ysqr)
        euler_X = math.degrees(math.atan2(t0, t1))

        t2 = +2.0 * (quaternion_w * quaternion_y - quaternion_z * quaternion_x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        euler_Y = math.degrees(math.asin(t2))

        t3 = +2.0 * (quaternion_w * quaternion_z + quaternion_x * quaternion_y)
        t4 = +1.0 - 2.0 * (ysqr + quaternion_z * quaternion_z)
        euler_Z = math.degrees(math.atan2(t3, t4))

        return euler_X, euler_Y, euler_Z

    def callback(self,msg):
        self.euler_X, self.euler_Y, self.euler_Z = self.quaternion_to_euler_angle(msg.orientation)
        if self.euler_X < 0:
            self.euler_X = self.euler_X + 360
        if self.euler_Y < 0:
            self.euler_Y = self.euler_Y + 360
        if self.euler_Z < 0:
            self.euler_Z = self.euler_Z + 360


class drivingManagement:
    def __init__(self,driving_setting):
        self.sub = rospy.Subscriber(driving_setting, MsgDriving, self.callback) # driving data 

        self.robot_id = ""
        self.driving_speed = 0.5
        self.driving_mode = ""
        self.direction_val = "0"
        self.repeat_driving_cycle = ""
        self.latitude = 0.0
        self.longitude = 0.0
        self.course_list = ""

    def callback(self,msg):
        self.direction_val = msg.direction_val
        self.driving_speed = msg.driving_speed
        # print("diving_callback : ",self.direction_val)
      
     

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('echobot_driving') 
     
    speed = rospy.get_param("~speed", 0.5)
    turn = rospy.get_param("~turn", 1.854)
    repeat = rospy.get_param("~repeat_rate", 0)
    key_timeout = rospy.get_param("~key_timeout", 0.0)
    imu = rospy.get_param("~imu", 'razor_imu')
    driving_setting = rospy.get_param("~driving_setting", 'driving_setting')

    if key_timeout == 0.0:
        key_timeout = None

    pub_thread = PublishThread(repeat) # 
    sub_imu = Quaternion_to_euler_angle(imu)
    sub_drivingInfo = drivingManagement(driving_setting)
      
    x = 0
    y = 0
    z = 0
    th = 0
    status = 0

    try:
        pub_thread.wait_for_subscribers() # wait for connection 
        #pub_thread.update(x, y, z, th, speed, turn) # 

        print(msg) # 
        print(vels(speed,turn)) #

        while(1):
            #key = getKey(key_timeout) # input key 
            direction_val = sub_drivingInfo.direction_val
            # print("direction_val: ", direction_val)
            if direction_val in moveBindings.keys(): # mapping 
                direction = moveBindings[direction_val]
                start = time.time()
                print("goal :", direction)
                while(True):
                    print("now postion :{postion} speed :{speed}".format(postion = sub_imu.euler_Z, speed = sub_drivingInfo.driving_speed))
                    print("goal :", direction)

                    # test 
                    if direction > sub_imu.euler_Z:
                        th = 1
                    else:
                        th = 1
                    if time.time() - start > 40:
                        break
                    if abs(direction - sub_imu.euler_Z) < 5:
                        print("find goal")
                        break
                    pub_thread.update(0, 0, 0, th, sub_drivingInfo.driving_speed, turn)
                    time.sleep(1)
                #pub_thread.update(0,0,0,0,0,0)
                #print("stop plz")
            elif direction_val in goback.keys(): # mapping:
                x = goback[direction_val][0]
                y = goback[direction_val][1]
                z = goback[direction_val][2]
                th = goback[direction_val][3]
                pub_thread.update(x, y, z, th, sub_drivingInfo.driving_speed, turn)
            else:
                # Skip updating cmd_vel if key timeout and robot already
                # stopped.
                if direction_val == '' and x == 0 and y == 0 and z == 0 and th == 0:
                    continue
                x = 0
                y = 0
                z = 0
                th = 0

                if (direction_val == '\x03'):
                    break
       
         #   pub_thread.update(0, 0, 0, th, speed, turn)

    except Exception as e:
        print(e)
    finally:
        pub_thread.stop()

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)