# kakfa的高可用性

kafka 在0.8 版本之前是不支持高可用的。一旦一个或者多个broker宕机 所有partitions都无法提供服务。如果该broker永远不能恢复的话 数据就会丢失。
所以kafka在0.8版本之后提供了high Availability机制。 主要增加了partitions的副本设计。

引入partition的replication后，一个partition就会有多个副本，把这些副本均匀的分布到多个broker上，就保证了数据的安全。在replica上选出一个leader，producer和consumer只和leader交互，其他replica作为follower从leader复制数据。

## 为何需要一个leader
    因为需要保证同一个partition的多个replica之间数据的一致性，如果没有一个leader，所有replica都可同时读写数据，那就需要保证多个replica之间互相同步数据，数据的一致性和有序性非常难保证，大大增加了replica实现的复杂性，也增加了出现异常的几率。而引入leader之后，只有leader负责读写，follower只向leader顺序fetch数据，系统简单高效。




## 如何将replica均匀分布到整个集群

    为了更好的做负载均衡，kafka尽量将所有的partition均匀分布在整个集群上。kafka分配replica的算法如下:
- 将所有broker和待分配的partition排序
- 将第i个partition分配到第（i mod n）个broker上
- 将第i个partition的第j个replica分配到第 （i+j mod n）个broker 上
  

## 生产者如何生产消息

    生产者发布消息到某个partition时。先通过zookeeper找到该partition的leader，然后该producer只讲消息发送到该partition的leader。leader会把消息写入到本地的log。每个follower都从leader pull数据。这种方式上，follower存储的数据顺序和leader保持一致。follower收到该消息并写入log后，想leader发送ack。如果leader收到所有ISR中的所有replica的ack，消息就会被认为是commit。leader就会增加hw并向producer发送ack。

    为了提高性能，每个foll接收到数据立马向leader发送ack。而不是等到数据写到log中


## ISR
leader会跟踪与其保持同步的replica列表，这个列表叫ISR.如果一个follower宕机，或者落后太多，那么leader就会把它从ISR中移除。这里的落后太多 指follower复制的消息落后于leader的条数超过预定值。或者follower超过一定时间没有向leader发送fetch请求。

kafka的复制机制既不是完全的同步复制，又不是单纯的异步复制。事实上，同步复制要求所有能工作的follower都复制完，这条消息才会被认为是commit。这种复制方式极大地影响的吞吐率。而异步复制，follower异步的从leader复制数据。数据只要被leader写入log 就被认为已经commit。这种情况下如果所有follower都落后于leader，如果leader宕机，就会丢失数据。ISR这种方式很好的均衡了确保数据不丢失和吞吐率。

## 如果leader宕机了，怎么在follower中选出新的leader
kafka在zookeeper中维护了一个ISR,只有ISR的成员才有可能被选为leader的可能。如果有f+1个replica，可能容忍f个replica的失败。所以只要ISR中至少有一个follower，kafka就可以保证commit不丢失。但是如果所有partition的所有replica都宕机，就无法保证数据不丢失了，有以下两种方法:
- 等待ISR中的一个replica活过来，选举成为leader
- 选择第一个活过来的replica(不一定是ISR中的) 作为leader

这需要在可用性和一致性中做一个折中。第一种方法等待时间比较长，可能完全僵死，第二种可能丢失消息。这个可以通过用户去具体配置


## kafka如何选举leader

之前是所有follower都尝试创建节点，创建成功就是leader。但是会有问题。
- 可能造成脑裂。并不能保证同一时间所有replica看到的状态是一样的。
- herd effect 如果partition比较多，就会负载比较重。同时集群内部有大量的调整。

0.8版本之后，是从所有broker上选出一个controller。所有partition的leader选举都有controller决定。controller会把leader的改变直通过RPC 的方式通知需要为此做出相应的broker。同时controller也负责增删topic以及replica的重新分配。