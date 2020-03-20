## spark vs storm vs Flink

### storm
    storm会执行一个由spout 和bolt形成的拓扑结构，属于真正的流式计算
### spark
    其实是按照minibatch的方法计算的 流式处理的话 就是spark-streaming。是spark core的一个扩展。是按照时间间隔将其分为一段一段的批处理作业。

### flink
    是一个针对流数据和批数据的分布式处理引擎。主要处理的场景是流数据。同时，Flink支持本地的快速迭代。
### 进行对比分析
-   数据处理方面。 storm 是真正的流式计算，每条数据都会触发计算。spark是minibatch计算，flink也是流式计算
-   延迟方面 storm是ms级别延迟，spark是s级别延迟，flink 是ms级别延迟。
-   吞吐量方面。storm相较于spark 和flink 来说， 是比较低的，flink和spark吞吐量大

storm 非常适合任务量小但是速度要求比较高的应用。如果非常在意延迟性的话，storm可能是首选。
spark streaming，如果对延迟要求不是很高的话，同时如果还要做机器学习的话，可以使用spark，天然对接spark生态技术栈的组间。
flink，支持乱序和延迟时间。如果对实时要求比较高的话，可以使用flink


## spark中常用算子的区别（map, mapPartitions, foreach, foreachPartition）
- map 用于遍历RDD, 将函数应用于每一个元素，返回新的RDD (transformation 算子)
- foreach 用于遍历RDD，将函数应用于每一个元素，没有返回值(action算子)
- mapPartitions 用于遍历操作RDD中的每一个分区，返回生成一个新的RDD(transformation算子)
- foreachPartition 用于遍历操作RDD中的每一个分区，无返回值(action算子)

一般使用 mappartition 和foreachpartition算子比map 和foreach更高效，推荐使用

## spark中的宽依赖 窄依赖
- 宽依赖 指的是多个子RDD 的partition会依赖同一个父RDD的partition 关系是一对多。父RDD的一个分区的数据会去到子RDD的不同分区里面。会有shuffle的产生
- 窄依赖 指一个父RDD的partition最多被子RDD的一个partition使用，是一对一的。没有shuffle的产生。

## spark中如何划分stage
 spark任务会根据RDD之间的依赖关系，形成一个DAG有向无环图。DAG会提交给DAGScheduler。DAGScheduler会把DAG划分成相互依赖的多个stage。划分依据是宽窄依赖。遇到宽依赖就划分一个stage。每个stage包含一个或者多个task。
 - spark可以因为不同的action触发多个job。一个程序中可以有多个job。每个job是由一个或者多个stage构成的。后面的stage依赖前面的stage，也就是只有前面的stage计算完毕后，后面的stage才会运行。
 - 比如 reducebykey，groupbykey，join算子，会导致宽依赖的产生。
 - 从后往前，遇到宽依赖就切割stage。

## RDD的操作
- transformation 转换算子。现有的RDD通过转换生成一个新的RDD，转换是lazy的。
- action 动作算子。在RDD上运行计算后，返回结果给驱动程序或者写入文件系统
  比如，map就是一种transformation ，他爸数据集中每一个元素都传递给函数，并返回一个新的数据集表示结果。reduce就是一个action，他会通过一些函数把所有元素叠加起来，并最终返回结果给driver程序。
  # TODO:补充算子
transformation算子有：
* map
* filter
* flatmap
* mapPartitions
* groupbyKey

action算子有：
* 


## RDD缓存
spark可以使用persist和cache方法将任意rdd缓存到内存或者磁盘文件系统中。缓存是容错的，如果一个rdd的分区丢失，可以通过构建他的transformation进行重构。一般executor内存60%用来做cache，剩下的40%做task。
如何选择不同的storageLevel：
- 如果RDD可以很好的和默认的存储级别就是memory only 契合的话 就不需要做修改的，因为这是最优的
- 如果不行，就试着用memory_only_ser并且选择一个快速序列化的库使得对象在又比较高的空间使用率的情况下，依然可以更快的被访问
- 尽量不要存储到硬盘上，除非数据特别大。因为重新计算一个分区的速度，和从硬盘中读取速度基本差不多快。


## RDD共享变量
spark在默认情况下，如果一个算子的函数使用到了外部的变量，那么这个变量的值就会拷贝到每个task当中。此时每个task智能操作自己的那份变量副本，如果多个task想要共享一个变量的话，那么这种方式是做不到的。

spark为此提供了两种共享变量。一种是 broadcast Variable(广播变量), 另外一种是Accumulator(累加变量)。broadcast variable会将使用到的变量，仅仅为每个节点拷贝一份，更大的用处是优化性能，减少网络传输以及内存消耗。Accumulator 则可以让多个task共同操作一分变量，主要可以进行累加操作。
spark 提供的broadcast variable 是只读的。并且在每个节点上只会有一个副本。而不会为每个task都拷贝一份副本。因此最大的作用就是减少变量到各个节点的网络传输消耗。以及在各个节点上的内存消耗。此外，spark内部也使用了高效的广播算法来减少网络消耗。

- 广播变量
    * 广播变量缓存到各个节点的内存中，而不是每个task
    * 广播变量被创建后，能在集群中运行的任何函数调用
    * 广播变量是只读的，不能再被广播后进行修改
    * 对于大数据的广播，spark尝试使用高效的广播算法来降低通信成本。
- 累加器
    * 只支持加法操作，可以实现计数器和变量的求和
  
## spark如何防止内存溢出
- driver端的内存溢出

可以通过增大driver的内存参数 spark.driver.memory来设置。
这个参数用来设置driver端的内存。在spark程序中，sparkcontext，dagscheduler 都是运行在driver端的。对应rdd的stage切分也是在driver端运行，如果自己写的程序有很多的步骤，切分出很多的stage，这部分信息消耗的是driver的内存，这个时候需要调大driver的内存
- map过程中产生大量对象导致内存溢出
  
这种溢出的原因是单个map中产生了大量的对象导致的。比如 rdd.map(x => for (i <-1 to 10000)yield i.toString) 这个操作在rdd中每个对象都产生了10000个对象，很容易产生内存溢出的问题。针对这种问题，在不增加内存的情况下，可以通过减少每个task的大小，以便达到每个task即使产生大量的对象 executor内存都装得下。具体点的做法就是可以再会产生大量对象的map操作之前调用repartition方法，分区成更小的块传入map。比如 rdd.repartition(10000).map(x => for (i < -1 to 100000) yield i.toString)

*面对这种问题不能使用rdd.coalesce方法，这个方法只能减少分区，不能增加分区，不会有shuffle过程*

- 数据不平衡导致内存溢出

数据不平衡有可能导致内存溢出之外，也有可能导致性能的问题，解决办法和上面类似，就是调用repartition重新分区。

- shuffle后内存溢出

shuffle内存溢出的情况可以说是shuffle后，单个文件过大导致的。在spark中，join，reducebykey这一类的过程，都会有shuffle的过程，在shuffle的使用，需要传入一个partitioner。大部分spark中的shuffle操作，默认的partitioner都是hashpartitioner。默认值是父rdd最大的分区数，这个参数通过spark.default.parallelism控制。这个参数只对hashpartitioner有效，如果是别的或者是自己实现的，需要在代码里面增加partition的数量

- standalone模式下资源分配不均衡导致内存溢出

在standalone模式下，如果配置了total-executor-cores和executor-memory这两个参数，但是没有配置executor-core这个参数的话，就可能导致每个executor的memory是一样的，但是cores的数量不同，那么在core数量多的executor中，由于能够同时执行多个task，就导致内存溢出情况。这种情况需要同时配置executor-cores参数，确保资源分配均衡。


## spark的数据倾斜现象 原因 后果

### spark出现数据倾斜的现象

多数task执行速度较快，少数task执行时间非常长。或者等待很长时间后提示你内存不足，执行失败

### 数据倾斜原因
- 数据问题
  - key本身分布不均衡(包括大量的key为空)
  - key的设置不合理
- spark使用问题
  - shuffle并发度不够
  - 计算方式有问题

### 数据倾斜后果

stage最后的执行时间受限于最后那个执行完成的task，因此运行缓慢的任务会拖垮整个程序的运行速度

过多的数据在同一个task中，会把executor撑爆


## spark数据倾斜的处理

### 1. 使用hive ETL预处理数据

#### 适应场景
导致数据倾斜的是hive表。如果hive表本身的数据就很不均衡，而且业务需要频繁的使用spark 对hive某个分析进行操作，那么比较适合这种方案

#### 实现思路
通过hive进行数据预处理，通过etl预先对数据按照key聚合或者是预先进行join，这样的话 就不需要使用原先shuffle算子执行操作了

#### 方案优点
实现简单便捷，完全规避掉了数据倾斜。spark性能大幅度提升

### 2. 过滤少数导致倾斜的key

#### 使用场景
如果发现导致数据倾斜的key只有那么几个，而且对数据计算本身影响不大
#### 实现思路
将导致数据倾斜的key过滤掉之后，这些key就不会参与计算了
#### 方案优点
实现简单，效果很好，规避掉数据倾斜
#### 方案缺点
使用场景不多，很多时候导致数据倾斜的key还是很多的

### 3.提高shuffle并行度

#### 实现思路
在执行shuffle算子的时候，给算子传入一个参数 比如reducebykey(1000) 这个参数就设置了这个算子执行时shuffle read task的数量。
#### 实现原理
增加shuffle read task的数量。把原本分配给一个task的多个key分配给多个task，从而让每个task处理比原来更少的数据
#### 方案优点
实现简单，有效缓解和减轻数据倾斜影响
#### 方案缺点 
效果有限 通常无法彻底解决数据倾斜。比如有一个key有100w的数据，那么增加多少还是会分配到一个task上处理。

### 4 两阶段聚合(局部聚合+全局聚合)

#### 使用场景
对rdd执行reduceByKey等聚合类shuffle算子或者在spark sql中使用group by语句进行分组聚合的时候。比较适合
#### 实现思路
第一次聚合，是局部聚合，先给每个key打上一个随机数，比如(hello, 1) (hello, 1) (hello, 1) (hello, 1)，就会变成(1_hello, 1) (1_hello, 1) (2_hello, 1) (2_hello, 1) 然后对打随机数的数据进行reducebykey的操作，进行局部聚合 那么局部聚合结果，就会变成了(1_hello, 2) (2_hello, 2)。然后将各个key的前缀给去掉，就会变成(hello,2)(hello,2)，再次进行全局聚合操作，就可以得到最终结果了，比如(hello, 4)
#### 方案有点
 对于聚合类的shuffle操作导致的数据倾斜效果是不错的
 ### 方案缺点
 仅仅适用于聚合类的shuffle操作，如果是join类的，还要有其他方案

 ### 5.把reduce join 转成map join

#### 使用场景
在对rdd 进行join操作的时候，或者spark sql使用join 语句的时候，如果join操作中的一个rdd或者表数据量比较小，可以使用
#### 实现思路
不使用join进行连接操作，而使用broadcast变量以及map算子实现join操作，规避掉shuffle操作，避免数据倾斜
#### 实现原理
普通join是走shuffle过程的，一旦shuffle就会发生reduce join。如果一个rdd比较小，就可以使用广播小rdd全量数据+map 算子来实现join同样的效果，也就是map join。不会发生shuffle
#### 方案优点
对join操作导致的数据倾斜效果非常好
#### 方案缺点 
只适用于一个大表一个小表
### 6.采样倾斜key拆分join操作
#### 使用场景
两个edd数据量都比较大，可以看一下key的分布，如果出现数据倾斜，是因为其中一个rdd的少数几个key数据量过大，而另外一个分布比较均匀，就可以采用这种方式

#### 实现原理
可以吧少数几个key拆成独立的rdd，然后加前缀去join。
对包含少数几个数据量过大的key的那个RDD，通过sample算子采样出一份样本来，然后统计一下每个key的数量，计算出来数据量最大的是哪几个key。
然后将这几个key对应的数据从原来的RDD中拆分出来，形成一个单独的RDD，并给每个key都打上n以内的随机数作为前缀，而不会导致倾斜的大部分key形成另外一个RDD。
接着将需要join的另一个RDD，也过滤出来那几个倾斜key对应的数据并形成一个单独的RDD，将每条数据膨胀成n条数据，这n条数据都按顺序附加一个0~n的前缀，不会导致倾斜的大部分key也形成另外一个RDD。
再将附加了随机前缀的独立RDD与另一个膨胀n倍的独立RDD进行join，此时就可以将原先相同的key打散成n份，分散到多个task中去进行join了。
而另外两个普通的RDD就照常join即可。
最后将两次join的结果使用union算子合并起来即可，就是最终的join结果。
#### 方案优点
join+少数key导致的 可以使用该方法
#### 方案缺点
倾斜key很多的话 不适合

### 使用随机前缀+扩容rdd进行join
#### 使用场景
如果join操作时候，有大量的key出现数据倾斜，拆分key也没有什么意义
#### 实现原理
方案的实现思路基本和“解决方案六”类似，首先查看RDD/Hive表中的数据分布情况，找到那个造成数据倾斜的RDD/Hive表，比如有多个key都对应了超过1万条数据。
然后将该RDD的每条数据都打上一个n以内的随机前缀。
同时对另外一个正常的RDD进行扩容，将每条数据都扩容成n条数据，扩容出来的每条数据都依次打上一个0~n的前缀。
最后将两个处理后的RDD进行join即可。
#### 方案优点
对join类型的数据倾斜基本都可以处理，而且效果也相对比较显著，性能提升效果非常不错。

#### 方案缺点
该方案更多的是缓解数据倾斜，而不是彻底避免数据倾斜。而且需要对整个RDD进行扩容，对内存资源要求很高



## spark中 map side join
将多分数据进行关联是数据处理过程中常见的做法，但是因为框架提供的join操作一般会把数据根据key发送到所有reduce的分区中去，发生shuffle。造成大量的网络和磁盘消耗，效率低，这种叫做reduce side join。如果其中有张表较小的话，我们则可以自己实现在 map 端实现数据关联，跳过大量数据进行 shuffle 的过程，运行时间得到大量缩短，根据不同数据可能会有几倍到数十倍的性能提升

原理：reduce side join 的缺陷在于会把key相同的数据发送到同一个partition中进行运算，大数据集的传输需要长时间的IO.
把少量的数据转化成map进行广播，发送到每个节点上。

## kakfa + sparkStreaming

### 如何实现sparkStreaming 读取kafka数据

- receiver
  - receiver是采用了kafka高级api，利用receiver接收器来接受kafka topic的数据，从kafka接收来的数据会存储在spark 的executor中，之后 spark streaming 提交job会处理这些数据，kafka中topic的偏移量是保存在zk中的。

  * 在receiver模式中，spark的partition和kafka的partition并不是相关的，所以我们加大每个topic的partition数量，仅仅是增加线程来处理由单一receiver消费的主题。并没有增加spark处理数据的并行度
  * 对于不同的group和topic 我们可以使用多个receiver创建不同的dstream并行接收数据，然后最后union起来形成一个dstream
  * 但是在默认配置下，这种情况可能会丢失数据， 因为receiver一直在接收数据，如果他ack zk但是数据还没处理的时候，executor挂掉，缓存的数据就丢失了。如果想要数据不丢失的话，可以启动WAL。这个wal会同步把接收到的kafka数据写到hdfs的预写日志中。失败了也可以从日志汇总回复

- direct
  direct模式会周期性的获取kafka中每个topic的每个partition中最新的offset。然后根据设定的rate去处理每个batch

  #### 两种方式的优缺点

  - receiver方式 
  
  这种方式可以保证数据不丢失，但是无法保证数据只被消费一次，wal实现的是at least once语义。如果写入到外部存储的数据还没有将offset更新到zookeeper就挂掉，数据就会被反复消费
  - direct方式

    - 这种方式比起reveiver模式机制更加健壮，区别于使用reveiver来被动接受数据，direct会周期性的主动查询kafka，来获取每个topic+partition的最新offset。
    - 简化并行读取。如果读取多个partition，不需要创建多个输入dstream然后union，spark会创建和kafka partition一样多的rdd partition，并且会并行从kafka中读取数据，所以kafka partition和rdd partition之间，有一个一对一的映射关系
    - 高性能。如果要保证数据不丢失，receiver方式需要开启wal机制。这种方式效率低下，因为数据本身在kafka上由于本身的高可靠机制就被复制了一份，然后在这里又会复制一份到wal中，而direct不需要开启wal，只要kafka有数据复制，就可以通过kafka副本进行恢复
    - 一次且仅一次的机制。reveiver机制数据可能被处理多次，但是direct方式，使用kafka简单api，spark自己负责追踪消费的offset，并保存到checkpoint中，可以保证数据是消费一次，不过需要自己完后才能将offset写入zk中。sparkStreaming程序自己消费完成后，自己主动去更新zk上面的偏移量
  
  ## spark master 进行HA 的时候，有哪些数据保存在zk？

    worker， master，application， executor standby节点都要从zk上获取元数据信息
在master切换的时候需要注意两点：
- 在master切换的过程中，所有已经正在运行的程序都正常运行，因为spark application在运行前已经通过cluster manager获得了计算资源，所以在运行时，jon本身的调度和处理和master没有关系
- 在master切换过程中 唯一影响的是不能提交新的job。一方面不能提交新的应用给集群，因为只有active master才能接受新的程序提交请求，另一方面，已经运行的程序不能action操作触发新的job提交请求。

## spark master HA 主从切换过程不会影响集群已有的作业的运行，为什么？
因为在程序运行之前，已经向集群申请过资源，这些资源已经提交给driver了，是粗粒度分配，一次性分配好之后不需要在关心，在运行时，让driver和executor自动交互。

## 什么是粗粒度，细粒度？优缺点？
- 粗粒度，启动的时候就分配好资源，程序启动，后续具体使用分配好的资源，不需要再分配，好处，作业特别多的时候，资源复用率比较高 缺点 容易造成资源浪费。
- 细粒度 用资源的时候分配，用完就回收，启动麻烦，启动一次分配一次

## driver 的功能
一个spark任务作业运行时，都会启动一个driver进程，也就是作业的主进程，具有main函数，并且有sparkcontext实例。是程序的入口。driver负责向集群申请资源，向master注册信息，负责作业的调度，负责作业的解析，生成stage并调度task到executor上，包括dagscheduler和taskscheduler

## spark的几种部署模式，每种模式的特点

- 本地模式
  
spark可以在本地跑，以多线程的方式直接运行在本地。分为3类
    * local: 只启动一个executor
    * local[k]: 启动k个executor
    * local[*]: 启动和cpu数目相同的executor
- standalone模式
  
分布式部署集群，自带完整的服务，资源管理和任务监控都是spark自己监控，这个模式也是其他模式的基础
- spark on yarn 模式
  
分布式部署集群 资源和任务监控交给yarn管理，但是目前只支持粗粒度资源分配模式，包括cluster和client运行模式。cluster是个生产，driver运行在集群子节点，具有容错，client适合调试，driver运行在客户端
- spark on mesos 模式

spark on mesos支持粗粒度模式和细粒度模式

## spark worker主要工作

主要功能：管理当前节点内存，CPU使用情况，接受master发送过来的资源指令，通过executorrunner启动程序分配任务，发送心跳给master。不会运行代码，具体运行的是executor。


## spark优化
- 平台层面的调优： 避免不必要的jar包分发，提高数据本地性，选择高效的存储格式如parquet
- 应用程序层面的调优：过滤操作符的优化降低过多小任务，降低单条记录的资源开销，处理数据倾斜，复用rdd进行缓存，作业并行执行等
- jvm层面的调优：设置合适的资源量，启用高效的序列化方法如kyro等。由于他需要对类进行注册，所以并没有把他当做默认的序列化方式，但是他速度更快，空间占用更小。

## RDD 的5大特性
- RDD 是有一个一个的partition组成的
- 每一个函数都可以作用于rdd的每一个partition上
- rdd之间依赖关系是血缘关系 可以根据血缘关系重新计算丢失分区的数据
- kv形式的partition，都可以用分片函数按照key重新分区
- 数据本地性，选择最优的位置去计算，将计算任务分配到他要处理数据块的存储位置上去计算

## RDD的创建方式
