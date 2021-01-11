#!/usr/bin/env python

from __future__ import print_function

import threading

# 패키지 매니페스트를 읽어오고 dependencies 기반으로 라이브러리 경로를 설정 
# cakin 빌드 시스템을 사용하고부턴 필요하지 않음 
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy
import math

from sensor_msgs.msg import Imu

from geometry_msgs.msg import Twist

import sys, select, termios, tty

msg = """

원하는 각에 따른 움직임 테스트 중입니다. 

Reading from the keyboard  and Publishing to Twist!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

w : go 
s : back 

t : up (+z)
b : down (-z)
anything else : stop
q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
CTRL-C to quit
"""

# moveBindings = {
#         'i':(1,0,0,0),
#         'o':(1,0,0,-1),
#         'j':(0,0,0,1),
#         'l':(0,0,0,-1),
#         'u':(1,0,0,1),
#         ',':(-1,0,0,0),
#         '.':(-1,0,0,1),
#         'm':(-1,0,0,-1),
#         'O':(1,-1,0,0),
#         'I':(1,0,0,0),
#         'J':(0,1,0,0),
#         'L':(0,-1,0,0),
#         'U':(1,1,0,0),
#         '<':(-1,0,0,0),
#         '>':(-1,-1,0,0),
#         'M':(-1,1,0,0),
#         't':(0,0,1,0),
#         'b':(0,0,-1,0),
#     }
moveBindings = {
        'i':0,
        'o':45,
        'l':90,
        '.':135,
        ',':180,
        'm':225,
        'j':270,
        'u':315
    }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
    }



euler_X = 0.0
euler_Y = 0.0
euler_Z = 0.0

# 쓰레드 시작 
# Thread : https://javaplant.tistory.com/29
# 인스턴스에 동시성 접근시 Lock, wait 을 이해해야함 


class PublishThread(threading.Thread): # Thread 클래스 상속 받음 
    def __init__(self, rate):
        super(PublishThread, self).__init__() # Thread 사용하기 하면 반드시 호출 
        self.publisher = rospy.Publisher('cmd_vel', Twist, queue_size = 1) # Twist 메시지 포밋으로 cmd_vel pub
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.th = 0.0
        self.speed = 0.0
        self.turn = 0.0
        self.condition = threading.Condition() # 다른 쓰레드의 신호를 기다리게 하는 객체 , 동시성 작업에 대한 설정 
        self.done = False



        # Set timeout to None if rate is 0 (causes new_message to wait forever
        # for new data to publish)
        if rate != 0.0:
            self.timeout = 1.0 / rate
        else:
            self.timeout = None

        # 파생 클래스 사용한 Thread 기법  http://pythonstudy.xyz/python/article/24-%EC%93%B0%EB%A0%88%EB%93%9C-Thread
        # start 하면 내부의 run 호출함 
        self.start() 

    def wait_for_subscribers(self): 
        i = 0
        while not rospy.is_shutdown() and self.publisher.get_num_connections() == 0: # sub이랑 연결이 안되면 
        # 또는 ctrl + c 누르기 전까지는 무한 루프
            if i == 4: # 2초 기다림 
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
        self.condition.notify() # thread wait 을 해제 
        self.condition.release() # Thread unlock

    def stop(self): # 모든 값을 0 으로 만들어 멈춤 
        self.done = True
        self.update(0, 0, 0, 0, 0, 0)
        self.join()

    def run(self): # 주행 
        twist = Twist() # Twist msg 객체 
        while not self.done: # done 은 stop message 
            self.condition.acquire() # thread lock 
            # Wait for a new message or timeout.
            self.condition.wait(self.timeout) # thread wait 상태로 변경 

            # Copy state into twist message.

            # # 입력받은 xyz 값이랑 속도랑 곱해서 발행 
            # twist.linear.x = self.x * self.speed
            # twist.linear.y = self.y * self.speed
            # twist.linear.z = self.z * self.speed
            twist.angular.x = 0
            twist.angular.y = 0
            # 이쪽에서 메시지는 그대로 발행하긴해야함 
            twist.angular.z = self.th * self.turn ## 회전 

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


def getKey(key_timeout): ## 간단히 말하자면 리눅스 계열에서 단일키 누르는 것을 받아옴 
    tty.setraw(sys.stdin.fileno()) # #fileno()를 raw로 전환, fileno()는 스트림의 기본이 되는 file descripter를 반환하는 함수.

    # select.select( sys.stdin,  ,  ,  0.1) -> 시스템 호출 관련 인터페이스. 
    # 첫번째 인자는 입력 관련. 중간 2개는 출력, 에러 관련, 0.1은 딜레이.
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)  

    if rlist:
        # 입력한 키를 읽은 후, key에 저장.
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings) #stdin의 에코를 끄고, 표준모드를 비활성화.
    return key


def vels(speed, turn): # 현재 속도와 회전 출력 
    return "currently:\tspeed %s\tturn %s " % (speed,turn)


def quaternion_to_euler_angle(msg):
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

def callback(msg):
    global euler_X,euler_Y,euler_Z
    euler_X, euler_Y, euler_Z = quaternion_to_euler_angle(msg.orientation)
    print "Euler -----------------------"
    print "euler_X : ", euler_X
    print "euler_Y : ", euler_Y
    print "euler_Z : ", euler_Z

    if euler_X < 0:
        euler_X = euler_X + 360
    if euler_Y < 0:
        euler_Y = euler_Y + 360
    if euler_Z < 0:
        euler_Y = euler_Y + 360




if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('teleop_twist_keyboard') # 노드 명 
     
    # parameter 있으면 읽어옴 
    speed = rospy.get_param("~speed", 0.5)
    turn = rospy.get_param("~turn", 0.2)
    repeat = rospy.get_param("~repeat_rate", 0.0)
    key_timeout = rospy.get_param("~key_timeout", 0.0)

    imu = rospy.get_param("~imu", 'razor_imu')

    if key_timeout == 0.0:
        key_timeout = None

    pub_thread = PublishThread(repeat) # 주기 전달 

    # imu 값 구독 및 변환 
    sub = rospy.Subscriber(imu, Imu, callback) # imu data 받기 

    x = 0
    y = 0
    z = 0
    th = 0
    status = 0

    global euler_X,euler_Y,euler_Z

    try:
        pub_thread.wait_for_subscribers() # wait for connection 
        pub_thread.update(x, y, z, th, speed, turn) # 시작은 정지 상태 

        print(msg) # 그 안내 메시지 
        print(vels(speed,turn)) #현재 속도 및 회전 출력 

        while(1):
            key = getKey(key_timeout) # input key 
            if key in moveBindings.keys(): # 수치값과 mapping 
                direction = moveBindings[key][0]
                length = abs(direction - euler_Z)
                while(length > 5):
                    if direction > euler_Z:
                        th = 1
                    else:
                        th = -1

                    pub_thread.update(0, 0, 0, th, speed, turn)

            pub_thread.update(0, 0, 0, 0, speed, turn)

        # while(1):
        #     key = getKey(key_timeout) # input key 
        #     if key in moveBindings.keys(): # 수치값과 mapping 
        #         x = moveBindings[key][0]
        #         y = moveBindings[key][1]
        #         z = moveBindings[key][2]
        #         th = moveBindings[key][3]
        #     elif key in speedBindings.keys(): # 속도 관련 키일시 
        #         speed = speed * speedBindings[key][0]
        #         turn = turn * speedBindings[key][1]

        #         print(vels(speed,turn)) # 현 속도 출력 
        #         if (status == 14): # 주기마다 키 출력 
        #             print(msg)
        #         status = (status + 1) % 15
        #     else:
        #         # Skip updating cmd_vel if key timeout and robot already
        #         # stopped.
        #         if key == '' and x == 0 and y == 0 and z == 0 and th == 0:
        #             continue
        #         x = 0
        #         y = 0
        #         z = 0
        #         th = 0
        #         if (key == '\x03'):
        #             break
 
        #     pub_thread.update(x, y, z, th, speed, turn)

    except Exception as e:
        print(e)

    finally:
        pub_thread.stop()

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)