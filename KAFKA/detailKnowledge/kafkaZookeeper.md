
- [kafka zookeeper的作用](#kafka-zookeeper%e7%9a%84%e4%bd%9c%e7%94%a8)
  - [1. Broker注册](#1-broker%e6%b3%a8%e5%86%8c)
  - [2. Topic注册](#2-topic%e6%b3%a8%e5%86%8c)
  - [3. Controller选举](#3-controller%e9%80%89%e4%b8%be)
  - [4. 消费者consumer 注册](#4-%e6%b6%88%e8%b4%b9%e8%80%85consumer-%e6%b3%a8%e5%86%8c)
  - [5. 分区和消费者的关系](#5-%e5%88%86%e5%8c%ba%e5%92%8c%e6%b6%88%e8%b4%b9%e8%80%85%e7%9a%84%e5%85%b3%e7%b3%bb)
  - [6. 消费者消费进度offset记录。](#6-%e6%b6%88%e8%b4%b9%e8%80%85%e6%b6%88%e8%b4%b9%e8%bf%9b%e5%ba%a6offset%e8%ae%b0%e5%bd%95)

# kafka zookeeper的作用

## 1. Broker注册

Broker是分布式部署，并且相互之间相互独立，需要有一个注册系统能够将集群中的broker管理起来。在Zookeeper上有一个专门用来进行Broker服务器列表记录的节点:**/brokers/ids**
每个broker在启动的时候，都会到zookeeper上进行注册，到 /brokers/ids下创建属于自己的节点。如 /brokers/ids/[0...N]

kafka使用全局唯一的数字来指代每个broker服务器。不同的broker必须使用不同的Broker ID 进行注册。创建节点后，每个Broker就会将自己的ip地址和端口信息记录到该节点上去，其中。broker创建的节点类型是临时节点，一旦broker宕机，对应的临时节点就会被自动删除。

## 2. Topic注册

在kafka中，同一个Topic的消息会被分成多个分区并且分布在多个broker上。这些分区信息及broker的对应关系也都有zookeeper维护。由专门的节点进行记录。如：/brokers/topics

kafka中每个topic都会以/brokers/topic/[topic]的形式被记录，如/brokers/topic/login和/brokers/topics/search等。broker服务器启动后，会到对应的topic节点（/brokers/topics）上注册自己的broker ID 并写入针对该topic的分区总数，如 /brokers/topics/login/3->2 这个节点表示broker ID 为3 的一个broker服务器，对于login这个Topic的消息，提供了2个分区进行消息存储，同时，这个分区节点也是临时节点。

## 3. Controller选举

Controller是一个特殊的broker，负责所有partition的leader/follower关系
Zookeeper负责从broker中选举出一个作为controller，并确保唯一性，当controller宕机后，选举新的。

## 4. 消费者consumer 注册

消费者服务器在初始化启动时加入消费者组的步骤如下：
  - 注册到消费者分组。每个消费者服务器启动之后，都会到zookeeper的指定节点上创建一个属于自己的消费者节点，例如/consumers/[group_id]/ids/[consumer_id]， 完成节点的创建后，消费者就会将自己订阅的topic信息写入该临时节点。
  - 对消费者分组中的消费者的变化注册监听。每个消费者需要关注所属消费者分组中其他消费者服务器的变化情况。即对/consumers/[group_id]/ids节点注册子节点变化的watcher监听，一旦发现消费者新增或者减少，就触发消费者的负载均衡。
  - 对broker服务器变化注册监听。消费者需要对/broker/ids/[0-N]中的节点进行监听，如果发现broker服务器列表发生变化，那么就会根据情况看是否需要进行消费者负载均衡。
  - 对消费者进行负载均衡。为了让同一个topic下不同分区的消息尽量均衡的被多个消费者消费而进行消费者和消费分区分配的过程。通常。如果一个消费者分组如果组内的消费者服务器发生变更或者broker发生变更，会发生消费者负载均衡。
  
## 5. 分区和消费者的关系

consumer group下面有多个consumer。对于每个consumer group，kafka会为其分配一个全局唯一的group ID，group内部的所有消费者共享该ID.订阅topic下的每个分区只能分配给某个group下的一个consumer。同时，kafka为每个消费者分配了一个consumerID。通常采用 hostname:uuid 形式表示。

在kakfa 中，规定了每个消息分区只能被同组的一个消费者进行消费，因此需要在zookeeper上记录消费分区和consumer之间的关系。每个消费者一旦确定了对一个消息分区的消费权力。需要将其consumerID 写入 zookeeper对应消息分区的临时节点上。例如：
**/consumers/[group_id]/owners/[topic]/[broker_id-partition_id]**
其中 [broker_id-partition_id] 就是一个消息分区的标识，节点内容就是该消费分区上消费者的consumer ID.

## 6. 消费者消费进度offset记录。
在消费者对指定消息分区进行消息消费的过程中，需要定时地将分区消息的消费进度Offset记录到Zookeeper上，以便在该消费者进行重启或者其他消费者重新接管该消息分区的消息消费后，能够从之前的进度开始继续进行消息消费。Offset在Zookeeper中由一个专门节点进行记录，其节点路径为:

/consumers/[group_id]/offsets/[topic]/[broker_id-partition_id]

节点内容就是Offset的值。

早期版本的 kafka 用 zk 做 meta 信息存储，consumer 的消费状态，group 的管理以及 offset的值。考虑到zk本身的一些因素以及整个架构较大概率存在单点问题，新版本中确实逐渐弱化了zookeeper的作用。新的consumer使用了kafka内部的group coordination协议，也减少了对zookeeper的依赖



