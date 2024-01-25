# SQLAGENT
## 总览
![head image](/asset/robot.jpeg)  

SQLAgent 是一个 **开源的（Open source）、大模型驱动的（LLM-Powered）、专注于私有化部署的Text2SQL 智能体（Agent）** 项目（Project），我们的目标是提供产品级的Text2SQL解决方案，致力于解决Text2SQL在实际应用中遇到的各种问题如模型私有化部署、面向Text2SQL任务的RAG最佳方案等等。为此，我们将持续探索什么是Text2SQL在实际应用中的最佳实践。
> SQLAgent可以简单的理解为Text2SQL + LLM-Powered Agent，是大模型驱动的面向Text2SQL任务的智能体。基于SQLAgent，你可以通过只调用几个服务接口来快速的开发属于自己的Text2SQL产品，且你只需要专注于你的业务应用，SQLAgent会以一种经过实验数据证明是最合理的方式来帮你解决那些关于Text2SQL的技术难题。
> Text2SQL（Text-to-SQL），顾名思义，即将自然语言转化为SQL，更为学术的定义是将以自然语言表达的数据库领域的问题转化为可执行的结构化查询语句。
> Agent，在本项目中更准确的叫法是LLM-Powered Agent，即⼤语⾔模型驱动的智能代理，是以LLM 作为⼤脑，可感知环境，具备任务规划、记忆、工具调用等能力的一组计算机程序（参考 https://lilianweng.github.io/posts/2023-06-23-agent/）。
## 为什么选择SQLAgent
与那些Text2SQL开发框架（Text2SQL Framework）、具备大模型聊天功能的数据库客户端等项目不同的是，SQLAgent项目的目标是一个支持完全私有化部署、专门面向Text2SQL任务的智能体，这意味着基于SQLAgent来开发产品你将 **无需收集数据来微调模型、无需开展繁琐的Prompt工程、无需关心如何组织数据来实现RAG、更无需关心大模型的Token费用等等问题** ，因为这一切都是由SQLAgent来提供。你可以将SQLAgent当做一个真正SQL专家，尽管问它问题即可！

| 项目 | 举例 | 目标                                                                                                                                                                                                    |
|----|----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Text2SQL 开发框架 | DB-GPT、Vanna-AI等 | 面向Text2SQL任务提供一系列开发工具集以便利产品开发。这类项目通常提供：  <br/>- 调用各种LLM的接口  <br/>- 调用各种Embedding模型的接口  <br/> - 调用各种向量数据库的接口  <br/> - 访问各种数据库的接口  <br/>...                                                             |
| 具备大模型聊天功能的数据库客户端 | Sqlchat、chat2db等 | 在数据库客户端的基础上叠加大模型对话功能，这类项目通常提供：  <br/>  - 调用各种LLM的接口  <br/>- 访问各种数据库的接口以及用户界面  <br/>...                                                                                                                |
| SQLAgent | SQLAgent | 提供产品级的Text2SQL解决方案，我们提供:  <br/>  - 经过专门为生成SQL而微调LLM（langcode-sql-coder-34B），不仅仅是LLM接口！  <br/>- 针对表结构、Gold SQL、指标计算公式等数据对象的高性能RAG的算法，百万检索小于1s，召回率大于95%！不仅仅是对接向量数据库的接口！  <br/>基于vLL的多卡推理的解决方案  <br/>... |

## 架构设计

## 特性
- **Text2SQL LLM**：基于CodeLlama-34b-Instruct模型进行微调得到的专门用于SQL生成的模型langcode-sql-coder-34B。
- **RAG**：针对表结构、Gold SQL、指标计算公式等数据对象的高性能RAG的算法，百万数据检索小于1s，召回率大于95%。
- **多卡推理**：基于vLL的多卡推理的部署方案。
- ...

## 未来的工作
- **SQL验证器**：对生成的SQL进行语法检查，对生成错误的SQL会根据错误信息让LLM重新生成。
- **日志服务**：独立的日志服务。
- **图表生成**：根据SQL查询的结果动态生成图表。

## 推理性能
![performance image](/asset/performance.png)  

## 在线演示系统
即将上线、敬请期待.....

## 如何开始
### SQLAgent部署
#### 资源要求
CPU：8核
内存：32GB+
#### 环境要求
项目存储依赖mongodb，在开始安装之前需要提前安装
#### 源码部署  

> SQLAgent依赖Python >= 3.9  

1、[可选] 创建conda环境  

    conda create -n sqlagent python=3.9
    conda activate sqlagent

2、可以通过运行以下命令来下载源码和安装依赖：  

    #源码下载
    git clone https://github.com/hitsz-ids/SQLAgent.git``  
    cd SQLAgent 
    # 安装依赖
    pip install -r requirements.txt

3、创建``.env``文件，可以从``.env_template``文件复制  

    cp .env_template .env

4、请根据实际情况对以下变量进行配置  

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

    python sqlagent/server.py

#### Docker部署

1、构建镜像  

    bash docker/build.sh

2、创建embedding模型存储目录  

    mkdir -p /data/huggingface

3、启动容器  

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

### 模型部署
#### 资源要求
- CPU：8核 
- 内存：32GB+ 
- GPU：80G

1、下载模型文件
> curl xxx.xxx.xxx.xxx

2、部署模型  

这里展示使用FastChat来部署模型服务  
> 需要根据现实情况手动修改下列配置项：
{PATH_TO_SQL_MODEL_DIR} 需要替换成步骤1模型文件的下载地址
{MODEL_NAME} 是你希望暴露的模型调用的名称，使用接口调用部署了多个模型的服务时，可用此参数区分
{HOST}  暴露服务的地址，没有特殊需求可以写 0.0.0.0
{PORT}  暴露服务的端口

    #[可选] 创建conda环境
    conda create -n llmserver python=3.9
    conda activate llmserver
    #安装依赖
    pip3 install "fschat[model_worker,webui]" vllm
    #启动服务
    # 启动控制器模块
    python -m fastchat.serve.controller
    # 启动模型模型
    CUDA_VISIBLE_DEVICES=0 python -m fastchat.serve.vllm_worker --model-path {PATH_TO_SQL_MODEL_DIR} --model-names {MODEL_NAME} --controller-address http://localhost:21001 --port 31002 --worker-address http://localhost:31002 --limit-worker-concurrency 10 --conv-template llama-2
    # 启动server 模块
    python -m fastchat.serve.openai_api_server --host {HOST} --port {PORT}


### 对你的数据库进行提问
1、训练你的数据库  

    curl -X 'POST' \
    'http://localhost/v1/instruction/sync' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "db_connection_id": "db_connection_id",
    "table_names": ["table_name"]
    }'

2、训练你的知识库  

    curl -X 'POST' \
    'http://localhost/v1/knowledge/train' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "file_id": "file_id",
    "file_name": "file_name",
    "file":File
    }'

3、通过自然语言查询数据

    curl -X 'POST' \
    'http://localhost/v1/chat/completions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "model": "sql_model",
    "messages": [{"role":"user","content":"自然语言问题"}],
        
