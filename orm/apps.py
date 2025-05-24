from django.apps import AppConfig

class SharedOrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orm'