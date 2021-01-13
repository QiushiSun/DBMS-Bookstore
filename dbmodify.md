## 数据库修改指南

### 原有数据库

**users**：用户名，密码，钱，标志token，终端

最多添加代理键，不好改

**user_store**：记录用户开了哪些店

最多添加代理键，不好改

**store**：店ID，书ID，库存，书的信息

说是店也记录了书的信息，有明显冗余（书的信息）

可以改成店ID，书ID，库存，书的单价。

新建mongodb数据库记录书的信息。

**new_order**：oid，uid，sid记录当前订单信息

可以添加总价，下单后改价格（优惠）

**new_order_detail**：每个订单每本书的信息。

没有历史订单信息，可以加进去。

### 讨论内容

1. 改数据库，图书和订单

2. 增加功能：搜索。以图搜图，标题和作者倒排索引，content里面的关键词和章节，标签。author可以分成国家和作者名。多个关键词，空格分隔。建立一张大的包含题目作者标签关键字的倒排表或分开建多张倒排表。倒排表建立方法（逐字，分词）

3. 增加订单种类：已完成，发收货，自动取消，手动取消。

   

### book

```json
"book_info": {
    "tags": [ # 把关键字也加到这里面
      "tags1",
      "tags2",
      "tags3",
      "..."
    ],
    "pictures": [
      "$Base 64 encoded bytes array1$",
      "$Base 64 encoded bytes array2$",
      "$Base 64 encoded bytes array3$",
      "..."
    ],
    "id": "$book id$", # mongodb生成的OID
    "title": "$book title$", # 标题 建倒排索引
    "region": "$author region$", # 拆出作者国家
    "author": "$book author$", # 作者 建倒排索引
    "publisher": "$book publisher$", # 出版社
    "original_title": "$original title$", # 建到title的倒排索引里
    "translator": "translater", # 译者 建到作者的倒排索引里
    "pub_year": "$pub year$", # 出版年
    "pages": 10, # 页码
    "binding": "平装",
    "isbn": "$isbn$",
    "author_intro": "$author introduction$", # 关键字建索引
    "book_intro": "$book introduction$", # 关键字建索引
    "content": "$chapter1 ...$" #关键字建索引
    }
# 加入sql store的列
"price": 10, 
# 建sql表 labels
"tag": 标签和关键字 PK
"book_id": mongodb 
"search_id": daiding PK
# 建sql表 倒排索引
"keys":
"search_id":
"book_id":
"type":Title/Author/keyword
# 图片建立mongodb类似倒排表的以图搜图结构
# pending 要建立的数据库 

```

### 订单



