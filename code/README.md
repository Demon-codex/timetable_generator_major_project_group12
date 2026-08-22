# Automated Timetable Scheduling System

A Django-based web application that automatically generates optimized timetables for educational departments using Genetic Algorithms.

## 🎯 What This Project Does

This system helps colleges/universities create **conflict-free weekly timetables** by:
- Managing department resources (teachers, classrooms, labs)
- Scheduling lectures and practical sessions
- Handling batch divisions for lab capacity constraints
- Avoiding teacher and room conflicts
- Generating multiple timetable versions with quality scores

---

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Basic command line knowledge**
- **Web browser** (Chrome, Firefox, Edge, etc.)

---

## 🚀 How to Run This Project

### **Step 1: Activate Virtual Environment**

**What it does:** Isolates project dependencies from your system Python  
**Why needed:** Prevents package conflicts with other Python projects

```powershell
# Navigate to project root (if not there already)
cd "c:\Users\pilla\Downloads\major_ProjectTimetable (1)\major_ProjectTimetable"

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Expected result:** You'll see `(venv)` before your command prompt

---

### **Step 2: Navigate to Django Project**

**What it does:** Moves to the folder containing `manage.py` (Django's command center)

```powershell
cd UseDjango\project_name
```

---

### **Step 3: Apply Database Migrations**

**What it does:** Creates database tables from your models  
**Why needed:** Sets up SQLite database structure for storing departments, teachers, subjects, etc.

```powershell
python manage.py migrate
```

**What happens:** Django creates tables like:
- `timetable_setupmodel` (departments)
- `timetable_teachermodel` (teachers)
- `timetable_subjectmodel` (subjects)
- `timetable_departmenttimetablemodel` (saved timetables)

---

### **Step 4: Create Admin User (Optional but Recommended)**

**What it does:** Creates a superuser account to access Django admin panel  
**Why useful:** View/edit database records directly without code

```powershell
python manage.py createsuperuser
```

**You'll be asked:**
- Username: (choose anything, e.g., `admin`)
- Email: (press Enter to skip)
- Password: (type password - won't show on screen)

---

### **Step 5: Start Development Server**

**What it does:** Runs a local web server to access your application  
**Why needed:** Makes the application accessible in your web browser

```powershell
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### **Step 6: Access the Application**

Open your web browser and visit:

- **Main Application:** http://127.0.0.1:8000/timetable/home/
- **Admin Panel:** http://127.0.0.1:8000/admin/ (login with superuser credentials)

---

## 📱 Using the Application (User Workflow)

### **1. Setup Department**
- Click "Get Started" from home page
- Fill in department details:
  - Department name
  - Working hours (start/end time)
  - Number of working days per week (1-7)
  - Add recess/break times
  - Add teachers (names)
  - Add classrooms (ID and capacity)
  - Add lab rooms (ID and capacity)

### **2. Add Academic Years**
- From department dashboard, click "Add Year"
- Enter:
  - Year name (e.g., "First Year", "Second Year")
  - Total students
  - Students per batch (for practicals)

### **3. Add Subjects (Lectures)**
- Click "Add Subject" for a year
- Enter:
  - Subject name
  - Select teachers who can teach it
  - Hours per week needed

### **4. Add Practicals (Lab Sessions)**
- Click "Add Practical" for a year
- Enter:
  - Practical name
  - Select teachers
  - Hours per week needed

### **5. Allocate Rooms**
- Assign classrooms to each year
- Assign lab rooms to each year

### **6. Generate Timetable**
- Click "Generate Timetable"
- System will:
  - Run genetic algorithm (~100 seconds timeout per year)
  - Create conflict-free schedule
  - Show fitness score (quality metric)
  - Display teacher workload charts

### **7. Save & Manage**
- Name and save the generated timetable
- View saved timetables anytime
- Generate multiple versions to compare

---

## 🛠️ Technical Details

### **Dependencies Explained**

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 6.0.2 | Web framework (handles routing, templates, database) |
| deap | 1.4.3 | Genetic algorithm library (timetable optimization) |
| numpy | 2.4.2 | Numerical computations (fitness calculations) |

### **How the Scheduling Works**

1. **Input Phase:** Collects all constraints (teachers, rooms, subjects, hours)
2. **Practical Scheduling:** Assigns lab sessions to batches using available slots
3. **Lecture Scheduling:** Uses genetic algorithm to optimize lecture placement
4. **Conflict Resolution:** Ensures no teacher/room overlaps
5. **Fitness Evaluation:** Scores timetable quality (lower = better)

### **Key Constraints**

- ✅ No teacher in multiple places simultaneously
- ✅ No room double-booking
- ✅ All weekly hours fulfilled
- ✅ Batch capacity doesn't exceed lab capacity
- ✅ Recess periods respected

---

## 🔧 Common Commands

```powershell
# Activate virtual environment (always do this first)
.\venv\Scripts\Activate.ps1

# Navigate to project
cd UseDjango\project_name

# Run server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open Python shell with Django loaded
python manage.py shell

# Deactivate virtual environment (when done)
deactivate
```

---

## ⚡ Simpler Alternatives

### **If You Want Easier Dependency Management:**

Instead of manually activating venv each time:

1. **Use VS Code Python Extension:**
   - Install Python extension
   - Select interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose `venv`
   - Terminal automatically activates venv

2. **Create a Run Script:**
   Save as `run.ps1`:
   ```powershell
   .\venv\Scripts\Activate.ps1
   cd UseDjango\project_name
   python manage.py runserver
   ```
   Then just run: `.\run.ps1`

### **If You Want Simpler Scheduling Logic:**

The current genetic algorithm is powerful but complex. Simpler alternatives:

1. **Greedy Algorithm:** Fill time slots one-by-one (faster but less optimal)
2. **Constraint Satisfaction:** Use libraries like `python-constraint`
3. **Manual Scheduling:** Provide UI for drag-and-drop slot assignment

### **If You Want Cloud Deployment:**

Instead of running locally:
- **PythonAnywhere** (free tier, easy Django hosting)
- **Heroku** (simple deployment with `git push`)
- **Railway.app** (modern, free tier available)

---

## 📁 Project Structure

```
major_ProjectTimetable/
├── venv/                      # Virtual environment (isolated Python packages)
├── UseDjango/
│   └── project_name/          # Main Django project
│       ├── manage.py          # Django command-line utility
│       ├── db.sqlite3         # Database file (created after migrations)
│       ├── project_name/      # Project settings
│       │   ├── settings.py    # Configuration (database, apps, etc.)
│       │   ├── urls.py        # Main URL routing
│       │   └── wsgi.py        # Server deployment
│       └── timetable/         # Main application
│           ├── models.py      # Database schema (tables)
│           ├── views.py       # Request handlers (business logic)
│           ├── urls.py        # App-specific routes
│           ├── forms.py       # HTML form definitions
│           ├── admin.py       # Admin panel config
│           ├── services/
│           │   └── schedule.py # Genetic algorithm (2753 lines!)
│           ├── templates/     # HTML files
│           ├── static/        # CSS, JS, images
│           └── migrations/    # Database change history
├── requirements.txt           # Dependency list
└── README.md                  # This file
```

---

## 🐛 Troubleshooting

### **"No module named 'django'" error**
➜ **Solution:** Activate virtual environment first: `.\venv\Scripts\Activate.ps1`

### **"Table doesn't exist" error**
➜ **Solution:** Run migrations: `python manage.py migrate`

### **"Port already in use" error**
➜ **Solution:** Use different port: `python manage.py runserver 8001`

### **Scheduling takes too long**
➜ **Check:** Timeout is set to 100 seconds in `schedule.py` line 284  
➜ **Reduce:** Lower `max_total_attempts` or simplify constraints

---

## 📚 Documentation

### User Documentation
- **[📖 User Guide](USER_GUIDE.md)** - Complete documentation for using the application
- **[⚡ Quick Reference](QUICK_REFERENCE.md)** - Fast lookup for common tasks

### Technical Documentation
- **[⚡ Performance Optimization](PERFORMANCE_OPTIMIZATION.md)** - Database & frontend optimization guide

### Additional Resources
- **Django Documentation:** https://docs.djangoproject.com/
- **Genetic Algorithms:** https://deap.readthedocs.io/
- **Timetabling Problem:** Wikipedia "Timetabling"

---

## 💡 Tips for Understanding the Code

1. **Start with models.py** - Understand data structure
2. **Follow URL flow** - `urls.py` → `views.py` → `templates/`
3. **Use Django admin** - Visualize database records
4. **Add print statements** - Debug scheduling logic
5. **Read migrations** - See how database evolved

---

## 🎓 Key Concepts to Learn

- **Django MVT Pattern:** Model-View-Template architecture
- **ORM (Object-Relational Mapping):** Python code ↔ Database tables
- **Foreign Keys:** Relationships between models (e.g., Teacher → Department)
- **ManyToMany:** Multiple connections (e.g., Subject ↔ Teachers)
- **Genetic Algorithms:** Evolution-inspired optimization
- **Fitness Functions:** Measuring solution quality

---

**Need Help?** Check Django logs in terminal or use `python manage.py shell` to test queries!
