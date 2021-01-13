## 三.数据库设计

### 3.1 总体设计思路





### 3.2 ER图



### 3.3 关系数据库



#### 3.3.1 users table

* **设计思路**

users表用于存储用户实体类及其属性。表中每一行为一个用户，记录了其基本属性。本表中所有属性均为非空属性。

* **表格结构**

<img src="C:\Users\汤琼\AppData\Roaming\Typora\typora-user-images\image-20210109201548206.png" alt="image-20210109201548206" style="zoom:80%;" />

**user_id**：string类型，是本表唯一的主键。用于记录用户名。

**password**：string类型。用于记录用户密码的暗文。为了安全性考虑，数据库不存储明文密码。

**balance**：integer类型，初始值为0，约束为不能小于0。用于记录用户账户内的金额。

**token**：string类型。用于记录登录时用户名、时间和终端号生成的标记。在进行重要操作时，需要检查本属性以确定消息来自同一终端。

**terminal**：string类型。用于记录登录时终端号。

#### 3.3.2 user_store table

* **设计思路**

user_store表用于存储商店实体类以及开店联系类。表中每一行为一家店。

* **表格结构**

<img src="C:\Users\汤琼\AppData\Roaming\Typora\typora-user-images\image-20210109201631033.png" alt="image-20210109201631033" style="zoom:80%;" />

**user_id**：string类型，是本表的主键之一。外键约束引用users表中的user_id，用于记录商店的店主。

**store_id**：string类型，是本表的主键之一。用于记录商店名。

#### 3.3.3 store table

* **设计思路**

本表中所有属性均为非空属性。

* **表格结构**

<img src="C:\Users\汤琼\AppData\Roaming\Typora\typora-user-images\image-20210109201711754.png" alt="image-20210109201711754" style="zoom:80%;" />

**store_id**：string类型，是本表的主键之一。外键约束引用users表中的user_id，用于记录书籍所在的商店名。

**book_id**：string类型，是本表的主键之一。用于记录对应书籍的id。

**stock_level**：integer类型，默认值为0。用于记录书籍的库存，本属性值需大于等于0。

**price**：integer类型。用于记录书籍的单价，需满足书籍单价大于0。在不同的商店中，书籍的单价可以不同。

#### 3.3.4 new_order table

* **设计思路**



* **表格结构**

<img src="C:\Users\汤琼\AppData\Roaming\Typora\typora-user-images\image-20210109201838883.png" alt="image-20210109201838883" style="zoom:80%;" />

#### 3.3.5 new_order_detail_table

* **设计思路**



* **表格结构**

<img src="C:\Users\汤琼\AppData\Roaming\Typora\typora-user-images\image-20210109201924403.png" alt="image-20210109201924403" style="zoom:80%;" />

#### 3.3.6 invert_index table

* **设计思路**



* **表格结构**

<img src="C:\Users\汤琼\AppData\Roaming\Typora\typora-user-images\image-20210109201950219.png" alt="image-20210109201950219" style="zoom:80%;" />





### 3.4 文档型数据库



### 3.4 关系模式优化

#### 3.4.1 表的分裂和合并



#### 3.4.2 冗余属性引入



#### 3.4.3 属性 or成表



#### 3.4.4 范式规则



#### 3.4.5 索引创建





## 