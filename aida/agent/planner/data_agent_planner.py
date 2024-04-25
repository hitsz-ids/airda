from aida.agent.planner.data_agent_pipeline import DataAgentPipeline
from aida.agent.planner.data_agent_planner_params import DataAgentPlannerParams
from aida.framework.agent.module.planner.planner import Planner


class DataAgentPlanner(Planner[DataAgentPlannerParams, DataAgentPipeline]):
    def plan(self, params: DataAgentPlannerParams) -> DataAgentPipeline:
        return DataAgentPipeline(params, self.context)
