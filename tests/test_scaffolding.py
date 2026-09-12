import subprocess
from basic_chan.scaffolding.project_gen import scaffold_chan_project


def test_scaffold_project(tmp_path):
    target = tmp_path / "ninja-chan"
    scaffold_chan_project(
        name="Ninja-chan",
        slug="ninja-chan",
        target_dir=target,
        japanese_name="忍者ちゃん",
        tagline="Stealth operations.",
    )

    assert (target / "install.sh").exists()
    assert (target / "setup.sh").exists()
    assert (target / "start.sh").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "src" / "ninja_chan" / "__init__.py").exists()

    # Validate bash syntax on generated scripts
    for script_name in ("install.sh", "setup.sh", "start.sh"):
        res = subprocess.run(["bash", "-n", str(target / script_name)], capture_output=True)
        assert res.returncode == 0, f"Syntax error in {script_name}: {res.stderr.decode()}"
