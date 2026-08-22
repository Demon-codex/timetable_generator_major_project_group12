# SmartTimetable Quick Reference Guide

⚡ **Fast reference for common tasks** - Bookmark this page!

---

## 🎯 Quick Start (5 Minutes)

```
1. Setup → Create Department
2. Manage Years → Add Years (e.g., "Year 1", "Year 2")
3. Add Subjects → For each year
4. Generate → Click "Generate Timetable"
5. View → Check results & export
```

---

## 📋 Common Tasks

### Create New Department
```
Setup → Fill Form → Add Teachers/Classrooms/Labs → Save
```

### Add Year to Department
```
Setup → Manage Years (on department) → Add New Year → Fill Details → Save
```

### Add Subject
```
Years Page → Expand Year → Add Subject → Select Teachers → Set Hours → Save
```

### Generate Timetable
```
Years Page → Generate Timetable → Set Parameters → Generate → Wait
```

**Recommended Parameters:**
- Population: 50-100
- Generations: 100-200  
- Mutation Rate: 0.1-0.3

### Export Timetable
```
View Timetable → Click Export Button (Excel/PDF/Print)
```

---

## ⌨️ Keyboard Shortcuts

| Keys | Action |
|------|--------|
| `Ctrl + Z` | Undo |
| `Ctrl + Y` | Redo |
| `Ctrl + Shift + T` | Toggle Theme |
| `Tab` | Next Field |
| `Shift + Tab` | Previous Field |
| `Escape` | Close Modal |

---

## 🎨 Form Fields Quick Reference

### Department Setup

| Field | Example | Notes |
|-------|---------|-------|
| Department Name | "Computer Science" | Unique identifier |
| Sessions | 6 | Daily lecture slots |
| Hours in Lecture | 1.0 | Duration per session |
| Start Time | 09:00 | First session starts |
| End Time | 16:00 | Last session ends |

### Year Setup

| Field | Example | Notes |
|-------|---------|-------|
| Year Name | "Second Year" | Clear label |
| Total Students | 120 | Enrollment count |
| Batches | 3 | For practicals |
| Students/Batch | 40 | Per practical group |

### Subject Setup

| Field | Example | Notes |
|-------|---------|-------|
| Subject Name | "Data Structures" | Course name |
| Teachers | [Prof. Smith] | Can select multiple |
| Hours/Week | 4 | Weekly lectures |

### Practical Setup

| Field | Example | Notes |
|-------|---------|-------|
| Practical Name | "DS Lab" | Lab course name |
| Teachers | [Prof. Smith] | Lab supervisors |
| Hours/Week | 2 | Per batch |

### Generation Parameters

| Parameter | Range | Recommended | Effect |
|-----------|-------|-------------|--------|
| Population | 10-500 | 50-100 | More = better quality, slower |
| Generations | 10-1000 | 100-200 | More = better convergence |
| Mutation Rate | 0.0-1.0 | 0.1-0.3 | Balance exploration vs exploitation |

---

## 🏆 Fitness Score Guide

| Score | Quality | Action |
|-------|---------|--------|
| 90-100 | ✅ Excellent | Accept & export |
| 75-89 | ✅ Good | Review minor conflicts |
| 60-74 | ⚠️ Fair | Regenerate with better params |
| Below 60 | ❌ Poor | Check constraints, increase generations |

---

## 🛠️ Troubleshooting Quick Fixes

### Issue: Low Fitness Score
```
✓ Increase population to 100-150
✓ Increase generations to 200-300
✓ Check for over-allocated teachers
✓ Ensure sufficient classrooms assigned
```

### Issue: Generation Takes Too Long
```
✓ Reduce population to 50-75
✓ Reduce generations to 100-150
✓ Close other browser tabs
```

### Issue: "Insufficient Resources"
```
✓ Add more classrooms/labs
✓ Assign classrooms to years
✓ Check year has allocated rooms
```

### Issue: Validation Errors
```
✓ Fill all required fields (marked with *)
✓ Check time format (HH:MM)
✓ Ensure end time > start time
✓ Remove duplicate names
```

---

## 📊 Workflow Checklist

### Initial Setup
- [ ] Create department with details
- [ ] Add all teachers
- [ ] Add all classrooms
- [ ] Add all lab rooms
- [ ] Set recess periods

### Per Year
- [ ] Create year with student count
- [ ] Assign classrooms to year
- [ ] Assign lab rooms to year
- [ ] Add all subjects with teachers
- [ ] Add all practicals with supervisors

### Generation
- [ ] Set descriptive timetable name
- [ ] Choose appropriate parameters
- [ ] Generate and wait for completion
- [ ] Check fitness score
- [ ] Generate 2-3 more versions
- [ ] Compare and select best

### Finalization
- [ ] Review selected timetable
- [ ] Export to Excel/PDF
- [ ] Print copies if needed
- [ ] Archive/backup files

---

## 💡 Pro Tips

### ⚡ Performance
- Keep population ≤ 150 for speed
- Use pagination for large timetable lists
- Close unused browser tabs during generation

### 🎯 Better Results
- Assign 2-3 teachers per subject for flexibility
- Don't over-allocate teachers (max 15-20 hours/week)
- Ensure classroom capacity ≥ year enrollment
- Use realistic hours per week per subject

### 💾 Data Management
- Use descriptive names with dates
- Export important timetables immediately
- Compare multiple versions before finalizing
- Keep backup copies of generated timetables

### 🔄 Efficiency
- Use batch operations to delete multiple items
- Use undo/redo instead of re-entering data
- Let auto-save work (wait 2-3 seconds between changes)
- Use theme toggle for comfortable viewing

---

##  📱 Export Format Comparison

| Format | Best For | Features |
|--------|----------|----------|
| **Print** | Physical copies | Direct to printer/PDF |
| **Excel** | Editing/Analysis | Editable spreadsheet, color-coded |
| **PDF** | Sharing/Archive | Professional, unchangeable, compact |

---

## 🎓 Best Practices Summary

### DO ✅
- Set up department thoroughly before adding years
- Add multiple teachers to subjects for algorithm flexibility
- Generate 3-5 timetables and compare
- Use descriptive naming conventions
- Export backups regularly

### DON'T ❌
- Rush through setup (leads to poor results)
- Use extreme parameter values without testing
- Ignore low fitness scores
- Delete departments without exporting first
- Expect perfect results on first generation

---

## 📞 Quick Help

### Form Not Saving?
1. Check for error messages (red text)
2. Fill all required fields (*)
3. Wait 2-3 seconds for auto-save
4. Click "Save" button explicitly

### Can't Generate?
1. Ensure year has subjects/practicals
2. Check classrooms assigned to year
3. Verify teachers assigned to subjects
4. Review error message details

### Low Performance?
1. Reduce population/generations
2. Clear browser cache
3. Use latest Chrome/Edge
4. Close other applications

---

## 🔗 Related Documentation

- **[Full User Guide](USER_GUIDE.md)**: Complete documentation
- **[README](README.md)**: Project overview & setup
- **[Performance Guide](PERFORMANCE_OPTIMIZATION.md)**: Optimization tips

---

**Version 1.0** | Last Updated: March 4, 2026  
*SmartTimetable Quick Reference © 2026*
