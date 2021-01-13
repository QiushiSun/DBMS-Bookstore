## be
后端

所有__init__.py都没有内容，不用管
### app.py
### server.py

### model
#### __init__.py
空
#### buyer.py
new_order 创建新订单 涉及store,new_order,new_order_detail 表

payment 支付订单 涉及new_order,user,user_store,new_order_detail表

add_funds 增加余额 涉及user表

#### dbconn.py
类DBConn，三个函数判断：user，book，store是否存在

#### error.py
错误代码含义，401+511to528

不需要整体大改
#### seller.py
add_book 给店铺增加图书 涉及store表

add_stock_level 添加书籍库存 涉及store表

create_store 创建店铺 涉及user_store表

#### store.py
类store，初始化了5张表
user(user_id,password,balance,token,terminal)

user_store(user_id,store_id)

store(store_id,book_id,book_info,stock_level)

new_order(order_id,user_id,store_id)

new_order_detail(order_id,book_id,count,price)


#### user.py
register 登录 涉及user表

check_token 核对token 涉及user表

check_password 核对password 涉及user表

login 登录 涉及user表

logout 登出 涉及user表

unregister 注销 涉及user表

change_password 修改密码 涉及user表

### view
和model中匹配的route

view/auth.py --- model/user.py

view/buyer.py --- model/buyer.py

view/seller.py --- model/seller.py

## doc
和be/view对应的接口定义，包括各功能的 URL,request,response

doc/auth.md --- view/auth.py --- model/user.py

doc/buyer.md --- view/buyer.py --- model/buyer.py

doc/seller.md --- view/seller.py --- model/seller.py

## fe
前端，类似于我们的route.py

### access
据翁ls说有连接数据库的部分

## script