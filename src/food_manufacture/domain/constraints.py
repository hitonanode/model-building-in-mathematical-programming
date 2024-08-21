from abc import ABCMeta, abstractmethod

import mip  # type: ignore
from pydantic import BaseModel

from .manufacturing_plan import ManufacturingPlan
from .oil import OilType
from .task import Task


class AbstractConstraint(BaseModel, metaclass=ABCMeta):
    eps: float = 1e-12

    @abstractmethod
    def constraints(self, task: Task, plan: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        raise NotImplementedError


class StockTransitionConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for oil in task.oils:
            prev_month_stock = task.init_stock_tons_per_raw_oil
            for month in task.target_months:
                cur_stock = prev_month_stock + vars.purchase(oil, month) - vars.refine(oil, month)

                if self.eps > 0:
                    ret.append(vars.stock(oil, month) >= cur_stock - self.eps)
                    ret.append(vars.stock(oil, month) <= cur_stock + self.eps)
                else:
                    ret.append(vars.stock(oil, month) == cur_stock)

                prev_month_stock = vars.stock(oil, month)

        return ret


class StockNonnegativeConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for oil in task.oils:
            for month in task.target_months:
                ret.append(vars.stock(oil, month) >= -self.eps)

        return ret


class MaxStorageConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for month in task.target_months:
            for oil in task.oils:
                ret.append(vars.stock(oil, month) <= task.max_stock_tons_per_raw_oil + self.eps)

        return ret


class FinalStorageConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for oil in task.oils:
            ret.append(
                vars.stock(oil, task.last_month) >= task.final_min_stock_tons_per_raw_oil - self.eps
            )

        return ret


class MaxRefinePerMonthConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for month in task.target_months:
            refine_to_sum: dict[str, list[mip.LinExpr]] = {s: [] for s in OilType.names()}

            for oil in task.oils:
                refine_to_sum[str(oil.oil_type.name)].append(vars.refine(oil, month))

            for key, val in task.max_refine_tons_per_month.items():
                ret.append(mip.xsum(refine_to_sum[key.name]) <= val + self.eps)

        return ret


class HardnessConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for month in task.target_months:
            hardness_sum = mip.xsum([vars.refine(oil, month) * oil.hardness for oil in task.oils])
            amount_sum = mip.xsum([vars.refine(oil, month) for oil in task.oils])

            ret.append(task.final_hardness_lb * amount_sum <= hardness_sum + self.eps)
            ret.append(hardness_sum <= task.final_hardness_ub * amount_sum + self.eps)

        return ret


class MinRefineConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for month in task.target_months:
            for oil in task.oils:
                min_refine = task.min_refine_tons_per_month_per_oil_if_used * vars.is_refined(
                    oil, month
                )
                f = vars.refine(oil, month) >= min_refine - self.eps
                ret.append(f)

        return ret


class MaxTypesOfOilsToRefinePerMonthConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for month in task.target_months:
            f = (
                mip.xsum([vars.is_refined(oil, month) for oil in task.oils])
                <= task.max_types_of_oils_to_refine_per_month + self.eps
            )
            ret.append(f)

        return ret


class DependencyConstraint(AbstractConstraint):
    def constraints(self, task: Task, vars: ManufacturingPlan[mip.LinExpr]) -> list[mip.LinExpr]:
        ret: list[mip.LinExpr] = list()
        for if_used, must_use in task.dependency_rules:
            for month in task.target_months:
                f = (
                    mip.xsum([vars.is_refined(task.oil(oil), month) for oil in if_used])
                    - vars.is_refined(task.oil(must_use), month)
                    <= len(if_used) - 1 + self.eps
                )
                ret.append(f)

        return ret
