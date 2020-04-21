# HIVE分桶

## hive分桶

- 对于每一个表或者分区，hive可以进一步组织成桶，也就是说桶是更细粒度的数据范围划分，hive也是针对某一列进行桶的组织，hive采取对列值哈希，然后除以桶的个数再取余的方式决定了该条数据存放在哪个桶中。

## 把表或者分区组织称桶的理由：
    1. 获得更高的查询处理效率。桶为表加上了额外的结构，hive在处理有些查询时，能够利用这个结构。具体而言，连接两个在（包含连接列的）相同列上划分了桶的表，可以使用map端连接（map-side join）高效的实现。比如join操作。对于join操作的两个表有一个相同的列，如果对这两个表都进行了分桶操作，那么将存储相同列值得桶进行join就可以。
    2. 让取样更高效。处理大规模数据集的时候，在开发和修改查询的阶段，如果能在数据集的一小部分数据上试运行查询，会更方便。


## bucket map join

    如果想在map端执行map side join，必须有一个小表足以放到各个mapper所在的机器的内存中。但是当这个条件不满足，同时还想做map side join的时候，就需要bucket map join

    bucket map join 需要待连接的两个表在联结字段上分桶（内阁分桶对应hdfs上的一个文件），而且小表的桶数需要时大表桶数的倍数。

    ```
    CREATE TABLE my_user
    (
        uid int,
        name string

    )
    clustered by (uid) into 32buckets
    stored as textfile
    ```
    这样 my_user表就对应32个桶，数据根据uid的hash value和32取余，然后分发到不同的桶中。
    如果两个表在连接字段上分桶，则可以执行bucket map join。具体如下
*设置属性hive.optimize.bucketmapjoin=true* 控制hive执行bucket map join；
对小表的每个分桶文件建立一个hashtable，兵分发到所有做链接的map端。
map端接受了N个小表的hashtable，做链接操作的时候，只需要将小表的一个hashtable放入内存即可。然后将大表对应的split拿出来进行连接，所以内存限制为小表中最大的那个hashtable的大小。

## sort merge bucket map join

对于bucket map join的两个表，如果每个桶内分区字段也是有序的，则还可以进行sort merge bucket map join。建表语句为
```
CREATE TABLE my_user
(
    uid int,
    name string
)
clustered by(id) sorted by (uid) into 21buckets
stored as textfile
```
这样一来，两边bucket做局部join的时候，只需要用类似merge sort算法的merge操作一样，把两个bucker顺序遍历一遍就可以完成，这样甚至不用把一个bucket完整的加载成hashtable，而且可以做全连接操作。

运行sort merge bucket map join时，需要设置的属性为：
set hive.optimize.bucketmapjoin=true;

set hive,optimize.bucketmapjoin.sortedmerge=true;

set hive.input.format=org.apache.hadoop.hive.ql.io.bucketizedHiveInputFormat;


https://www.cnblogs.com/ggjucheng/archive/2013/01/03/2842821.html

https://www.aboutyun.com/thread-12880-1-1.html

http://www.360doc.com/content/18/0412/16/14808334_745066516.shtml