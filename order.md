### 订单管理

订单状态

下单1 已付款2 已发货3 已收货4 取消0



涉及到（订单ID-订单创建时间） 数组的操作：

下单时 append( order ID , 创建订单时间 time)

付款时 delete(order ID)

手动取消 delete(order ID)：检查status是否为1

自动取消（超时） (每隔一段时间判断当前时间和订单创建时间 )