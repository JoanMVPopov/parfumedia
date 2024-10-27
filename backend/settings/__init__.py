from decouple import config


if config('PIPELINE') == 'production':
    from .production import *
else:
    from .dev import *


# # Import Celery app
# from .celery import app as celery_app
#
# # Specify what should be exported when the module is imported
# __all__ = ('celery_app',)