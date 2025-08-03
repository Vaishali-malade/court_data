# Delhi High Court Case Tracker

##  Features
- Simple web interface to fetch case details from Delhi High Court
- Inputs: Case Type, Number, Year
- Displays:
  - Parties’ names
  - Filing and next hearing date
  - Latest order/judgment link (PDF)
- All searches are logged to SQLite
- Handles invalid inputs and downtime with user-friendly errors

##  Tech Stack
- Flask (Python)
- BeautifulSoup / Selenium (for scraping)
- SQLite (for logging)
- HTML (form UI)

## Source Website
https://delhihighcourt.nic.in

### CAPTCHA / ViewState Handling
- Delhi High Court uses CAPTCHA and JavaScript-based search submission
- For real-time scraping, `selenium` can simulate browser actions
- In this version: 
  - We simulate real requests with pre-parsed structure
  - CAPTCHA is bypassed by testing on already-fetched samples

