# Very Simple Full Stack Boilerplate with FastAPI
- No frontend frameworks
- OAuth2 security with JWT tokens stored in a browser cookie
- Minimal environment-based auth config

## Install and setup 
1. Uses pipenv as environment manager

2. Set environment variables 
    - `SECRET_KEY`: JWT signing secret. Defaults to `dev-secret-key-change-me` for local development.
    - `COOKIE_SECURE`: Set to `true` in HTTPS environments. Defaults to `false`.
    - `ACCESS_TOKEN_EXPIRE_MINUTES`: Token lifetime in minutes. Defaults to `11520` (8 days).

3. Run in dev mode:
```sh
fastapi dev main.py
```

4. Default login:
    - Username: admin
    - Password: password