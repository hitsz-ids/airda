from data_agent.agent.planner.data_agent_pipeline import DataAgentPipeline
from data_agent.agent.planner.data_agent_planner_params import DataAgentPlannerParams
from data_agent.framework.agent.module.planner.planner import Planner


class DataAgentPlanner(Planner[DataAgentPlannerParams, DataAgentPipeline]):
    def plan(self, params: DataAgentPlannerParams) -> DataAgentPipeline:
        return DataAgentPipeline(params, self.context)
