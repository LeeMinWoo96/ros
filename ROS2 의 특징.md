### ROS2 의 특징 

**간단히 정리하자면 실제 산업 현장에서 사용할 수 있게끔 통신 방식을 TCPROS 에서 OGM 에서 표준화한 DDS 로 변환시켜
실시간 응답성을 증대시키었고 DDS의 동적 노드 탐색으로 인한 Master 노드 없이도 노드 탐색이 가능해짐
또한 보안성 또한 DDS-Security를 통해 큰 혜탁을 얻음**

출처 : [오르카 커뮤니티](https://cafe.naver.com/openrt/24477?fbclid=IwAR3bBLEhfSGNwcpEJgHTpn8QWv4or9gqbAUld2vJ628p2M-Iqz1ALVqaO8A)

참고 사항ㄹ : [오르카 커뮤니티 ROS1 과 2의 차이](https://cafe.naver.com/openrt/24477?fbclid=IwAR3bBLEhfSGNwcpEJgHTpn8QWv4or9gqbAUld2vJ628p2M-Iqz1ALVqaO8A)

*아래 부턴 발췌 내용*

-----


(Data Distribution Service)

- ROS 2의 가장 큰 변화점이자 특징 -

Created Date: 2020.08.03

Modified Date: 2020.08.11

revision 16

​


1. ROS의 메시지 통신

본격적인 ROS 2 프로그래밍 강좌에 앞서서 로봇 운영체제 ROS에서 중요시 여기는 몇 가지 용어 정의 및 메시지, 메시지 통신에 대해 먼저 알아보도록 하자. 특히, 메시지 통신은 ROS 프로그래밍에 있어서 ROS 1과 2의 공통된 중요한 핵심 개념이기에 ROS 프로그래밍에 들어가기 전에 꼭 이해하고 넘어가야 할 부분이다.

​

ROS에서는 프로그램의 재사용성을 극대화하기 위하여 최소 단위의 실행 가능한 프로세서라고 정의하는 노드(node, [1], [2]) 단위의 프로그램을 작성하게 된다. 이는 하나의 실행 가능한 프로그램으로 생각하면 된다. 그리고 하나 이상의 노드 또는 노드 실행을 위한 정보 등을 묶어 놓은 것을 패키지(package)라고 하며, 패키지의 묶음을 메타패키지(metapackage)라 하여 따로 분리한다.

​

여기서 제일 중요한 것은 실제 실행 프로그램인 노드인데 앞서 이야기한 것과 마찬가지로 ROS에서는 최소한의 실행 단위로 프로그램을 나누어 프로그래밍하기 때문에 노드는 각각 별개의 프로그램이라고 이해하면 된다. 이에 수많은 노드들이 연동되는 ROS 시스템을 위해서는 노드와 노드 사이에 입력과 출력 데이터를 서로 주고받게 설계해야만 한다. 여기서 주고받는 데이터를 ROS에서는 메시지(message, [3]~[8])라고 하고 주고받는 방식을 메시지 통신이라고 한다. 여기서 데이터에 해당되는 메시지(message)는 integer, floating point, boolean, string 와 같은 변수 형태이며 메시지 안에 메시지를 품고 있는 간단한 데이터 구조 및 메시지들의 배열과 같은 구조도 사용할 수 있다. 그리고 메시지를 주고받는 통신 방법에 따라 토픽(topic, [9]), 서비스(service, [10]), 액션(action, [11]), 파라미터(prameter, [12])로 구분된다. 참고로 더 자세한 설명은 하기 참고 자료 및 아래 링크의 유튜브 강좌[13]에서도 메시지 및 통신에 대해 설명하고 있으니 참고하도록 하자.

​
​

2. ROS 2와 DDS

ROS에서 사용되는 메시지 통신 방법으로는 토픽(topic), 서비스(service), 액션(action), 파라미터(prameter)가 있다. 각 메시지 통신 방법의 목적과 사용 방법은 다르기는 하지만 토픽의 발간(publish)과 구독(subscribe)의 개념을 응용하고 있다. 이 데이터를 보내고 받는 발간, 구독 개념은 ROS 1은 물론 ROS 2에서도 매우 중요한 개념으로 변함이 없는데 이 기술에 사용된 통신 라이브러리는 ROS 1, 2에서 조금씩 다르다. ROS 1에서는 자체 개발한 TCPROS[14]와 같은 통신 라이브러리를 사용하고 있던 반면, ROS 2에서는 OMG(Object Management Group, [15])에 의해 표준화된 DDS(Data Distribution Service, [16])의 리얼타임 퍼블리시와 서브스크라이브 프로토콜인 DDSI-RTPS(Real Time Publish Subscribe, [17])를 사용하고 있다. ROS 2 개발 초기에는 기존 TCPROS를 개선하거나 ZeroMQ, Protocol Buffers 및 Zeroconf 등을 이용하여 미들웨어처럼 사용하는 방법도 제안되었으나 무엇보다 산업용 시장을 위해 표준 방식 사용을 중요하게 여겼고, ROS 1때와 같이 자체적으로 만들기 보다는 산업용 표준을 만들고 생태계를 꾸려가고 있었던 DDS를 통신 미들웨어로써 사용하기로 하였다. DDS 도입에 따라 그림 2과 같이 ROS의 레이아웃은 크게 바뀌게 되었다. 처음에는 DDS 채용에 따른 장점과 단점에 대한 팽팽한 줄다리기 토론으로 걱정의 목소리도 높았지만 지금에 와서는 ROS 2에서의 DDS 도입은 상업적인 용도로 ROS를 사용할 수 있게 발판을 만들었다는 것에 가장 큰 역할을 했다는 평가가 지배적이다.

​



DDS 도입으로 기존 메시지 형태 이외에도 OMG의 CORBA [18]시절부터 사용되던 IDL(Interface Description Language, [19])를 사용하여 메시지 정의 및 직렬화를 더 쉽게, 더 포괄적으로 다룰 수 있게 되었다. 또한 DDS의 중요 컨셉인 DCPS(data-centric publish-subscribe), DLRL(data local reconstruction layer)의 내용을 담아 재정한 통신 프로토콜로인 DDSI-RTPS을 채용하여 실시간 데이터 전송을 보장하고 임베디드 시스템에도 사용할 수 있게 되었다. DDS의 사용으로 노드 간의 동적 검색 기능을 지원하고 있어서 기존 ROS 1에서 각 노드들의 정보를 관리하였던 ROS Master가 없어도 여러 DDS 프로그램 간에 통신할 수 있다. 또한 노드 간의 데이터 통신을 세부적으로 조정하는 QoS(Quality of Service, [20])를 매개 변수 형태로 설정할 수 있어서 TCP처럼 데이터 손실을 방지함으로써 신뢰도를 높이거나, UDP처럼 통신 속도를 최우선시하여 사용할 수도 있다. 그리고 산업용으로 사용되는 미들웨어인 만큼 DDS-Security [21] 도입으로 보안 측면에도 큰 혜택을 얻을 수 있었다. 이러한 다양한 기능을 갖춘 DDS를 이용하여 ROS 1의 퍼블리시, 서브스크라이브형 메시지 전달은 물론, 실시간 데이터 전송, 불안정한 네트워크에 대한 대응, 보안 등이 강화되었다. DDS의 채용은 ROS 1에서 ROS 2로 바뀌면서 가장 큰 변화점이자 그림 3과 같이 개발자 및 사용자로 하여금 통신 미들웨어에 대한 개발 및 이용 부담을 줄여 진짜로 집중해야 할 부분에 더 많은 시간을 쏟을 수 있게 되었다. DDS에 대한 더 자세한 사항은 아래 참고 자료 및 관련 글들을 참고하도록 하자. [22]~[28]

​


3. DDS란?

자~ 이제 기본 배경이 되는 썰을 풀었으니 본격적으로 DDS에 대해 알아보자. 처음 DDS를 ROS 2에 도입하자는 이야기가 나왔을 때, DDS라는 단어 자체를 처음 들어봤기에 너무 어려웠다. 결론부터 말하자면 DDS는 데이터 분산 시스템이라는 용어로 OMG에서 표준을 정하고자 만든 트레이드 마크(TM)였다. 그냥 용어이고 그 실체는 데이터 통신을 위한 미들웨어이다.

​

DDS가 ROS 2의 미들웨어로 사용하는 만큼 그 자체에 대해 너무 자세히 알 필요는 없을 듯싶고 ROS 프로그래밍에 필요한 개념만 알고 넘어가면 될 듯싶다. 우선 정의부터 알아보자. DDS는 Data Distribution Service, 즉 데이터 분산 서비스의 약자이다. OMG DDS Foundation [29]에서는 다음과 같이 정의하고 있다.

The Data Distribution Service (DDS™) is a middleware protocol and API standard for data-centric connectivity from the Object Management Group® (OMG®). It integrates the components of a system together, providing low-latency data connectivity, extreme reliability, and a scalable architecture that business and mission-critical Internet of Things (IoT) applications need.

​

In a distributed system, middleware is the software layer that lies between the operating system and applications. It enables the various components of a system to more easily communicate and share data. It simplifies the development of distributed systems by letting software developers focus on the specific purpose of their applications rather than the mechanics of passing information between applications and systems.

https://www.dds-foundation.org/what-is-dds-3/

즉, DDS는 데이터 분산 시스템이라는 개념을 나타내는 단어이고 실제로는 데이터를 중심으로 연결성을 갖는 미들웨어의 프로토콜(DDSI-RTPS, [30])과 같은 DDS 사양[31]을 만족하는 미들웨어 API가 그 실체이다. 이 미들웨어는 그림 4와 같이 ISO 7 계층 레이어[32]에서 호스트 계층(Host layers)에 해당되는 4~7 계층에 해당되고 ROS 2에서는 위에서 언급한 그림 3과 같이 운영 체제와 사용자 애플리케이션 사이에 있는 소프트웨어 계층으로 이를 통해 시스템의 다양한 구성 요소를 보다 쉽게 통신하고 데이터를 공유할 수 있게 된다.

​

