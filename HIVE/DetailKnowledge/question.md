# Hive

## hive的概念
hiev是一个构建在hadoop上的数据仓库软件，他可以使数据结构化，提供类sql的方式对数据进行分析处理，hive把hivesql转换成一系列的mapreduce作业执行。目前hive支持的几种计算引擎有： spark，mapreduce Tez


## hive执行原理
- 用户提交查询任务给driver
- 编译器获得该用户的任务plan
- 编译器根据用户任务从metastore里面获取需要的hive元数据信息
- 编译器得到元数据信息之后，对任务进行编译，先把hive转换成抽象语法树，然后遍历抽象语法树，转换成基本的查询逻辑单元，然后将查询单元转换成操作树，优化操作树，转换成mapreduce任务
- 把任务提交给driver
- driver将任务转发给executionENGINE 执行，任务会直接读取hdfs文件进行相应的操作。
- 获取执行结果


## hive支持的几种计算引擎的区别

- mapreduce: 把算法抽象成map和reduce两个阶段进行处理，非常适合数据密集型计算，在大数据量下比较有优势，但是读取hdfs次数比较多
- tez: 源于mapreduce框架，把mapreduce过程拆分成多个子过程，拆分之后可以进行合理组合，产生新的操作，最后形成一个大的dag作业，减少任务运行时间。比较适合DAG应用，小数据量下性能比较优秀
- spark: 基于mapreduce，中间结果保存在内存中，不需要读写hdfs。 对于需要迭代的算法更友好，但是大数据量下吃内存

## hive和关系型数据库的区别
- 首先，hive的延迟性较高，数据量比较大，具有可扩展性，对于处理小数据来说，没有什么优势， 而传统的关系型数据库适用于OLTP，即时性较高
- hive大部分做的操作是select，通常是用作数据分析，不支持数据更新 而关系型数据库支持CURD
- hive存储的数据是在hdfs， 数据库则保存在本地
- hive底层是mapreduce，mysql底层是excutor执行器
- hive数据格式可以用户自定义，mysql有自己的系统定义格式

## 行式存储和列式存储的区别
- 行式存储一行是一条记录，放在一个bolck快中，方便进行CRUD操作，但是如果只查询某几列的时候需要读取整行的数据，数据量大的时候会影响性能，同时，一整行的数据都放到一个block中，不容易获得一个高的压缩比。主要适合于在线交易性质的OLTP  
- 列式存储只有涉及到的列才会被查询，同一属性的数据放到一起压缩性能好，但是insert/update不方便，不适合数据量小的数据。以及频繁更新会更新的数据，主要是和海量数据静态分析 OLAP

## hive表几种存储格式的区别

- textfile 默认的存储格式，存储方式是行存储，数据不做压缩，磁盘开销大
- Sequencefile 也是行存储，是二进制文件，他把数据以kv的形式序列化到文件中，存储要比textfile大一些。因为多存储了一些冗余信息包括header，metadata等数据
- ORC是先根据行进行分块，然后再吧块按照列式存储 压缩效率高，存取也快
- parquet 列式存储。压缩率比orc低。查询效率也比orc低，但是支持impala查询。所以说如果仅仅是在hive中存储和查询的话，建议使用orc，如果使用impala的话 就使用parquet

## SQL转换成mapreduce的过程
* 首先根据语法规则进行SQL的语法解析和词法解析，然后生成抽象语法树AST tree
* 遍历抽象语法树，抽象出查询的基本组成单元QueryBlock
* 遍历QuerybLock， 翻译成执行操作树 OperatorTree
* 逻辑层优化器进行operatorTree变换，合并，减少shuffle数据量
* 遍历OperatorTree,翻译成mapreduce任务
* 物理层优化器进行mapreduce任务的变换，生成最终的执行计划

## Hive内部表和外部表的区别
hive的外部表创建的时候被external修饰
区别：
- 内部表数据由hive自身进行管理，外部表的数据有hdfs管理
- 内部表数据存储的位置是hive.metastore.warehouse.dir下面，外部表的数据的存储位置有自己制定
- 删除内部表会删除原数据以及存储的数据，删除外部表仅仅会删除元数据，hdfs上的数据不会被删除

外表可以大家一起用，被误删也可以恢复，比如日志的原始数据，具有安全性。内部表可以存出一些中间结果。


## Hive静态分区动态分区
为了对表进行合理的管理以及提高查询效率  hive可以把表进行分区 按照物理分层的方式
set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;
如果一张表同时有静态分区和动态分区的话 静态分区一定要在动态分区前面，同时，动态分区的分区名称是根据位置来决定的。比如
create table table_1 (
    name string,
    ip string
)
partitioned by (dt string , ht string)
row format delimited fields terminated by '\t'

insert overwrite table table1 partition(dt, ht) select a, b, dt, ht from ***;


## HIVE优化

### 列裁剪 分区裁剪
在hive读取数据的时候，只读取查询中需要使用到的列， 节省开销，同时，查询的过程中，只选择需要的分区，减少查询的数据量

### map 输入合并
在执行mapreduce程序的时候，一般情况下一个文件需要一个mapper来处理，但是如果数据源是大量的小文件的话，就会启动大量的mapper任务，会浪费大量的资源，这种情况下，可以吧输入的小文件进行合并，减少mapper数量。

set hive.input.format=org.apache.hadoop.hive.ql.combineHiveInputFormat;

### map/reduce输出合并合并小文件
文件数目小，容易在文件存储造成瓶颈我们可以合并map 和reduce的结果文件来消除影响
hive.merge.mapfiles=true

hive.merge.mapredfiles=true

设置合并文件的大小

set hive.merge.size.per.task=25610001000;

### 合理控制map reduce的数量
#### mapper设置
如果想要调整mapper个数，在调整之前，需要确定下处理文件的大概的大小以及文件的存在形式，是大量小文件，还是单个大文件，然后设置合适的参数。
如果是单个大文件的话，我们可以适当增加mapper个数，即调整mapreduce.map.tasks 来设置成一个比较大的值。
如果是想要减少mapper个数的话，可以设置mapred.max.split.size 为一个比较大的值


#### reducer设置
reduce的个数对整个作业运行来说有很大影响，如果reduce设置过大，就会产生很多小文件，如果reduce个数设置过小，每个reduce处理的数据就会变大，会引起OOM异常
如果设置了mapred.reduce.tasks参数，hive会直接吧这个值当做reduce的个数。
如果没有设置的话，hive 会自己进行计算，会根据设置的参数 每个reduce任务处理的数据量 以及 每个任务最大的reduce个数 来判断，首先会根据数据总量/每个reduce任务处理的数据量 来计算需要多少reduce，然后和每个任务reduce个数取最小。
如何调整reduce数量呢？
- 调整每个reduce处理数据的值的大小 hive.exec.reducers.bytes.per.reducer
- 直接设置 reduce.task的值

reduce并不是越多越好，启动和初始化也会消耗时间和资源。同时呢，也会产生过多的小文件给下一个输入

小文件是如何产生的呢：
- 动态分区插入数据产生小文件（少用动态分区，用时记得按distribute by分区。）
- reduce数量越多，产生小文件数量越多（可以通过减少reduce的数量）
- 数据源本身就包含小文件（用 hadoop archive把小文件进行归档）
  

  ### sql语法优化

  #### 优先过滤数据
  减少每个阶段的数据量，能用分区字段尽量使用，这样最大限度的减少参加join的数据量

  #### 小表join大表
  小表join大表的时候应该遵守小表在前，大表灾后的原则，因为在reduce阶段，左边的表会被加载到内存，吧数据量少的表放到左边会减少内存溢出的几率。应该保证表的大小从左到右以此增加

  #### 使用相同的连接键
  如果3张或者3张以上的表进行join的时候，如果on条件使用相同字段，那么会合并为一个mapreduce job，利用这种特性，可以吧相同的join on的放入一个jon来节省执行时间。

 #### 启用mapjoin
    mapjoin是把join的两个表中较小的一个表分发到各个map的进程的内存中，在map阶段进行join操作，这样就不用reduce步骤，避免shuffle

    set hive.auto.convert.join = true; 会自动吧reduce端的common join 转换成map
    join    有一个参数 默认25M
#### 尽量避免原子操作
尽量避免一个SQL包含复杂的逻辑，可以使用中间表来完成复杂的逻辑查询

#### groupby优化
##### map端聚合
默认情况下，map阶段同一个key的数据会分发到同一个reduce上，当一个key的数据过大的时候，会产生数据倾斜。
并不是所有的聚合操作都需要在reduce端进行，很多局和操作可以现在map端进行部分聚合


set hive.map.aggr=true;

#### 有数据倾斜的时候进行负载均衡
set hive.groupby.skewindata=true;
当选项为true的时候，会生成两个mapreduce任务，第一个mapreduce任务中，map输出结果会随机分布到reduce中，每个reduce做部分局和操作，然后第二个mapreduce任务会根据预处理的结果按照group by key 分布到reduce中，最后完成聚合操作

#### order by 优化

order by只在一个reduce中进行，若果一个大数据及进行order by，会导致order by 的数据相当大，造成查询缓慢。
- 只在最终结果上进行order by。不在中间的结果集上进行排序
- 如果只是取排序后的前N条数据，可以使用distribute by 和sort by在各个reduce上进行排序后取前N条。然后再对合并后的所有结果排序取前N条。

#### 优化count distinct
可以用子查询的方式来优化 count distinct，避免发生数据倾斜
#### 本地化执行
如果hive处理数据量比较小的时候，没有必要启动分布式模式，直接通过本地模式就可以
set hive.exec.mode.local.auto=true;


#### 并行执行

有的查询可能会被转化成多个阶段，包括mapreduce，合并，limit ，默认情况下，一次只执行一个阶段，但是如果不相互依赖的话  是可以并行执行的，但是比较浪费资源

set hive.exec.parallel=true;
   
### hive如何解决数据倾斜
hive 出现数据倾斜的原因有很多，比如说数据本身就是这样，比如说 key的分布不均匀或者是key太集中
那么通常解决hive的数据倾斜的问题有两种大的方向，一种 是设置参数，一种是优化SQL

- 设置参数
    - set hive.map.aggr= true;
    有些时候是可以在map端提前进行举个的，吧相同的key归到一起，减少数据量，这种可以在一定程度上提高性能，但是也可能作用不大
    - set hive.groupby.skewindata=true.进行负载均衡，生成的查询计划会有两个mr，第一个mr会把map的输出结果随机分布到reduce当中，每个reduce进行聚合操作 然后输出结果，这样处理相同的key 可能会被分发到不同的reduce当中，第二个mr 的job根据预处理的结果按照key分布到reduce当中，最终完成聚合操作。就是预处理 进行一次聚合来减小数据量的操作。

- sql 语句优化
* 如果是count distinct 导致的数据倾斜，可以用groupby 或者子查询来代替
  * 进行表join 的时候，通常会产生数据倾斜
    * 首先，在小表join大表的时候，可以采用map join 的方法，就避免了shuffle以及reduce产生的数据倾斜
    * 其次，如果是大表join大表的时候，分情况讨论。首先，如果造成数据倾斜的key都是无效的数据的话，那就可以首先过滤掉这种数据，或者把空值的数据替换成随机数，分散到不同的reduce中，这样就不会对结果产生影响，
  其次，如果有用的只有一小部分的话，就可以先把这一小部分取出来，然后进行map join。

总的来说，数据倾斜的根本原因就是key分布不均衡，所以要么设计从源头解决，直接在map端搞定，要么就是在分区的时候把无效的数据都过滤掉，或者打乱数据，让他们进入到不同的reduce中。