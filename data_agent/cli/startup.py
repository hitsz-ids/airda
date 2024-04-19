import asyncio
import logging.config
import os
import sys
import time

import click
import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from data_agent.agent.agent import DataAgent
from data_agent.agent.env import DataAgentEnv
from data_agent.agent.planner.data_agent_planner_params import DataAgentPlannerParams
from data_agent.agent.storage import StorageKey
from data_agent.agent.storage.entity.datasource import Datasource, Kind
from data_agent.agent.storage.repositories.datasource_repository import (
    DatasourceRepository,
)
from data_agent.connector.mysql import MysqlConnector
from data_agent.server.agent_server import DataAgentServer

# 获取当前文件所在目录的上两层目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 添加上两层目录到sys.path
sys.path.append(current_dir)
# 定义样式
style = Style.from_dict(
    {
        "prompt": "bold #50fa7b",
        "input": "#f8f8f2",
        "output": "#f8f8f2",
        "highlighted": "bg:#44475a #f8f8f2",
        "separator": "#6272a4",
        "error": "#ff5555 bold",
        "info": "#8be9fd",
    }
)
session = PromptSession(style=style)


# command cli
@click.group()
def main():
    pass


@main.group()
def cli():
    pass


@cli.command()
@click.option(
    "-e",
    "--env",
    type=str,
    required=False,
    default="",
    help="环境变量文件路径, 如果没有则默认使用当前运行的环境变量",
)
def run(env: str):
    context = DataAgent().run()
    while True:
        user_input = session.prompt("输入你的问题:")
        if user_input.lower() == "exit":
            break
        params = {
            "question": user_input,
            "datasource_id": "str",
            "database": "str",
            "knowledge": "str",
            "session_id": "str",
            "file_name": "str",
            "file_id": "str",
        }
        pipeline = context.plan(DataAgentPlannerParams(**params))

        async def execute():
            async for item in pipeline.execute():
                session.output.write(item)
                session.output.flush()
            session.output.write("\n")
            session.output.flush()

        asyncio.run(execute())


# command server
@main.group()
def server():
    pass


@server.command()
@click.option(
    "-p",
    "--port",
    type=int,
    required=True,
    help="服务端口号",
)
@click.option(
    "-e",
    "--env",
    type=str,
    required=False,
    default="",
    help="环境变量文件路径, 如果没有则默认使用当前运行的环境变量",
)
def start(port: int, env: str):
    data_agent_server = DataAgentServer(port=port)
    data_agent_server.run_server()
    pass


# command datasource
@main.group()
def datasource():
    pass


@datasource.command(help="添加数据源")
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="数据源名称",
)
@click.option(
    "-h",
    "--host",
    type=str,
    required=True,
    help="数据源的地址",
)
@click.option(
    "-p",
    "--port",
    type=int,
    required=True,
    help="数据源的端口",
)
@click.option(
    "-k",
    "--kind",
    type=str,
    required=False,
    help="数据源种类目前只支持: [{}]".format(Kind.MYSQL.name),
)
@click.option(
    "-d",
    "--database",
    type=str,
    required=True,
    help="数据库名称",
)
@click.option(
    "-u",
    "--username",
    type=str,
    required=False,
    help="数据源的用户名",
)
@click.option(
    "-w",
    "--password",
    type=str,
    required=False,
    help="数据源的密码",
)
def add(name: str, host: str, port: int, database: str, kind: str, username: str, password: str):
    kind = Kind.getKind(kind)
    if kind is None:
        session.output.write("不支持的数据源类型[{}], PS: 支持类型: [{}]".format(kind, Kind.MYSQL.value))
        session.output.write("\n")
        return
    context = DataAgent().run()
    datasource_repository = context.get_repository(StorageKey.DATASOURCE).convert(
        DatasourceRepository
    )
    datasource_repository.add(
        Datasource(
            name=name,
            host=host,
            port=port,
            database=database,
            kind=kind,
            username=username,
            password=password,
        )
    )


@datasource.command(help="同步数据源的表字段信息并进行向量化")
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="需要同步的数据源名称",
)
def sync(name: str):
    context = DataAgent().run()
    datasource_repository = context.get_repository(StorageKey.DATASOURCE).convert(
        DatasourceRepository
    )
    item = datasource_repository.find_one(name)
    if item:
        if item.kind == Kind.MYSQL.value:
            mysql_conn = MysqlConnector(item, context)
            mysql_conn.query_schema()
    else:
        raise Exception("datasource is not exist")


@datasource.command(help="查询当前已添加的数据源")
def ls():
    context = DataAgent().run()
    datasource_repository = context.get_repository(StorageKey.DATASOURCE).convert(
        DatasourceRepository
    )
    datasource_list = datasource_repository.ls()
    session.output.write("存在" + str(len(datasource_list)) + "个数据源")
    session.output.write("\n")
    for item in datasource_list:
        session.output.write("========================")
        session.output.write("\n")
        session.output.write("名称：" + item.name)
        session.output.write("\n")
        session.output.write("地址：" + item.host)
        session.output.write("\n")
        session.output.write("端口：" + str(item.port))
        session.output.write("\n")
        session.output.write("数据源类型：" + str(item.kind))
        session.output.write("\n")
        session.output.write("数据库：" + str(item.database))
        session.output.write("\n")
        session.output.write("当前已选中：" + str(item.enable))
        session.output.write("\n")
        session.output.write("========================")
        session.output.write("\n")
    session.output.flush()


@datasource.command(help="指定Agent使用的数据源")
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="数据源名称",
)
def enable(name: str):
    context = DataAgent().run()
    datasource_repository = context.get_repository(StorageKey.DATASOURCE).convert(
        DatasourceRepository
    )
    success = datasource_repository.enable(name)
    if success:
        session.output.write("执行成功")
        session.output.write("\n")
    else:
        session.output.write("执行失败")
        session.output.write("\n")
    session.output.flush()


@datasource.command(help="取消Agent使用的数据源")
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="数据源名称",
)
def disable(name: str):
    context = DataAgent().run()
    datasource_repository = context.get_repository(StorageKey.DATASOURCE).convert(
        DatasourceRepository
    )
    success = datasource_repository.disable(name)
    if success:
        session.output.write("执行成功")
        session.output.write("\n")
    else:
        session.output.write("执行失败")
        session.output.write("\n")
    session.output.flush()


@datasource.command(help="删除已存在的数据源")
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="数据源名称",
)
def delete(name: str):
    context = DataAgent().run()
    datasource_repository = context.get_repository(StorageKey.DATASOURCE)
    datasource_repository.delete(name)


if __name__ == "__main__":
    DataAgentEnv("/Users/jianchuanli/Documents/GitHub/SQLAgent/.env")
    with open("/Users/jianchuanli/Documents/GitHub/SQLAgent/log_config.yml", "r") as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    main()
