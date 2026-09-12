"""basic_chan.intelligence.dag — Kahn's algorithm Directed Acyclic Graph dependency resolver."""

from __future__ import annotations

from typing import Dict, Generic, List, Optional, Set, TypeVar

T = TypeVar("T")


class DependencyCycleError(ValueError):
    """Raised when a dependency cycle is detected in a DAG."""
    pass


class WorkflowDAG(Generic[T]):
    """Generic Directed Acyclic Graph (DAG) for prerequisite resolution & pipeline execution."""

    def __init__(self):
        self._nodes: Dict[str, T] = {}
        self._prerequisites: Dict[str, Set[str]] = {}

    def add_node(self, node_id: str, value: T, prerequisites: Optional[List[str] | Set[str]] = None) -> None:
        self._nodes[node_id] = value
        self._prerequisites[node_id] = set(prerequisites or [])

    def is_acyclic(self) -> bool:
        try:
            self.topological_sort()
            return True
        except DependencyCycleError:
            return False

    def topological_sort(self) -> List[str]:
        """Returns linear topological execution order using Kahn's algorithm O(V + E)."""
        in_degree = {nid: 0 for nid in self._nodes}
        for nid, prereqs in self._prerequisites.items():
            in_degree[nid] = len([p for p in prereqs if p in self._nodes])

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []

        # Reverse adjacency: prereq -> dependents
        dependents: Dict[str, List[str]] = {nid: [] for nid in self._nodes}
        for nid, prereqs in self._prerequisites.items():
            for p in prereqs:
                if p in dependents:
                    dependents[p].append(nid)

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for dep in dependents.get(curr, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        if len(order) != len(self._nodes):
            raise DependencyCycleError("Cycle detected in DAG; prerequisites cannot be satisfied.")

        return order

    def get_unlocked_nodes(self, completed_ids: Set[str]) -> List[str]:
        """Returns list of node IDs whose prerequisites are fully satisfied."""
        unlocked = []
        for nid, prereqs in self._prerequisites.items():
            if nid in completed_ids:
                continue
            if prereqs.issubset(completed_ids):
                unlocked.append(nid)
        return unlocked
