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

.. _header-n5:

源码部署
--------

   SQLAgent依赖Python >= 3.10

1、[可选] 创建conda环境

.. code::

   conda create -n sqlagent python=3.10
   conda activate sqlagent

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

4、请根据实际情况对以下变量进行配置

.. code::

   # mongodb 配置
   MONGODB_URI="mongodb://localhost:27017"
   MONGODB_DB_NAME='sqlagent'
   MONGODB_DB_USERNAME=''
   MONGODB_DB_PASSWORD=''
   # OpenAI 配置，留空即可
   OPENAI_KEY=''
   MODEL_NAME=''
   # [可选]embedding 模型名称 默认使用 infgrad/stella-large-zh-v2
   EMBEDDINGS_MODEL_NAME='infgrad/stella-large-zh-v2'
   # [可选]embedding 模型名称 默认使用 infgrad/stella-large-zh-v2
   EMBEDDINGS_MODEL_NAME='infgrad/stella-large-zh-v2'

5、启动服务

.. code::

   python sqlagent/server.py

.. _header-n18:

Docker部署
----------

1、构建镜像

.. code::

   bash docker/build.sh

2、创建embedding模型存储目录

.. code::

   mkdir -p /data/huggingface

3、启动容器

.. code::

   docker run -idt --privileged=true \
   -p 8888:8888 \
   -v /data/huggingface:/root/.cache/huggingface \
   -e LLM_SQL_ORIGIN=http://xxx.xxx.xxx.xxx:8000 \ # 按实际情况替换
   -e MONGODB_URI=mongodb://xxx.xxx.xxx.xxx:27017 \ # 按实际情况替换
   -e MONGODB_DB_NAME=sqlagent \
   -e MONGODB_DB_USERNAME=xxx \ # 按实际情况替换
   -e MONGODB_DB_PASSWORD=xxx \ # 按实际情况替换
   -e EMBEDDINGS_MODEL_NAME=infgrad/stella-large-zh-v2 \
   --restart always \
   --name sqlagent \
   langcode/sqlagent:Alpha
