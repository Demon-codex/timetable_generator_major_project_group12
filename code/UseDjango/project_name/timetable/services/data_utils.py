"""
Business-logic helpers extracted from views.py.
Handles timetable data preparation, merging, and statistics.
"""
from datetime import datetime, timedelta
from collections import defaultdict
from django.conf import settings

# mapping day numbers to names
DAY_NAMES = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}


def normalize_recess_windows(
    recess_list,
    start_time_str="09:00",
    end_time_str="16:15",
    time_format="%H:%M"
):
    """Normalize recess windows into valid in-day 24h ranges.

    If a window is entered as 12-hour style afternoon time (e.g. 01:15-02:15)
    while the configured working day starts in the morning, shift it by +12 hours
    when that corrected range fits within the configured day.
    """
    start_time = datetime.strptime(start_time_str, time_format)
    end_time = datetime.strptime(end_time_str, time_format)
    start_min = start_time.hour * 60 + start_time.minute
    end_min = end_time.hour * 60 + end_time.minute

    normalized = []
    seen = set()

    for r_start, r_end in recess_list or []:
        try:
            rs = datetime.strptime(r_start, time_format)
            re = datetime.strptime(r_end, time_format)
        except (TypeError, ValueError):
            continue

        rs_min = rs.hour * 60 + rs.minute
        re_min = re.hour * 60 + re.minute

        # Auto-correct common PM entry without 24h conversion (01:15 -> 13:15).
        if rs_min < start_min and re_min <= start_min:
            pm_rs = rs_min + (12 * 60)
            pm_re = re_min + (12 * 60)
            if start_min <= pm_rs < end_min and pm_rs < pm_re <= end_min:
                rs_min, re_min = pm_rs, pm_re

        if not (start_min <= rs_min < end_min and rs_min < re_min <= end_min):
            continue

        key = (rs_min, re_min)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(key)

    normalized.sort(key=lambda x: x[0])

    return [
        [f"{start//60:02d}:{start%60:02d}", f"{end//60:02d}:{end%60:02d}"]
        for start, end in normalized
    ]

#============================================== timetable generation part

# problem: I changed it to return time in 24 hour format like 13.15 for 1.15 and also used string format instead of float
def calculate_1or_2hour_slots(hour_taken = 1,start_time_str="09:00", end_time_str="16:15", recess_list=[["11:00", "11:15"], ["13:15","14:15"]], time_format="%H:%M"):
    """returns a list of starting time of time slots for lectures based on start and end time and recess time"""
    hour_taken = int(hour_taken * 60)

    # Parse time strings into time objects
    start_time = datetime.strptime(start_time_str, time_format)
    end_time = datetime.strptime(end_time_str, time_format)
    
    normalized_recess = normalize_recess_windows(
        recess_list,
        start_time_str,
        end_time_str,
        time_format,
    )

    # Convert recess times to minutes
    recessmin = []
    for recess in normalized_recess:
        # strptime converts string to time data type
        recstart = datetime.strptime(recess[0], time_format).time() 
        recend = datetime.strptime(recess[1], time_format).time() 
        
        startmin = recstart.hour * 60 + recstart.minute
        endmin = recend.hour * 60 + recend.minute
        
        recessmin.append((startmin, endmin))  # Fixed: use tuple
    
    current_min = start_time.hour * 60 + start_time.minute
    end_min = end_time.hour * 60 + end_time.minute 
    slots = []
    
    while current_min + hour_taken <= end_min:  # Changed to <= to include boundary
        slot_start_min = current_min
        slot_end_min = current_min + hour_taken
        
        # Check if this slot overlaps with any recess period
        valid = True
        for recess_start, recess_end in recessmin:
            # Check for overlap: if slot overlaps with recess in any way
            if (slot_start_min < recess_end and slot_end_min > recess_start):
                valid = False
                # Skip to after the recess period
                current_min = recess_end
                break      
        if valid:
            # Convert minutes back to time format
            hour = int(slot_start_min // 60)
            minute = int(slot_start_min % 60)

            slot_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M")
            slots.append(slot_time.strftime(time_format))
            current_min += hour_taken  # Move to next hour
        # If not valid, current_min was already updated to recess_end
    return slots
    # float_slots = []
    # for each_value in slots:
    #     convert24hourformat = float(each_value.replace(":", "."))
    #     if convert24hourformat >=13:
    #         convert24hourformat = round(convert24hourformat, 2) # removed convert24hourformat - 12 <-

    #     float_slots.append(convert24hourformat)
    # logger.debug(float_slots)
    # # removing trailing zeros for ex. 10.0 to 10
    # custom_representation = []
    # for eachvalue in float_slots:
    #     if eachvalue.is_integer():
    #         custom_representation.append(int(eachvalue))
    #     else:
    #         custom_representation.append(eachvalue)
    # return custom_representation


def createData(department):
    year_data_all = {}
    for year in department.relatedNameYearSetupModel.all():
         year_key = year.year_name.lower().replace(" ", "_")
         year_data_all[year_key]= {}


         year_data_all[year_key]['total_students'] = year.total_students
         # accessing the number of days from department model
         num_of_week = year.department.number_of_days
         year_data_all[year_key]['num_of_week'] = num_of_week
         year_data_all[year_key]['weekDays_list'] = [i+1 for i in range(num_of_week)]  # i+1 becuase we need 1 based

        # time
         departmentSTARTTIME = year.department.start_time.strftime("%H:%M")
         departmentENDTIME = year.department.end_time.strftime("%H:%M")
         year_data_all[year_key]['start_time_str'] = departmentSTARTTIME
         year_data_all[year_key]['end_time_str'] = departmentENDTIME

         recess_list = []
         for each_recess in year.department.relatedNameRecesses.all():
                recess_list.append([
                    each_recess.recess_start_time.strftime("%H:%M"),
                    each_recess.recess_end_time.strftime("%H:%M")
                ])
         recess_list = normalize_recess_windows(
             recess_list,
             departmentSTARTTIME,
             departmentENDTIME,
         )
         year_data_all[year_key]['recess_list'] = recess_list

         pracHOURS = year.department.hours_in_practical 
         year_data_all[year_key]['each_practicalHours'] = pracHOURS
         # calculating practical time slots
         year_data_all[year_key]['practical_timeSlots_list'] = calculate_1or_2hour_slots(pracHOURS, departmentSTARTTIME, departmentENDTIME, recess_list  )

         practical_list = {}
         for practical in year.practicals.all():
             practical_list[practical.practical_name] = [practical.id, practical.hours_per_week, 0]
         year_data_all[year_key]['practical_list'] = practical_list

         practical_ability_list = {}
         for practical in year.practicals.all():
            practical_ability_list[practical.practical_name] = [
                teacher.teacher_name
                for teacher in practical.teachers.all()
             ]
         year_data_all[year_key]["practical_ability_list"] = practical_ability_list

         # one thing is i used django id for id and name is in string format insted of a number
         lab_rooms_list = {}
         for each_labroom in year.yearLabRoomsAllocated.labrooms.all(): # since we need years allocated labrooms
             lab_rooms_list[each_labroom.id] = [each_labroom.labroom_id, each_labroom.labroom_capacity]
         year_data_all[year_key]["lab_rooms_list"] = lab_rooms_list

         # calculating lecture time slots
         lectureHOURS = year.department.hours_in_lecture
         year_data_all[year_key]['each_lectureHours'] = lectureHOURS

         year_data_all[year_key]['lecture_timeSlots_list'] = calculate_1or_2hour_slots(lectureHOURS, departmentSTARTTIME, departmentENDTIME, recess_list)

         lecture_list = {}
         for each_subject in year.subjects.all():
            lecture_list[each_subject.subject_name] = [each_subject.hours_per_week]
         year_data_all[year_key]['lecture_list'] = lecture_list

         lecture_ability_list = {}
         for each_subject in year.subjects.all():
             lecture_ability_list[each_subject.subject_name] = [
                 teacher.teacher_name
                 for teacher in each_subject.teachers.all()
             ]
         year_data_all[year_key]['lecture_ability'] = lecture_ability_list
         # i used django id for id and name is in string format insted of a number
         lecture_rooms_list = {}
         for each_classroom in year.yearClassRoomsAllocated.classrooms.all(): # since we need years allocated labrooms
             lecture_rooms_list[each_classroom.id] = [each_classroom.classroom_id, each_classroom.classroom_capacity]
         year_data_all[year_key]['lecture_rooms_list'] = lecture_rooms_list


         # soft constaints key (not implemented yet), same as year name
         year_data_all[year_key]['soft_constraints_key'] = year_key

         year_data_all[year_key]['num_of_students_in_each_batch_practical'] = year.number_of_students_in_batch

    return year_data_all


from datetime import datetime, timedelta
# to generate time range list from start to end time of department year
def generate_time_range(
    hour_taken=1,
    start_time_str="09:00",
    end_time_str="16:15",
    recess_list=[["11:00", "11:15"], ["13:15", "14:15"]],
    time_format="%H:%M"
):
    hour_taken = int(hour_taken * 60)

    start_time = datetime.strptime(start_time_str, time_format)
    end_time = datetime.strptime(end_time_str, time_format)

    normalized_recess = normalize_recess_windows(
        recess_list,
        start_time_str,
        end_time_str,
        time_format,
    )

    # Convert recess times to minutes
    recessmin = []
    for r_start, r_end in normalized_recess:
        rs = datetime.strptime(r_start, time_format)
        re = datetime.strptime(r_end, time_format)
        recessmin.append((rs.hour * 60 + rs.minute, re.hour * 60 + re.minute))

    current_min = start_time.hour * 60 + start_time.minute
    end_min = end_time.hour * 60 + end_time.minute

    slots = []

    while current_min < end_min:

        # If current time is exactly a recess start → add recess
        for recess_start, recess_end in recessmin:
            if current_min == recess_start:
                slots.append(f"{recess_start//60:02d}:{recess_start%60:02d}")
                current_min = recess_end
                break
        else:
            slot_end_min = current_min + hour_taken

            # Check if slot crosses a recess
            crossed = False
            for recess_start, recess_end in recessmin:
                if current_min < recess_start < slot_end_min:
                    slots.append(f"{current_min//60:02d}:{current_min%60:02d}")
                    current_min = recess_start
                    crossed = True
                    break

            # Normal lecture slot
            if not crossed:
                if slot_end_min <= end_min:
                    slots.append(f"{current_min//60:02d}:{current_min%60:02d}")
                    current_min = slot_end_min
                else:
                    break

    return slots
# to check if a time is in list of recesses
def is_recess_time(time_str, recess_list, start_time_str=None, end_time_str=None):
    t = datetime.strptime(time_str, "%H:%M")

    normalized_recess = recess_list
    if start_time_str and end_time_str:
        normalized_recess = normalize_recess_windows(
            recess_list,
            start_time_str,
            end_time_str,
            "%H:%M",
        )

    for start, end in normalized_recess:
        rs = datetime.strptime(start, "%H:%M")
        re = datetime.strptime(end, "%H:%M")
        if rs <= t < re:
            return True

    return False



def combine_timetables(lecture_tt, practical_tt, year_data_all):
    """
        combine lecture and practical timetables into a single timetable

        None	           => Free period
        {type: "recess"}	=> Break
        {type: "lecture"}	=> Lecture
        {type: "practical"} => Practical
    """
    combined_tt = {}
    timeslot_ranges = generate_time_range(
        year_data_all[next(iter(year_data_all))]['each_lectureHours'],
        year_data_all[next(iter(year_data_all))]['start_time_str'],
        year_data_all[next(iter(year_data_all))]['end_time_str'],
        year_data_all[next(iter(year_data_all))]['recess_list']
    )


    for year_key in year_data_all.keys():
        combined_tt[year_key] = {}

        for day in year_data_all[year_key]['weekDays_list']:
            
            # creating empty day filled with lecture time slots and none value and recess if its recess time
            recess_list = year_data_all[year_key]['recess_list']
            combined_tt[year_key][day] = {}

            # for time in timeslot_ranges:
            for time in timeslot_ranges:
                if is_recess_time(
                    time,
                    recess_list,
                    year_data_all[year_key]['start_time_str'],
                    year_data_all[year_key]['end_time_str'],
                ):
                    combined_tt[year_key][day][time] = {
                        "type": "recess"
                    }
                else:
                    combined_tt[year_key][day][time] = None



        # lecture
        for day, day_data in lecture_tt.get(year_key, {}).items():

            for time_slot, lecture_info in day_data.items():

                if lecture_info is not None:
                    if time_slot in combined_tt[year_key][day]:
                        lecture_duration = year_data_all[year_key]["each_lectureHours"]  # usually 1

                        times = list(combined_tt[year_key][day].keys())
                        idx = times.index(time_slot)

                        for i in range(lecture_duration):
                            if idx + i < len(times):
                                if combined_tt[year_key][day][times[idx + i]] is None:
                                    combined_tt[year_key][day][times[idx + i]] = {
                                        "type": "lecture",
                                        "details": lecture_info
                                    }


        # practical (2 hours)
        for day, day_data in practical_tt[year_key].items():
            if day_data:
                for group in day_data:  # each group = list of batches
                    start_time = group[0]["slot"]

                    if start_time not in combined_tt[year_key][day]:
                        continue

                    times = list(combined_tt[year_key][day].keys())
                    idx = times.index(start_time)

                    practical_info = {
                        "type": "practical",
                        "batches": [
                            {
                                "batch": p["batch"],
                                "lab": p["lab"],
                                "faculty": p["faculty"],
                                "room": p["Room id"]
                            } for p in group
                        ]
                    }


                    practical_duration = year_data_all[year_key]["each_practicalHours"]  # eg: 2

                    for i in range(practical_duration):
                        if idx + i < len(times):
                            if combined_tt[year_key][day][times[idx + i]] is None:
                                combined_tt[year_key][day][times[idx + i]] = practical_info
    return combined_tt


# ok so my timetable is days and then timeslots in that day
# but for display i need timeslots and then days in that timeslot

def prepare_rows(combined_timetable, timeSlot_ranges):
    """Convert combined timetable into a format suitable for rendering in template."""
    result = {}

    for year, daysData in combined_timetable.items():
        rows = []
        day_numbers = list(daysData.keys())
        for time in timeSlot_ranges:
            row = {
                "time": time,
                "cells": []
            }

            for day in daysData.keys():
                row["cells"].append(daysData[day].get(time))

            rows.append(row)

        result[year] = {
            "days": [DAY_NAMES[d] for d in day_numbers],
            "rows": rows
        }

    return result


# had to bruteforce hours 
def calculate_hours_per_week(combined_timetable, year_data_all):
    stats = {}

    for year, days in combined_timetable.items():
        lecture_hours = defaultdict(int)
        practical_hours = defaultdict(lambda: defaultdict(int))
        teacher_hours = defaultdict(lambda: {
            "lecture": 0,
            "practical": 0,
            "total": 0
        })

        for day, timeslots in days.items():
            for time, cell in timeslots.items():
                if not cell or cell["type"] == "recess":
                    continue

                # ---------- LECTURE ----------
                if cell["type"] == "lecture":
                    details = cell["details"]
                    subject = details["lecture"]
                    teacher = details["teacher"]

                    # each slot = 1 hour
                    lecture_hours[subject] += 1
                    teacher_hours[teacher]["lecture"] += 1
                    teacher_hours[teacher]["total"] += 1

                # ---------- PRACTICAL ----------
                elif cell["type"] == "practical":
                    for batch in cell["batches"]:
                        practical_name = batch["lab"]
                        teacher = batch["faculty"]
                        batch_name = batch["batch"]

                        # each slot = 1 hour
                        practical_hours[practical_name][batch_name] += 1
                        teacher_hours[teacher]["practical"] += 1
                        teacher_hours[teacher]["total"] += 1

        # store stats ONCE per year
        stats[year] = {
            "lecture_hours": dict(lecture_hours),
            "practical_hours": {
                k: dict(v) for k, v in practical_hours.items()
            },
            "teacher_hours": dict(teacher_hours),
        }

    return stats


def prepare_lecture_hours_table(hours_stats, year_data_all):
    table_data = {}
    for year, stats in hours_stats.items():
        table_data[year] = []

        assigned = stats.get("lecture_hours", {})
        expected = year_data_all[year].get("lecture_list", {})

        for lecture_name, expected_data in expected.items():
            expected_hours = expected_data[0]  # hours_per_week
            assigned_hours = assigned.get(lecture_name, 0)

            table_data[year].append({
                "lecture": lecture_name,
                "expected": expected_hours,
                "assigned": assigned_hours,
                "match": expected_hours == assigned_hours
            })

    return table_data

def prepare_practical_hours_table(hours_stats, year_data_all):
    table_data = {}

    for year, stats in hours_stats.items():
        table_data[year] = []

        assigned_practicals = stats.get("practical_hours", {})
        expected_practicals = year_data_all[year].get("practical_list", {})

        # fallback batch count from year config
        default_batch_count = year_data_all[year].get(
            "num_of_students_in_each_batch_practical", 0
        )

        for practical_name, practical_info in expected_practicals.items():
            expected_hours = practical_info[1]  # hours per batch

            # Get batches that actually appeared in timetable
            assigned_batches = assigned_practicals.get(practical_name, {}).keys()

            # If none scheduled yet → generate batches from year config
            if assigned_batches:
                batch_names = sorted(assigned_batches)
            else:
                batch_names = [f"B{i+1}" for i in range(default_batch_count)]

            # Build rows
            for batch_name in batch_names:
                assigned_hours = (
                    assigned_practicals
                    .get(practical_name, {})
                    .get(batch_name, 0)
                )

                table_data[year].append({
                    "practical": practical_name,
                    "batch": batch_name,
                    "expected": expected_hours,
                    "assigned": assigned_hours,
                    "match": expected_hours == assigned_hours
                })

    return table_data


def prepare_teacher_vs_year_chart(hours_stats):

    teachers = set()
    year_data = {}
    teacher_totals = {}  # Track total hours per teacher
    teacher_details = {}  # Track detailed breakdown per teacher

    # collect all teachers and their hours
    for year, data in hours_stats.items():
        if "teacher_hours" in data and data["teacher_hours"]:
            for teacher, hours_info in data["teacher_hours"].items():
                teachers.add(teacher)
                # Initialize teacher totals if not exists
                if teacher not in teacher_totals:
                    teacher_totals[teacher] = 0
                    teacher_details[teacher] = {
                        'total_hours': 0,
                        'years': {},
                        'lecture_hours': 0,
                        'practical_hours': 0
                    }
                
                # Add hours to total
                total_hours = hours_info.get("total", 0)
                teacher_totals[teacher] += total_hours
                teacher_details[teacher]['total_hours'] += total_hours
                teacher_details[teacher]['years'][year] = total_hours
                teacher_details[teacher]['lecture_hours'] += hours_info.get("lecture", 0)
                teacher_details[teacher]['practical_hours'] += hours_info.get("practical", 0)

    teachers = sorted(teachers)

    # build year-wise dataset
    for year, data in hours_stats.items():
        totals = []
        for teacher in teachers:
            totals.append(
                data.get("teacher_hours", {}).get(teacher, {}).get("total", 0)
            )
        year_data[year] = totals
    
    # Workload analysis — thresholds are configurable via settings.py
    MIN_RECOMMENDED_HOURS = getattr(settings, 'TEACHER_WORKLOAD_MIN', 10)
    MAX_RECOMMENDED_HOURS = getattr(settings, 'TEACHER_WORKLOAD_MAX', 30)
    IDEAL_MIN_HOURS = getattr(settings, 'TEACHER_WORKLOAD_IDEAL_MIN', 15)
    IDEAL_MAX_HOURS = getattr(settings, 'TEACHER_WORKLOAD_IDEAL_MAX', 25)
    
    workload_analysis = {
        'overloaded': [],
        'underutilized': [],
        'balanced': [],
        'total_teachers': len(teachers),
        'avg_hours': sum(teacher_totals.values()) / len(teachers) if teachers else 0
    }
    
    teacher_workload_status = {}
    
    for teacher in teachers:
        total = teacher_totals.get(teacher, 0)
        
        if total > MAX_RECOMMENDED_HOURS:
            status = 'overloaded'
            workload_analysis['overloaded'].append({
                'name': teacher,
                'hours': total,
                'excess': total - MAX_RECOMMENDED_HOURS
            })
        elif total < MIN_RECOMMENDED_HOURS:
            status = 'underutilized'
            workload_analysis['underutilized'].append({
                'name': teacher,
                'hours': total,
                'deficit': MIN_RECOMMENDED_HOURS - total
            })
        else:
            status = 'balanced'
            if IDEAL_MIN_HOURS <= total <= IDEAL_MAX_HOURS:
                status = 'ideal'
            workload_analysis['balanced'].append({
                'name': teacher,
                'hours': total
            })
        
        teacher_workload_status[teacher] = {
            'status': status,
            'total_hours': total,
            'details': teacher_details[teacher]
        }
    
    return {
        "teachers": teachers,
        "years": year_data,
        "teacher_totals": teacher_totals,
        "teacher_workload_status": teacher_workload_status,
        "workload_analysis": workload_analysis,
        "thresholds": {
            'min': MIN_RECOMMENDED_HOURS,
            'max': MAX_RECOMMENDED_HOURS,
            'ideal_min': IDEAL_MIN_HOURS,
            'ideal_max': IDEAL_MAX_HOURS
        }
    }


