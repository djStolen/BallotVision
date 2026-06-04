from ballot_vision.core.models import ElectionProtocol

class ProtocolValidator:
    """Validates the mathematical consistency of election protocols."""
    
    def validate_math(self, protocol: ElectionProtocol) -> bool:
        """
        Validates that protocol figures are mathematically consistent.
        """
        # Rule 1: Sum of invalid and valid ballots must equal ballots in the box[cite: 1, 2]
        if protocol.invalid_votes + protocol.valid_votes != protocol.ballots_in_box:
            return False
            
        # Rule 2: Sum of all individual candidate votes must equal the valid votes total[cite: 1, 2]
        if sum(protocol.candidate_votes.values()) != protocol.valid_votes:
            return False
            
        return True

