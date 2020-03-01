
- [MySQL 聚簇索引和非聚簇索引 以及覆盖索引](#mysql-聚簇索引和非聚簇索引-以及覆盖索引)
    - [什么叫做聚簇索引](#什么叫做聚簇索引)
    - [哪里会用到聚簇索引](#哪里会用到聚簇索引)
    - [聚簇索引的存储方式](#聚簇索引的存储方式)
    - [聚簇索引二级索引为什么存放的是行的主键值，而不是行的指针呢？](#聚簇索引二级索引为什么存放的是行的主键值而不是行的指针呢)
    - [聚簇索引的好处](#聚簇索引的好处)
    - [聚簇索引的缺点](#聚簇索引的缺点)
    - [什么是覆盖索引？](#什么是覆盖索引)
    - [哪些场景可以利用索引覆盖来优化SQL？](#哪些场景可以利用索引覆盖来优化sql)
        - [场景1：全表count查询优化](#场景1全表count查询优化)
        - [场景2：列查询回表优化](#场景2列查询回表优化)

# MySQL 聚簇索引和非聚簇索引 以及覆盖索引

## 什么叫做聚簇索引
    聚簇索引的特点是将数据存储顺序按照索引顺序存储的

## 哪里会用到聚簇索引
    InnoDB的主键采用聚簇索引，其余的是非聚簇索引，而MyISAM 都采用的是非聚簇索引

## 聚簇索引的存储方式
    首先，Innodb的主键采用的是聚簇索引，聚簇索引的叶子节点存放的是数据行本身，因为无法将数据存储到两个不同的地方，所以一个表只能有一个聚簇索引
    
    **聚簇索引的叶子节点存放的是主键值，事务ID，用于事务和MVCC的回流指针以及剩余的所有列**

    聚簇索引的二级索引的叶子节点存放的是索引的值以及行的主键值。

    所以当用二级索引查找数据数据的时候，首先根据二级索引查找对应的索引树，找到对应的行的主键值，然后再去根据聚簇索引去查找对应的数据。

    MyISAM 无论是主键索引或者二级索引，都没有什么区别，叶子节点中都是保存的数据的存储地址，都需要根据存储地址再去寻找最终的数据。

## 聚簇索引二级索引为什么存放的是行的主键值，而不是行的指针呢？

    虽然存放行的指针会占用的空间少一些，但是这样减少了当出现行移动或者数据页分裂时带来的二级索引的维护工作。

    **所以使用聚簇索引的时候尽量将主键定义的小一些，减少占用的空间**


## 聚簇索引的好处

- 当取出一定范围的数据的时候 采用聚簇索引会好一些

- 根据聚簇索引查找的数据会比非聚簇索引查找数据快一些

- 使用覆盖索引扫描的查询可以直接使用页节点中的主键值。


## 聚簇索引的缺点

- 插入速度严重依赖于插入顺序 如果不是按照主键的顺序加载顺序 就不是最快的插入速度
- 更新聚簇索引代价很高
- 采用聚簇索引插入新值得顺序比采用非聚簇索引插入新值的顺序要慢。因为首先要保证主键不能重复， 需要遍历叶子节点，而聚簇索引的叶子节点还记录其他的信息，所以开销要大
- 二级索引可能很大
- 二级索引是两次查找 不是一次查找

## 什么是覆盖索引？
    如果索引包含所有满足查询需要的数据的索引成为覆盖索引(Covering Index)，也就是平时所说的不需要回表操作

    这样通过覆盖索引查找数据的话 就不需要进行回表操作，一次就能查到数据。

## 哪些场景可以利用索引覆盖来优化SQL？

### 场景1：全表count查询优化
        将需要count 的列直接加到索引或者联合索引里面

### 场景2：列查询回表优化
        将需要查询的列加到索引里面 不用进行回表


