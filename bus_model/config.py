class BaseConfig:
    TESTING = False
    DEBUG = False
    MAKE_DB = True
    APP_FACTORY_ONLY = False

class TestConfig(BaseConfig):
    """Test configuration."""
    TESTING = True
    DEBUG = True
    MAKE_DB = False
    APP_FACTORY_ONLY = True

class ProductionConfig(BaseConfig):
    """Production configuration."""
    ...