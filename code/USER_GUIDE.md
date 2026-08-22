# SmartTimetable User Guide

**Version 1.0** | Last Updated: March 4, 2026

Welcome to SmartTimetable! This comprehensive guide will help you generate optimal timetables for your educational institution using our advanced genetic algorithm.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Department Setup](#department-setup)
3. [Year Management](#year-management)
4. [Subjects & Practicals](#subjects--practicals)
5. [Generating Timetables](#generating-timetables)
6. [Viewing & Comparing Results](#viewing--comparing-results)
7. [Export Options](#export-options)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### What is SmartTimetable?

SmartTimetable is an intelligent timetable generation system that uses a genetic algorithm to automatically create conflict-free schedules for educational institutions. It considers:

- Teacher availability
- Classroom/lab capacity
- Subject hours per week
- Break times
- Multiple sessions per day

### Quick Start (5 Minutes)

1. **Navigate to Setup** → Click "Get Started" on the home page
2. **Create Department** → Enter basic details (name, sessions, timings)
3. **Add Years** → Define academic years (e.g., "Year 1", "Year 2")
4. **Add Subjects** → Assign subjects and teachers to each year
5. **Generate** → Click "Generate Timetable" and wait for results!

---

## Department Setup

### Step 1: Access Setup Page

From the home page, click **"Get Started"** or navigate to **Setup** in the navigation bar.

### Step 2: Fill Department Information

#### Basic Information

| Field | Description | Example |
|-------|-------------|---------|
| **Department Name** | Name of your department | "Computer Science" |
| **Number of Sessions** | Daily teaching sessions | 6 |
| **Hours in Lecture** | Duration of each lecture (hours) | 1.0 |
| **Lecture Start Time** | When lectures begin | 09:00 |
| **Lecture End Time** | When lectures end | 16:00 |

#### Adding Recess/Breaks

Click **"New Recess"** to add break times:

- **Recess Start Time**: When break begins (e.g., 11:00)
- **Recess End Time**: When break ends (e.g., 11:30)
- **Tip**: You can add multiple recess periods (lunch, tea breaks, etc.)

#### Adding Teachers

Click **"New Teacher"** to add faculty members:

- **Teacher Name**: Full name of the teacher
- **Tip**: Add all teachers who will be assigned to subjects later

#### Adding Classrooms

Click **"New Classroom"** to add teaching spaces:

- **Classroom ID**: Room number/name (e.g., "Room 101", "CS-Lab-1")
- **Classroom Capacity**: Maximum students (e.g., 60)

#### Adding Lab Rooms

Click **"New Lab"** to add laboratory spaces:

- **Lab Room ID**: Lab identifier (e.g., "Physics Lab", "Computer Lab 2")
- **Lab Capacity**: Maximum students for practical sessions

### Step 3: Save Department

Click **"Save"** at the bottom of the form. Your department will appear in the list.

### Managing Departments

- **View**: Click on a department card to see its details
- **Edit**: Click the "Edit" button on the department card
- **Delete**: Click the "Delete" button (confirmation required)
- **Manage Years**: Click "Manage Years" to configure academic years

---

## Year Management

### Adding a New Year

1. **Navigate**: From Setup page, click **"Manage Years"** on your department
2. **Click**: "Add New Year" button
3. **Fill Details**:
   - **Year Name**: e.g., "First Year", "Second Year", "Year 1"
   - **Number of Students**: Total enrolled students
   - **Number of Batches**: How many groups for practicals (default: 1)
   - **Students per Batch**: Students in each practical group

**Example**:
- Year Name: "Second Year"
- Total Students: 120
- Batches: 3
- Students per Batch: 40

### Assigning Classrooms to Years

1. Click **"Assign Classrooms"** next to the year
2. Select classrooms from the available list
3. **Tip**: Assign classrooms with capacity ≥ total students

### Assigning Lab Rooms to Years

1. Click **"Assign Labs"** next to the year
2. Select lab rooms from the available list
3. **Tip**: Ensure lab capacity ≥ students per batch

### Editing Year Details

- **Total Students**: Click "Edit Total Students"
- **Batch Size**: Click "Edit Students per Batch"
- **Delete Year**: Click delete icon (removes all subjects/practicals too!)

---

## Subjects & Practicals

### Adding Subjects

1. **Navigate**: Go to Years page for your department
2. **Expand Year**: Click to expand the year section
3. **Click**: "Add Subject" button

#### Subject Form Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Subject Name** | Name of the subject | "Data Structures" |
| **Teachers** | Select one or more teachers who can teach this subject | [Prof. Smith, Dr. Johnson] |
| **Hours per Week** | How many lectures needed weekly | 4 |

**Important Notes**:
- Multiple teachers can be assigned (algorithm will choose the best fit)
- Hours per week should fit within weekly sessions
- Subjects are theory lectures taught to entire year

### Adding Practicals

1. **Navigate**: Same as subjects - Years page
2. **Expand Year**: Click to expand the year section
3. **Click**: "Add Practical" button

#### Practical Form Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Practical Name** | Name of the lab session | "Data Structures Lab" |
| **Teachers** | Teachers who can supervise practicals | [Prof. Smith] |
| **Hours per Week** | Weekly practical hours per batch | 2 |

**Important Notes**:
- Practicals are conducted per batch (smaller groups)
- If 3 batches exist, 3 practical sessions will be scheduled
- Lab rooms are automatically assigned based on year's allocated labs

### Editing & Deleting

- **Edit Subject/Practical**: Click the edit icon
- **Delete**: Click the delete icon (confirmation required)
- **Batch Operations**: Select multiple items and click "Delete Selected"

---

## Generating Timetables

### Step 1: Navigate to Generation Page

From the department's Years page, click **"Generate Timetable"** button.

### Step 2: Fill Generation Form

| Field | Description | Recommendation |
|-------|-------------|----------------|
| **Timetable Name** | Unique identifier for this timetable | "Spring 2026 - Version 1" |
| **Population Size** | Number of solutions in each generation | 50-100 (larger = better but slower) |
| **Generations** | How many iterations to run | 100-200 (more = better quality) |
| **Mutation Rate** | Probability of random changes (0-1) | 0.1-0.3 (10-30%) |

### Step 3: Start Generation

Click **"Generate Timetable"**. You'll see a loading screen with progress updates.

**Processing Time**:
- Small department (2-3 years): ~30 seconds
- Medium department (4-5 years): ~1-2 minutes
- Large department (6+ years): ~2-5 minutes

### Understanding Fitness Score

After generation completes, you'll see a **Fitness Score** (0-100):

- **90-100**: Excellent! Minimal to no conflicts
- **75-89**: Good, minor conflicts may exist
- **60-74**: Acceptable, some optimization needed
- **Below 60**: Poor, consider adjusting parameters or constraints

---

## Viewing & Comparing Results

### Viewing a Saved Timetable

1. **Navigate**: Setup → Select Department → "View Saved Timetables"
2. **Select**: Click "View" next to the timetable you want to see

### Timetable Display

The timetable shows:
- **Years**: Each year's schedule in separate sections
- **Days**: Monday through Friday (or Saturday if configured)
- **Time Slots**: Rows showing each session
- **Subjects**: Color-coded cells with:
  - Subject name
  - Teacher name
  - Room number

**Color Coding**:
- Regular subjects: Blue/cyan tones
- Practicals: Green/yellow tones
- Recesses: Gray
- Free periods: White/transparent

### Comparing Timetables

1. **Select Multiple**: Check boxes next to 2-3 timetables
2. **Click**: "Compare Selected" button
3. **View Comparison**:
   - Side-by-side display
   - Fitness scores comparison
   - Conflict analysis
   - Generation parameters

**Use Cases**:
- Compare different parameter settings
- Choose between multiple good solutions
- Identify why one performs better than another

### Deleting Timetables

- **Single Delete**: Click "Delete" button next to timetable
- **Batch Delete**: Select multiple, click "Delete Selected"

---

## Export Options

### Print Timetable

1. Open the timetable view
2. Click **"🖨️ Print Timetable"** button
3. Use browser's print dialog to:
   - Save as PDF
   - Print to physical printer
   - Adjust print settings

**Tips**:
- Use Landscape orientation for better fit
- Adjust margins to fit more content
- Print in color for better readability

### Export to Excel

1. Click **"📊 Export to Excel"** button
2. File downloads automatically (.xlsx format)
3. Open in Microsoft Excel, Google Sheets, or LibreOffice

**Excel Export Includes**:
- Separate sheets for each year
- Formatted tables with borders
- Color-coded cells
- Teacher and room assignments

**Use Cases**:
- Further customization
- Email to staff
- Archive copies
- Integration with other systems

### Export to PDF

1. Click **"📄 Export to PDF"** button
2. PDF downloads automatically
3. Open with any PDF reader

**PDF Features**:
- Professional formatting
- High-quality output
- Embedded fonts
- Ready to print or share

---

## Advanced Features

### Auto-Save

Forms automatically save your progress while typing:

- **Indicator**: See "Saved" or "Saving..." at top of form
- **Storage**: Saved in browser's local storage
- **Restore**: Automatically restored if you navigate away and return
- **Clear**: Data cleared after successful form submission

### Undo/Redo

Accidentally changed something? Use undo/redo:

- **Undo**: Press `Ctrl + Z` or click "Undo" button
- **Redo**: Press `Ctrl + Y` or click "Redo" button
- **History**: Up to 50 changes remembered per session
- **Available On**: All forms (setup, year, subject, practical)

### Dark/Light Theme

Toggle between themes for comfortable viewing:

- **Switch**: Click theme toggle button (top-right)
- **Shortcut**: Press `Ctrl + Shift + T`
- **Persistence**: Preference saved automatically
- **Default**: Dark theme (easier on eyes)

### Batch Operations

Efficiently manage multiple items:

- **Select**: Click checkboxes next to items
- **Select All**: Click header checkbox
- **Delete Selected**: Remove multiple items at once
- **Available On**: Subjects, Practicals, Saved Timetables

### Pagination

Large lists are paginated for better performance:

- **Items per Page**: 20 items
- **Navigate**: First / Previous / Next / Last buttons
- **Page Info**: Shows "Showing X to Y of Z items"
- **Available On**: Saved timetables list

---

## Troubleshooting

### Common Issues & Solutions

#### 1. **"Cannot generate timetable - insufficient resources"**

**Cause**: Not enough classrooms/labs for the number of years.

**Solutions**:
- Add more classrooms in Department Setup
- Add more lab rooms
- Assign classrooms to years that don't have any
- Reduce number of simultaneous sessions

#### 2. **"Low fitness score (below 60)"**

**Causes**:
- Conflicting constraints
- Too few classrooms
- Teachers over-allocated
- Unrealistic hour requirements

**Solutions**:
- Increase population size (try 100-150)
- Increase generations (try 200-300)
- Adjust mutation rate (try 0.15-0.25)
- Review subject hours per week (reduce if too high)
- Add more teachers to subjects
- Ensure classrooms  are assigned to all years

#### 3. **"Timetable generation taking too long"**

**Causes**:
- Very high population size
- Too many generations
- Large number of years/subjects

**Solutions**:
- Reduce population size to 50-75
- Reduce generations to 100-150
- Generate timetables for subsets of years
- Close other browser tabs to free memory

#### 4. **"Teacher appears multiple times in same slot"**

**Cause**: This shouldn't happen if fitness is good. May indicate a bug or very low fitness.

**Solutions**:
- Regenerate with better parameters
- Check if teacher is assigned to too many subjects
- Ensure generation completes successfully (check fitness score)

#### 5. **"Cannot save form - validation errors"**

**Causes**:
- Required fields missing
- Invalid time ranges
- Negative numbers
- Duplicate names

**Solutions**:
- Check error messages in red below fields
- Ensure all required fields (*) are filled
- Verify times are in correct format (HH:MM)
- Make sure end time > start time

#### 6. **"Form data disappeared after refresh"**

**Cause**: Auto-save might not have triggered yet, or browser cleared storage.

**Solutions**:
- Wait 2-3 seconds between edits for auto-save
- Click "Save" button instead of relying on auto-save for important data
- Don't clear browser cache while editing
- Use undo/redo feature to recover recent changes

---

## Tips & Best Practices

### Department Setup

✅ **DO**:
- Use clear, descriptive names for departments
- Add all teachers before creating subjects
- Double-check classroom capacities against enrollment
- Include buffer time between sessions for transitions

❌ **DON'T**:
- Create unrealistic time ranges (e.g., 16-hour days)
- Skip adding recess periods
- Forget to add lab rooms if you have practicals
- Use duplicate classroom IDs

### Year Configuration

✅ **DO**:
- Name years clearly (First Year, Second Year, Y1, Y2, etc.)
- Calculate batches based on lab capacity
- Assign multiple classrooms for flexibility
- Update student counts at the start of each semester

❌ **DON'T**:
- Set batch size larger than lab capacity
- Leave years without assigned classrooms
- Create more batches than necessary (wastes time slots)

### Subjects & Practicals

✅ **DO**:
- Assign 2-3 teachers to popular subjects for flexibility
- Keep subject names concise but clear
- Align hours per week with credit hours
- Add practicals for all lab-based courses

❌ **DON'T**:
- Assign only one teacher to every subject (reduces flexibility)
- Set unrealistic hours (e.g., 10 hours/week for one subject)
- Create subjects without any teachers
- Forget to add corresponding practicals for lab courses

### Timetable Generation

✅ **DO**:
- Start with moderate parameters (Population: 50, Generations: 100)
- Use descriptive names with dates ("Fall 2026 - V1", "Spring 2026 - Final")
- Generate multiple versions and compare
- Save best results before experimenting with new parameters

❌ **DON'T**:
- Use extreme values (Population: 500, Generations: 1000) unless necessary
- Overwrite good timetables without backup
- Expect 100% fitness on first try with complex constraints
- Close browser during generation (will lose progress)

### General Workflow

✅ **DO**:
- Work  in stages: Setup → Years → Subjects → Generate
- Use undo feature if you make mistakes
- Export timetables as soon as generated (backup)
- Compare multiple generated timetables before finalizing
- Clear auto-saved form data after successful submission

❌ **DON'T**:
- Rush through setup (garbage in = garbage out)
- Delete departments without exporting timetables first
- Ignore low fitness scores
- Forget to assign teachers to subjects

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Z` | Undo last change |
| `Ctrl + Y` | Redo change |
| `Ctrl + Shift + T` | Toggle dark/light theme |
| `Ctrl + P` | Print (when viewing timetable) |
| `Tab` | Navigate to next field |
| `Shift + Tab` | Navigate to previous field |
| `Enter` | Submit form / Activate button |
| `Escape` | Close modal dialogs |

---

## Frequently Asked Questions (FAQ)

### Q1: Can I generate timetables for multiple departments?

**A**: Yes! Create separate departments for each faculty/division. Each department maintains its own teachers, classrooms, and years.

### Q2: How does the genetic algorithm work?

**A**: It mimics natural selection:
1. Creates random timetables (population)
2. Evaluates each for conflicts (fitness)
3. Keeps best ones, removes worst
4. Creates new offspring by combining good timetables (crossover)
5. Randomly modifies some (mutation)
6. Repeats for specified generations

### Q3: What makes a good fitness score?

**A**: The algorithm checks for:
- Teacher conflicts (same teacher, multiple slots)
- Classroom conflicts (same room, multiple classes)
- Proper recess timing
- Hours per week met for each subject
- Student batch availability

**Score 90+** = Almost no conflicts  
**Score 75-89** = Minor conflicts  
**Score <75** = Significant conflicts

### Q4: Can I manually edit generated timetables?

**A**: Currently, no. The system generates complete timetables. If you need changes:
1. Adjust constraints (teachers, hours, classrooms)
2. Regenerate with different parameters
3. Compare multiple versions
4. Export to Excel for manual tweaking

### Q5: How many timetables should I generate?

**A**: Generate 3-5 versions with different parameters, then compare. Choose the one with highest fitness and best teacher distribution.

### Q6: What if two years need the same teacher at the same time?

**A**: The algorithm automatically handles this:
- Assigns teachers to different time slots
- Uses alternate teachers if available
- Distributes hours across the week

### Q7: Can I save multiple versions of the same semester?

**A**: Yes! Use descriptive names:
- "Fall 2026 - Version 1"
- "Fall 2026 - 100 Generations"
- "Fall 2026 - Final"

### Q8: Does the data persist after closing the browser?

**A**: 
- **Saved Data**: Yes (departments, years, subjects stored in database)
- **Form Drafts**: Yes (auto-save in browser storage)
- **Generated Timetables**: Yes (saved in database)
- **Undo History**: No (cleared on page refresh)

### Q9: Can I use this for schools/colleges/universities?

**A**: Yes! SmartTimetable works for:
- Schools (classes, sections, periods)
- Colleges (years, departments, lectures)
- Universities (programs, courses, faculty)

Just adapt terminology to your context.

### Q10: What browsers are supported?

**A**: 
- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE 11 (Limited support)

For best experience, use latest Chrome or Edge.

---

## Glossary

| Term | Definition |
|------|------------|
| **Department** | An academic division (e.g., Computer Science, Physics) |
| **Year** | Academic level/class (e.g., First Year, Second Year) |
| **Subject** | Theory course taught to entire year |
| **Practical** | Lab session conducted for smaller batches |
| **Batch** | Subset of students for practical sessions |
| **Session** | Time slot in the timetable (e.g., 9:00-10:00) |
| **Fitness** | Quality score of generated timetable (0-100) |
| **Population** | Number of candidate timetables per generation |
| **Generation** | One iteration of the genetic algorithm |
| **Mutation** | Random changes to explore new solutions |
| **Crossover** | Combining two timetables to create offspring |
| **Conflict** | Scheduling error (e.g., teacher in two places) |

---

## Getting Help

### Support Resources

- **This User Guide**: Comprehensive documentation
- **In-App Tooltips**: Hover over (?) icons for quick help
- **Error Messages**: Clear descriptions of what went wrong

### Reporting Issues

If you encounter bugs or have suggestions:

1. Note the exact steps that caused the issue
2. Check if issue persists after refreshing
3. Try in a different browser
4. Contact your system administrator

### Feature Requests

We're always improving! Suggest features:
- Better algorithm parameters
- Additional export formats
- Custom constraints
- Advanced filtering

---

## Version History

### Version 1.0 (March 4, 2026)
- ✨ Initial release
- 🧬 Genetic algorithm for timetable generation
- 📊 Excel and PDF export
- 🔄 Undo/Redo functionality
- 📦 Batch operations
- ⚡ Performance optimizations
- 🎨 Dark/Light themes
- 💾 Auto-save functionality
- 📱 Responsive design

---

## Conclusion

Congratulations! You now know how to use SmartTimetable effectively. 

**Remember**:
1. Take time to set up departments properly
2. Generate multiple timetables and compare
3. Export results for backup
4. Adjust parameters based on fitness scores

**Happy Scheduling! 📅✨**

---

*SmartTimetable User Guide v1.0 | © 2026 Timetable Generator. All rights reserved.*
