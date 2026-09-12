from pathlib import Path
from basic_chan import DynamicSisterResolver, SisterDescriptor


def test_dynamic_sister_resolver_workspace(tmp_path):
    workspace_dir = Path.home() / ".openclaw" / "workspace" / "projects"
    if not workspace_dir.exists():
        workspace_dir = tmp_path / "projects"
        mock_sister = workspace_dir / "mock-chan"
        mock_sister.mkdir(parents=True)
        (mock_sister / "manifest.json").write_text('{"name": "Mock-chan", "slug": "mock-chan"}')

    resolver = DynamicSisterResolver(
        current_slug="basic-chan",
        workspace_roots=[workspace_dir],
    )

    sisters = resolver.discover_all()
    slugs = [s.slug for s in sisters]

    # Verify dynamic discovery finds existing workspace sister projects without static lists
    assert len(slugs) > 0


def test_dynamic_sister_runtime_registration():
    resolver = DynamicSisterResolver(current_slug="my-chan", workspace_roots=[])
    desc = SisterDescriptor(name="Mock Sister", slug="mock-sister")
    resolver.register_runtime_sister(desc)

    resolved = resolver.get("mock-sister")
    assert resolved is not None
    assert resolved.name == "Mock Sister"
