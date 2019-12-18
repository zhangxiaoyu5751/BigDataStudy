kafka“各自为政”的leader选举
kafka在kafka0.8.2之前的版本均是采用这种选举方式

1）“各自为政”Leader Election
 每个Partition的多个Replica同时竞争Leader

2）优点
实现简单

3）缺点
Herd Effect
Zookeeper负载过重
Latency较大

总结：缺点很明显，假设有很多个kafka的broker，每个broker又有多个topic，每个topic又有多个partition。这样各自为政的选举，相当耗性能的。

kafka基于controller的leader选举
kafka在0.8.2版开始采用了这种选举方式

1）基于Controller的Leader Election
整个集群中选举出一个Broker作为Controller
Controller为所有Topic的所有Partition指定Leader及Follower

2）优点
极大缓解Herd Effect问题
减轻Zookeeper负载
Controller与Leader及Follower间通过RPC通信，高效且实时

3）缺点
引入Controller增加了复杂度
需要考虑Controller的Failover

总结：1、kafka利用zookeeper去选举出controller；2、kafka通过controller选指定出leader和follower，而无需通过zookeeper了。
