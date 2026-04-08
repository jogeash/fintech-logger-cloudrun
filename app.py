from flask import Flask, jsonify
from google.cloud import storage, bigquery
import os
import datetime
import uuid
import random

app = Flask(__name__)

# ── Home ──────────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return jsonify({
        "message": "👋 Hi to the Fintech World — Let's Excel! 🚀💳",
        "app": "💳 Fintech Transaction Logger",
        "status": "running",
        "endpoints": {
            "/log":   "Upload a simulated transaction record to Cloud Storage",
            "/stats": "Top 10 payment companies by transaction volume (BigQuery)",
            "/risk":  "Flag high-value transactions above $100 threshold (BigQuery)"
        }
    })

# ── Upload a Transaction Log to Cloud Storage ─────────────────────────────────
@app.route('/log')
def log_transaction():
    bucket_name = os.environ.get('BUCKET_NAME')
    if not bucket_name:
        return jsonify({"error": "BUCKET_NAME environment variable is not set"}), 500

    transaction_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    amount = round(random.uniform(5.0, 500.0), 2)
    status = "approved" if amount < 400 else "flagged"

    record = (
        f"Transaction ID : {transaction_id}\n"
        f"Timestamp      : {timestamp}\n"
        f"Amount         : ${amount}\n"
        f"Status         : {status}\n"
        f"Source         : Fintech Transaction Logger on Cloud Run\n"
    )

    filename = f"transactions/txn_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{transaction_id[:8]}.txt"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(record, content_type='text/plain')

    return jsonify({
        "message": "Transaction record uploaded successfully! 💾",
        "transaction_id": transaction_id,
        "amount": f"${amount}",
        "status": status,
        "bucket": bucket_name,
        "file": filename
    })

# ── Top Payment Companies by Transaction Volume ───────────────────────────────
@app.route('/stats')
def payment_stats():
    client = bigquery.Client()

    query = """
        SELECT
            company                         AS payment_company,
            COUNT(*)                        AS total_transactions,
            ROUND(SUM(fare), 2)             AS total_volume_usd,
            ROUND(AVG(fare), 2)             AS avg_transaction_usd
        FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
        WHERE fare IS NOT NULL
          AND company IS NOT NULL
          AND EXTRACT(YEAR FROM trip_start_timestamp) = 2023
        GROUP BY company
        ORDER BY total_transactions DESC
        LIMIT 10
    """

    query_job = client.query(query)
    results = query_job.result()

    rows = [
        {
            "payment_company":     row.payment_company,
            "total_transactions":  row.total_transactions,
            "total_volume_usd":    row.total_volume_usd,
            "avg_transaction_usd": row.avg_transaction_usd
        }
        for row in results
    ]

    return jsonify({
        "message": "Top 10 payment processors by transaction count (2023) 📊",
        "data": rows
    })

# ── Risk Flagging: High-Value Transactions ────────────────────────────────────
@app.route('/risk')
def risk_analysis():
    client = bigquery.Client()

    query = """
        SELECT
            company                     AS payment_company,
            COUNT(*)                    AS flagged_transactions,
            ROUND(MAX(fare), 2)         AS max_transaction_usd,
            ROUND(AVG(fare), 2)         AS avg_flagged_usd
        FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
        WHERE fare > 100
          AND company IS NOT NULL
          AND EXTRACT(YEAR FROM trip_start_timestamp) = 2023
        GROUP BY company
        ORDER BY flagged_transactions DESC
        LIMIT 10
    """

    query_job = client.query(query)
    results = query_job.result()

    rows = [
        {
            "payment_company":      row.payment_company,
            "flagged_transactions": row.flagged_transactions,
            "max_transaction_usd":  row.max_transaction_usd,
            "avg_flagged_usd":      row.avg_flagged_usd
        }
        for row in results
    ]

    return jsonify({
        "message": "⚠️ High-value transaction risk report (fare > $100, 2023)",
        "threshold": "$100",
        "data": rows
    })

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)