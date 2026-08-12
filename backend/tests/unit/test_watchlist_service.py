from app.services.watchlist_service import normalize_group_key


def test_normalize_group_key_trims_and_lowercases():
    assert normalize_group_key("  iPhone 15  128GB ") == "iphone 15 128gb"


def test_normalize_group_key_collapses_internal_whitespace():
    assert normalize_group_key("iPhone   15") == "iphone 15"


def test_normalize_group_key_treats_case_insensitive_variants_as_equal():
    assert normalize_group_key("Nike Revolution 7") == normalize_group_key("nike revolution 7")
