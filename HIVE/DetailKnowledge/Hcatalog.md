# Hcatalog 简介

## 相关描述

**Hcatalog是hadoop的表存储管理工具 提供了一个统一的元数据服务，允许不同的工具如PIG，MapReduce等通过Hcatalog直接访问存储在HDFS上的底层文件。**

Hcatalog 使用了HIve的元数据存储，这样使得像MapReduce这样的第三方应用可以直接从hive底层数据中读取数据，同时，Hcatalog 还支持用户在MapReduce程序中只读取需要的表分区和字段，而不需要读取整个表。

Hcatalog 还提供了一个消息通知服务。

Hcatalog主要解决的问题是，将以前各自为政的数据处理工具（mapreduce，）有机的整合到一起，让合作更加顺畅，提高效率。


## 场景



上面对 HCatalog 解决的问题描述的比较抽象，可能还是有点不好理解，下面通过一个具体的场景来展示 HCatalog 的作用（PS：场景来自 Hive 官网）：

张三将数据上传到 HDFS 上，并且将这些数据加载到相应的表中：
```
hadoop distcp file:///file.dat hdfs://data/rawevents/20100819/data

hcat "alter table rawevents add partition (ds='20100819') location 'hdfs://data/rawevents/20100819/data'"
```

李四需要在 Pig 中对张三加载的这些数据进行处理，如果不使用 HCatalog，那么他只能等到张三把数据加载成功后再手动在 Pig 中进行加载处理：

```
A = load '/data/rawevents/20100819/data' as (alpha:int, beta:chararray, ...);
B = filter A by bot_finder(zeta) = 0;
...
store Z into 'data/processedevents/20100819/data';
```

但如果使用 HCatalog 的话，当数据被张三加载成功后会自动发送消息，之后 Pig 会自动开始处理：
```
A = load 'rawevents' using org.apache.hive.hcatalog.pig.HCatLoader();
B = filter A by date = '20100819' and by bot_finder(zeta) = 0;
...
store Z into 'processedevents' using org.apache.hive.hcatalog.pig.HCatStorer("date=20100819");
```

王五需要在 Hive 中对这些数据进行分析，如果不使用 HCatalog 的话，需要手动将数据加载到 Hive 中的表中，然后进行一系列的分析操作：

```
alter table processedevents add partition 20100819 hdfs://data/processedevents/20100819/data

  select advertiser_id, count(clicks)
  from processedevents
  where date = '20100819'
  group by advertiser_id;
```
但如果使用 HCatalog 的话，王五就可以直接对数据进行分析而不需要再手动加载，因为 Hive、Pig 共享的是同一份元数据：

```
select advertiser_id, count(clicks)
from processedevents
where date = ‘20100819’
group by advertiser_id;
```

由以上的场景可以看出，HCatalog 省去了许多需要人工干预的过程，使各个组件之间的协作自动化，大大提升了效率。
