# Object Storage MCP Server

[![CI](https://github.com/creafly/object-storage-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/creafly/object-storage-mcp/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/creafly/object-storage-mcp)](https://github.com/creafly/object-storage-mcp/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/creafly/object-storage-mcp)](https://github.com/creafly/object-storage-mcp/pulls)

MCP server for working with AWS S3 Object Storage. Allows AI agents to upload, download, and manage files in cloud storage.

## Features

- **upload_file** — Upload files to S3 (supports text and base64)
- **download_file** — Download files from S3
- **list_files** — List files with prefix filtering
- **get_file_info** — Get file metadata without downloading
- **delete_file** — Delete files

### Security

- **Path Safety** — Protection against directory traversal attacks (blocks `..` and absolute paths)
- **Conflict Detection** — Prevents accidental file overwriting
- **File Validation** — Validates file size and extensions

## Requirements

- Python 3.11+
- AWS S3 or S3-compatible storage (MinIO, Yandex Object Storage, etc.)

## Installation

```bash
cd object-storage-mcp

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync
```

## Configuration

Create a `.env` file in the project root:

```env
# Required variables
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=your-bucket-name

# Optional variables
AWS_REGION=us-east-1
S3_ENDPOINT_URL=https://storage.yandexcloud.net  # for S3-compatible storage
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Security limits
MAX_FILE_SIZE_MB=100
MAX_LIST_OBJECTS=1000
ALLOWED_EXTENSIONS=pdf,docx,xlsx,txt,json  # optional, if not set — all allowed
```

## Running

```bash
# Activate environment
source .venv/bin/activate

# Start the server
python -m src.entrypoints.server
```

Server will be available at: `http://localhost:8000/mcp`

## Docker

```bash
# Build image
make build

# Run with environment variables from .env
make run
```

## Environment Variables

| Variable                | Required | Default     | Description                          |
| ----------------------- | -------- | ----------- | ------------------------------------ |
| `AWS_ACCESS_KEY_ID`     | Yes      | —           | AWS Access Key ID                    |
| `AWS_SECRET_ACCESS_KEY` | Yes      | —           | AWS Secret Access Key                |
| `S3_BUCKET_NAME`        | Yes      | —           | S3 bucket name                       |
| `AWS_REGION`            | No       | `us-east-1` | AWS region                           |
| `S3_ENDPOINT_URL`       | No       | —           | Endpoint for S3-compatible storage   |
| `PORT`                  | No       | `8000`      | Server port                          |
| `HOST`                  | No       | `0.0.0.0`   | Server host                          |
| `LOG_LEVEL`             | No       | `INFO`      | Logging level                        |
| `MAX_FILE_SIZE_MB`      | No       | `100`       | Maximum file size (MB)               |
| `MAX_LIST_OBJECTS`      | No       | `1000`      | Maximum objects when listing         |
| `ALLOWED_EXTENSIONS`    | No       | —           | Allowed extensions (comma-separated) |

## Tool Usage

### upload_file

Upload a file to S3:

```json
{
  "key": "documents/report.pdf",
  "content": "base64_encoded_content_here",
  "content_type": "application/pdf",
  "is_base64": true,
  "overwrite": false
}
```

### download_file

Download a file:

```json
{
  "key": "documents/report.pdf",
  "as_base64": true
}
```

### list_files

Get list of files:

```json
{
  "prefix": "documents/",
  "max_keys": 100
}
```

### get_file_info

Get file information:

```json
{
  "key": "documents/report.pdf"
}
```

### delete_file

Delete a file:

```json
{
  "key": "documents/old_report.pdf"
}
```

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run linting
make lint

# Run tests
make test

# Run tests with coverage
make test-cov
```

## License

MIT
