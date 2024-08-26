import mip  # type: ignore

from ..domain.manufacturing_plan import ManufacturingPlan
from ..domain.task import Task


class Objective:
    @classmethod
    def objective(cls, task: Task, vars: ManufacturingPlan[mip.Var]) -> mip.LinExpr:
        storage_cost = mip.xsum(
            task.storage_cost_per_ton_per_month * vars.stock(oil, month)
            for oil in task.oils
            for month in task.target_months
        )

        purchase_cost = mip.xsum(
            task.market_price[(month, oil.name)] * vars.purchase(oil, month)
            for oil in task.oils
            for month in task.target_months
        )

        sell = mip.xsum(
            task.sell_price_per_ton * vars.refine(oil, month)
            for oil in task.oils
            for month in task.target_months
        )

        return sell - storage_cost - purchase_cost
