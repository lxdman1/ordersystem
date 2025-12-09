# ordersystem
## 介绍
一个基于django的点餐网站，实现点餐、上菜、结算、后台管理等基础功能。可以拿来做个毕业设计或者课程大作业的参考。

## 如何使用
把文件打包下来，在自己的电脑上配置python环境，安装django、channels、channels-redis等，安装redis（windows用户要安装docker才可以使用redis）。
打开cmd进入文件夹使用“uvicorn orderSystem.asgi:application --reload”启动服务（runserver默认是不支持websocket的）

## 效果图
### 点餐界面
![image](https://github.com/lxdman1/ordersystem/blob/main/%E7%82%B9%E9%A4%90%E7%95%8C%E9%9D%A2.PNG)

### 桌台管理界面
![image](https://github.com/lxdman1/ordersystem/blob/main/%E6%A1%8C%E5%8F%B0%E7%AE%A1%E7%90%86%E7%95%8C%E9%9D%A2.PNG)

### 桌台点餐信息界面
![image](https://github.com/lxdman1/ordersystem/blob/main/%E6%A1%8C%E5%8F%B0%E7%82%B9%E9%A4%90%E4%BF%A1%E6%81%AF%E7%95%8C%E9%9D%A2.PNG)

### 厨房界面
![image](https://github.com/lxdman1/ordersystem/blob/main/%E5%8E%A8%E6%88%BF%E7%95%8C%E9%9D%A2.PNG)



