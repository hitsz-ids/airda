from pydantic import BaseModel

from data_agent.framework.agent.module.planner.pipeline.pipeline_params import (
    PipelineParams,
)
from data_agent.framework.agent.module.planner.planner_params import PlannerParams


class DataAgentPlannerParams(BaseModel, PlannerParams, PipelineParams):
    question: str
    datasource_id: str
    database: str
    knowledge: str
    session_id: str
    sql_type: str = "mysql"
    file_name: str
    file_id: str
