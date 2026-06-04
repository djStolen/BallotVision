from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ElectionProtocol:
    """Represents a parsed Serbian Election Protocol (Zapisnik)."""
    precinct_id: int
    location: str
    total_voters_turned_out: int  # Field 11.1
    ballots_in_box: int           # Field 11.2
    invalid_votes: int            # Field 11.3
    valid_votes: int              # Field 11.4
    candidate_votes: Dict[int, int] = field(default_factory=dict) # Field 11.5

