# sharebin - Simple File, Link and Text Sharing

**sharebin** is a modern and user-focused platform built with [FastAPI](https://fastapi.tiangolo.com/) and [PostgreSQL](https://www.postgresql.org/) for easy, ephemeral sharing of files, links, and text pastes. It's a *minimalist, open-source* utility built on the principle of **ephemeral data transfer**.

> **⚠ Note:** All issues, pull requests, and discussions will be handled only on the [original repo](https://codeberg.org/hect1k/sharebin). Please direct contributions there.

## Table of Contents

* [Features](#features)
* [Philosophy](#philosophy)
* [Getting Started](#getting-started)
  * [Installation](#installation)
  * [Configuration](#configuration)
  * [Running](#running)
* [Docker](#docker)
* [Usage](#usage)
* [To-Do](#to-do)
* [Contributing](#contributing)
* [Code of Conduct](#code-of-conduct)
* [License](#license)

## Features

sharebin provides a robust set of features focusing on speed, security, and integrity:

* **Ephemeral Sharing:** Set mandatory **expiry times** on all shared items (files, text, links) to ensure automatic cleanup and minimize data retention.
* **Atomic Transactions:** Guarantees data integrity. If a file upload or email verification fails, the corresponding database record is automatically **rolled back**.
* **Background Cleanup:** Uses **`APScheduler`** to run a robust background job every minute, automatically deleting expired database records and their corresponding physical files on disk.
* **Rate Limiting:** Implements secure, IP-based rate limiting using **`slowapi`** to protect against brute-force attacks on login/registration and prevent resource exhaustion.
* **Minimalist Sharing:** File Share, URL Shortener, and Pastebin - nothing more, nothing less.
* **Anonymous-Friendly:** Excellent usage limits for anonymous sharing via the command line or web.
* **User Accounts:** Registered users gain access to custom shortcodes, extended expiry options, and history tracking.

## Philosophy

Inspired by the [suckless philosophy](https://suckless.org/philosophy), sharebin is designed to be **lightweight, fast, and unbloated**. While the primary goal is simple utility, we've ensured the platform remains highly *usable* for everyone.

## Getting Started

### Installation

#### Prerequisites

You will need the following installed on your system:

* **Python 3.10+**
* **PostgreSQL** database server
* **Docker & Docker Compose** (optional, see [Docker section](#docker))

#### Steps

1.**Clone the Repository:**

```bash
git clone https://codeberg.org/hect1k/sharebin
cd sharebin
```

2.**Create and Activate Virtual Environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3.**Install Dependencies:**

```bash
pip install -r requirements.txt
```

### Configuration

Copy the sample environment file and update settings:

```bash
cp sample.env .env
```

Set values for the following sections:

#### General & Authentication

| Variable                  | Description                                      | Example Value            |
| :------------------------ | :----------------------------------------------- | :----------------------- |
| `PORT`                    | Host port the server will run on.                | `8000`                   |
| `DOMAIN`                  | Public URL for the application.                  | `https://shareb.in`      |
| `JWT_SECRET_KEY`          | Secret key for JWT signing (long random string). | `supersecretjwtkey_here` |
| `JWT_ALGORITHM`           | Algorithm for JWT signing.                       | `HS256`                  |
| `JWT_EXPIRE_MINUTES`      | Access token lifespan (minutes).                 | `60`                     |
| `JWT_REFRESH_EXPIRE_DAYS` | Refresh token lifespan (days).                   | `30`                     |

#### Database & Storage

| Variable                        | Description                                      | Example Value                      |
| :------------------------------ | :----------------------------------------------- | :--------------------------------- |
| `DB_USER`, `DB_PASSWORD`        | PostgreSQL credentials.                          | `postgres`, `S3cur3P@ss`           |
| `DB_NAME`, `DB_HOST`, `DB_PORT` | Database connection details.                     | `sharebin_db`, `localhost`, `5432` |
| `STORAGE_PATH`                  | Directory for storing uploaded files (writable). | `./data`                           |
| `LOG_PATH`                      | Directory for logs.                              | `./logs`                           |

#### Mail (SMTP)

| Variable                         | Description             | Example Value            |
| :------------------------------- | :---------------------- | :----------------------- |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | SMTP login credentials. | `login`, `app_password`  |
| `MAIL_FROM`                      | Sender email address.   | `noreply@shareb.in`      |
| `MAIL_FROM_NAME`                 | Sender display name.    | `Quagmire from sharebin` |
| `MAIL_HOST`, `MAIL_PORT`         | SMTP server details.    | `smtp.gmail.com`, `587`  |
| `MAIL_STARTTLS`, `MAIL_SSL_TLS`  | Encryption settings.    | `true`, `false`          |

#### Usage Limits (Bytes & Seconds)

| Limit Type      | Variable            | Anonymous | Free Tier | Paid Tier |
| :-------------- | :------------------ | :-------- | :-------- | :-------- |
| **File Size**   | `*_FILE_SIZE_LIMIT` | 50 MB     | 250 MB    | 5 GB      |
| **Text Size**   | `*_TEXT_SIZE_LIMIT` | 1 MB      | 5 MB      | 10 MB     |
| **Expiry Time** | `*_EXPIRY_LIMIT`    | 1 day     | 7 days    | 30 days   |

### Running

Make sure your PostgreSQL database is running and configured correctly. Then, run the FastAPI app in development mode:

```bash
fastapi dev
```

The app will be available at `http://localhost:8000`. The background scheduler for cleanup will start automatically.

## Docker

sharebin can be run fully containerized using Docker Compose. This simplifies deployment and ensures consistent environment configuration.

### Using Docker Compose

1.**Build and Start Containers:**

```bash
docker-compose up -d --build
```

2.**Access the Application:**

```
http://localhost:8000
```

3.**Stop Containers:**

```bash
docker-compose down
```

### Notes

* The `docker-compose.yml` includes services for:
  * **sharebin** (FastAPI app)
  * **postgres** (Database)
* Make sure your `.env` file is in the same directory as `docker-compose.yml` for environment variable injection.
* Storage and logs are mounted as volumes inside the container for persistence.

## Usage

### Web UI

Navigate to your domain:

```
https://shareb.in/
```

Register, log in, upload files/text pastes, and manage your shared items.

### API / CLI

The API is documented via [Redoc](https://shareb.in/redoc) and [Swagger UI](https://shareb.in/docs). CLI-friendly for power users.

```bash
curl -X POST "https://shareb.in/" -F "file=@path/to/file.txt"
```

## To-Do

* [x] Implement password reset flow.
* [x] Implement Docker support for easier deployment.
* [ ] Add file download counting and statistics.
* [ ] Optimize file cleanup frequency based on traffic.

## License

This project is licensed under the GNU Affero General Public License v3 - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions from the community! Please read our [Contribution Guidelines](CONTRIBUTING.md) for details on how to get started.

## Code of Conduct

We maintain a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all contributors and users.
