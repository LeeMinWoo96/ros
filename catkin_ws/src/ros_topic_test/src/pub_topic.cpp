#include "ros/ros.h" // Ros 기본 헤더 파일 
#include "ros_topic_test/MsgTutorial.h" // Msg 파일 빌드 후 자동생성됨 

int main(int argc, char **argv)
{
    ros::init(argc,argv, "topic_publisher"); // 노드 명 
    ros::NodeHandle nh;  // Ros 시스템과 통신을 위한 노드 핸들러 

    // 퍼블리셔 선언 , ros_topic_test 패키지의 MsgTutorial 파일을 이용한
    // 퍼블려서 pub_topic 을 작성   토픽명은 msgmsg
    // pub 큐 사이즈가 100개 
    ros::Publisher pub_topic = nh.advertise<ros_topic_test::MsgTutorial>("msgmsg",100);
    
    ros::Rate loop_rate(10);

    // MsgTutorial 형식으로 msg 라는 메시지 선언 
    ros_topic_test::MsgTutorial msg;

    int count = 0;

    while (ros::ok())
    {
        msg.stamp = ros::Time::now();  // 현재 시간을 msg 하위 stamp 에 담든다. stamp 은 MsgTutorial.msg 에서 정의한 변수 명 
        msg.data = count;
        
        // ECHO 와 비슷 
        ROS_INFO("send msg = %d", msg.stamp.sec);
        ROS_INFO("send msg = %d", msg.stamp.nsec);
        ROS_INFO("send msg = %d", msg.data);

        pub_topic.publish(msg);   // 메시지 pub

        loop_rate.sleep(); //위에서 정한 루프에따라 슬립

        ++count;
    }

    return 0;
}

