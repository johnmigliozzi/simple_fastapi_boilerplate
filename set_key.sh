# Run this before starting up the application to set a new secret key
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")