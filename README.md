# CloudForm App

The application layer of the **CloudForm** project — a simple Flask web app that collects user submissions (name, email, message) through a form and stores them in an AWS RDS MySQL database. This repository also contains the CI pipeline that builds, containerizes, and ships the app to the CloudForm EKS cluster.

## 📌 Purpose

`cloudform-app` is where the actual product code lives. On every push to `main`, it automatically:

1. Builds a Docker image of the Flask app
2. Pushes it to Amazon ECR
3. Updates the deployment manifest in [`cloudform-gitops`](https://github.com/rajeshdangi409/cloudform-gitops) with the new image tag
4. Lets FluxCD (already bootstrapped on the cluster by [`cloudform-infra`](https://github.com/rajeshdangi409/cloudform-infra)) pick up the change and roll it out to EKS

No manual `kubectl apply` is ever needed — this is a push-based CI step feeding into a pull-based GitOps deployment.

## 🖥️ What the App Does

- `/` — renders a styled registration form (name, email, message)
- `/submit` (POST) — validates the form, inserts the submission into a `users` table in MySQL via `PyMySQL`, and renders a success page

## 🛠️ Tech Stack

- Python 3.11, Flask 3.1
- PyMySQL for MySQL connectivity
- python-dotenv for local environment variable loading
- Docker (`python:3.11-slim` base image)
- GitHub Actions for CI
- Deployed on AWS EKS, backed by AWS RDS (MySQL)

## 📁 Repository Structure

```
cloudform-app/
│
├── .github/
│   └── workflows/
│       └── app-pipeline.yml   # build → push to ECR → update GitOps repo
│
├── templates/
│   ├── index.html              # registration form
│   └── success.html            # success page
│
├── app.py                        # Flask application
├── requirements.txt              # Python dependencies
├── Dockerfile                    # container build definition
├── .dockerignore
└── .gitignore
```

## ⚙️ Configuration — Environment Variables

The app reads all database configuration from environment variables — nothing is hardcoded in the code:

| Variable | Description |
|---|---|
| `DB_HOST` | RDS endpoint |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | Database name |
| `DB_PORT` | Database port (defaults to `3306` if unset) |

In the cluster, these are injected via a Kubernetes ConfigMap (non-sensitive values) and a Secret (`DB_PASSWORD`) — see `cloudform-gitops` for the manifest.

## 🚀 CI/CD Pipeline — `app-pipeline.yml`

Triggered automatically on every push to `main`:

1. **Checkout** the repository
2. **Configure AWS credentials** and log in to ECR
3. **Tag** the build using the short Git SHA (`IMAGE_TAG`)
4. **Build** the Docker image
5. **Tag & push** the image to ECR
6. **Clone** the `cloudform-gitops` repository
7. **Update** `apps/cloudform/deployment.yaml` with the new image reference (`sed`)
8. **Commit & push** the change back to the GitOps repo

Flux then detects the new commit and rolls the update out to EKS automatically.

### Required GitHub repository configuration

**Secrets**
| Name | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_ACCOUNT_ID` | AWS account ID (used to build the ECR image URI) |
| `GH_PAT` | GitHub token with push access to `cloudform-gitops` |

**Variables**
| Name | Description |
|---|---|
| `AWS_REGION` | AWS region |
| `ECR_REPOSITORY` | ECR repository name |
| `GITOPS_REPO` | GitOps repo, in `owner/repo` format |

## 🐳 Running Locally

**With Docker:**

```bash
docker build -t cloudform-app .
docker run -p 5000:5000 \
  -e DB_HOST=<your-db-host> \
  -e DB_USER=<your-db-user> \
  -e DB_PASSWORD=<your-db-password> \
  -e DB_NAME=<your-db-name> \
  cloudform-app
```

**Without Docker:**

```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt

# create a .env file with DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
python app.py
```

App runs on `http://localhost:5000`.

> **Note:** `app.run(debug=True)` is currently hardcoded in `app.py`. This is fine for local development, but for a production image it's worth switching to an environment-driven flag (e.g. `debug=os.getenv("FLASK_DEBUG", "false") == "true"`) so debug mode is never accidentally enabled in the cluster.

## 🗄️ Database Schema

The app expects a `users` table in the target database:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔗 Usage with Other CloudForm Repositories

```
cloudform-bootstrap  →  cloudform-infra  (VPC, EKS, RDS, ECR + Flux bootstrap)
                              │
                              ▼
                    cloudform-app  ← this repository
                    builds image, pushes to ECR,
                    updates cloudform-gitops
                              │
                              ▼
                    cloudform-gitops
                    Flux watches this repo and
                    deploys the new image to EKS
```

## 👨‍💻 Project

**CloudForm** is a DevOps project demonstrating Infrastructure as Code, containerization, Kubernetes, CI/CD, and GitOps using AWS and modern DevOps tools.

Related repositories:
- [`cloudform-bootstrap`](https://github.com/rajeshdangi409/cloudform-bootstrap) — remote state backend
- [`cloudform-infra`](https://github.com/rajeshdangi409/cloudform-infra) — VPC, EKS, RDS, ECR + Flux bootstrap
- [`cloudform-gitops`](https://github.com/rajeshdangi409/cloudform-gitops) — FluxCD GitOps manifests

## 📄 License

This project is licensed under the Apache License 2.0.