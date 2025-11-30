import pytest
from unittest.mock import patch

from app.services.analytics_service import (
    _compute_request_counts,
    _compute_delta_requests,
    get_trending_books
)


# Test: _compute_request_counts

def test_compute_request_counts_aggregates_correctly():
    records = [
        {"book_id": "A", "request_count": "2"},
        {"book_id": "B", "request_count": "5"},
        {"book_id": "A", "request_count": "3"},
    ]

    result = _compute_request_counts(records)

    assert result == {
        "A": 5,   # 2 + 3
        "B": 5
    }

# Test: _compute_delta_requests


def test_compute_delta_requests_with_two_records():
    records = [
        {"book_id": "X", "date": "2025-01-02", "request_count": "10"},
        {"book_id": "X", "date": "2025-01-01", "request_count": "7"},
    ]

    delta = _compute_delta_requests(records, "X")
    assert delta == 3  


def test_compute_delta_requests_with_one_record():
    records = [
        {"book_id": "X", "date": "2025-01-02", "request_count": "10"},
    ]

    delta = _compute_delta_requests(records, "X")
    assert delta == 0  



# Test: get_trending_books
# Integration-like test


@patch("app.services.analytics_service.analytics_repo.load_all")
@patch("app.services.analytics_service._compute_request_counts")
@patch("app.services.analytics_service._compute_delta_requests")
def test_get_trending_books(mock_delta, mock_total, mock_load):

    mock_load.return_value = [
        {"book_id": "B1", "date": "2025-01-02", "request_count": "4"},
        {"book_id": "B1", "date": "2025-01-01", "request_count": "2"},
        {"book_id": "B2", "date": "2025-01-02", "request_count": "10"},
        {"book_id": "B2", "date": "2025-01-01", "request_count": "5"},
    ]


    mock_total.return_value = {
        "B2": 15,
        "B1": 6
    }

    mock_delta.side_effect = [5, 2] 

    result = get_trending_books(2)
    assert len(result) == 2
    assert result[0]["book_id"] == "B2"   
    assert result[0]["delta_requests"] == 5
    assert result[1]["book_id"] == "B1"
