from basic_chan import BaselineManager, PragmaParser


def test_baseline_manager(tmp_path):
    sig = BaselineManager.compute_signature("vuln", "CWE-89", "routes/auth.py", "SELECT * FROM users")
    assert isinstance(sig, str) and len(sig) == 64

    baseline_file = tmp_path / "baseline.json"
    BaselineManager.save_baseline_signatures(baseline_file, [sig])

    loaded = BaselineManager.load_baseline_signatures(baseline_file)
    assert sig in loaded


def test_pragma_parser(tmp_path):
    code_file = tmp_path / "test_code.py"
    code_file.write_text("""
def foo():
    # chan-ignore
    secret = "AKIA123456"
    return True
""")
    suppressed = PragmaParser.get_suppressed_lines(code_file, chan_slug="kunoichi-chan")
    # Line 3 is the comment, line 4 is the suppressed target line
    assert 3 in suppressed
    assert 4 in suppressed
