from ballot_vision.validation.rules import ProtocolValidator

def test_protocol_math_is_valid(valid_protocol_41, valid_protocol_44):
    """Ensure protocols with correct math pass validation."""
    validator = ProtocolValidator()
    
    assert validator.validate_math(valid_protocol_41) is True
    assert validator.validate_math(valid_protocol_44) is True

def test_protocol_math_catches_invalid_sum(valid_protocol_41):
    """Ensure a protocol fails if candidate sum does not match valid votes."""
    validator = ProtocolValidator()
    
    # Simulate an OCR error where a candidate's vote was misread (360 -> 36)
    valid_protocol_41.candidate_votes[1] = 36 
    
    assert validator.validate_math(valid_protocol_41) is False

def test_protocol_math_catches_box_mismatch(valid_protocol_44):
    """Ensure a protocol fails if valid + invalid != ballots in box."""
    validator = ProtocolValidator()
    
    # Simulate an OCR error reading invalid votes
    valid_protocol_44.invalid_votes = 99 
    
    assert validator.validate_math(valid_protocol_44) is False

