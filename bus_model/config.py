class BaseConfig:
    TESTING = False
    DEBUG = False
    MAKE_DB = True

class TestConfig(BaseConfig):
    """Test configuration."""
    TESTING = True
    DEBUG = True
    MAKE_DB = False

class ProductionConfig(BaseConfig):
    """Production configuration."""
    TESTING = False
    DEBUG = False
    MAKE_DB = True