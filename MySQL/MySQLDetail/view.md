# MySQL视图


## 视图的好处
- 安全。
    一些数据表有重要的信息，有些字段是保密的，不能让用户直接看到，这样可以创建一个属兔，在这张视图当中只保留一部分字段，这样 用户就可以查询自己需要的字段，不能查看保密的字段。
- 简单
    不需要关心背后的表结构，关联条件和筛选条件，直接使用符合条件的结果集就可以
-  数据独立
    一旦视图的结构确定了， 可以屏蔽表结构变化对用户带来的影响，原表添加列队视图没有影响。

## 视图ALGORITHM参数

- 使用merge策略。MySQL会先将输入的查询语句和视图的声明语句进行合并，然后执行合并后的语句进行返回。但是如果输入的查询语句中不允许包含聚合函数。
- 使用temptable策略。MySQL 先基于视图的声明创建一张temporary table，当输入查询语句时会直接查询这张temporary table。但是temptable的效率要比merge策略低。
- undifined策略，如果创建视图的时候不指定策略，默认使用此策略。