#include "ros/ros.h"
#include "ros_service/SrvTutorial.h"

// 서비스 요청이 들어온다면 

bool calculation(ros_service::SrvTutorial::Request &req, ros_service::SrvTutorial::Response &res){

    res.result = req.a + req.b;
   
    ROS_INFO("requst a = %d, b = %d, response = %d", req.a, req.b, res.result);


    return true;
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "service_server");
    ros::NodeHandle nh;

    ros::ServiceServer ros_service_sv = nh.advertiseService("ros_tutorial_srv2", calculation);

    ROS_INFO("ready srv server");

    ros::spin();

    return 0;
}
