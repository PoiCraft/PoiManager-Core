# PoiManager-Core

一个给予 Bedrock Server 一些 API 的简易程序

## 安装 

本程序需要以下环境:

* Python3
* pip3
* Git
* 良好的网络
* Bedrock Server (原生或其他)

### 一、获取

打开终端, 执行 `git clone https://github.com/PoiCraft/PoiManager-Core.git`   
`clone` 完成后进入 `PoiManager-Core` 目录

### 二、配置

打开终端, 执行 `pip3 install -r requirement.txt` 安装依赖  
依赖安装完成后执行 `python3 db_init.py` 初始化数据库, 您可在这一步修改部分配置, 但大多数情况下这是不必要的.  
新建文件夹 `bedrock_core`, 并将您下载的 Bedrock Server 放入此文件夹  

### 三、使用

打开终端, 执行 `python3 run.py` 运行 `Manager-Core`  
请留意输出中类似于 `>Manager Token: xxx` 的内容, 这将成为您访问 API 的凭据

WEBUI页面： http://127.0.0.1:5500/
