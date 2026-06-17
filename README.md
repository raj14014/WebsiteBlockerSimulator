# 🌐 Website Blocker Simulator

A Flask-based Website Blocker Simulator that allows users to manage blocked websites, check whether a website is blocked, and maintain a history of all website checks. The project also includes user authentication, CSV export, pagination, and an admin dashboard.

---

## 📌 Features

- 🔐 User Registration & Login
- 🚪 Logout
- 🌐 Add Blocked Websites
- ✏️ Edit Existing Websites
- 🗑️ Delete Websites
- 🔍 Search Blocked Websites
- ✅ Check if a Website is Blocked
- 📜 Website Check History
- 📊 Dashboard Statistics
- 📄 Export Blocked Websites to CSV
- 📑 Pagination
- 🔒 Password Hashing
- 💾 SQLite Database

---

## 🛠 Technologies Used

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- Jinja2

---

## 📂 Project Structure

```
WebsiteBlockerSimulator/
│
├── app.py
├── database.py
├── website_blocker.db
├── requirements.txt
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── edit.html
│
├── static/
│   └── css/
│       └── style.css
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/raj14014/WebsiteBlockerSimulator.git

cd WebsiteBlockerSimulator
```

### Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Project

Create the database

```bash
python database.py
```

Start Flask

```bash
python app.py
```

Open your browser

```
http://127.0.0.1:5000
```

---

## 📷 Screenshots

### Login Page

- Secure login page for users.

### Dashboard

- View blocked websites
- Search websites
- Dashboard statistics
- Website history
- Pagination

### Check Website

Enter a website to determine whether access is:

- ✅ Allowed
- ❌ Blocked

---

## 📊 Database Tables

### users

| Field | Type |
|-------|------|
| id | Integer |
| username | Text |
| password | Text |
| role | Text |

---

### blocked_websites

| Field | Type |
|-------|------|
| id | Integer |
| website | Text |

---

### history

| Field | Type |
|-------|------|
| id | Integer |
| website | Text |
| status | Text |
| checked_at | Timestamp |

---

## 🔐 Authentication

Passwords are securely stored using Werkzeug password hashing.

---

## 📄 CSV Export

The application allows downloading all blocked websites as a CSV file.

---

## 🚀 Future Improvements

- Admin/User Roles
- Email Verification
- Password Reset
- Dark Mode
- REST API
- Docker Support
- Deployment on Render/Vercel

---

## 👨‍💻 Author

**Raj**

GitHub:
https://github.com/raj14014

---

## 📜 License

This project is for educational purposes.
