DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'static_data',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

INSTALLED_APPS = [
    'orm',
]

TIME_ZONE = 'UTC'
USE_TZ = True