# FinanceFlow - Personal Expense Tracker

A clean and modern desktop expense tracker built with Python to help you track your spending, manage budgets, and take control of your finances.

---

## Features

- Add, Edit, and Delete expenses
- Categorize expenses (Food, Transport, Entertainment, Shopping, Bills, Healthcare, Other)
- Monthly budget tracking with real-time status
- Export all expenses to CSV file
- Persistent cloud database storage (MongoDB)
- Clean and simple interface using Tkinter
- Total spending calculation

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3 | Core programming language |
| Tkinter | GUI framework |
| MongoDB Atlas | Cloud database |
| PyMongo | Database driver |
| CSV module | Export functionality |
| Datetime module | Date handling |

---

## Running the Project Locally

Follow these steps to set up and run FinanceFlow on your local machine.

### Prerequisites

Make sure you have the following installed:

- Python 3.6 or higher
- pip package manager
- MongoDB Atlas account (free)

### 1. Install Required Packages

Open terminal and run:

```bash
pip install pymongo dnspython
```
### 2. Configure MongoDB
Update your MONGO_URI in config.py with your Atlas connection string.

### 3. Run the application
```bash
python financeflow.py
```

## How to Use
First Time: Run the app, enter your monthly budget, and click "Set Budget"

Add Expense: Enter amount, select category, add description, pick date → Click "Add Expense"

Edit Expense: Double-click any row or select it and click "Edit Selected"

Delete Expense: Select the row and click "Delete Selected"

Export Data: Click "Export to CSV" to save all expenses to a file

Budget Tracking: Set a monthly budget and watch the status bar update in real-time

## Security Note
Your config.py contains your MongoDB password. Do not upload this file to GitHub.

Add this to .gitignore:

text
``` bash
config.py
__pycache__/
*.pyc
```

