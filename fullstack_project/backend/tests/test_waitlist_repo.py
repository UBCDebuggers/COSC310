import pytest
from datetime import datetime
import app.repositories.waitlist_repo as wr

# TDD: add a waitlist entry, then retrieve it for the ISBN
def test_add_and_get_waitlist_entry(tmp_path, monkeypatch):
    # Use a temporary CSV file for isolation
    path = tmp_path / "waitlist.csv"
    monkeypatch.setattr(wr.WaitlistRepository, "DATA_PATH", path)

    # The repo should provide add_to_waitlist and get_waitlist_for_isbn
    wr.add_to_waitlist("student1", "isbn-123", "student1@example.com")

    entries = wr.get_waitlist_for_isbn("isbn-123")
    assert len(entries) == 1
    e = entries[0]
    assert e["userid"] == "student1"
    assert e["isbn"] == "isbn-123"
    assert e["email"] == "student1@example.com"
    assert "waitlistid" in e and e["waitlistid"]
    # joined_at should be a datetime (parsed on load)
    assert isinstance(e["joined_at"], datetime)
