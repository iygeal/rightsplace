import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "rightsplace_project.settings"
)
django.setup()

User = get_user_model()


def create_superuser():
    enabled = os.getenv("CREATE_SUPERUSER") == "1"
    if not enabled:
        print("CREATE_SUPERUSER not enabled. Skipping.")
        return

    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

    if not username or not password:
        print("Superuser env vars missing. Skipping.")
        return

    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists.")
        return

    print(f"Creating superuser '{username}'...")
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print("Superuser created successfully.")


if __name__ == "__main__":
    create_superuser()
