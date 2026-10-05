# 🌱 Growly

**Smart Internship, Placement and Coding Assessment Platform**

Growly is a web-based platform that connects a student's *demonstrated* coding ability with real internship opportunities. Instead of using one site to practice coding, another to find internships, another for a resume, and yet another for company assessments, Growly brings everything into a single system.

> **Learn → Practice → Prove Skills → Find Internship → Apply → Get Assessed → Get Shortlisted → Interview → Placement**

This project is developed as a BCA 6th Semester project at **Lumbini I.C.T. Campus** (Gaidakot, Nawalpur), affiliated with **Tribhuvan University**.

---

## ✨ Features

### For Students
- Create a technical profile (skills, projects, certifications, coding performance)
- Browse, search, and filter internships and placements
- Practice coding problems and submit solutions
- Take timed coding assessments assigned by companies
- Apply to internships and track application status
- Get internship recommendations based on skills and preferences
- View interview schedules and results

### For Companies
- Register and manage a company profile
- Post internships and placement opportunities with skill requirements
- Create coding problems and assessments
- View applicants along with their verified coding performance
- Shortlist candidates and schedule interviews
- Track placements

### For Administrators
- Manage users, companies, internships, and coding problems
- Approve company registrations
- Monitor applications and platform activity
- Generate reports

---

## 👥 User Roles

| Role | Responsibilities |
|------|------------------|
| **Student** | Builds a technical profile, practices coding, applies for internships, takes assessments |
| **Company** | Posts opportunities, creates assessments, evaluates and shortlists candidates |
| **Administrator** | Manages platform data, users, approvals, and reports |

---

## 🧩 Modules

1. **Admin**: platform and infrastructure management
2. **Student Management**: profiles, academic info, skills, resumes
3. **Company Management**: company profiles, recruiters, open positions
4. **Internship Management**: create, update, search, filter internships
5. **Coding Problem Management**: problems with descriptions, difficulty levels, test cases, required skills
6. **Code Submission & Evaluation**: submit code, run test cases, automated evaluation
7. **Interview & Placement Management**: scheduling, shortlisting, placement tracking
8. **Admin & Reporting**: monitoring, records, and reports
9. **Internship Recommendations**: skill-based matching for students
10. **Coding Assessment**: create, schedule, and conduct assessments

### Hiring Pipeline

```
Applied → Test Assigned → Test Completed → Shortlisted → Interview → Selected / Rejected
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap |
| Backend | Python, **Django** |
| Database | MySQL |
| Code Execution | Judge0 API |
| Version Control | Git & GitHub |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Database Setup

Create a MySQL database:

```sql
CREATE DATABASE growly CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=growly
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306

JUDGE0_API_URL=your-judge0-api-url
JUDGE0_API_KEY=your-judge0-api-key
```

### Run the Project

```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create an admin account
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## 📁 Project Structure

```
growly/
├── manage.py
├── requirements.txt
├── growly/              # Project settings and root URLs
├── accounts/            # Authentication, roles, profiles
├── internships/         # Internship listings and applications
├── assessments/         # Coding problems, submissions, evaluation
├── companies/           # Company profiles and recruiter tools
├── templates/           # HTML templates
└── static/              # CSS, JavaScript, images
```

> Update this to match your actual folder layout.

---

## 🔄 Development Methodology

Growly follows the **Waterfall model**:

1. Feasibility Study
2. Requirement Analysis
3. System Design (use-case, activity, and ER diagrams)
4. Implementation
5. Testing
6. Maintenance

The project prioritizes a realistic academic MVP, with advanced features kept as future scope.

---

## 🧪 Testing

- **Unit Testing**: individual components tested in isolation
- **System Testing**: the fully integrated system tested against requirements

```bash
python manage.py test
```

---

## 🗺 Roadmap

- [ ] Authentication and role-based dashboards
- [ ] Student technical profile
- [ ] Company profile and internship posting
- [ ] Coding problem bank and code editor
- [ ] Code submission and automated evaluation (Judge0)
- [ ] Application tracking and hiring pipeline
- [ ] Interview scheduling and placement tracking
- [ ] Skill-based internship recommendations
- [ ] Admin reports and analytics

---

## 👨‍💻 Team

| Name | Roll No. |
|------|----------|
| Rajan Poudel | 119402143 |
| Abin Ghimire | 119402118 |

**Institution:** Lumbini I.C.T. Campus, Gaidakot, Nawalpur
**Affiliation:** Tribhuvan University
**Program:** Bachelor of Computer Application (BCA), 6th Semester

---

## 📄 License

This project is developed for academic purposes. Add a license here if you plan to open-source it (e.g., MIT).
