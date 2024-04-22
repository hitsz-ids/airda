.. _header-n0:

DataAgent部署
=============

.. _header-n27:

资源要求
--------

CPU：8核 内存：32GB+

.. _header-n3:

环境要求
--------

项目存储依赖mongodb，在开始安装之前需要提前安装

.. _header-n7:
快速开始
--------
.. code::

   pip install data-agent

启动命令行运行

.. code::

   data-agent run cli

启动服务运行

.. code::

   data-agent run server -p 8080

.. _header-n5:

源码部署
--------
    DataAgent依赖Python >= 3.10


1、[可选] 创建conda环境

.. code::

   conda create -n dataagent python=3.10
   conda activate dataagent

2、可以通过运行以下命令来下载源码和安装依赖：

.. code::

   #源码下载
   git clone https://github.com/hitsz-ids/SQLAgent.git``
   cd SQLAgent
   # 安装依赖
   pip install poetry && poetry install

3、创建\ ``.env``\ 文件，可以从\ ``.env_template``\ 文件复制

.. code::

   cp .env_template .env


4、创建\ ``log_config.yml``\ 文件，可以从\ ``log_config.yml.template``\ 文件复制

.. code::

   cp log_config.yml.template .log_config.yml


5、请根据实际情况对以下变量进行配置

.. code::

   # mongodb 配置
   MONGODB_URI="mongodb://localhost:27017"
   MONGODB_DB_NAME=''
   MONGODB_DB_USERNAME=''
   MONGODB_DB_PASSWORD=''
   # OpenAI 配置
   OPENAI_KEY=''
   MODEL_NAME=''
   # [可选]embedding 模型名称 默认使用 infgrad/stella-large-zh-v2
   EMBEDDINGS_MODEL_NAME='infgrad/stella-large-zh-v2'
   # [可选]embedding 模型名称 默认使用 infgrad/stella-large-zh-v2
   EMBEDDINGS_MODEL_NAME='infgrad/stella-large-zh-v2'

6、启动

.. code::

   #启动命令行模式
   python cli/startup run cli
   #启动服务模式
   python cli/startup run server -p 8080
