import pytest

from coi.models.enums import (
    EmploymentType,
    ExtractionStatus,
    PostingStatus,
    SalaryPeriod,
    SourceType,
    WorkplaceType,
)


@pytest.mark.parametrize(
    ("enum_class", "value"),
    [
        (SourceType, "api"),
        (EmploymentType, "full_time"),
        (WorkplaceType, "remote"),
        (PostingStatus, "active"),
        (ExtractionStatus, "success"),
        (SalaryPeriod, "annual"),
    ],
)
def test_enum_values(enum_class, value):
    """Test that enum members have the expected string values."""
    assert enum_class(value).value == value


def test_str_enum_behaves_like_string():
    """Test that StrEnum members can be compared with strings."""
    assert EmploymentType.FULL_TIME == "full_time"


def test_invalid_enum_value():
    """Test that invalid values raise ValueError."""
    with pytest.raises(ValueError):
        EmploymentType("invalid")
