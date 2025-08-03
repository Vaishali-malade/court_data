from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'case_queries.db'


# Initialize SQLite database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                court TEXT,
                case_type TEXT,
                case_number TEXT,
                case_year TEXT,
                timestamp TEXT,
                raw_html TEXT
            )
        ''')
init_db()


# Scraper for Faridabad eCourts portal (mocked)
import random

def scrape_faridabad_case(case_type, case_number, case_year):
    try:
        # Simulate random parties
        party_names = [
            "Ravi Sharma vs State of Haryana",
            "Anita Gupta vs Rajesh Mehra",
            "XYZ Ltd vs ABC Corp",
            "Sunita Devi vs Haryana Police",
            "Kunal Batra vs Municipal Corporation"
        ]
        parties = random.choice(party_names)

        # Simulate filing date between 2019-2024
        filing_date = datetime.strptime(f"{random.randint(2019, 2024)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}", "%Y-%m-%d").date()

        # Simulate next hearing date after filing
        next_hearing = filing_date.replace(year=2025, month=random.randint(1,12))

        # Simulate status
        statuses = ["Pending", "Disposed", "Listed", "Under Review", "Adjourned"]
        status = random.choice(statuses)

        metadata = {
            "Court": "Faridabad District Court",
            "Case Type": case_type,
            "Case Number": case_number,
            "Case Year": case_year,
            "Parties": parties,
            "Filing Date": filing_date.strftime("%Y-%m-%d"),
            "Next Hearing": next_hearing.strftime("%Y-%m-%d"),
            "Status": status
        }

        orders = [
            {
                "date": "2025-07-01",
                "order": "Latest Order Issued",
                "pdf_url": "https://ecourts.gov.in/sample_order_101.pdf"
            }
        ]

        # Simulate raw HTML
        raw_html = f"<html><body><h1>{parties}</h1></body></html>"

        # Log to DB
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (court, case_type, case_number, case_year, timestamp, raw_html)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                "Faridabad District Court", case_type, case_number, case_year,
                datetime.now().isoformat(), raw_html
            ))

        return {"metadata": metadata, "orders": orders}

    except Exception as e:
        return {"error": f"Error fetching Faridabad data: {str(e)}"}

# Simulated scraper for Delhi High Court
import random
from datetime import datetime
import sqlite3

def scrape_delhi_high_court(case_type, case_number, case_year):
    try:
        # Random party names
        party_names = [
            "ABC Corp vs Union of India",
            "Meena Sharma vs Delhi Development Authority",
            "XYZ Pvt Ltd vs Delhi Jal Board",
            "Sunil Kumar vs Delhi Police",
            "Rekha Gupta vs State of NCT of Delhi"
        ]
        parties = random.choice(party_names)

        # Random filing date (2020–2024)
        filing_date = datetime.strptime(
            f"{random.randint(2020, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", "%Y-%m-%d"
        ).date()

        # Random next hearing date in 2025
        next_hearing = filing_date.replace(year=2025, month=random.randint(1, 12))

        # Random status
        statuses = ["Listed", "Pending", "Reserved", "Dismissed", "In Progress"]
        status = random.choice(statuses)

        # Metadata dict
        metadata = {
            "Court": "Delhi High Court",
            "Case Type": case_type,
            "Case Number": case_number,
            "Case Year": case_year,
            "Parties": parties,
            "Filing Date": filing_date.strftime("%Y-%m-%d"),
            "Next Hearing": next_hearing.strftime("%Y-%m-%d"),
            "Status": status
        }

        # Orders (dummy PDF)
        orders = [
            {
                "date": "2025-07-15",
                "order": "Show Cause Notice Issued",
                "pdf_url": "https://delhihighcourt.nic.in/sample_order_delhi.pdf"
            }
        ]

        # Simulated HTML
        raw_html = f"<html><body><h1>{parties}</h1></body></html>"

        # Log to DB
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (court, case_type, case_number, case_year, timestamp, raw_html)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                "Delhi High Court", case_type, case_number, case_year,
                datetime.now().isoformat(), raw_html
            ))

        return {"metadata": metadata, "orders": orders}

    except Exception as e:
        return {"error": f"Error fetching Delhi High Court data: {str(e)}"}

@app.route('/', methods=['GET', 'POST'])
def search_case():
    if request.method == 'POST':
        court = request.form.get('court')
        case_type = request.form.get('case_type')
        case_number = request.form.get('case_number')
        case_year = request.form.get('case_year')

        if not all([court, case_type, case_number, case_year]):
            return render_template("error.html", message="All fields are required.")

        if court == "faridabad":
            result = scrape_faridabad_case(case_type, case_number, case_year)
        elif court == "delhi":
            result = scrape_delhi_high_court(case_type, case_number, case_year)
        else:
            return render_template("error.html", message="Unsupported court selected.")

        if "error" in result:
            return render_template("error.html", message=result["error"])

        return render_template("result.html", metadata=result["metadata"], orders=result["orders"])

    return render_template("index.html")


from flask import send_file
from io import BytesIO
import urllib.parse

@app.route('/view-pdf')
def view_pdf():
    pdf_url = request.args.get('pdf_url')
    if not pdf_url:
        return "Missing PDF URL", 400

    try:
        decoded_url = urllib.parse.unquote(pdf_url)
        response = requests.get(decoded_url)
        response.raise_for_status()
        return send_file(BytesIO(response.content),
                         mimetype='application/pdf',
                         as_attachment=False,
                         download_name='case_order.pdf')
    except Exception as e:
        return f"Failed to load PDF: {str(e)}", 500

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM logs')
        total_queries = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM logs WHERE court = "Delhi High Court"')
        delhi_queries = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM logs WHERE court = "Faridabad District Court"')
        faridabad_queries = cursor.fetchone()[0]

        cursor.execute('''
            SELECT id, court, case_type, case_number, case_year, timestamp
            FROM logs
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        recent_logs = cursor.fetchall()

    return render_template('dashboard.html',
                           total_queries=total_queries,
                           delhi_queries=delhi_queries,
                           faridabad_queries=faridabad_queries,
                           recent_logs=recent_logs)



if __name__ == '__main__':
    app.run(debug=True)
