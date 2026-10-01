# Luxe Hotel Management System

A Django hotel website for browsing rooms, creating bookings, and managing reservations.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Set `DJANGO_SECRET_KEY` to a private random value. The other optional settings and email examples are in `.env.example`; configure environment variables in your shell or hosting provider.
4. Run `python manage.py migrate`.
5. Run `python manage.py createsuperuser` to create an admin account.
6. Start the site with `python manage.py runserver` and open `http://127.0.0.1:8000/`.

For production, set `DJANGO_DEBUG=False`, provide a unique `DJANGO_SECRET_KEY`, and set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` for the deployed domain. Configure SMTP credentials through environment variables, never in source control. The default email backend prints messages to the console.

## Tests

Run `python manage.py test`.