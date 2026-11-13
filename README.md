# I-Tech Computer Education — Student Portal (Streamlit)

A complete Python-only web app built with **Streamlit** for managing students, agents, fees, attendance, and enquiries at I-Tech Computer Education.

## Features

- **Student Login** — view profile, courses, fees, attendance, payment history
- **Agent Login** — dashboard, add/edit/delete students, collect fees, mark attendance, view enquiries, manage agents
- **Guest** — browse courses & fees, timing, submit an enquiry
- Role-based menus; separate credentials for students and agents
- SHA-256 hashed passwords (never stored in plain text)
- JSON/CSV file-based storage (no external database)

## Courses & Fees (INR)

| Course            | Fee   |
|-------------------|-------|
| BCC               | 4,000 |
| CCC               | 6,000 |
| DOM               | 8,000 |
| DCA               | 12,000 |
| ADCA              | 16,000 |
| Graphic Design    | 8,000 |
| Video Editing     | 8,000 |

**Timing:** 1 hour daily (all courses)

## Demo Accounts

| Role    | ID         | Password   |
|---------|------------|------------|
| Student | ITECH001   | 1234       |
| Agent   | AGENT01    | admin123   |

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## File Structure

```
.
├── app.py              # Main Streamlit app (single file)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── students.json       # Student data (auto-created on first run)
├── agents.json         # Agent data (auto-created on first run)
└── enquiries.csv       # Guest enquiries (auto-created on first run)
```

## Design

- **iPhone-style glassmorphism theme** — translucent glass cards, blur effects, soft shadows
- **Responsive** — different layouts for web (sidebar) and mobile (stacked, bigger touch targets)
- **Professional UI** — gradient header, stat cards with icons, progress bars, badges
- **Role-based sidebar** — user info card at top, clean menu, logout button

## Notes

- Data files (`students.json`, `agents.json`, `enquiries.csv`) are created automatically on first run.
- The first agent (`AGENT01`) is the main admin and can add/remove other agents.
- All passwords are stored as SHA-256 hashes.
