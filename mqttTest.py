#!/usr/bin/env python

import paho.mqtt.client as mqtt
import rospy
from echobot_driving.msg import MsgDriving
import threading
import json

class mqttSubsciber:
    def __init__(self, client_id, username, password,  topic, RosPublisher, host = '~~', port = 1883):
        self.client = mqtt.Client(client_id=client_id,clean_session=False)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.RosPublisher = RosPublisher
        
        self.client.username_pw_set(username = username, password= password)
        self.client.connect(host, port)
        self.client.subscribe(topic, qos = 1)


	    ## message format 
        # self.robot_id = "robot a"
        # self.driving_speed = 0.0
        # self.driving_mode = ""
        # self.direction_val = 0.0
        # self.repeat_driving_cycle = ""
        # self.latitude = "0.0"
        # self.longitude = "0.0"
        # self.course_list = ""
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)


    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        # print(msg.payload)
        # print(type(msg.payload))
        # print(type(msg.payload.decode("utf-8")))
        # print(msg.payload.decode("utf-8"))
        # msg_data = json.loads(str(msg.payload.decode("utf-8")))
        msg_data = json.loads(msg.payload)
        print("json_format ; ", msg_data)
        # print(type(msg_data['direction_val']))
        # print(type(msg_data['robot_id']))
        # print(msg_data['robot_id'].encode("utf-8"))
        # print(msg_data['course_list'])
        # print(type(msg_data['course_list']))
  
        # print(type(msg_data['course_list'][0]))
        # print(msg_data['course_list'][0])

        msg_data['course_list'] = list(map(json.dumps, msg_data['course_list']))

    
        self.RosPublisher.update(
		msg_data['robot_id'].encode("utf-8"),msg_data['driving_speed'],msg_data['driving_mode'].encode("utf-8")
		,msg_data['direction_val'],msg_data['repeat_driving_cycle'].encode("utf-8"),msg_data['latitude']
		,msg_data['longitude'],msg_data['course_list']
		)

        

class PublishDrivingMsg(threading.Thread):
    def __init__(self):
        super(PublishDrivingMsg, self).__init__() 
        self.publisher = rospy.Publisher('driving_setting', MsgDriving, queue_size = 1)

        self.robot_id = ""
        self.driving_speed = 0.0
        self.driving_mode = ""
        self.direction_val = 0.0
        self.repeat_driving_cycle = ""
        self.latitude = "0.0"
        self.longitude = "0.0"
        self.course_list = ""
        self.timeout = 1.0
        self.condition = threading.Condition() 

        self.start() 

    def update(self, robot_id, driving_speed,driving_mode, direction_val, repeat_driving_cycle, latitude , longitude , course_list):

        self.condition.acquire()# thread lock 

        self.robot_id = robot_id
        self.driving_speed = driving_speed
        self.driving_mode = driving_mode
        self.direction_val = direction_val
        self.repeat_driving_cycle = repeat_driving_cycle
        self.latitude = latitude
        self.longitude = longitude
        self.course_list = course_list
        # Notify publish thread that we have a new message.
        self.condition.notify() # thread wait 
        self.condition.release() # Thread unlock
        print("a")


    def run(self): #  
        echo_driving = MsgDriving() 
        while True:
            self.condition.acquire() # thread lock 
            # Wait for a new message or timeout.
            self.condition.wait(self.timeout) # thread wait 

	        # Copy state into twist message.

            echo_driving.robot_id = self.robot_id
            echo_driving.driving_speed = self.driving_speed
            echo_driving.driving_mode = self.driving_mode
            echo_driving.direction_val = self.direction_val
            echo_driving.repeat_driving_cycle = self.repeat_driving_cycle
            echo_driving.latitude = self.latitude
            echo_driving.longitude = self.longitude
            echo_driving.course_list  = self.course_list 


            self.condition.release() # thread unlock 
            print(echo_driving.robot_id)
            print(type(echo_driving.robot_id))
	        # Publish.
            self.publisher.publish(echo_driving)


if __name__=="__main__":
	rospy.init_node('echobot_driving_mqtt') 
	rosPub = PublishDrivingMsg()
	mqttSub = mqttSubsciber(client_id= "minwoo_lee",username="user",password="user",topic = "ros/execute_drive", RosPublisher =rosPub)
	
	# rosPub.update(
	# 	mqttSub.robot_id,mqttSub.driving_speed,mqttSub.driving_mode
	# 	,mqttSub.direction_val,mqttSub.repeat_driving_cycle,mqttSub.latitude
	# 	,mqttSub.longitude,mqttSub.course_list
	# 	)
