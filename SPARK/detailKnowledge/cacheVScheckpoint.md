# spark cache() checkpoint() persisit() 的区别
- 从源码中可以看出，cache底层调用的是 persist方法， 存储等级为：memory only.
cache将RDD以及RDD 的血统缓存到了内存中，当缓存的rdd失效的时候，他们可以通过血统重新计算来恢复。但是checkpoint将rdd缓存到HDFS上，同时忽略了他的血统。
在进行checkpoint时候，需要设置checkpoint路径，另外，在进行checkpoint时候，需要对rdd进行cache。checkpoint会等到job结束后，另外启动专门的job去完成checkpoint，也就是说需要checkpoint的rDD会被计算两次
-  rdd.persist方法和checkpoint区别是，前者虽然可以将rdd的partitions持久化到磁盘，但是该partitions有blockmanager管理，一旦driver program执行结束，也就是executor所在的进程stop。bolckmanager也会被stop。被cache到磁盘上的rdd也就会被清空。但是checkpoint将rdd持久化到hdfs或者本地文件夹，如果不是被手动remove掉，是一直存在的。也就是可以被下一个driver program使用，而cached rdd不能被其他的driver program使用。