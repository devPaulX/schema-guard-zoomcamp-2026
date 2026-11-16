import pytest

from app.validation import InvalidCSV, MAX_CSV_BYTES, validate_csv


def test_pass_at_threshold_and_case_sensitive_headers():
    result = validate_csv(b"Name,age\nAlice,20\n ,21\n", ["Name"], 50)
    assert result.status == "PASS"
    assert result.reasons == []
    mismatch = validate_csv(b"name,age\nAlice,20\n", ["Name"], 0)
    assert mismatch.status == "FAIL"
    assert mismatch.reasons == ["Required column 'Name' is missing."]


def test_reports_every_violation():
    result = validate_csv(b"a,b\n , \nvalue, \n", ["a", "b", "c"], 0)
    assert result.status == "FAIL"
    assert len(result.reasons) == 3
    assert "'c' is missing" in result.reasons[0]
    assert "50.00%" in result.reasons[1]
    assert "100.00%" in result.reasons[2]


@pytest.mark.parametrize("contents, message", [
    (b"", "empty"), (b"\xff", "UTF-8"), (b"\n", "headers"),
    (b"a,,c\n1,2,3\n", "headers"), (b"a,a\n1,2\n", "duplicate"),
    (b"a,b\n1\n", "row 2"), (b'a,b\n"unterminated,2\n', "Malformed"),
    (b"a,b\n", "data row"), (b"a,b\n1,\x00\n", "NUL"),
    (b"a\n" + b"x" * MAX_CSV_BYTES, "5 MiB"),
])
def test_invalid_csv(contents, message):
    with pytest.raises(InvalidCSV, match=message):
        validate_csv(contents, ["a"], 0)
