.. _header-n20:

模型部署
========

.. _header-n22:

资源要求
--------

-  CPU：8核

-  内存：32GB+

-  GPU：80G

部署模型
--------

1、下载模型文件

   下载地址，敬请期待

2、部署模型

这里展示使用FastChat来部署模型服务

   | 需要根据现实情况手动修改下列配置项：
   | {PATH\ *TO*\ SQL\ *MODEL*\ DIR} 需要替换成步骤1模型文件的下载地址
   | {MODEL_NAME}
     是你希望暴露的模型调用的名称，使用接口调用部署了多个模型的服务时，可用此参数区分
   | {HOST} 暴露服务的地址，没有特殊需求可以写 0.0.0.0
   | {PORT} 暴露服务的端口

.. code::

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
