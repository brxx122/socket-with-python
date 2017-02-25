
基于socket的类HTTP协议设计
===
  本项目是数据通信和计算机网络的期末Project，基于python的socket类实现server和client之间简单的文件操作和传输，前台是使用flask实现的Web应用。




安装
---
1. Python 2.7
2. flask模块
  > pip install flask




工作目录
---

```
Project                      
├── src				# 源代码
│	├── server				    
│	│   ├── document		# server存储的文件
│	│   ├── image			# server存储的图像
│	│	  │    └── head			#学生名单头像图片
│	│   └── server.py		# server源码            
│	└── client				    
│	    ├── node_modules	# npm安装的jquery包
│	    ├── static			# flask的静态文件
│	    │   ├── ...				# bootstrap框架
│	    │   ├── temp			# 下载的文件
│	    │   ├── Uploads			# 上传的文件
│	    │   └── ...				# bootstrap框架
│	    ├── template		# flask的网页模板
│	    ├── client.py		# client的前端app源码
│	    └── client_back.py	# client的后台源码    
├── requirement		# 依赖包
├── README.md		# README
└── 实验报告.pdf	 # 实验报告
```




快速开始
---
1. 在server目录下，运行server.py
   > python server.py

2. 在client目录下，运行client.py
   > python client.py

3. 使用浏览器打开http://127.0.0.1:5000 (建议使用chrome)

4. 在Log in界面输入

   * host：localhost(或者127.0.0.1)
   * port：8000

5. 登录后转到类HTTP协议的介绍页面，通过右上角图标切换页面




功能列表
---
* 文件操作：server端保存/document/student.txt
  * 查看学生名单
  * 查看单个学生信息
    * ID和Name必须存在一个
  * 增加单个学生信息
    * ID、Name、Picture必须同时存在
    * ID和Name不得重复
  * 删除单个学生信息
    * ID和Name必须存在一个
  * 修改单个学生信息
    * SID和SName必须存在一个
    * RID和RName不得重复
* 文件传输：server端保存在/document，client端保存在/static/temp
  * 查看/document文件夹目录
  * 上传文件
    * 文件名不得重复
  * 下载文件
  * 删除server端文件


【注】相应条件在server端检查，通过响应报文中status反馈

