# 📊 Simple Job Applications Tracker

A lightweight desktop app built in Python using [Flet](https://flet.dev) that connects to a **Google Spreadsheet** and displays your job application data in a clean, native window interface.

No browser tabs. No Excel formulas. Just simple job tracking with real GUI vibes.

---

## 💡 Features

- Native GUI using Flet (not another web app in disguise)
- Reads your job application data directly from a Google Sheet
- Minimal, fast, and cross-platform
- One click to refresh your existential dread

---

## 🚀 Requirements

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) or pip
- A Google Spreadsheet (with at least some hopes and dreams)
- A Google Cloud **Service Account**

---

## 🔧 Setup Instructions

### 1. 📁 Clone this repo

```bash
git clone https://github.com/yourusername/simple-job-applications-tracker.git
cd simple-job-applications-tracker
```

### 2. 🐍 Create a virtual environment

Using `uv` (recommended):

```bash
uv venv
source .venv/bin/activate
```

Or with `venv`:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

---

### 3. 📦 Install dependencies

Using `uv`:

```bash
uv pip install "flet[all]" gspread google-auth
```

Or using pip:

```bash
pip install "flet[all]" gspread google-auth
```

---

### 4. 🔐 Set up Google Sheets access

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (e.g., "Job Tracker")
3. Go to **IAM & Admin → Service Accounts**
4. Create a new service account
5. Generate a **JSON key** and download it
6. Place the file in your project folder as `creds.json`
7. Share your Google Sheet with the service account email  
   (e.g., `your-bot@jobtracker.iam.gserviceaccount.com`)

---

### 5. 📝 Create your spreadsheet

Create a Google Sheet with columns like this in the first row:

| Company | Role | Status | Date Applied |
| ------- | ---- | ------ | ------------ |

Give it a name like **Job Applications Tracker**, and make sure it's shared with your service account.

---

### 6. 🧪 Run the app

```bash
python app.py
```

A window will open, showing your job application data from the spreadsheet.

---

## 🛡️ `.gitignore` Safety Reminder

Make sure you don’t commit your Google credentials:

```bash
echo creds.json >> .gitignore
```

---

## 📦 Optional: Package as Desktop App

You can package the app as a standalone `.exe`, `.app`, or binary using [Flet's packaging guide](https://flet.dev/docs/guides/packaging/overview).

---

## 🧠 Ideas for Future Features

- Form UI to submit new job applications
- Filters for status (applied, interviewed, ghosted, etc.)
- Email notifications (just kidding... unless?)
- A graph showing the number of jobs you applied for vs your will to live

---

## 👨‍💻 Author

Built by someone tired of tracking job apps in spreadsheets, and even more tired of forgetting which companies ghosted them.

---

## 📄 License

MIT. Use it, modify it, blame your bugs on me—I won’t respond anyway.