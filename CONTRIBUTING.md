# Contributing to sharebin - Simple File, Link and Text Sharing

Thank you for considering contributing to **sharebin**! We appreciate your interest in helping improve this minimalist and privacy-focused sharing platform. This document outlines how to contribute effectively to the project.

## Table of Contents

* [Code of Conduct](#code-of-conduct)
* [How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Submitting Changes](#submitting-changes)
* [Development Setup](#development-setup)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Configuration](#configuration)
  * [Running the App](#running-the-app)
  * [Running with Docker](#running-with-docker)
* [Coding Standards](#coding-standards)

## Code of Conduct

Before contributing, please review the [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors to follow it to maintain a respectful and inclusive environment.

## How Can I Contribute?

### Reporting Bugs

If you find a bug or an unexpected behavior, please [open a new issue](https://codeberg.org/hect1k/sharebin/issues/new).
When submitting a bug report, include:

* A short, descriptive title.
* Steps to reproduce the issue.
* Expected vs. actual behavior.
* Environment details (OS, Python version, deployment method, etc.).
* Relevant logs or stack traces if available.

### Suggesting Enhancements

Got an idea for improving sharebin? [Open an enhancement request](https://codeberg.org/hect1k/sharebin/issues/new) and describe:

* What problem it solves or value it adds.
* How you imagine it working.
* Any related tools or references.

Enhancement ideas should align with sharebin’s goals: simplicity, privacy, and minimalism.

### Submitting Changes

To contribute code:

1. **Fork** the repository on Codeberg.
2. **Create a new branch** from `main` for your change.
3. Make your changes and commit them with clear messages.
4. Test your changes locally.
5. **Submit a Pull Request (PR)** describing:
   * The purpose of the change.
   * Issues fixed or features added.
   * Steps to verify your changes.

PRs should be small, focused, and follow the project’s coding conventions.

## Development Setup

### Prerequisites

* Python **3.10+**
* `uv`
* PostgreSQL database server
* Optional: Docker and Docker Compose for containerized development

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://codeberg.org/hect1k/sharebin
   cd sharebin
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

> [!NOTE]
> Make sure you run `pip freeze > requirements.txt` to generate the `requirements.txt` file if you add/remove any dependencies. This is required for docker to build the image.

### Configuration

Copy the example environment file and edit it as needed:

```bash
cp sample.env .env
```

At minimum, set values for:

```bash
PORT=8000
DOMAIN=https://shareb.in
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=sharebin_db
DB_HOST=localhost
STORAGE_PATH=./data
LOG_PATH=./logs
JWT_SECRET_KEY=supersecretjwtkey_here
```

Ensure the storage and logs directories exist and are writable.

### Running the App

Start the development server:

```bash
uv run fastapi dev
```

The app runs at [http://localhost:8000](http://localhost:8000).
Expired files and records are cleaned automatically via the background scheduler.

### Running with Docker

You can also run sharebin entirely via Docker:

```bash
docker-compose up -d --build
```

The `docker-compose.yml` sets up both the FastAPI app and PostgreSQL database.
Make sure `.env` is in the same directory for environment variable loading.

To stop:

```bash
docker-compose down
```

## Coding Standards

* Use **Black** and **isort** for formatting.
* Follow **PEP 8** style guidelines.
* Keep functions and modules small and focused.
* Avoid unnecessary dependencies.
* Write meaningful commit messages (e.g., `fix: handle expired link cleanup`).
* Prefer async functions for I/O operations where applicable.

---

Thank you for contributing to sharebin.
Your effort helps keep the project fast, minimal, and reliable for everyone.
