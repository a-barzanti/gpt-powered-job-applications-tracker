# 📊 GPT-Powered Job Application Tracker

A painfully efficient desktop app for tracking job applications — built with Python, [Flet](https://flet.dev), and just enough automation to fool yourself into feeling productive.

No browser tabs. No Excel formulas. Just simple job tracking with real GUI vibes and a healthy side of existential dread.

---

## 💡 Features

- Native GUI using Flet (not another web app in disguise)
- Scrapes job listing text using Playwright (headless browser)
- Uses GPT to extract Company + Role automatically
- Writes to your personal Google Sheet (because yes, you still need hope)
- Minimal, fast, and cross-platform
- One click to parse job postings with GPT
- One click to refresh your existential dread ☠️

---

## 🚀 Requirements

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) or plain `pip`
- A Google Spreadsheet (with at least some hopes and dreams)
- A Google Cloud **Service Account**
- An OpenAI API key
- A basic will to keep applying

---

## 🔧 Setup Instructions

### 1. 📁 Clone this repo

```bash
git clone https://github.com/a-barzanti/gpt-powered-job-applications-tracker.git
cd gpt-powered-job-applications-tracker
```

---

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
uv pip install "flet[all]" gspread google-auth openai playwright beautifulsoup4
```

Or with `pip`:

```bash
pip install "flet[all]" gspread google-auth openai playwright beautifulsoup4
```

Then install Playwright’s browser dependencies:

```bash
playwright install
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

### 5. 🧾 Set up your OpenAI API key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new key
3. Save it to a text file named `openai_key.txt` in your project root  
   (Yes, just a plain file with the key inside. Nothing fancy.)

---

### 6. 📝 Create your spreadsheet

Create a Google Sheet with **this exact name**:

```
Job Applications Tracker
```

And make sure the first row has these columns:

| Company | Role | Status | Date Applied | URL |
| ------- | ---- | ------ | ------------ | --- |

It must be shared with your service account. Otherwise, your app will silently cry in a corner and do nothing.

---

### 7. 🧪 Run the app

```bash
python main.py
```

A glorious little window will open, scraping job listings and extracting info while you sip your cold brew and question your life choices.

---

## 🛡️ `.gitignore` Safety Reminder

```bash
echo creds.json >> .gitignore
echo openai_key.txt >> .gitignore
```

Because accidentally uploading your keys to GitHub is the fastest way to become poor.

---

## 📦 Optional: Package as Desktop App

You can package this app as a standalone `.exe`, `.app`, or binary using [Flet's packaging guide](https://flet.dev/docs/guides/packaging/overview).

---

## 🧠 Ideas for Future Features

- Form UI to manually submit new job applications
- Filters for status (applied, interviewed, ghosted, rage quit, etc.)
- Email reminders (you asked for this, not me)
- Dashboard showing your ratio of effort vs success
- Built-in coping mechanism

---

## 👨‍💻 Author

Built by someone tired of tracking job apps in spreadsheets — and even more tired of forgetting which companies ghosted them.

---

## 📄 License

MIT. Use it, break it, ignore it — just don’t @ me when it fails.

---

> “Hope is not a strategy, but this app kinda is.” – Alessandro Barzanti
