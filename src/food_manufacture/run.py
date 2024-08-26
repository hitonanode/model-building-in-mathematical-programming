import csv
import logging

from ..env import DATASET_ROOT_DIR
from .domain.constraints import (
    DependencyConstraint,
    FinalStorageConstraint,
    HardnessConstraint,
    MaxRefinePerMonthConstraint,
    MaxStorageConstraint,
    MaxTypesOfOilsToRefinePerMonthConstraint,
    MinRefineConstraint,
    StockNonnegativeConstraint,
    StockTransitionConstraint,
)
from .domain.month import Month
from .domain.oil import Oil, OilName, OilType
from .domain.task import Task
from .optimization.model import Model
from .optimization.objective import Objective

DATSET_DIR = DATASET_ROOT_DIR / "food_manufacture"

logging.basicConfig()
logger = logging.getLogger(__name__)
# logger.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


def load_oil_master() -> list[Oil]:
    ret: list[Oil] = list()

    with open(DATSET_DIR / "oil_master.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            tmp_dict = {k: v for k, v in zip(header, row, strict=False)}
            ret.append(
                Oil(
                    name=OilName(tmp_dict["name"]),
                    oil_type=OilType(tmp_dict["oil_type"]),
                    hardness=float(tmp_dict["hardness"]),
                )
            )

    return ret


def load_market_price() -> dict[tuple[Month, OilName], float]:
    ret: dict[tuple[Month, OilName], float] = dict()

    with open(DATSET_DIR / "market_price.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            month = Month.from_str(row[0])
            for h, r in zip(header[1:], row[1:], strict=False):
                oil_name = OilName(h)
                price = float(r)
                ret[(month, oil_name)] = price

    return ret


def run() -> None:
    market_price = load_market_price()
    oils = load_oil_master()

    task = Task.build(
        first_month=Month.from_str("2024/01"),
        last_month=Month.from_str("2024/06"),
        oils=oils,
        market_price=market_price,
    )

    m = Model.build(task)

    m.add_constraint(StockTransitionConstraint())
    m.add_constraint(StockNonnegativeConstraint())
    m.add_constraint(MaxStorageConstraint())
    m.add_constraint(FinalStorageConstraint())
    m.add_constraint(MaxRefinePerMonthConstraint())
    m.add_constraint(HardnessConstraint())

    # 12.2
    m.add_constraint(MinRefineConstraint())
    m.add_constraint(MaxTypesOfOilsToRefinePerMonthConstraint())
    m.add_constraint(DependencyConstraint())

    m.set_objective(Objective)

    ret = m.model.optimize()
    logger.info("Status: %s, Objective value: %f", ret.name, m.model.objective.x)

    logger.info("Stock:")
    for month in task.target_months:
        for oil in task.oils:
            logger.info(
                "Stock of %s in the end of %s: %.2f", month, oil.name, m.var.stock(oil, month).x
            )

    logger.info("Refine:")
    for month in task.target_months:
        for oil in task.oils:
            logger.info(
                "Refine of %s in the end of %s: %.2f", month, oil.name, m.var.refine(oil, month).x
            )


if __name__ == "__main__":
    run()
