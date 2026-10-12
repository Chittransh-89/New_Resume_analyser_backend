"""Parser prompt + experience-years handling tests (no LLM calls)."""
import tests.conftest  # noqa: F401
from services.parser import RESUME_PROMPT
from routers.analyze import _to_years


def test_prompt_asks_for_experience_years():
    # Regression: the parser never requested this field, so the API
    # always returned null and the UI always showed "N/A".
    assert '"experience_years"' in RESUME_PROMPT


def test_to_years_numbers():
    assert _to_years(2) == 2.0
    assert _to_years(2.5) == 2.5
    assert _to_years(0) == 0.0


def test_to_years_bad_values_become_zero():
    assert _to_years(None) == 0.0
    assert _to_years("") == 0.0
    assert _to_years("fresher") == 0.0
    assert _to_years(True) == 0.0
    assert _to_years(-3) == 0.0


def test_to_years_strings_take_first_number():
    assert _to_years("2-3 years") == 2.0
    assert _to_years("around 4.5 yrs") == 4.5
