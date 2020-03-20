# kafka 幂等性

在旧的版本中，kafka只支持两种语义， at most once和at least once。at most once 保证消息不会多，但是可能会丢失，at least once保证消息不会丢失，但是可能会重复。
在kafka 0.11.0版本中，增加了对幂等的支持，幂等是针对生产者的角度的特性，幂等可以保证生产者发送的消息不会丢失，而且不会重复。

## kafka 实现幂等性原理

    为了实现producer的幂等性， kafka引入了producerID，也就是PID，和Sequence Number。

- PID.每个新的producer在初始化的时候都会被分配一个唯一的PID,这个PID对用户是不可见的。
- Sequence Number. 对于每个PID，该producer发送数据的每个topic partition 都对应一个从0开始递增的sequence number

kafka可能存在多个生产者，同时产生消息，但是对kafka来说，只要保证每个生产者内部的消息幂等就可以了，所以引入PID来标识不同的生产者。
同时不能跨会话，因为如果producer重启的话 会重新赋值一个新的PID


*如果需要跨会话、跨多个 topic-partition 的情况，需要使用 Kafka 的事务性来实现。*
对于每个给定的PID, sequence number都会从0开始自增，每个topic-partition 都会有一个独立的 sequence number.
producer发送数据的时候，将会给每条消息标识一个sequence number，server 也就通过这个来验证数据是否重复的。broker都有缓存了这个sequence number，对于接受的每条消息，如果序号比broker缓存中序号大，那么就接受它，否则就丢弃。这样就能保证幂等。



