from basic_chan import ChanIdentity, DEFAULT_DOT_MASCOT_ASCII


def test_identity_creation():
    ident = ChanIdentity(
        name="Test-chan",
        slug="test-chan",
        japanese_name="テスト・ちゃん",
        tagline="Testing everything.",
        theme_color="magenta",
    )
    assert ident.name == "Test-chan"
    assert ident.slug == "test-chan"
    assert ident.prefix == "test"
    assert "テスト・ちゃん" in ident.format_banner()
    assert ident.to_dict()["slug"] == "test-chan"
