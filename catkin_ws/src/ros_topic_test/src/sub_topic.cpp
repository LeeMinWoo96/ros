#include "ros/ros.h" 
#include "ros_topic_test/MsgTutorial.h"


void msgCallback(const ros_topic_test::MsgTutorial::ConstPtr& msg)
{
    // msg 를참조형 변수로 선언했기 때문에 ->를 사용
   
    ROS_INFO("recieve msg = %d", msg->stamp.sec);
    ROS_INFO("recieve msg = %d", msg->stamp.nsec);
    ROS_INFO("recieve msg = %d", msg->data);
}

int main(int argc, char **argv)
{
    ros::init(argc,argv, "sub_topic"); // 노드명 

    ros::NodeHandle nh; // ros 시스템과 통신을 위한 노드 핸들 선언

    // Sub 선언 노드에는 pub sub 둘다 존재하게 가능하기도 함 
    ros::Subscriber ros_topic_sub = nh.subscribe("msgmsg",100,msgCallback);


    // 백그라운드에서 계속 돌면서 메시지가 수신되면 위에 정의한 Callback 함수를 실행한다.
    ros::spin();

    return 0;

}


