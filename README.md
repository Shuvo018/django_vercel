# Setup Vercel app
## build_files.sh

```

#!/usr/bin/env bash
set -euo pipefail

# Create and use an isolated virtual environment to avoid modifying system Python
VENV_DIR=".vercel_venv"
VENV_PY="$VENV_DIR/bin/python"

python -m venv "$VENV_DIR"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt

# Run collectstatic with the venv Python
"$VENV_PY" manage.py collectstatic --noinput

```

## vercel.json

```

{
  "version": 2,
  "builds": [
    {
      "src": "blog_main/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb", "runtime": "python3.11" }
    },
    {
      "src": "build_files.sh",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "staticfiles_build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "blog_main/wsgi.py"
    }
  ]
}

```

## settings.py

```

ALLOWED_HOSTS = ['.vercel.app', 'localhost', '127.0.0.1', '.now.sh']



from django.core.exceptions import ImproperlyConfigured
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    parsed_url = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql' if parsed_url.scheme in ('postgres', 'postgresql') else os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
            'NAME': parsed_url.path[1:],
            'USER': parsed_url.username or '',
            'PASSWORD': parsed_url.password or '',
            'HOST': parsed_url.hostname or '',
            'PORT': str(parsed_url.port or ''),
        }
    }
else:
    db_engine = os.environ.get('DB_ENGINE')
    if db_engine == 'django.db.backends.postgresql':
        db_host = os.environ.get('DB_HOST')
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_port = os.environ.get('DB_PORT', '5432')
        if not db_host or not db_name or not db_user or not db_password:
            raise ImproperlyConfigured(
                'PostgreSQL on Vercel requires DATABASE_URL or DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, and DB_PORT environment variables.'
            )
        DATABASES = {
            'default': {
                'ENGINE': db_engine,
                'NAME': db_name,
                'USER': db_user,
                'PASSWORD': db_password,
                'HOST': db_host,
                'PORT': db_port,
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

```

## wsgi.py
```

app = application

```

## urls.py 

```

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

```