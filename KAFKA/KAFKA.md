
- [KAFKA知识储备](#kafka%e7%9f%a5%e8%af%86%e5%82%a8%e5%a4%87)
  - [消息系统](#%e6%b6%88%e6%81%af%e7%b3%bb%e7%bb%9f)
    - [消息系统分类](#%e6%b6%88%e6%81%af%e7%b3%bb%e7%bb%9f%e5%88%86%e7%b1%bb)
      - [点对点消息传递](#%e7%82%b9%e5%af%b9%e7%82%b9%e6%b6%88%e6%81%af%e4%bc%a0%e9%80%92)
      - [发布-订阅模式消息传递](#%e5%8f%91%e5%b8%83-%e8%ae%a2%e9%98%85%e6%a8%a1%e5%bc%8f%e6%b6%88%e6%81%af%e4%bc%a0%e9%80%92)
    - [消息系统好处](#%e6%b6%88%e6%81%af%e7%b3%bb%e7%bb%9f%e5%a5%bd%e5%a4%84)
  - [kafka](#kafka)
    - [kafka 基础概念](#kafka-%e5%9f%ba%e7%a1%80%e6%a6%82%e5%bf%b5)
    - [kafka架构原理](#kafka%e6%9e%b6%e6%9e%84%e5%8e%9f%e7%90%86)
      - [kafka 分布式](#kafka-%e5%88%86%e5%b8%83%e5%bc%8f)
      - [kafka topic 和 partition](#kafka-topic-%e5%92%8c-partition)
      - [kafka重平衡 rebalance 相关策略](#kafka%e9%87%8d%e5%b9%b3%e8%a1%a1-rebalance-%e7%9b%b8%e5%85%b3%e7%ad%96%e7%95%a5)
      - [kafka 副本机制](#kafka-%e5%89%af%e6%9c%ac%e6%9c%ba%e5%88%b6)
      - [kafka 日志存储](#kafka-%e6%97%a5%e5%bf%97%e5%ad%98%e5%82%a8)
      - [kafka 应答保证](#kafka-%e5%ba%94%e7%ad%94%e4%bf%9d%e8%af%81)
      - [kafka 消息发送分区策略](#kafka-%e6%b6%88%e6%81%af%e5%8f%91%e9%80%81%e5%88%86%e5%8c%ba%e7%ad%96%e7%95%a5)
      - [如何获取Partition的leader信息](#%e5%a6%82%e4%bd%95%e8%8e%b7%e5%8f%96partition%e7%9a%84leader%e4%bf%a1%e6%81%af)
    - [kafka 常见问题](#kafka-%e5%b8%b8%e8%a7%81%e9%97%ae%e9%a2%98)
      - [kafka的高可用性](#kafka%e7%9a%84%e9%ab%98%e5%8f%af%e7%94%a8%e6%80%a7)
      - [kafka ISR](#kafka-isr)
      - [kafka ack机制](#kafka-ack%e6%9c%ba%e5%88%b6)
      - [kafka zookeeper](#kafka-zookeeper)
    - [kafka leader选举](#kafka-leader%e9%80%89%e4%b8%be)
    - [如何保证kafka幂等性，数据只被消费一次](#%e5%a6%82%e4%bd%95%e4%bf%9d%e8%af%81kafka%e5%b9%82%e7%ad%89%e6%80%a7%e6%95%b0%e6%8d%ae%e5%8f%aa%e8%a2%ab%e6%b6%88%e8%b4%b9%e4%b8%80%e6%ac%a1)
    - [如何保证kakfa数据不丢失](#%e5%a6%82%e4%bd%95%e4%bf%9d%e8%af%81kakfa%e6%95%b0%e6%8d%ae%e4%b8%8d%e4%b8%a2%e5%a4%b1)
    - [如何保证kakfa](#%e5%a6%82%e4%bd%95%e4%bf%9d%e8%af%81kakfa)

# KAFKA知识储备

## 消息系统
消息系统分为两种消息传递模式。一种是点对点传递模式，一种是发布订阅模式。

### 消息系统分类
#### 点对点消息传递
在点对点消息系统中，消息持久化到一个队列当中。如果有一个或者多个消费者消费队列中的数据，那么这条消息只被消费一次，当一个消费者消费了队列中的数据之后，该数据会从消息队列中删除，这种模式即使有多个消费者的话 也能保证数据被处理的顺序。

**生产者发送一条消息到queue，只有一个消费者能收到**
![结构图](./pic/点对点消息队列.png)

#### 发布-订阅模式消息传递
在发布-订阅消息系统中，消息被持久化到一个topic中。
消费者可以订阅一个或者多个topic，消费者可以消费topic所有的数据，同一条数据可以被多个消费者消费，数据被消费后不会立即删除。
**发布者发送到topic的消息，只有订阅了topic的消费者才会收到消息**
![结构图](./pic/发布订阅消息系统.png)

### 消息系统好处
* 解耦
        
    比如说一个A系统，产生的数据同时需要供给BCD 下游三个系统使用，那么完全可以使用消息系统发布订阅模式，只需要将消息放松到消息队列，BCD 自己去取就可以，不用再A系统里面进行维护三套BCD系统的接口。

* 冗余 备份
  
    有些时候数据处理会发生失败情况，消息队列可以将消息进行持久化，避免数据丢失
* 扩展性
  
    通过消息队列进行解耦，只需要增大数据的入队和处理频率就可以
* 灵活&削减峰值
  
    在访问量激增的时候，可以使用消息队列来进行限流，保证消费者不会瞬间崩溃掉。
* 可恢复性
  
    系统一部分组件失效后，不也会影响到整个系统。

* 顺序保证

    在大多使用场景下，数据处理的顺序都很重要。大部分消息队列本来就是排序的，并且能保证数据会按照特定的顺序来处理。Kafka保证一个Partition内的消息的有序性
* 缓冲

    有助于控制和优化数据流经过系统的速度，解决生产消息和消费消息的处理速度不一致的情况。
* 异步通信

    很多时候，用户不想也不需要立即处理消息。消息队列提供了异步处理机制，允许用户把一个消息放入队列，但并不立即处理它。想向队列中放入多少消息就放多少，然后在需要的时候再去处理它们。

## kafka

### kafka 基础概念

* broker:

    kafka集群包括一个或者多个服务器，每个服务器节点叫broker
    broker存储topic的数据。
    * 如果一个topic 有N个partition,一个kafka集群有N个broker，那么每个broker存储一个topic 的partition.
    如果某topic有N个partition。
    * 集群有(N+M)个broker，那么其中有N个broker存储该topic的一个partition，剩下的M个broker不存储该topic的partition数据。
    * 如果某topic有N个partition，集群中broker数目少于N个，那么一个broker存储该topic的一个或多个partition。在实际生产环境中，尽量避免这种情况的发生，这种情况容易导致Kafka集群数据不均衡。

* topic:
  
  主题。每条发送到kafka集群的消息都需要制定一个topic。kafka根据topic对消息进行归类。
* partition:
  
    分区。每个topic都被分成一个或者多个partition.每个topic至少一个partition。每个partition中的数据使用多个segment文件存储。partition中的数据是有序的，不同partition间的数据丢失了数据的顺序。如果topic有多个partition，消费数据时就不能保证数据的顺序。在需要严格保证消息的消费顺序的场景下，需要将partition数目设为1。
* producer:

    生产者.即数据的发布者，该角色将消息发布到Kafka的topic中。broker接收到生产者发送的消息后，broker将该消息追加到当前用于追加数据的segment文件中。生产者发送的消息，存储到一个partition中，生产者也可以指定数据存储的partition

* consumer

    消费者 消费者可以从broker读取消息。一个消费者可以读取多个topic 的数据。
* consumer Group
    
    消费者组。每个Consumer属于一个特定的Consumer Group（可为每个Consumer指定group name，若不指定group name则属于默认的group）。这是kafka用来实现一个topic消息的广播（发给所有的consumer）和单播（发给任意一个consumer）的手段。一个topic可以有多个CG。topic的消息会复制-给consumer。如果需要实现广播，只要每个consumer有一个独立的CG就可以了。要实现单播只要所有的consumer在同一个CG。用CG还可以将consumer进行自由的分组而不需要多次发送消息到不同的topic。

* leader
    
    每个partition有多个副本，其中有且仅有一个作为Leader，Leader是当前负责数据的读写的partition。

* Follower
  
    Follower跟随Leader，所有写请求都通过Leader路由，数据变更会广播给所有Follower，Follower与Leader保持数据同步。如果Leader失效，则从Follower中选举出一个新的Leader。当Follower与Leader挂掉、卡住或者同步太慢，leader会把这个follower从“in sync replicas”（ISR）列表中删除，重新创建一个Follower
* offset

    偏移量。

### kafka架构原理
![架构图](./pic/kafka架构图.png)

#### kafka 分布式

Kafka每个主题的多个分区日志分布式地存储在Kafka集群上，同时为了故障容错，每个分区都会以副本的方式复制到多个消息代理节点上。其中一个节点会作为主副本（Leader），其他节点作为备份副本（Follower，也叫作从副本）。主副本会负责所有的客户端读写操作，备份副本仅仅从主副本同步数据。当主副本出现故障时，备份副本中的一个副本会被选择为新的主副本。因为每个分区的副本中只有主副本接受读写，所以每个服务器端都会作为某些分区的主副本，以及另外一些分区的备份副本，这样Kafka集群的所有服务端整体上对客户端是负载均衡的.

Kafka生产者客户端发布消息到服务端的指定主题，会指定消息所属的分区。生产者发布消息时根据消息是否有键，采用不同的分区策略。消息没有键时，通过轮询方式进行客户端负载均衡；消息有键时，根据分区语义（例如hash）确保相同键的消息总是发送到同一分区.

Kafka的消费者通过订阅主题来消费消息，并且每个消费者都会设置一个消费组名称。因为生产者发布到主题的每一条消息都只会发送给消费者组的一个消费者。所以，如果要实现传统消息系统的“队列”模型，可以让每个消费者都拥有相同的消费组名称，这样消息就会负责均衡到所有的消费者；如果要实现“发布-订阅”模型，则每个消费者的消费者组名称都不相同，这样每条消息就会广播给所有的消费者.

Kafka的消费者消费消息时，只保证在一个分区内的消息的完全有序性，并不保证同一个主题汇中多个分区的消息顺序。而且，消费者读取一个分区消息的顺序和生产者写入到这个分区的顺序是一致的。比如，生产者写入“hello”和“Kafka”两条消息到分区P1，则消费者读取到的顺序也一定是“hello”和“Kafka”。如果业务上需要保证所有消息完全一致，只能通过设置一个分区完成，但这种做法的缺点是最多只能有一个消费者进行消费。


#### kafka topic 和 partition

Topic在逻辑上可以被认为是一个queue，每条消费都必须指定它的Topic，可以简单理解为必须指明把这条消息放进哪个queue里。为了使得Kafka的吞吐率可以线性提高，物理上把Topic分成一个或多个Partition，每个Partition在物理上对应一个文件夹，该文件夹下存储这个Partition的所有消息和索引文件。创建一个topic时，同时可以指定分区数目，分区数越多，其吞吐量也越大，但是需要的资源也越多，同时也会导致更高的不可用性，kafka在接收到生产者发送的消息之后，会根据均衡策略将消息存储到不同的分区中。因为每条消息都被append到该Partition中，属于顺序写磁盘，因此效率非常高（经验证，顺序写磁盘效率比随机写内存还要高，这是Kafka高吞吐率的一个很重要的保证）。

**因此Kafka提供两种策略删除旧数据。一是基于时间，二是基于Partition文件大小。例如可以通过配置$KAFKA_HOME/config/server.properties，让Kafka删除一周前的数据，也可在Partition文件超过1GB时删除旧数据**

**因为Kafka读取特定消息的时间复杂度为O(1)**，即与文件大小无关，所以这里删除过期文件与提高Kafka性能无关。选择怎样的删除策略只与磁盘以及具体的需求有关。


####  kafka重平衡 rebalance 相关策略

当新的消费者加入消费组，它会消费一个或多个分区，而这些分区之前是由其他消费者负责的；另外，当消费者离开消费组（比如重启、宕机等）时，它所消费的分区会分配给其他分区。这种现象称为重平衡（rebalance）。重平衡是Kafka一个很重要的性质，这个性质保证了高可用和水平扩展。不过也需要注意到，在重平衡期间，所有消费者都不能消费消息，因此会造成整个消费组短暂的不可用。而且，将分区进行重平衡也会导致原来的消费者状态过期，从而导致消费者需要重新更新状态，这段期间也会降低消费性能。

之前的版本是说 消费者通过定期发送心跳（hearbeat）到一个作为组协调者（group coordinator）的broker来保持在消费组内存活。这个broker不是固定的，每个消费组都可能不同。当消费者拉取消息或者提交时，便会发送心跳。如果消费者超过一定时间没有发送心跳，那么它的会话（session）就会过期，组协调者会认为该消费者已经宕机。**在0.10.1版本，Kafka对心跳机制进行了修改，将发送心跳与拉取消息进行分离，这样使得发送心跳的频率不受拉取的频率影响**

**消费者对象不是线程安全的，也就是不能够多个线程同时使用一个消费者对象；而且也不能够一个线程有多个消费者对象。简而言之，一个线程一个消费者，如果需要多个消费者那么请使用多线程来进行一一对应。**



#### kafka 副本机制

#### kafka 日志存储


#### kafka 应答保证


#### kafka 消息发送分区策略

生产者发送消息时整个分区路由的步骤如下：

判断消息中的partition字段是否有值，有值的话即指定了分区，直接将该消息发送到指定的分区就行。
如果没有指定分区，则使用分区器进行分区路由（也可以自定义分区策略），首先判断消息中是否指定了key。
如果指定了key，则使用该key进行hash操作，并转为正数，然后对topic对应的分区数量进行取模操作并返回一个分区。
如果没有指定key，则通过先产生随机数，之后在该数上自增的方式产生一个数，并转为正数之后进行取余操作。

**上述第4点需要注意一下，如果该topic有可用分区，则优先分配可用分区，如果没有可用分区，则分配一个不可用分区。这与第3点中key有值的情况不同，key有值时，不区分可用分区和不可用分区，直接取余之后选择某个分区进行分配。**

#### 如何获取Partition的leader信息
* 从broker获取Partition的元数据。由于Kafka所有broker存有所有的元数据，所以任何一个broker都可以返回所有的元数据
* broker选取策略：将broker列表随机排序，从首个broker开始访问，如果出错，访问下一个
* 出错处理：出错后向下一个broker请求元数据
  
注意:
* Producer是从broker获取元数据的，并不关心zookeeper。
* broker发生变化后，producer获取元数据的功能不能动态变化。
* 获取元数据时使用的broker列表由producer的配置中的 metadata.broker.list 决定。该列表中的机器只要有一台正常服务，producer就能获取元数据。获取元数据后，producer可以写数据到非 metadata.broker.list 列表中的broker

### kafka 常见问题

#### kafka的高可用性
    * [KAFKA高可用.md](./detailKnowledge/kafkaHighAvailability.md)
  
#### kafka ISR
    * [KAFKAISR.md](./detailKnowledge/kafkaISR.md)
#### kafka ack机制
    * [KAFKAAck.md](./detailKnowledge/kafkaAck.md)
#### kafka zookeeper
    * [kafkaZookeeper.md](./detailKnowledge/kafkaZookeeper.md)

### kafka leader选举
    *[kafka leader选举.md](./detailKnowledge/kafkaLeaderSelection.md)

### 如何保证kafka幂等性，数据只被消费一次
    *【[123.md](./detailKnowledge/kafka幂等性.md)

### 如何保证kakfa数据不丢失

### 如何保证kakfa