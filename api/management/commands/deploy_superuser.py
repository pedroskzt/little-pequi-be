import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django management command to create a superuser automatically if one doesn't exist.

    This command is useful for initializing applications, especially in containerized
    environments where manual superuser creation isn't practical.
    """
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        """
        Execute the command to create a superuser.
        Required environment variables:
        - DJANGO_SUPERUSER_EMAIL
        - DJANGO_SUPERUSER_FIRST_NAME
        - DJANGO_SUPERUSER_LAST_NAME

        Optional environment variables:
        - DJANGO_SUPERUSER_PASSWORD
            If not provided, a random password will be generated.
        Returns:
            None. Outputs status messages to the command line.
        """
        # Get the user model configured for the project
        User = get_user_model()

        # Check if any superuser already exists in the database
        if not User.objects.filter(is_superuser=True).exists():
            # Get superuser credentials from environment variables
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
            first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME')
            last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

            # Generate a random password if none is provided in environment variables
            if not password:
                password = User.objects.make_random_password()
                self.stdout.write(self.style.WARNING(f"Random password generated: {password}"))

            # Create the superuser with the email as both username and email
            User.objects.create_superuser(first_name=first_name, last_name=last_name, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            # Inform that a superuser already exists
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
