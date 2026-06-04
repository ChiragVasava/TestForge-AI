from app.config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def test_config_constants():
    assert ALGORITHM == "HS256"
    assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
