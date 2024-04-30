from typing import TYPE_CHECKING

import mysql.connector

if TYPE_CHECKING:
    from airda.agent.data_agent_context import DataAgentContext

from airda.agent.storage.entity.colunm_detail import ColumnDetail
from airda.agent.storage.entity.datasource import Datasource
from airda.agent.storage.entity.instruction import Instruction

config = {
    "user": "your_username",
    "password": "your_password",
    "host": "localhost",
    "database": "your_database",
}


class MysqlConnector:
    datasource: Datasource
    context: "DataAgentContext"

    def __init__(self, datasource: Datasource, context: "DataAgentContext"):
        self.datasource = datasource
        self.context = context
        self.cnx = mysql.connector.connect(
            **{
                "user": datasource.username,
                "password": datasource.password,
                "host": datasource.host,
                "port": datasource.port,
                "database": datasource.database,
            }
        )

    def query_schema(self):
        self.context.delete_instruction(
            database=self.datasource.database, datasource_id=self.datasource.id
        )
        cursor = self.cnx.cursor()

        # 获取所有表名
        cursor.execute(
            f"SELECT TABLE_NAME, TABLE_COMMENT FROM information_schema.tables WHERE table_schema = "
            f"'{self.datasource.database}'"
        )
        tables = cursor.fetchall()
        instruction_list = []
        for table in tables:
            cursor.execute(f"SHOW CREATE TABLE `{table[0]}`")
            table_schema = cursor.fetchall()
            cursor.execute(
                f"SELECT COLUMN_NAME, COLUMN_COMMENT FROM information_schema.COLUMNS WHERE table_name = '{table[0]}'"
                f" AND table_schema = '{self.datasource.database}'"
            )
            columns = cursor.fetchall()
            columns_detail_list = []
            for column in columns:
                column_detail = ColumnDetail(name=column[0], description=column[1])
                columns_detail_list.append(column_detail)
            instruction = Instruction(
                datasource_id=self.datasource.id,
                database=self.datasource.database,
                table_name=table[0],
                table_schema=table_schema[0][1],
                columns=columns_detail_list,
                table_comment=table[1],
            )
            self.context.sync_instruction(instruction)
        cursor.close()
