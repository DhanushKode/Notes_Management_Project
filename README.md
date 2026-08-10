# Notes Management Project

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

A Flask-based web application for managing personal notes and files. Users can create an account, verify it using an email OTP, sign in, manage their notes, upload files, search stored content, and export notes to Excel.

## Features

- User registration and login
- Email OTP account verification with a five-minute expiry
- Filesystem-based login sessions
- Add, view, update, and delete notes
- Upload, view, download, and delete files
- Search notes and uploaded files
- Export notes as an Excel workbook
- Forgot-password email and time-limited reset link
- User-specific data access
- Flash messages for success and error feedback

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, Jinja2 |
| Database | MySQL |
| Sessions | Flask-Session |
| Email | Python SMTP |
| Excel export | Flask-Excel, PyExcel, OpenPyXL |
| Reset tokens | ItsDangerous |

## Project Structure

```text
Notes_Management_Project/
├── Templates/              # Jinja2 HTML templates
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── otp.html
│   ├── dashboard.html
│   ├── addnotes.html
│   ├── viewallnotes.html
│   ├── viewnotes.html
│   ├── updatenotes.html
│   ├── uploadfile.html
│   ├── viewallfiles.html
│   ├── searchdata.html
│   ├── forgot.html
│   ├── newpassword.html
│   └── reset.html
├── static/
│   └── dashboard.css       # Dashboard styles
├── app.py                  # Flask application and routes
├── cmail.py                # SMTP email helper
├── otp.py                  # OTP generator
├── stoken.py               # Password-reset token helper
├── data.sql                # MySQL schema and sample data
└── requirements.txt        # Python dependencies
```

## Database Design

| Table | Purpose |
|---|---|
| `users` | Stores user details, OTP information, and account status |
| `notesdata` | Stores each user's notes and creation time |
| `filesdata` | Stores uploaded filenames, binary data, and creation time |

The notes and files tables are connected to `users` through the `userid` foreign key.

## Prerequisites

Install the following before running the project:

- Python 3.10 or newer
- MySQL Server 8.x
- Git
- An SMTP-enabled email account for OTP and password-reset messages

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/DhanushKode/Notes_Management_Project.git
cd Notes_Management_Project
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Create and import the MySQL database

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS smp;"
mysql -u root -p smp < data.sql
```

You can also create the `smp` database and import `data.sql` using MySQL Workbench.

### 5. Configure the application

Update the MySQL connection settings in `app.py` so they match your local MySQL username and password.

Configure the SMTP sender account in `cmail.py` so registration OTPs and password-reset links can be delivered. For a deployed application, keep database passwords, SMTP credentials, Flask secret keys, and serializer keys in environment variables instead of source files.

> **Template folder note:** Flask normally searches for a lowercase `templates` folder. Windows accepts the current `Templates` folder, but Linux and macOS may require you to rename it to `templates` or initialize Flask with `template_folder="Templates"`.

### 6. Run the application

```bash
python app.py
```

Open the application at:

```text
http://127.0.0.1:5000
```

## Application Flow

1. Create a user account.
2. Enter the OTP received by email.
3. Sign in using the verified account.
4. Open the dashboard.
5. Create and manage notes or upload files.
6. Search stored content or export notes to Excel.
7. Sign out when finished.

## Screenshots

Add screenshots to a `screenshots` directory and replace the examples below with the correct filenames:

```markdown
![Home page](screenshots/home.png)
![Dashboard](screenshots/dashboard.png)
![Notes page](screenshots/notes.png)
```

## Security Notice

This project is currently suitable for learning and local development. Before deploying it publicly:

- Remove and rotate credentials or secret keys committed to the repository.
- Store configuration in environment variables and add `.env` to `.gitignore`.
- Hash passwords using Werkzeug, bcrypt, or Argon2 instead of storing plain text.
- Remove personal/sample records and binary files from `data.sql`.
- Add CSRF protection and use POST/DELETE requests for destructive actions.
- Validate uploaded file types and sizes.
- Disable debug mode and serve the app through a production WSGI server.

## Future Improvements

- Organize notes with categories, tags, and favourites
- Add pagination and advanced search filters
- Support Markdown notes
- Add profile management
- Use cloud object storage for uploaded files
- Add automated tests
- Add Docker support
- Deploy the application to a cloud platform

## Author

**Dhanush Kode**

- GitHub: [@DhanushKode](https://github.com/DhanushKode)
- Project: [Notes Management Project](https://github.com/DhanushKode/Notes_Management_Project)

## Contributing

Contributions, issues, and feature suggestions are welcome. Fork the repository, create a feature branch, make your changes, and open a pull request.

## License

No license has been added yet. Add a `LICENSE` file if you want others to use, modify, or distribute this project under specific terms.
