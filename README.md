# 📈 Trading Journal 

Trading Journal is a professional trading  built with Flask that helps traders track, analyze, and improve their trading performance.

The application supports both manual trade logging and automatic synchronization with the CoinDCX exchange through secure API integration.

---

## 🚀 Live Demo

https://trading-journal-zjp7.onrender.com

---

## ✨ Features

### 📊 Dashboard
- Trading performance overview
- Total trades
- Win rate
- Total PnL
- Average PnL
- Recent trades

### 📝 Manual Trade Journal
- Add trades manually
- Long & Short positions
- Strategy tracking
- Timeframe tracking
- Emotion logging
- Trade grading
- Notes
- Before & After chart screenshots

### 🔄 CoinDCX Integration
- Secure API authentication
- Test API connection
- Import Spot trades
- Import Futures trades
- Automatic duplicate detection
- Scheduled synchronization every 15 minutes

### 📈 Analytics
- Equity curve
- Win/Loss statistics
- Strategy performance
- Emotion analysis
- Best trade
- Worst trade
- Overall trading statistics

### 🔐 Security
- API keys stored securely
- API keys never exposed to frontend
- Backend-only API communication
- Environment variable support for deployment

### ☁ Deployment
- Hosted on Render
- Production-ready Flask application
- Gunicorn WSGI server
- GitHub integration

---

# 🛠 Tech Stack

### Backend
- Python
- Flask

### Database
- SQLite

### Frontend
- HTML
- CSS
- JavaScript

### APIs
- CoinDCX REST API

### Libraries
- APScheduler
- Requests
- Matplotlib
- Pillow
- Gunicorn
- Python-dotenv

---

# 📂 Project Structure

```
EdgeJournal/
│
├── app.py
├── database.py
├── scheduler.py
├── sync.py
├── requirements.txt
├── Procfile
├── runtime.txt
│
├── static/
│   ├── css/
│   ├── uploads/
│   └── images/
│
├── templates/
│   ├── dashboard.html
│   ├── trades.html
│   ├── analytics.html
│   ├── settings.html
│   └── add_trade.html
│
└── trades.db
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/manipenumajji/Trading_Journal.git
```

Move into the project

```bash
cd Trading_Journal
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

---

# 🔑 CoinDCX API Setup

1. Create API keys from your CoinDCX account.
2. Paste the API Key and Secret in the application's Settings page.
3. Test the connection.
4. Sync your Spot and Futures trades.

---

# 📷 Screenshots

## Dashboard



---

## Trade Journal

(Add screenshot here)

---

## Analytics
<img width="1920" height="1080" alt="Screenshot 2026-06-25 105959" src="https://github.com/user-attachments/assets/b879da0e-e510-490f-b7b0-1bc857c08a84" />


---

## Settings

(Add screenshot here)

---

# Future Improvements

- PostgreSQL support
- Multi-exchange support
- Binance integration
- Bybit integration
- Interactive charts
- Risk-to-Reward tracking
- Position sizing calculator
- CSV/PDF export
- Trade replay
- Mobile responsive design
- User authentication
- Docker support

---

# Learning Outcomes

This project helped me gain practical experience with:

- Flask Web Development
- REST API Integration
- API Authentication (HMAC SHA256)
- SQLite Database Design
- Scheduled Background Jobs
- Secure Backend Development
- CRUD Operations
- File Upload Handling
- Data Visualization
- Deployment using Render
- Git & GitHub Workflow

---

# Author

**Mani Kanta**

AI & Machine Learning Engineering Student

Interested in:

- Python Development
- Algorithmic Trading
- Machine Learning
- Backend Development
- FinTech

LinkedIn:
(Add your LinkedIn)

GitHub:
https://github.com/manipenumajji

---

# License

This project is licensed under the MIT License.
