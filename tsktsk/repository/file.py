import contextlib
from pathlib import Path
from typing import Any, Dict, Iterator, Set

import yaml
from tsktsk.task import Category, Effort, Task, Value

YamlDict = Dict[str, Any]


def task_from_yaml(values: YamlDict) -> Task:
    category = values.get("category")
    if category:
        values["category"] = Category.__members__[category.upper()]

    value = values.get("value")
    if value:
        values["value"] = Value.__members__[value.upper()]

    effort = values.get("effort")
    if effort:
        values["effort"] = Effort.__members__[effort.upper()]

    values["dependencies"] = set(values.get("dependencies", []))

    return Task(**values)


def task_to_yaml(task: Task) -> YamlDict:
    return dict(
        key=task.key,
        message=task.message,
        category=task.category.name,
        effort=task.effort.name.lower(),
        value=task.value.name.lower(),
        done=task.done,
        dependencies=list(task.dependencies),
    )


class FileRepository:
    def __init__(self, path: Path):
        self.path = path

    def add(
        self,
        category: Category,
        value: Value,
        effort: Effort,
        message: str,
        dependencies: Set[str],
    ) -> Task:
        with self.tasks() as tasks:
            missing = dependencies.difference(tasks)
            if missing:
                raise ValueError(*missing)

            key = str(len(tasks) + 1)
            task = Task(key, message, category, value, effort, dependencies)
            tasks[key] = task_to_yaml(task)

        return task

    @contextlib.contextmanager
    def tasks(self) -> Iterator[YamlDict]:
        if not self.path.exists():
            raise FileNotFoundError("No tsktsk repository here")

        with self.path.open(mode="r") as f:
            tasks = yaml.safe_load(f) or {}

        yield tasks

        with self.path.open("w") as f:
            yaml.dump(tasks, f)

    @contextlib.contextmanager
    def task(self, key: str) -> Iterator[Task]:
        with self.tasks() as tasks:
            task = task_from_yaml(tasks[key])
            yield task
            tasks[key] = task_to_yaml(task)

    def __iter__(self) -> Iterator[Task]:
        with self.tasks() as tasks:
            return (task_from_yaml(value) for value in tasks.values())
