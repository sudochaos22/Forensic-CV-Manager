"""Backward-compatible sample seeding module.

Release builds contain only fictitious data. No developer or user CV information is included.
"""
from sample_data import load_sample_profile

def seed(db):
    profile = db.get_profile()
    if db.count("employment") or profile.get("full_name"):
        return
    load_sample_profile(db, clear=False)
