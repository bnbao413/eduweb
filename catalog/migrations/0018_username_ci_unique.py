from django.conf import settings
from django.db import migrations


# Enforce case-insensitive unique usernames at the database level, so "JOHN"
# and "john" can never both exist — even via the admin, shell, bulk imports,
# or a race between two simultaneous signups (the form check can't cover those).
# Functional unique index; supported by SQLite (3.9+) and PostgreSQL.
CREATE_INDEX = (
    "CREATE UNIQUE INDEX IF NOT EXISTS catalog_auth_user_username_ci "
    "ON auth_user (LOWER(username));"
)
DROP_INDEX = "DROP INDEX IF EXISTS catalog_auth_user_username_ci;"


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0017_delete_lesson'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(sql=CREATE_INDEX, reverse_sql=DROP_INDEX),
    ]
