
#include "ros/ros.h"
#include "ros_service/SrvTutorial.h"
#include <cstdlib>

int main(int argc, char **argv)
{
    ros::init(argc, argv, "service_client");

    if (argc !=3){
        ROS_INFO("plz 3 arg");
        return 1;
    }

    ros::NodeHandle nh; 
    // 보낼 서비스 명과 클라이언트 객체 생성
    ros::ServiceClient ros_service_client = nh.serviceClient<ros_service::SrvTutorial>("ros_tutorial_srv2");

    ros_service::SrvTutorial srv;

    srv.request.a = atoll(argv[1]);
    srv.request.b = atoll(argv[2]);

    if (ros_service_client.call(srv)) // 서비스를 전송 해봄 
    {
        ROS_INFO("Response : %d", srv.response.result);
    }
    else
    {   
        ROS_ERROR("Fail");
        return 1;
    }
    return 0;
}
