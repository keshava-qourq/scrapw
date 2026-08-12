from app.services.deduplication_service import build_match_signature


def test_signature_matches_across_gendered_marketplace_titles():
    amazon_title = "Nike Revolution 7 Men's Running Shoes"
    flipkart_title = "Nike Revolution 7 Running Shoes"
    myntra_title = "Nike Revolution 7 Men Running Shoes"

    sig_amazon = build_match_signature(amazon_title, "Nike")
    sig_flipkart = build_match_signature(flipkart_title, "Nike")
    sig_myntra = build_match_signature(myntra_title, "Nike")

    assert sig_amazon == sig_flipkart == sig_myntra


def test_signature_differs_for_different_products():
    sig_a = build_match_signature("Nike Revolution 7", "Nike")
    sig_b = build_match_signature("Nike Air Zoom Pegasus", "Nike")
    assert sig_a != sig_b


def test_signature_is_case_and_punctuation_insensitive():
    sig_a = build_match_signature("Nike Revolution-7!!", "Nike")
    sig_b = build_match_signature("nike revolution 7", "Nike")
    assert sig_a == sig_b


def test_empty_name_and_brand_produces_empty_signature():
    assert build_match_signature("", None) == ""
