from bps_etl.extract.client import BPSRequest, build_query_params
from bps_etl.transform.normalize import normalize_numeric_value
from bps_etl.transform.validate import is_valid_year


TEST_API_KEY_PLACEHOLDER = "test-api-key-placeholder"


def test_build_query_params_does_not_mutate_request():
    request = BPSRequest(model="var", domain="0000", params={"page": 1})
    params = build_query_params(request, api_key=TEST_API_KEY_PLACEHOLDER)
    assert params["model"] == "var"
    assert params["domain"] == "0000"
    assert params["page"] == 1
    assert params["key"] == TEST_API_KEY_PLACEHOLDER
    assert request.params == {"page": 1}


def test_normalize_numeric_value_supports_indonesian_decimal():
    assert normalize_numeric_value("12,34") == 12.34
    assert normalize_numeric_value("bad") is None


def test_is_valid_year_range():
    assert is_valid_year("2023")
    assert not is_valid_year("1800")
    assert not is_valid_year("not-year")
