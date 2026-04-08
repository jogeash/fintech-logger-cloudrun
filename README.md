# 💳 Fintech Transaction Logger on Google Cloud Run

A containerized Flask microservice deployed on **Google Cloud Run** that simulates a fintech transaction logging and risk analysis system. Built as part of an MLOps Cloud Run lab.

---

## 🚀 Live Service

**Base URL:** `https://fintech-logger-service-1098537554013.us-central1.run.app`

| Endpoint | Description |
|----------|-------------|
| `/`      | Service status and available endpoints |
| `/log`   | Generates a simulated transaction and uploads it to Cloud Storage |
| `/stats` | Queries top 10 payment companies by transaction volume (BigQuery) |
| `/risk`  | Flags high-value transactions above $100 threshold (BigQuery) |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python + Flask | Web application framework |
| Google Cloud Run | Serverless container deployment |
| Google Cloud Storage | Transaction log file storage |
| Google BigQuery | Public fintech dataset queries |
| Docker | Containerization |
| Google Container Registry | Docker image hosting |
| gunicorn | Production WSGI server |

---

## 📁 Project Structure

```
fintech-logger-cloudrun/
├── app.py               # Flask application with 3 endpoints
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ⚙️ How It Works

### `/log` — Transaction Logger
- Generates a unique transaction ID using `uuid`
- Simulates a random payment amount between $5–$500
- Auto-flags transactions above $400 as `flagged`, rest as `approved`
- Uploads a `.txt` record to a GCS bucket under the `transactions/` folder

### `/stats` — Payment Volume Analytics
- Queries the `bigquery-public-data.chicago_taxi_trips.taxi_trips` public dataset
- Treats taxi companies as payment processors and fares as transaction amounts
- Returns top 10 companies by transaction count and total volume for 2023

### `/risk` — Risk Analysis
- Queries transactions with fare > $100 (high-value threshold)
- Returns flagged transaction count, max and average values per company
- Simulates a basic fraud/risk detection pipeline

---

## 🏗️ Deployment Steps

### 1. Clone the repo
```bash
git clone https://github.com/jogeash/fintech-logger-cloudrun.git
cd fintech-logger-cloudrun
```

### 2. Set your GCP Project
```bash
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID
```

### 3. Enable required APIs
```bash
gcloud services enable run.googleapis.com storage.googleapis.com bigquery.googleapis.com
```

### 4. Create Cloud Storage bucket
```bash
gsutil mb -l us-central1 gs://your-bucket-name
```

### 5. Create Service Account
```bash
gcloud iam service-accounts create fintech-logger-sa \
  --display-name="Fintech Logger Service Account"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:fintech-logger-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:fintech-logger-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.user"
```

### 6. Build and push Docker image
```bash
# Important: use --platform linux/amd64 for M1/M2 Macs
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/fintech-logger-app .
docker push gcr.io/$PROJECT_ID/fintech-logger-app
```

### 7. Deploy to Cloud Run
```bash
gcloud run deploy fintech-logger-service \
  --image gcr.io/$PROJECT_ID/fintech-logger-app \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --update-env-vars BUCKET_NAME=your-bucket-name \
  --service-account fintech-logger-sa@$PROJECT_ID.iam.gserviceaccount.com
```

---

## 🧹 Clean Up
```bash
gcloud run services delete fintech-logger-service --region us-central1
gcloud container images delete gcr.io/$PROJECT_ID/fintech-logger-app --force-delete-tags
gsutil rm -r gs://your-bucket-name
```

---

## 💡 Key Learnings

- Deploying containerized Python apps to **Google Cloud Run**
- Integrating **Cloud Storage** and **BigQuery** from a running container
- Using **Service Accounts** for secure GCP authentication
- Fixing **ARM vs AMD64** Docker platform issues on Apple Silicon Macs
- Using **gunicorn** as a production-grade WSGI server
- Managing **environment variables** in Cloud Run deployments

---

## 👩‍💻 Author

**Jogeashwini** — MS Data Analytics Engineering, Northeastern University