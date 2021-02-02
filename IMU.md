## IMU

먼저 나같이 하드웨어 초보는 IMU가 뭔지 알아야 하는데,

IMU : Inertial Measurement Unit의 약자로 한글로는 관성측정유닛이라 한다. 사람으로 치면 귓속의 세반고리관(신체의 회전을 지각하는 역할을 한다고 한다.)이다. 자이로스코프, 가속도계가 기본으로 해서 여기서는 지자계 센서가 포함되어 있다. 

로봇, 드론에서는 자세 제어, 위치 제어할 때 중요한 역할을 한다. 글로 된 설명보다는 이미지가 이해하기 쉬웠다.

![IMU](./img/Roll_Pitch_Yaw.jpg)

이미지 출처 : wikipedia


위 이미지에서 3개의 축을 중심으로 롤(Roll), 피치(Pitch), 요(Yaw) 운동을 하는데, 화살표만큼 이동하는 것을 감지하는 것을 가속도 센서, 3개의 축 회전을 감지하는 것을 자이로스코프 센서로 측정한다고 생각하면 이해하기 쉽다. 이 측정값으로 로봇이나 드론이 3차원 공간에서 좌표나 움직임을 표시할 수 있다. 

---
필터 개념 
https://ahnbk.com/?p=96

---
IMU 적분 개념
https://ddangeun.tistory.com/97


---

 **출처 :** http://blog.naver.com/PostView.nhn?blogId=jaydee88&logNo=221315445531&from=search&redirect=Log&widgetTypeCall=true&directAccess=false