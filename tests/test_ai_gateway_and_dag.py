import pytest
from basic_chan import AIGateway, ConfusionTracker, WorkflowDAG
from basic_chan.intelligence.dag import DependencyCycleError


def test_ai_gateway():
    gateway = AIGateway(primary_provider="mock")
    res = gateway.generate("Hello world")
    assert "mock response" in res


def test_confusion_tracker():
    tracker = ConfusionTracker(default_threshold=3)
    assert tracker.is_confused("task-1") is False

    tracker.record_failure("task-1", "SyntaxError")
    tracker.record_failure("task-1", "TypeError")
    assert tracker.is_confused("task-1") is False

    tracker.record_failure("task-1", "MemoryError")
    assert tracker.is_confused("task-1") is True

    tracker.record_success("task-1")
    assert tracker.is_confused("task-1") is False


def test_workflow_dag():
    dag = WorkflowDAG[str]()
    dag.add_node("recon", "Recon Task", prerequisites=[])
    dag.add_node("routes", "Routes Task", prerequisites=["recon"])
    dag.add_node("sinks", "Sinks Task", prerequisites=["routes"])

    assert dag.is_acyclic() is True
    order = dag.topological_sort()
    assert order == ["recon", "routes", "sinks"]

    # Unlocked nodes
    unlocked = dag.get_unlocked_nodes(completed_ids=set())
    assert unlocked == ["recon"]

    unlocked_next = dag.get_unlocked_nodes(completed_ids={"recon"})
    assert unlocked_next == ["routes"]


def test_workflow_dag_cycle():
    dag = WorkflowDAG[str]()
    dag.add_node("A", "Node A", prerequisites=["B"])
    dag.add_node("B", "Node B", prerequisites=["A"])

    assert dag.is_acyclic() is False
    with pytest.raises(DependencyCycleError):
        dag.topological_sort()
