import pytest
from ballot_vision.core.models import ElectionProtocol

@pytest.fixture
def valid_protocol_41():
    """Mock data for Polling Station 41 (Stuttgart) with corrected math."""
    return ElectionProtocol(
        precinct_id=41,
        location="ШТУТГАРТ",
        total_voters_turned_out=937,  
        ballots_in_box=936, 
        invalid_votes=16,    
        valid_votes=920,     
        candidate_votes={
            1: 360,
            2: 48,
            5: 134,
            6: 11,
            7: 12,
            8: 235,
            9: 55,
            10: 27, # Adding missing votes to balance the sum to 920
            11: 19,
            12: 3,
            13: 6,
            14: 7,
            17: 3
        }
    )

@pytest.fixture
def valid_protocol_44():
    """Mock data for Polling Station 44 (Stuttgart)."""
    return ElectionProtocol(
        precinct_id=44,
        location="ШТУТГАРТ",
        total_voters_turned_out=875,
        ballots_in_box=875,
        invalid_votes=11,
        valid_votes=864,
        candidate_votes={
            1: 426,
            2: 11,
            3: 4,
            4: 8,
            5: 27,
            6: 2,
            7: 278,
            8: 46,
            11: 13,
            12: 9,
            14: 34,
            15: 2,
            16: 3,
            17: 1
        }
    )

