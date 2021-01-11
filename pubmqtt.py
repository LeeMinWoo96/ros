import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("dis")
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)



client = mqtt.Client(client_id="mw",clean_session=False)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish


client.username_pw_set(username = "user", password= "user")


client.connect('~~', 1883)

#client.loop_start()
msg = {
    "robot_id" : "robotid",
    "driving_speed" : 1,
    "driving_mode" : "drivingmode",
    "direction_val" : 45,
    "repeat_driving_cycle" : "10",
    "latitude" : "37",
    "longitude" : "150",
    "course_list" : [{"seq":0, "s_latitude":"", "s_longitude":""}],    
}
client.publish('ros/execute_drive', json.dumps(msg), qos=1)

#client.loop_stop()
#client.disconnect()

client.loop_forever()
