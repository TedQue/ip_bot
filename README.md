## IP Bot
作者: 阙荣文 - Que's C++ Studio
___

以前的版本 <https://blog.csdn.net/querw/article/details/6004724?spm=1001.2014.3001.5501> 不再维护有以下原因:
- 不支持 https 格式的 url 地址,导致可用的网页选择较少
- 不支持标准的正则表达式模式串捕获网页中的 IP 地址,使用不便
- 无法访问需要 SSL 的 SMTP 服务器发送邮件,导致不支持大多数常用邮箱,使用不便
- 作者本人已不再使用的 MFC 技术栈

新版本 **IP Bot** 切换到 Python 技术栈,完全解决了上述问题.  
(**IP Bot** 以源码发布,只提供命令行版本,不再提供 GUI 版本)

### 安装

1. 安装 Python

- 访问 <https://www.python.org/downloads/> 下载 Python 解释器安装程序,如无其他软件或系统特殊需求,安装最新版(v3.12.0)即可.

- 安装完成后打开控制台 cmd (按 Win+R 输入 cmd 回车) 后输入 `python --version`  
如果可以在屏幕看到类似 `Python 3.12.0` 的字样则表明 Python 解释器安装成功

2. 安装 requests 

- 打开控制台 cmd 输入 `python -m pip install requests`
- `requests` 是目前业界最常用于访问 http/https 页面的开源库,是大部分网络爬虫的核心依赖包
- 由于安装过程需要访问外网服务器,可能速度较慢或者失败,在不同时间段多尝试几次一般都可以安装成功

3. 解压 **IP Bot** 软件包到本地目录

### 配置
IP Bot 使用源码包中 `default.conf` 作为程序运行的配置文件,主要包括 IP 地址获取网页相关的设置和邮件发送相关设置.请直接查看该文件,里面包含了详细的配置项说明.

### 用法
打开控制台 cmd, `cd` 进入到软件包所在目录,然后运行 `python ip_bot.py`, 如果需要使用非默认配置文件,则运行 `python ip_bot.py <your_conf_file>`.

### 测试
以 `-t` 选项运行 `python ip_bot.py -t` 观察是否能从配置文件中所有可选网页正确获取 IP 地址.

### 自动运行
Windows 平台下,把命令 `python ip_bot.py` 添加到计划任务,指定执行周期即可;
Linux 平台下使用 crontab 或者其他类似工具.