# shpr

A simple shopping list web application built with Flask. Intended to be self-hosted with a limited subset of users.

## Install

Pull the latest image:
```bash
$ docker pull ghcr.io/johnsonl104/shpr:latest
```

## Run

To run the app and Postgres run the following command using the included [docker-compose.yml](https://github.com/JohnsonL104/shpr/blob/main/docker-compose.yml):

```bash
$ docker-compose up -d
```

Open [http://127.0.0.1:7477](http://127.0.0.1:7477) in a browser.

## Test

Install Dependencies:
```bash
$ pip install '.[test]'
```

Run the tests:

```bash
$ pytest
```

Run with a coverage report:

```bash
$ coverage run -m pytest
$ coverage report
$ coverage html  # Open htmlcov/index.html in a browser.
```

## Environment Variables

The following environment variables can be configured in the `docker-compose.yml` file under the `shpr` service:

- `FLASK_ENV`: Set the Flask environment. Example: `production`.
- `SQLALCHEMY_DATABASE_URI`: Database connection string. Example: `postgresql://user:Password123@shpr-db:5432/shpr`.
- `SECRET_KEY`: Secret key for Flask. Replace `REPLACE` with a secure value.

### Optional HTTPS Configuration

To enable HTTPS, add the following environment variables to the `shpr` service in `docker-compose.yml`:

- `ENABLE_HTTPS`: Set to `"true"` to enable HTTPS. Default is `"false"`.
- `SSL_CERT_PATH`: Path to the SSL certificate file inside the container. Example: `/certs/cert.pem`.
- `SSL_KEY_PATH`: Path to the SSL key file inside the container. Example: `/certs/key.pem`.

Additionally, mount the certificate and key files into the container using the `volumes` section in `docker-compose.yml`:

Example configuration in `docker-compose.yml`:

```yaml
services:
  shpr:
    environment:
      ENABLE_HTTPS: "true"
      SSL_CERT_PATH: "/certs/cert.pem"
      SSL_KEY_PATH: "/certs/key.pem"
    volumes:
      - /path/to/local/cert.pem:/certs/cert.pem:ro
      - /path/to/local/key.pem:/certs/key.pem:ro
```
## Features

- User authentication system with registration, login, and logout functionality.
- CRUD operations for shopping list items, including create, update, delete, and mark as complete.
- Mobile-friendly UI with swipe-to-complete functionality.
- Filtering and searching for items by username and status.

## Contributing

Feel free to fork the repository and submit pull requests for improvements or bug fixes.
