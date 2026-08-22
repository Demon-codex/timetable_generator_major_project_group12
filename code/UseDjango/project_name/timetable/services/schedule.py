
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
import random
import copy
import time
import numpy as np
from deap import base, creator, tools, algorithms

def run_full_timetable_scheduler(year_data_all):
    """
    Runs complete timetable scheduling:
    - Practical scheduling
    - Lecture scheduling (Genetic Algorithm)
    """


    """
    code works for different days to assign for each year
    also for different ammount of years

    """


    # dividing total students in class into batches as labs don't have the capacity
    def isLabEnoughForStudents(numberStudents, labCapacity):
        if numberStudents > labCapacity:
            return False # also return how many are left
        else:
            return True

    def mapBatchesToID(batches):
        """returns batch name and last roll number in that batch"""
        id = 1
        name = 'B'
        batchesList = {}
        for i in batches:
            batchesList[name+str(id)] = i
            id+=1
        return batchesList

    def divideIntoBatches(numberStudents, labCapacity):
        """returns batch list"""
        full_batches = numberStudents // labCapacity
        remainder = numberStudents % labCapacity
        batches = [labCapacity] * full_batches
        if remainder:
            batches.append(remainder)
        return mapBatchesToID(batches)

    def calculate_nof_practicalSlotPerWeek(practical_list, noOfHoursPerSlot = 2):
        # change if removed
        """returns no. of practical slots to be conducted in a week for a year"""
        total = 0
        for lab,lab_data in practical_list.items():
            total += lab_data[1]  # second value in the dictionary

        return total // noOfHoursPerSlot
    def generate_cartesian_product(base, length, totalPracticals):
        """returns list of possible combinations for no. of practicals in day for a week
        
        base = max practicals allowed in a day, 0 
        length = no. of days in week
        totalPracticals = total no. of practicals to be conducted in a week
        """
        totalValidCombinations = []
        total = base ** length
        for i in range(total):
            combo = []
            count = 0
            num = i
            for len in range(length):
                    number = num % base
                    combo.append(number)
                    count += number
                    if count > totalPracticals:  # i could add something that also filters out weird combinations so that practicals would be spread out (but i already limit it to base 3)
                        break
                    num //= base
                
            if count == totalPracticals:
                totalValidCombinations.append(combo)
        return totalValidCombinations



    def yearlyDayWiseUsedFaculty_LabRooms_Creation(timeSlots, DaysInWeek):
        """return a empty dictionary containing structure for occupied faculty & labs for all days and times"""
        yearlyDayWiseUsedFaculty_LabRooms = {}

        for i in range(1,len(DaysInWeek)+1):
            for time in timeSlots:
                tupleKey = (i,time)
                yearlyDayWiseUsedFaculty_LabRooms[tupleKey] = {"faculty": [], "labs": []}

        return yearlyDayWiseUsedFaculty_LabRooms

    def yearlyDayWiseUsedFaculty_LabRooms_Add(timetable_dict, tracker):
        """fill the dictionary containing structure for occupied faculty & labs for all days and times"""
        for day, outlist in timetable_dict.items():
            if not outlist:
                continue
            for eachSlot in outlist:
                for eachBatch in eachSlot:
                    tracker[(day,eachBatch["slot"])]["faculty"].append(eachBatch["faculty"])
                    tracker[(day,eachBatch["slot"])]["labs"].append(eachBatch["Room id"])
        return tracker

    class timetableInput:
        def __init__(self,practicalList ,practicalFacultyAbilityList,labRoomsList, timeSlots, week, softConstraints=None):
            self.practicalList = practicalList
            self.practicalFacultyAbilityList = practicalFacultyAbilityList
            self.labRoomsList = labRoomsList
            self.timeSlots = timeSlots
            self.week = week
            # to remove soft constraints
            # self.softConstraints = softConstraints

            self.batchPracticalCount = {} # reset bPC

    class scheduling:
        # class variables:
        good_list_faculty = None # place holders as time_list not initialised
        bad_list_faculty = None

        good_list_labs = None
        bad_list_labs = None

        @classmethod # tied to class and not instance
        def initialize_class_vars_goodbadlist(cls, soft_constraints, time_slots):
            """Initialize the faculty and lab soft constraints good bad list with time as key once(on first instance of the class)"""
            if cls.good_list_faculty is None or cls.bad_list_faculty is None:
                cls.good_list_faculty, cls.bad_list_faculty = cls.create_good_and_bad_maps_faculty_constraints(soft_constraints, time_slots)
            if cls.good_list_labs is None or cls.bad_list_labs is None:
                cls.good_list_labs, cls.bad_list_labs = cls.create_good_and_bad_maps_lab_constraints(soft_constraints,time_slots)


        @staticmethod
        def generate_one_batch_one_practical(practical_name, practical_faculty_name, time,batch, room_id):
            """Initialises and returns the dictioinary only for 1 batch and 1 slot"""
            return {
                'lab' : practical_name,
                'Room id' : room_id,
                'batch' : batch,
                'faculty' : practical_faculty_name,
                'slot' : time,        
            }
        @staticmethod
        def arrange_faculty_based_on_softconstraints(current_time,mapping_good, mapping_bad, faculty_list):
            "returns list of faculty arranged based on constraints if any and shuffles if none"

            if len(faculty_list) < 2:
                return faculty_list
            priority = set(mapping_good.get(current_time,[]))
            leastPriority = set(mapping_bad.get(current_time,[]))

            goodDream = []
            neutral = []
            nightMare = []
            for faculty in faculty_list:
                if faculty in priority:
                    goodDream.append(faculty)
                elif faculty in leastPriority:
                    nightMare.append(faculty)
                else:
                    neutral.append(faculty)
            # Categorize faculty
            categories = {
                'good': goodDream,
                'neutral': neutral,
                'bad': nightMare
            }
            # # Shuffle each category for fairness
            # for category in categories.values():
            #     random.shuffle(category)  
            # Return combined list in priority order
            return categories['good'] + categories['neutral'] + categories['bad']
        
        @staticmethod
        def arrange_labs_based_on_softconstraints(current_time,mapping_good, mapping_bad, practical_list):
            "returns list of faculty arranged based on constraints if any"
            priority = set(mapping_good.get(current_time,[]))
            leastPriority = set(mapping_bad.get(current_time,[]))
            # logger.debug(priority,leastPriority)
            goodDream = []
            neutral = []
            nightMare = []
            for practical in practical_list:
                # logger.debug(practical)  # Debug print
                if practical in priority:
                    goodDream.append(practical)
                elif practical in leastPriority:
                    nightMare.append(practical)
                else:
                    neutral.append(practical)
            # Categorize faculty
            categories = {
                'good': goodDream,
                'neutral': neutral,
                'bad': nightMare
            }

                # Shuffle each category for fairness
            for category in categories.values():
                if len(category) > 4:  # Only shuffle if there's more than one item changed from 2 to 4
                    random.shuffle(category)

            #Return combined list in priority order
            return categories['good'] + categories['neutral'] + categories['bad']
        

        
        @staticmethod
        def create_good_and_bad_maps_faculty_constraints(wish_list, time_list):
            """returns two dictionary with time as keys and list of faculty as values based on soft constraints"""
            good_times = {}
            bad_times = {}

            for time in time_list:
                good_times[time] = []
                bad_times[time] = []
                for person, data in wish_list["faculty"].items():
                
                    if time in data.get("TimeWanted",[]):
                        good_times[time].append(person)
                    elif time in data.get("TimeUnwanted",[]):
                        bad_times[time].append(person)     
            # logger.debug("good and bad list:",good_times,bad_times)
            # logger.debug("*"*20)
            return good_times, bad_times
        

        @staticmethod
        def create_good_and_bad_maps_lab_constraints(wish_list, time_list):
            """returns two dictionary with time as keys and list of faculty as values based on soft constraints of all years"""
            allyears_list = ["practical_fy","practical_ty","practical_sy"] # brute
            good_times = {}
            bad_times = {}
            for time in time_list:
                good_times[time] = []
                bad_times[time] = []
            for year_practical in allyears_list:
                for time in time_list:
                    for person, data in wish_list[year_practical].items():
                    
                        if time in data.get("TimeWanted",[]):
                            good_times[time].append(person)
                        elif time in data.get("TimeUnwanted",[]):
                            bad_times[time].append(person)     
            # logger.debug("good and bad list of labs:",good_times,bad_times)
            # logger.debug("*"*20)
            return good_times, bad_times
        

        def __init__(self, input_data: timetableInput, totalNoOfStudents, labCapacity, noOfWeekDays, totalPracticalsPerWeek):
            "takes timetableInput class, total no. of students, lab capacity, no of days in a week, total no of practicals to conduct for each batch in a week"
            self.practicalList = input_data.practicalList
            self.practicalFacultyAbilityList = input_data.practicalFacultyAbilityList
            self.labRoomsList = input_data.labRoomsList
            self.timeSlots = input_data.timeSlots
            self.week = input_data.week
            self.batchPracticalCount = input_data.batchPracticalCount
            # TO REMOVE Soft constraints 
            #self.softConstraints = input_data.softConstraints # soft constraints

            # Initialize class variables if not already done
            # TO REMOVE Soft constraints
            # scheduling.initialize_class_vars_goodbadlist(self.softConstraints, self.timeSlots)

            # calling external functions
            self.batchList = divideIntoBatches(totalNoOfStudents, labCapacity) 
            # Calculate max practicals per day from available time slots
            max_practicals_per_day = len(self.timeSlots)
            if max_practicals_per_day > 3:
                max_practicals_per_day = 3  # limit to 2 practicals per day
            self.allCombination = generate_cartesian_product(max_practicals_per_day,noOfWeekDays,totalPracticalsPerWeek) # changed from 3 to max practicals per day
            self.totalPracticalsPerWeek = totalPracticalsPerWeek
            
            # Add timeout tracking
            self.start_time = None
            self.max_runtime_seconds = 100  # 1 min 40 sec timeout per year
            self.attempt_count = 0
            self.max_total_attempts = 1000  # very important 100, changed from 400 to 1000 ***

        
    

        def is_timeout_reached(self):
            """Check if timeout has been reached"""
            if self.start_time is None:
                return False
            return (time.time() - self.start_time) > self.max_runtime_seconds

        # not used 
        def get_total_hours_needed(self):
            """Calculate total hours needed for all practicals"""
            total_hours = 0
            for practical, details in self.practicalList.items():
                total_hours += details[1]  # hours per week
            return total_hours

        def validate_timetable_completeness(self):
            """Check if all practicals have been scheduled completely"""
            for batch in self.batchList.keys():
                if batch not in self.batchPracticalCount:
                    return False
                
            
                for practical_name, details in self.practicalList.items():
                    required_hours = details[1]
                    if practical_name not in self.batchPracticalCount[batch]:
                        return False
                    
                    scheduled_hours = self.batchPracticalCount[batch][practical_name][0]
                    if scheduled_hours < required_hours:
                        return False
            return True
        # this is weird and i removed its use
        def get_scheduling_status(self):
            """Get current scheduling status for diagnostics"""
            status = {
                'total_batches': len(self.batchList),
                'scheduled_batches': 0,
                'partially_scheduled': 0,
                'unscheduled_batches': 0,
                'practical_completion': {}
            }
            
            for batch in self.batchList.keys():
                if batch not in self.batchPracticalCount:
                    status['unscheduled_batches'] += 1
                    continue
                    
                batch_scheduled = True
                batch_partial = False
                
                for practical_name, details in self.practicalList.items():
                    required_hours = details[1]
                    if practical_name not in self.batchPracticalCount[batch]:
                        batch_scheduled = False
                    else:
                        scheduled_hours = self.batchPracticalCount[batch][practical_name][0]
                        if scheduled_hours < required_hours:
                            batch_scheduled = False
                            if scheduled_hours > 0:
                                batch_partial = True
                                
                        # Track practical completion
                        if practical_name not in status['practical_completion']:
                            status['practical_completion'][practical_name] = {
                                'completed_batches': 0,
                                'partial_batches': 0,
                                'total_batches': len(self.batchList)
                            }
                        
                        if practical_name in self.batchPracticalCount[batch]:
                            if scheduled_hours >= required_hours:
                                status['practical_completion'][practical_name]['completed_batches'] += 1
                            elif scheduled_hours > 0:
                                status['practical_completion'][practical_name]['partial_batches'] += 1
                
                if batch_scheduled:
                    status['scheduled_batches'] += 1
                elif batch_partial:
                    status['partially_scheduled'] += 1
                else:
                    status['unscheduled_batches'] += 1
                    
            return status

        def assign_batch_practical(self, batch_index, batch_list, practical_list, practical_list_sorted, practical_faculty_list, 
                                lab_room_list, time, day, usedFacultyInSlot, usedLabRoomInSlot, 
                                current_assignments, yearly_used_faculty_lab):
            
            # Check timeout
            if self.is_timeout_reached():
                return False
                
            if yearly_used_faculty_lab == None:
                flag_forPastYear = False
            else:
                flag_forPastYear = True

            """Recursive backtracking helper for assigning one batch at a time."""
            # Base case: all batches assigned
            if batch_index == len(batch_list):
                return True  
            
            batch_actual_list = list(batch_list)
            batch = batch_actual_list[batch_index]

            # Initialize batch in batchPracticalCount if not present
            if batch not in self.batchPracticalCount:
                self.batchPracticalCount[batch] = {}
        

            # Try each practical for this batch
            for practical_name in practical_list_sorted:
                if practical_name not in self.batchPracticalCount[batch]:
                    self.batchPracticalCount[batch][practical_name] = [0, None, None]  # [hours, faculty, room]

                bpcData = list(self.batchPracticalCount[batch][practical_name])

                # Check if this practical still has hours left
                if bpcData[0] >= practical_list[practical_name][1]:
                    continue

                # ================== CASE 1: Faculty not assigned yet ===================
                if bpcData[1] is None:
                    faculty_candidates = practical_faculty_list.get(practical_name, [])
                    # to remove soft constraints, we dont arrange
                    # faculty_candidates1 = self.arrange_faculty_based_on_softconstraints(time, scheduling.good_list_faculty,scheduling.bad_list_faculty,faculty_candidates)
                    random.shuffle(faculty_candidates)  # shuffle as we removed soft constraints shuffling
                    

                    for faculty_name in faculty_candidates:
                        if faculty_name in usedFacultyInSlot:
                            continue  
                        # bruteforce check ****************************
                        if flag_forPastYear:
                            if faculty_name in yearly_used_faculty_lab[(day,time)]["faculty"]:
                                continue

                        # ================== CASE 1a: Lab not assigned yet ===================
                        if bpcData[2] is None:
                            room_id_keys = list(lab_room_list.keys())
                            random.shuffle(room_id_keys) # randomn

                            for room_id in room_id_keys:
                                # Check timeout before expensive operations
                                if self.is_timeout_reached():
                                    return False
                                    
                                # bruteforce check *************************************
                                if flag_forPastYear:
                                    if room_id in yearly_used_faculty_lab[(day,time)]["labs"]:
                                        continue

                                if room_id in usedLabRoomInSlot:
                                    continue
                                if batch_list[batch] > lab_room_list[room_id][1]:
                                    continue

                                # ---- Assign faculty + lab ----
                                self.batchPracticalCount[batch][practical_name][0] += 2
                                self.batchPracticalCount[batch][practical_name][1] = faculty_name
                                self.batchPracticalCount[batch][practical_name][2] = room_id
                                usedFacultyInSlot.add(faculty_name)
                                usedLabRoomInSlot.add(room_id)
                                # lab_room_list[room_id][0] to get room name from id as we dont want django by default id
                                gene = scheduling.generate_one_batch_one_practical(practical_name, faculty_name, time, batch, lab_room_list[room_id][0])
                                current_assignments.append(gene)

                                # Recurse
                                if self.assign_batch_practical(batch_index + 1, batch_list, practical_list, practical_list_sorted, practical_faculty_list, lab_room_list, time,day, usedFacultyInSlot, usedLabRoomInSlot, current_assignments, yearly_used_faculty_lab):
                                    return True  

                                # ---- Rollback ----
                                current_assignments.pop()
                                usedFacultyInSlot.remove(faculty_name)
                                usedLabRoomInSlot.remove(room_id)
                                self.batchPracticalCount[batch][practical_name][0] -= 2
                                self.batchPracticalCount[batch][practical_name][1] = None
                                self.batchPracticalCount[batch][practical_name][2] = None

                        else:
                            # ================== CASE 1b: Faculty None, Lab fixed ===================
                            room_id = bpcData[2]
                            if flag_forPastYear:
                                if room_id in yearly_used_faculty_lab[(day,time)]["labs"]:
                                    continue
                            if room_id in usedLabRoomInSlot:
                                continue

                            # ---- Assign faculty + reuse lab ----
                            self.batchPracticalCount[batch][practical_name][0] += 2
                            self.batchPracticalCount[batch][practical_name][1] = faculty_name
                            usedFacultyInSlot.add(faculty_name)
                            usedLabRoomInSlot.add(room_id)

                            gene = scheduling.generate_one_batch_one_practical(practical_name, faculty_name, time, batch, lab_room_list[room_id][0])

                            current_assignments.append(gene)

                            if self.assign_batch_practical(batch_index + 1, batch_list, practical_list,practical_list_sorted, practical_faculty_list, lab_room_list, time, day, usedFacultyInSlot, usedLabRoomInSlot, current_assignments, yearly_used_faculty_lab):
                                return True  

                            # ---- Rollback ----
                            current_assignments.pop()
                            usedFacultyInSlot.remove(faculty_name)
                            usedLabRoomInSlot.remove(room_id)
                            self.batchPracticalCount[batch][practical_name][0] -= 2
                            self.batchPracticalCount[batch][practical_name][1] = None

                else:
                    # ================== CASE 2: Faculty already assigned ===================
                    faculty_name = bpcData[1]
                    if flag_forPastYear:
                        if faculty_name in yearly_used_faculty_lab[(day,time)]["faculty"]:
                            continue
                    if faculty_name in usedFacultyInSlot:
                        continue  

                    # ================== CASE 2a: Lab not assigned yet ===================
                    
                    if bpcData[2] is None:
                        room_id_keys = list(lab_room_list.keys())
                        random.shuffle(room_id_keys) # randomn

                        for room_id in room_id_keys:
                            if self.is_timeout_reached():
                                return False
                                
                            if flag_forPastYear:
                                if room_id in yearly_used_faculty_lab[(day,time)]["labs"]:
                                    continue
                            if room_id in usedLabRoomInSlot:
                                continue
                            if batch_list[batch] > lab_room_list[room_id][1]:
                                continue

                            # ---- Assign reuse faculty + new lab ----
                            self.batchPracticalCount[batch][practical_name][0] += 2
                            self.batchPracticalCount[batch][practical_name][2] = room_id
                            usedFacultyInSlot.add(faculty_name)
                            usedLabRoomInSlot.add(room_id)

                            gene = scheduling.generate_one_batch_one_practical(practical_name, faculty_name, time, batch, lab_room_list[room_id][0])
                            current_assignments.append(gene)

                            if self.assign_batch_practical(batch_index + 1, batch_list, practical_list,practical_list_sorted, practical_faculty_list, lab_room_list, time, day, usedFacultyInSlot, usedLabRoomInSlot, current_assignments, yearly_used_faculty_lab):
                                return True  

                            # ---- Rollback ----
                            current_assignments.pop()
                            usedFacultyInSlot.remove(faculty_name)
                            usedLabRoomInSlot.remove(room_id)
                            self.batchPracticalCount[batch][practical_name][0] -= 2
                            self.batchPracticalCount[batch][practical_name][2] = None

                    else:
                        # ================== CASE 2b: Faculty + Lab both fixed ===================
                        room_id = bpcData[2]
                        if flag_forPastYear:
                            if room_id in yearly_used_faculty_lab[(day,time)]["labs"]:
                                continue
                        if room_id in usedLabRoomInSlot:
                            continue

                        # ---- Assign reuse faculty + reuse lab ----
                        self.batchPracticalCount[batch][practical_name][0] += 2
                        usedFacultyInSlot.add(faculty_name)
                        usedLabRoomInSlot.add(room_id)

                        gene = scheduling.generate_one_batch_one_practical(practical_name, faculty_name, time, batch, lab_room_list[room_id][0])

                        current_assignments.append(gene)

                        if self.assign_batch_practical(batch_index + 1, batch_list, practical_list, practical_list_sorted,practical_faculty_list, lab_room_list, time, day, usedFacultyInSlot, usedLabRoomInSlot, current_assignments, yearly_used_faculty_lab):
                            return True  

                        # ---- Rollback ----
                        current_assignments.pop()
                        usedFacultyInSlot.remove(faculty_name)
                        usedLabRoomInSlot.remove(room_id)
                        self.batchPracticalCount[batch][practical_name][0] -= 2

            return False  # no valid assignment found for this batch
        #passes daty, time and practical list sorted using soft constraints
        def generate_one_slot_assignment(self, time, day, pastData):
            """Try to generate assignment for one time slot"""
            individual = []
            usedFacultyInSlot = set()
            usedLabRoomInSlot = set()

            practical_list_keys_unsorted= list(self.practicalList.keys())
            # to remove soft constraints
            # arrange labs based on current time soft constraints
            # practical_list_sorted = self.arrange_labs_based_on_softconstraints(time, scheduling.good_list_labs,scheduling.bad_list_labs,practical_list_keys_unsorted)
            random.shuffle(practical_list_keys_unsorted) # shuffle as we removed soft constraints shuffling
            practical_list_sorted = practical_list_keys_unsorted


            success = self.assign_batch_practical(
                0, self.batchList, self.practicalList,practical_list_sorted, self.practicalFacultyAbilityList, 
                self.labRoomsList, time, day, usedFacultyInSlot, usedLabRoomInSlot, 
                individual, pastData
            )
            
            return individual if success else None

        # Creates the timetable for eaach day,time, no. of practicals on that day and passes day,time further to generate timetable
        def generate_timetable_iterative(self, pastData, combination):
            """Iterative approach to generate timetable for better control"""
            self.batchPracticalCount = {}
            timetable = {day: [] for day in self.week}
            
            max_global_attempts = 15  # very very important changed 200 to 10 ***********
            global_attempts = 0
            
            day_index = 0
            while day_index < len(combination) and global_attempts < max_global_attempts:
                global_attempts += 1
                self.attempt_count += 1
                
                # Check timeout and max attempts
                if self.is_timeout_reached() or self.attempt_count > self.max_total_attempts:
                    return None
                
                day = self.week[day_index]
                slots_needed = combination[day_index]
                
                # no practicals for that day
                if slots_needed == 0:
                    day_index += 1
                    continue
                
                # Save state before attempting this day
                saved_state = copy.deepcopy(self.batchPracticalCount)
                day_slots = []
                success = True
                
                # Try to fill required slots for this day
                for slot_idx in range(slots_needed):
                    slot_attempts = 0
                    max_slot_attempts = 50  # Reduced from 50 important
                    slot_found = False
                    
                    while slot_attempts < max_slot_attempts and not slot_found:
                        slot_attempts += 1
                        
                        if self.is_timeout_reached():
                            success = False
                            break
                        
                        # Try different times for this slot
                        available_times = self.timeSlots[:]

                        random.shuffle(available_times)
                        
                        for time in available_times:
                            # Check if this time is already used in this day
                            time_already_used = any(
                                slot and len(slot) > 0 and slot[0]['slot'] == time 
                                for slot in day_slots
                            )
                            if time_already_used:
                                continue
                                
                            slot_assignment = self.generate_one_slot_assignment(time, day, pastData)
                            if slot_assignment:
                                day_slots.append(slot_assignment)
                                slot_found = True
                                break

                    
                    if not slot_found:
                        success = False
                        break
                
                if success:
                    # Day completed successfully
                    timetable[day] = day_slots
                    day_index += 1
                else:
                    # Day failed, backtrack
                    self.batchPracticalCount = saved_state
                    timetable[day] = []
                    
                    if day_index > 0:
                        day_index -= 1
                        

                        # clear the previous assignment that caused the failure in current one
                        # timetable[self.week[day_index]] = []
                    else:
                        return None
            
            if global_attempts >= max_global_attempts:
                return None
                
            # Validate completeness
            if self.validate_timetable_completeness():
                return timetable
            else:
                return None

        def generate_timetable_with_backtracking(self, pastData, max_attempts=8): # changed max from 3 to 20
            """Generate timetable with iterative backtracking"""
            
            self.start_time = time.time()
            self.attempt_count = 0
            
            for attempt in range(max_attempts):
                if self.is_timeout_reached():
                    break
                    
                # Try different day combinations
                combinations = self.allCombination[:]
                random.shuffle(combinations) # random important
                
                # Limit combination attempts
                max_combinations_to_try = min(len(combinations), 10)  # no. of combinations to try: 2
                
                for combo_idx, combination in enumerate(combinations[:max_combinations_to_try]):
                    if self.is_timeout_reached():
                        break
                        
                    result = self.generate_timetable_iterative(pastData, combination)
                    
                    if result:
                        return result
                
            return None

    # a function that takes summation of no of practicals per week of all years and checks if it is more than total practical slots possible per week? would be helpful?

    # to remove soft constraints, removed third last argument softConstraints
    def timetableCreation(practicalList, practicalFacultyAbilityList, LabRoomsList, timeSlots, weekDays, totalStudents, labCapacity, noOfWeek, totalPracticalsPerWeek, pastData=None, max_attempts=3):
        """outputs final timetable for one year with enhanced backtracking"""

        # Quick feasibility check
        total_slots_needed = totalPracticalsPerWeek
        total_slots_available = len(timeSlots) * len(weekDays)
        
        if total_slots_needed > total_slots_available:
            return None
        
        for attempt in range(0,max_attempts+1):
            # to remove soft constraints, removed last argument softConstraints
            oneYearData = timetableInput(practicalList, practicalFacultyAbilityList, LabRoomsList, timeSlots, weekDays)
            OneYearschedule = scheduling(oneYearData, totalStudents, labCapacity, noOfWeek, totalPracticalsPerWeek)
            
            oneYearTimetable = OneYearschedule.generate_timetable_with_backtracking(pastData)
            
            if oneYearTimetable:
                return oneYearTimetable
        
        return None


    # idea: 123, 321, 213, 132,231 switch up allocation of years?
    # first
    def generate_complete_timetables(year_data, max_overall_attempts=5): #changed to 20
        """Generate complete timetables for all three years with inter-year backtracking"""
        
        start_time = time.time()

        # Determine scheduling order (you can customize this)
        year_order = list(year_data.keys())  # Default order

        
        for overall_attempt in range(0,max_overall_attempts+1):
            try:    
                all_year_timetables = {}

                # create a empty Tracker for used resources
                past_data = None 

                # Schedule years in the determined order
                for year_name in year_order:
                    year_info = year_data[year_name]


                    
                    # Create empty tracker for used resources if its empty
                    if past_data is None:
                        past_data = yearlyDayWiseUsedFaculty_LabRooms_Creation(
                            year_info["practical_timeSlots_list"], 
                            year_info["weekDays_list"]
                        )
                    # num of hours of practical to assign
                    NumHoursPractical = year_info["each_practicalHours"]
                    # no of total practicals
                    total_practicals = calculate_nof_practicalSlotPerWeek(year_info["practical_list"], NumHoursPractical)

                    # Generate timetable for this year
                    year_timetable = timetableCreation(
                        year_info["practical_list"],
                        year_info["practical_ability_list"],

                        year_info["lab_rooms_list"],
                        year_info["practical_timeSlots_list"],

                        year_info["weekDays_list"],
                        year_info["total_students"],
                        year_info["num_of_students_in_each_batch_practical"],
                        year_info["num_of_week"],
                        total_practicals,
                        # to remove soft constraints
                        # softConstraints,
                        past_data

                    )
                    if not year_timetable:
                        break

                    all_year_timetables[year_name] = year_timetable
                    past_data = yearlyDayWiseUsedFaculty_LabRooms_Add(year_timetable, past_data)

                # for else loop else condition executes only if we dont break from the loop
                else:
                    total_time = time.time() - start_time
                    return all_year_timetables, past_data
                
            except Exception as e:
                continue
        
        total_time = time.time() - start_time
        return None, None







    def check_if_practicalPossible(practicalList,practicalFacultyAbilityList, yearName, batchnum = 3):
        """"""
        numOfPracticalsInWeek = calculate_nof_practicalSlotPerWeek(practicalList)
        numOfTeachers = 0
        for labname, listOfTeachers in practicalFacultyAbilityList.items():
            
            num = len(listOfTeachers)
            numOfTeachers += num
            
        # condition 1: num of teachers >= no of batches
        if numOfTeachers >= batchnum:
            condition1 = True
        else:
            logger.debug(f"Num of teachers assigned to this {yearName} Practicals: {numOfTeachers} are less than num of batches: {batchnum}") 
            return False
        
        notValidList = []
        for labname, data in practicalList.items():
            teacherList = practicalFacultyAbilityList.get(labname)
            if teacherList:
                numTeacher = len(teacherList)
            else:
                logger.debug(f"{labname} does not have any teacher assigned")
                return False
            numLabPerWeek = data[1]//2
            # condtion 2: no. of teachers for a practical x num of practicals per week >=  no. of practicals of that lab x no. of batches
            if ((numTeacher*numOfPracticalsInWeek) < (numLabPerWeek * batchnum)):
                notValidList.append(labname)
            
        if notValidList:
            for i in notValidList:
                logger.debug(f"Assign more teachers to the practical: {i} or reduce its hours")
            return False
        
        return True

    def analyze_scheduling_feasibility(year_data):
        """Analyze if the given constraints can theoretically work for all years"""
        logger.debug(f"\n{'='*60}")
        logger.debug("FEASIBILITY ANALYSIS")
        logger.debug(f"{'='*60}")
        
        total_demand = 0
        all_faculty = set()
        faculty_load = {}
        
        # Calculate total demand and faculty requirements for all years
        for year_name, year_info in year_data.items():
            total_practicals = calculate_nof_practicalSlotPerWeek(
                year_info["practical_list"], 
                year_info["each_practicalHours"]
            )
            total_demand += total_practicals
            
            # Faculty analysis for this year
            batches = len(divideIntoBatches(
                year_info["total_students"], 
                year_info["num_of_students_in_each_batch_practical"]
            ))
            
            for practical, faculty_list in year_info["practical_ability_list"].items():
                for faculty in faculty_list:
                    all_faculty.add(faculty)
                    faculty_load[faculty] = faculty_load.get(faculty, 0) + total_practicals // len(year_info["practical_list"])
            
            # Check if practicals can be assigned for this year
            year_feasible = check_if_practicalPossible(
                year_info["practical_list"],
                year_info["practical_ability_list"],
                year_name,
                batches
            )
            
            if not year_feasible:
                logger.debug(f"{year_name} appears infeasible")
                return False
            else:
                logger.debug(f"{year_name} appears feasible")
        logger.debug(faculty_load)
        # Calculate total supply (using first year's time slots as reference)
        first_year = list(year_data.values())[0]
        total_supply = len(first_year["practical_timeSlots_list"]) * len(first_year["weekDays_list"]) * len(first_year["lab_rooms_list"])
        
        logger.debug(f"\nWeekly Capacity Analysis:")
        logger.debug(f"  Supply: {total_supply} time slots available")
        logger.debug(f"  Demand: {total_demand} practicals needed")
        logger.debug(f"  Utilization: {(total_demand/total_supply)*100:.1f}%")
        
        if total_demand > total_supply:
            logger.debug(f"⚠️  High utilization: Demand exceeds supply by {total_demand - total_supply} slots")
        
        # Faculty load analysis
        logger.debug(f"\nFaculty Analysis:")
        logger.debug(f"  Available faculty: {len(all_faculty)}")
        if faculty_load:
            max_load = max(faculty_load.values())
            logger.debug(f"  Maximum faculty load: {max_load} sessions/week")
        
        return True

    def display_detailed_timetable(complete_timetables):
        """Display detailed timetables with all information in a clean tabular format"""
        if not complete_timetables:
            logger.debug("No timetables to display!")
            return
        
        day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
        
        logger.debug("\n" + "="*100)
        logger.debug("DETAILED LAB TIMETABLES")
        logger.debug("="*100)
        
        for year_name, year_timetable in complete_timetables.items():
            logger.debug(f"\n{'='*40} {year_name.replace('_', ' ').title()} {'='*40}")
            
            for day in range(1, 6):  # Days 1-5
                day_slots = year_timetable.get(day, [])
                day_title = f"{day_names[day]}:"
                logger.debug(f"\n{day_title}")
                logger.debug("-" * 80)
                
                if not day_slots:
                    logger.debug("  No practical sessions")
                    continue
                    
                # Group slots by time for better display
                time_slots = {}
                for slot in day_slots:
                    if slot:  # Only process non-empty slots
                        time_key = slot[0]['slot']
                        if time_key not in time_slots:
                            time_slots[time_key] = []
                        time_slots[time_key].extend(slot)
                
                # Display each time slot
                for time_slot in sorted(time_slots.keys()):
                    sessions = time_slots[time_slot]
                    logger.debug(f"  Time: {time_slot}")
                    logger.debug("  " + "-" * 70)
                    logger.debug(f"    {'Batch':<6} {'Lab':<8} {'Faculty':<10} {'Room ID':<8} {'Room No.':<10}")
                    logger.debug("    " + "-" * 50)
                    
                    for session in sessions:
                        # Get room number from your lab_rooms_list
                        room_info = year_data_all[year_name]["lab_rooms_list"].get(
                            session['Room id'], ['Unknown', 0]
                        )
                        room_number = room_info[0]
                        
                        logger.debug(f"    {session['batch']:<6} {session['lab']:<8} "
                            f"{session['faculty']:<10} {session['Room id']:<8} {room_number:<10}")
                    logger.debug()

    def display_summary_table(complete_timetables):
        """Display a compact summary table format"""
        if not complete_timetables:
            logger.debug("No timetables to display!")
            return
            
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        logger.debug("\n" + "="*120)
        logger.debug("TIMETABLE SUMMARY - ALL YEARS")
        logger.debug("="*120)
        
        total_sessions = 0
        year_stats = {}
        
        for year_name, year_timetable in complete_timetables.items():
            logger.debug(f"\n{year_name.replace('_', ' ').upper()} TIMETABLE")
            logger.debug("=" * 80)
            logger.debug(f"{'Day':<12} {'Time':<8} {'Batch':<6} {'Lab':<8} {'Faculty':<10} {'Room':<10}")
            logger.debug("-" * 80)
            
            year_sessions = 0
            
            for day in range(1, 6):
                day_name = day_names[day-1]
                slots = year_timetable.get(day, [])
                
                if not slots:
                    continue
                    
                day_printed = False
                for slot_idx, slot in enumerate(slots):
                    if not slot:
                        continue
                        
                    time_slot = slot[0]['slot']
                    
                    for batch_data in slot:
                        year_sessions += 1
                        
                        # Get room number
                        room_info = year_data_all[year_name]["lab_rooms_list"].get(
                            batch_data['Room id'], ['Unknown', 0]
                        )
                        room_number = room_info[0]
                        
                        # Only show day name for first entry of the day
                        day_display = day_name if not day_printed else ""
                        logger.debug(f"{day_display:<12} {time_slot:<8} {batch_data['batch']:<6} "
                            f"{batch_data['lab']:<8} {batch_data['faculty']:<10} {room_number:<10}")
                        
                        day_printed = True
            
            year_stats[year_name] = year_sessions
            total_sessions += year_sessions
            logger.debug(f"\nTotal sessions for {year_name.replace('_', ' ').title()}: {year_sessions}")
        
        logger.debug(f"\n{'='*50}")
        logger.debug("OVERALL STATISTICS")
        logger.debug(f"{'='*50}")
        logger.debug(f"Total years scheduled: {len(complete_timetables)}")
        logger.debug(f"Total lab sessions scheduled: {total_sessions}")
        
        for year_name, sessions in year_stats.items():
            logger.debug(f"  {year_name.replace('_', ' ').title()}: {sessions} sessions")

    # Alternative function for a more compact view
    def display_compact_timetable(complete_timetables):
        """Display a very compact timetable view"""
        if not complete_timetables:
            logger.debug("No timetables to display!")
            return
        
        day_names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
        
        logger.debug("\n" + "="*80)
        logger.debug("COMPACT TIMETABLE VIEW")
        logger.debug("="*80)
        
        for year_name, year_timetable in complete_timetables.items():
            logger.debug(f"\n{year_name.upper()}:")
            logger.debug("Day | Time  | Sessions")
            logger.debug("-" * 30)
            
            for day in range(1, 6):
                slots = year_timetable.get(day, [])
                if not slots:
                    continue
                    
                # Count sessions per time slot
                time_summary = {}
                for slot in slots:
                    if slot:
                        time_key = slot[0]['slot']
                        time_summary[time_key] = time_summary.get(time_key, 0) + len(slot)
                
                for time_slot in sorted(time_summary.keys()):
                    logger.debug(f"{day_names[day]:<3} | {time_slot:<5} | {time_summary[time_slot]:>2} batch(es)")

    # You can also add this function to display by batches
    def display_by_batches(complete_timetables):
        """Display timetable organized by batches"""
        if not complete_timetables:
            logger.debug("No timetables to display!")
            return
        
        day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
        
        logger.debug("\n" + "="*80)
        logger.debug("BATCH-WISE SCHEDULE")
        logger.debug("="*80)
        
        for year_name, year_timetable in complete_timetables.items():
            logger.debug(f"\n{year_name.replace('_', ' ').upper()} - BATCH SCHEDULE:")
            
            # Collect all batches and their schedules
            batch_schedules = {}
            
            for day in range(1, 6):
                slots = year_timetable.get(day, [])
                for slot in slots:
                    for session in slot:
                        batch = session['batch']
                        if batch not in batch_schedules:
                            batch_schedules[batch] = []
                        
                        batch_schedules[batch].append({
                            'day': day,
                            'time': session['slot'],
                            'lab': session['lab'],
                            'faculty': session['faculty'],
                            'room': session['Room id']
                        })
            
            # Display each batch's schedule
            for batch in sorted(batch_schedules.keys()):
                logger.debug(f"\nBatch {batch}:")
                logger.debug("-" * 50)
                logger.debug(f"{'Day':<10} {'Time':<8} {'Lab':<8} {'Faculty':<10} {'Room':<6}")
                logger.debug("-" * 50)
                
                for session in sorted(batch_schedules[batch], key=lambda x: (x['day'], x['time'])):
                    logger.debug(f"{day_names[session['day']]:<10} {session['time']:<8} "
                        f"{session['lab']:<8} {session['faculty']:<10} {session['room']:<6}")




    # ============================================================================
    # PART 1 ENDS HERE - Practical scheduling classes and functions defined above
    # ============================================================================

    """
    PART 2: LECTURE SCHEDULING USING GENETIC ALGORITHM

    Based on the practical timetable generated in Part 1, this section assigns 
    lectures using a genetic algorithm approach with the DEAP framework.

    """








    class LectureSchedulingConfig:
        """Configuration class for lecture scheduling system"""
        
        def __init__(self, year_data_all, practical_timetable, practical_occupancy, map_teachers_to_serialNum):
            self.year_data_all = year_data_all
            self.practical_timetable = practical_timetable
            self.practical_occupancy = practical_occupancy
            self.map_teachers_to_serialNum = map_teachers_to_serialNum
            
            # Extract general configuration
            self._extract_general_data()
            
            # Calculate derived data
            self.list_ofTotalLecturesPerYear = self._calculate_total_lectures_per_year()
            self.remaining_practical_encoding = self._encode_practical_timetable()
            self.lecture_remaining_slots = self._make_lecture_slots_available()
            self.occupiedFacultyForPractical_matrix = self._create_faculty_occupancy_matrix()
        
        def _extract_general_data(self):
            """Extract general data from year data that is common across all years"""
            maxWeekDaysList = []
            for eachYearKey, Single_year_data_user in self.year_data_all.items():
                weekDaysList = Single_year_data_user.get("weekDays_list")
                if len(maxWeekDaysList) < len(weekDaysList):
                    maxWeekDaysList = weekDaysList
            
            for eachYearKey, Single_year_data_user in self.year_data_all.items():
                self.each_practical_hour = Single_year_data_user.get("each_practicalHours")
                self.each_lecture_hour = Single_year_data_user.get("each_lectureHours")

                # converting time to string 
                # self.practical_timeSlots_list = Single_year_data_user.get("practical_timeSlots_list")
                # self.lecture_timeslots_list = Single_year_data_user.get("lecture_timeSlots_list")

                # Convert all times to strings for consistency
                self.practical_timeSlots_list = [str(time) for time in Single_year_data_user.get("practical_timeSlots_list", [])]
                self.lecture_timeslots_list = [str(time) for time in Single_year_data_user.get("lecture_timeSlots_list", [])]
            

                
                # self.map_lectureSlotsTime_to_index = {time: idx for idx, time in enumerate(self.lecture_timeslots_list)}
                # self.map_index_to_lectureSlotsTime = {index: time for time, index in self.map_lectureSlotsTime_to_index.items()}
               # Create dictionaries with STRING keys
                self.map_lectureSlotsTime_to_index = {str(time): idx for idx, time in enumerate(self.lecture_timeslots_list)}
                self.map_index_to_lectureSlotsTime = {idx: str(time) for idx, time in enumerate(self.lecture_timeslots_list)}
                self.map_practicalSlotsTime_to_lectureSlotIndices = self._create_practical_to_lecture_slot_mapping()
                
                self.maxWeekDaysList = maxWeekDaysList
                self.numDays = len(maxWeekDaysList)
                self.numLengthLecture_timeslots = len(self.lecture_timeslots_list)
                self.numLengthTeachers = len(self.map_teachers_to_serialNum)
                break
        
        def _create_practical_to_lecture_slot_mapping(self):
            """Creates mapping between practical time slots and lecture slot indices"""
            slotsNeeded = self.each_practical_hour // self.each_lecture_hour
            mapping = {}
            for time in self.practical_timeSlots_list:
                startIndex = self.map_lectureSlotsTime_to_index[time]
                indices = [startIndex + i for i in range(slotsNeeded)]
                mapping[time] = indices
            return mapping
        
        def _calculate_total_lectures_per_year(self):
            """Returns total number of lectures to conduct per year"""
            calculation = {}
            for year_name, year_data in self.year_data_all.items():
                totalSessions = 0
                lecture_list = year_data.get("lecture_list", {})
                for subjectId, ListData in lecture_list.items():
                    numOfSessions = ListData[0] if ListData else 0
                    totalSessions += numOfSessions
                calculation[year_name] = totalSessions
            logger.debug("Total lectures per year:", calculation)
            return calculation
        
        def _encode_practical_timetable(self):
            """Encode practical timetable as binary strings per day"""
            slotPositions = {value: index for index, value in enumerate(self.practical_timeSlots_list)}
            numSlots = len(slotPositions)
            
            map_noOfSlots = {year_name: [] for year_name in self.practical_timetable.keys()}
            
            for year_name, year_data in self.practical_timetable.items():
                for day, day_data in year_data.items():
                    day_slots = [0] * numSlots
                    for session in day_data:
                        if session:
                            first_session = session[0]
                            time = first_session.get("slot")
                            if time in slotPositions:
                                day_slots[slotPositions[time]] = 1
                    map_noOfSlots[year_name].append("".join(str(x) for x in day_slots))
            return map_noOfSlots
       
        def _make_lecture_slots_available(self):
            """Calculate available lecture slots based on practical occupancy"""
            availableSlotsForLectures = {yearKey: [] for yearKey in self.remaining_practical_encoding.keys()}
            
            # Get ALL possible lecture slot indices first
            all_lecture_indices = set(range(len(self.lecture_timeslots_list)))
            
            for yearKey, ttList in self.remaining_practical_encoding.items():
                for eachDay in ttList:
                    occupied_indices = set()  # Track which indices are occupied by practicals
                    
                    # Find which lecture slot indices are occupied by practicals
                    for count, eachTimeSlot in enumerate(eachDay):
                        if eachTimeSlot == '1':  # FIXED: '1' means practical IS scheduled (OCCUPIED)
                            practicalTime = str(self.practical_timeSlots_list[count])
                            
                            # Get the lecture slot indices that would be blocked by this practical
                            if practicalTime in self.map_practicalSlotsTime_to_lectureSlotIndices:
                                blocked_indices = self.map_practicalSlotsTime_to_lectureSlotIndices[practicalTime]
                                occupied_indices.update(blocked_indices)
                    
                    # Available slots = all lecture slots MINUS occupied slots
                    available_indices = all_lecture_indices - occupied_indices
                    
                    # Convert available indices back to time strings
                    timeList = []
                    for index in sorted(available_indices):
                        timeList.append(str(self.map_index_to_lectureSlotsTime[index]))
                    
                    availableSlotsForLectures[yearKey].append(timeList)
            
            logger.debug(f"\n[DEBUG] Available lecture slots per day:")
            for yearKey, days_list in availableSlotsForLectures.items():
                logger.debug(f"  {yearKey}: {days_list[0] if days_list else 'EMPTY'}")
                logger.debug(f"    Total available slots: {sum(len(day) for day in days_list)}")
            
            return availableSlotsForLectures
        
        def _create_faculty_occupancy_matrix(self):
            """Create and fill faculty occupancy matrix for practicals"""
            matrix = np.zeros((self.numDays, self.numLengthLecture_timeslots, self.numLengthTeachers), dtype=bool)
            
            for (day, time), data in self.practical_occupancy.items():
                occupied_faculty = data["faculty"]
                encoded_occupied_faculty = [self.map_teachers_to_serialNum[f] for f in occupied_faculty]
                
                day_index = day - 1
                time_indices = self.map_practicalSlotsTime_to_lectureSlotIndices[time]
                
                for faculty_id in encoded_occupied_faculty:
                    faculty_index = faculty_id - 1
                    for time_index in time_indices:
                        matrix[day_index, time_index, faculty_index] = True
            
            return matrix
        
        def check_is_faculty_occupied(self, dayNum, timeSlotIndex, facultyNum):
            """Check if faculty is occupied at given day and time slot"""
            dayIndex = dayNum - 1
            facultyIndex = facultyNum - 1
            if (0 <= dayIndex < self.occupiedFacultyForPractical_matrix.shape[0] and 
                0 <= timeSlotIndex < self.occupiedFacultyForPractical_matrix.shape[1] and 
                0 <= facultyIndex < self.occupiedFacultyForPractical_matrix.shape[2]):
                return self.occupiedFacultyForPractical_matrix[dayIndex, timeSlotIndex, facultyIndex]
            return False


    def encodePracticalTimetable(practical_timetable, time_practical_list):
        """returns a dictionary of years and list which describes day,time where that year is busy
        000 => represents no lecture in 9, no lecture in 11.15, no lecture in 2.15
        and [000,001,001,110,100] represents days
        """
        # remember to give this code list of all time slots where practical could be assigned
        # Define slot positions for binary representation: 9: 0, 11.15: 1, 2.15: 2  
        slotPositions = {}
        for index, value in enumerate(time_practical_list):
            slotPositions[value] = index


        numSlots = len(slotPositions)

        # Initialize the mapping structure
        numbTimetables = len(practical_timetable)
        map_noOfSlots = {year_name:[] for year_name in practical_timetable.keys()}
        for year_name, year_data in practical_timetable.items():
            for day, day_data in year_data.items():
                day_slots = [0]*numSlots
                
                for session in day_data:
                    if session:  # Safety check
                        first_session = session[0] # All batches same time so extract first batch 
                        time = first_session.get("slot")  
                        if time not in slotPositions:
                            logger.debug(f"Warning: Slot {time} not found in time_practical_list for {year_name} Day {day}")
                            continue
                        # Mark slot busy
                        try:
                            day_slots[slotPositions[time]] = 1
                        except Exception as e:
                            logger.debug(f"⚠️ Error updating slot {time} for {year_name} Day {day}: {e}")
            
                map_noOfSlots[year_name].append("".join(str(x) for x in day_slots))
        return map_noOfSlots

    
    # Teacher id to serial number mapping:
    # map_teachers_to_serialNum = {
    #     'T1': 1, 'T2': 2, 'T3': 3, 'T4': 4, 'T5': 5, 'T6': 6, 'T7': 7, 'T8': 8, 'T9': 9, 'T10': 10, 'T11': 11, 'T12': 12, 'T13': 13, 'T14': 14
    # }
    # ===========================================================================================
    # NOTE: practical_timetable and practical_occupancy will be generated dynamically
    # by running the Part 1 scheduling algorithm in the main execution section





    def create_map_practicalSlotsTime_to_lectureSlotIndices(practicalNumHour,lectureNumHour, practical_timeSlots_list, map_lectureSlotsTime_to_index):
        """Creates a dictionary that tells what practical slot is equivalent to lecture slot index
        Returns:
            Dictionary {9: [0, 1], 11.15: [2, 3],..
        
        """
        slotsNeeded = practicalNumHour // lectureNumHour
        map_practicalSlotsTime_to_lectureSlotIndices = {}
        for time in practical_timeSlots_list:

            startIndex = map_lectureSlotsTime_to_index[time]
            index = []

            for numOfTimes in range(slotsNeeded):
                index.append(startIndex)
                startIndex += 1

            map_practicalSlotsTime_to_lectureSlotIndices[time] = index 
        return map_practicalSlotsTime_to_lectureSlotIndices

    def extract_GeneralDataFrom_Input_lectures(year_data_user):
        """
        Used for extracting general data that is same in all years for lecture assignment
        since the 
            1. start,end time, recess time would be same for all years 
            2. num of hours in each practical, lecture would also be same
            3. Week days also same for each year? problematic ***
            Therfore I Would Take this common data out from single year
        """

        # 1. we need to get max week days and return them which we would use to generate Faculty occupancy matrix
        # 2. we need to create a list of all lectures and lectureabilitylist
        maxWeekDaysList = []
        for eachYearKey, Single_year_data_user in year_data_user.items():
            weekDaysList = Single_year_data_user.get("weekDays_list")
            if len(maxWeekDaysList) < len(weekDaysList):
                maxWeekDaysList = weekDaysList
            
            


        for eachYearKey, Single_year_data_user in year_data_user.items():
            EachPracticalHour = Single_year_data_user.get("each_practicalHours")
            EachLectureHour = Single_year_data_user.get("each_lectureHours")
            #weekDaysList = Single_year_data_user.get("weekDays_list")
            
            # direct value: [9, 11.15, 2.15 ]
            practical_timeSlots_list = Single_year_data_user.get("practical_timeSlots_list")
            # direct value:[9, 10, 11.15, 12.15, 2.15, 3.15]
            lecture_timeslots_list = Single_year_data_user.get("lecture_timeSlots_list")

            # Map time values to their indices in lecture_timeslots_list: # index; {9: 0, 10: 1, 11.15: 2, 12.15: 3, 2.15: 4, 3.15: 5}
            map_lectureSlotsTime_to_index = {time: idx for idx, time in enumerate(lecture_timeslots_list)} 
            # Reverse {0: 9, 1: 10, 2: 11.15, 3: 12.15, 4: 2.15, 5: 3.15}
            map_index_to_lectureSlotsTime = {index: time for time, index in map_lectureSlotsTime_to_index.items()} 

            #Bruteforce possible: Define how practical times map to lecture slot indices {9: [0, 1]11.15: [2, 3], 2.15: [4, 5]}
            map_practicalSlotsTime_to_lectureSlotIndices = create_map_practicalSlotsTime_to_lectureSlotIndices(EachPracticalHour, EachLectureHour, practical_timeSlots_list, map_lectureSlotsTime_to_index)


            # run for only one year as all the years would be sharing these data, problamatic in dynamic time,day
            return EachPracticalHour, EachLectureHour, maxWeekDaysList, practical_timeSlots_list, lecture_timeslots_list, map_lectureSlotsTime_to_index, map_index_to_lectureSlotsTime, map_practicalSlotsTime_to_lectureSlotIndices




    def make_dictionary_for_LectureSlots_availabe(remainingEncodedDictionary_ofPractical, practical_timeSlotsList, map_practicalSlotsTime_to_lectureSlotIndices, map_index_to_lectureSlotsTime):
        """returns remaining lecture slots for each year and each day"""

        # availableSlotsForLectures = {i : [] for i in range(1,len
        # (remainingEncodedDictionary_ofPractical)+1)}
        
        availableSlotsForLectures = {}
        for yearKey in remainingEncodedDictionary_ofPractical.keys():
            availableSlotsForLectures[yearKey] = []


        for yearKey, ttList in remainingEncodedDictionary_ofPractical.items():
            for eachDay in ttList:
                count = 0
                timeList = []

                for eachTimeSlot in eachDay:
                    # no practical therefore calculate slots available for lectures
                    if eachTimeSlot == '0':
                        practicalTime = practical_timeSlotsList[count]
                        slotsAvailable = map_practicalSlotsTime_to_lectureSlotIndices[practicalTime]
                        
                        for index in slotsAvailable:
                            timeList.append(map_index_to_lectureSlotsTime[index])       
                    count += 1
                availableSlotsForLectures[yearKey].append(timeList)
        return availableSlotsForLectures

    def create_empty_faculty_occupancymatrix(dayNum = 5, lectureSlotsNum = 6, facultyNum = 14):
        """ create a numpy matrix filled with zeros"""
        matrix = np.zeros((dayNum, lectureSlotsNum, facultyNum), dtype=bool)
        return matrix


    def fill_faculty_occupancymatrix_practicals(practical_occupancy,faculty_occupancy, map_teachers_to_serialNum, map_practicalSlotsTime_to_lectureSlotIndices):
        """ returns a numpy matrix with True if the faculty is occupied:
        # Check if faculty T5 (index 5 but in matrix 4) is occupied on day 2 (Tuesday index 2 but in matrix 1), slot 1 (index 0 and matrix 0)
        is_occupied = faculty_occupancy[1, 0, 4]

        as index starts from 0
        """
        for (day,time) , data in practical_occupancy.items():
            logger.debug(data)

            occupied_faculty = data["faculty"]
            encoded_occupied_faculty = []
            for i in occupied_faculty:
                encodedFaculty = map_teachers_to_serialNum[i]
                encoded_occupied_faculty.append(encodedFaculty)

            # Convert day to 0-based index as matrix is 0 based
            day_index = day-1
            
            # Get the time slot indices for this practical time
            time_indices = map_practicalSlotsTime_to_lectureSlotIndices[time]


            for faculty_id in encoded_occupied_faculty:
                # Convert teacher ID to array index (subtract 1 since arrays are 0-indexed)
                faculty_index = faculty_id - 1
                for time_index in time_indices:
                    faculty_occupancy[day_index, time_index, faculty_index] = True

        return faculty_occupancy

    def check_is_faculty_occupiedInAPractical(dayNum, timeSlotIndex, facultyNum, occupiedFacultyForPractical):
        """
        day slot faculty
        """
        # day and faculty index starts from 1
        dayIndex = dayNum -1
        facultyIndex = facultyNum - 1
        if 0 <= dayIndex < occupiedFacultyForPractical.shape[0] and 0 <= timeSlotIndex < occupiedFacultyForPractical.shape[1] and 0 <= facultyIndex < occupiedFacultyForPractical.shape[2]:
         return occupiedFacultyForPractical[dayIndex, timeSlotIndex, facultyIndex]
        return False


    # ==================== PART 2: LECTURE SCHEDULING (OOP APPROACH) ====================

    class LectureChromosome:
        """Represents a chromosome for lecture scheduling genetic algorithm"""
        
        def __init__(self, config):
            self.config = config
            self.chromosome = {}
            self.classroom_assignments = {}
            self.previous_subject_teacher_mapping = {}
            self.classroom_occupancy = {}
            self._initialize()
        
        def _initialize(self):
            """Initialize chromosome with random valid assignments"""
            self._assign_classrooms()
            self._generate_random_assignments()
        
        def _assign_classrooms(self):
            """Assign classrooms to each year without conflicts"""
            usedClassrooms = set()
            year_names = list(self.config.year_data_all.keys())
            
            for year_name in year_names:
                year_data = self.config.year_data_all[year_name]
                total_students = year_data["total_students"]
                lecture_rooms_list = year_data["lecture_rooms_list"]
                
                # Find suitable classrooms not already assigned
                possibleClassroom_ids = [
                    room_id for room_id, room_data in lecture_rooms_list.items()
                    if room_data[1] >= total_students and room_id not in usedClassrooms
                ]
                
                if possibleClassroom_ids:
                    # Pick classroom with capacity closest to student count
                    classroom_id = min(possibleClassroom_ids, 
                                    key=lambda x: abs(lecture_rooms_list[x][1] - total_students))
                    self.classroom_assignments[year_name] = classroom_id
                    usedClassrooms.add(classroom_id)
                else:
                    # Fallback: find any available classroom from all years
                    all_available_rooms = []
                    for y_name in year_names:
                        y_data = self.config.year_data_all[y_name]
                        y_rooms = y_data["lecture_rooms_list"]
                        for room_id, room_data in y_rooms.items():
                            if room_data[1] >= total_students and room_id not in usedClassrooms:
                                all_available_rooms.append((room_id, room_data[1]))
                    
                    if all_available_rooms:
                        classroom_id = min(all_available_rooms, key=lambda x: x[1] - total_students)[0]
                        self.classroom_assignments[year_name] = classroom_id
                        usedClassrooms.add(classroom_id)
                    else:
                        # Last resort
                        all_rooms = [room_id for y_name in year_names 
                                for room_id in self.config.year_data_all[y_name]["lecture_rooms_list"].keys()]
                        self.classroom_assignments[year_name] = all_rooms[0] if all_rooms else None
        
        def _generate_random_assignments(self):

            year_names = list(self.config.year_data_all.keys())

            for year_name in year_names:

                year_data = self.config.year_data_all[year_name]
                self.chromosome[year_name] = {}

                lecture_list = year_data.get("lecture_list", {})
                lecture_ability = year_data.get("lecture_ability", {})
                available_days = self.config.lecture_remaining_slots.get(year_name, [])
                assigned_classroom = self.classroom_assignments.get(year_name)

                if not assigned_classroom:
                    continue

                # 1 Create EMPTY timetable first
                for day_index, day_list in enumerate(available_days, 1):
                    self.chromosome[year_name][day_index] = {}
                    for time in day_list:
                        self.chromosome[year_name][day_index][time] = None

                # 2 Collect all free slots
                free_slots = []
                for day_index, day_list in enumerate(available_days, 1):
                    for time in day_list:
                        free_slots.append((day_index, time))

                random.shuffle(free_slots)

                # 3️ Place EXACT required sessions
                for lecture, requirements in lecture_list.items():

                    required_sessions = requirements[0]
                    available_teachers = lecture_ability.get(lecture, [])

                    if not available_teachers:
                        continue

                    for _ in range(required_sessions):

                        if not free_slots:
                            break

                        day_index, time = free_slots.pop()

                        teacher = random.choice(available_teachers)

                        self.chromosome[year_name][day_index][time] = {
                            'lecture': lecture,
                            'teacher': teacher,
                            'classroom': assigned_classroom
                        }

        
        def _try_assign_lecture(self, year_name, day_index, time, lecture_list, 
                            lecture_ability, assigned_classroom, max_attempts=80):
            """Try to assign a lecture at given time slot"""
            # Check classroom occupancy
            if (day_index in self.classroom_occupancy and 
                time in self.classroom_occupancy[day_index] and
                assigned_classroom in self.classroom_occupancy[day_index][time]):
                return None
            
            for attempt in range(max_attempts):
                if not lecture_list:
                    break
                
                lecture = random.choice(list(lecture_list.keys()))
                
                # Get or assign teacher
                teacher = self.previous_subject_teacher_mapping[year_name].get(lecture)
                if not teacher:
                    available_teachers = lecture_ability.get(lecture, [])
                    if not available_teachers:
                        continue
                    teacher = random.choice(available_teachers)
                
                # Check faculty availability
                time_slot_index = self.config.map_lectureSlotsTime_to_index[time]
                teacher_serial_num = self.config.map_teachers_to_serialNum[teacher]
                
                if self.config.check_is_faculty_occupied(day_index, time_slot_index, teacher_serial_num):
                    continue
                
                # Valid assignment found
                assignment = {
                    'lecture': lecture,
                    'teacher': teacher,
                    'classroom': assigned_classroom
                }
                
                # Update tracking
                if day_index not in self.classroom_occupancy:
                    self.classroom_occupancy[day_index] = {}
                if time not in self.classroom_occupancy[day_index]:
                    self.classroom_occupancy[day_index][time] = set()
                self.classroom_occupancy[day_index][time].add(assigned_classroom)
                
                self.previous_subject_teacher_mapping[year_name][lecture] = teacher
                return assignment
            
            return None
        
        def get_chromosome(self):
            """Return the chromosome data structure"""
            return self.chromosome
        
        def get_classroom_assignments(self):
            """Return classroom assignments"""
            return self.classroom_assignments


    def chromosomeCreation(year_data_all, lectureRemainingSlots, occupiedFacultyForPractical_matrix, list_ofTotalLecturesPerYear, map_lectureSlotsTime_to_index, map_teachers_to_serialNum):
        """
        Create chromosome for genetic algorithm based on your data structure
        
        Parameters:
            year_data_all: Main data structure containing all year information
            lectureRemainingSlots: Available lecture slots for each year
            occupiedFacultyForPractical_matrix: Faculty occupancy matrix
            list_ofTotalLecturesPerYear: Total lectures to assign per year
            map_lectureSlotsTime_to_index: Mapping from time to slot index
            map_teachers_to_serialNum: Mapping from teacher ID to serial number
        """
        chromosome = {}
        previousData = {}
        classRoomAssigned = {}
        usedClassrooms = set()  # Track assigned classrooms to prevent clashes

        # Create year name to index mapping for consistent access
        year_names = list(year_data_all.keys())
        year_name_to_index = {name: idx for idx, name in enumerate(year_names)}
        
        # Initialize previousData structure
        for year_name in year_names:
            previousData[year_name] = {}

        # Assign classrooms for each year (without clashes)
        for year_name in year_names:
            year_data = year_data_all[year_name]
            total_students = year_data["total_students"]
            lecture_rooms_list = year_data["lecture_rooms_list"]
            
            # Find suitable classrooms for this year that are not already assigned
            possibleClassroom_ids = []
            for room_id, room_data in lecture_rooms_list.items():
                room_capacity = room_data[1]  # Second element is capacity
                if room_capacity >= total_students and room_id not in usedClassrooms:
                    possibleClassroom_ids.append(room_id)
            
            if possibleClassroom_ids:
                # Pick classroom with capacity closest to student count
                classroom_id = min(possibleClassroom_ids, 
                                key=lambda x: abs(lecture_rooms_list[x][1] - total_students))
                classRoomAssigned[year_name] = classroom_id
                usedClassrooms.add(classroom_id)  # Mark as used
                logger.debug(f"Assigned classroom {classroom_id} to {year_name}")
            else:
                # Fallback: try to find any available classroom from all years
                all_available_rooms = []
                for y_name in year_names:
                    y_data = year_data_all[y_name]
                    y_rooms = y_data["lecture_rooms_list"]
                    for room_id, room_data in y_rooms.items():
                        if room_data[1] >= total_students and room_id not in usedClassrooms:
                            all_available_rooms.append(room_id)
                
                if all_available_rooms:
                    classroom_id = min(all_available_rooms, 
                                    key=lambda x: get_room_capacity(x, year_data_all) - total_students)
                    classRoomAssigned[year_name] = classroom_id
                    usedClassrooms.add(classroom_id)
                    logger.debug(f"Assigned shared classroom {classroom_id} to {year_name}")
                else:
                    # Last resort: use first room (this will cause clash but avoids crash)
                    all_rooms = []
                    for y_name in year_names:
                        all_rooms.extend(list(year_data_all[y_name]["lecture_rooms_list"].keys()))
                    if all_rooms:
                        classRoomAssigned[year_name] = all_rooms[0]
                        logger.debug(f"Warning: Classroom clash - assigned room {all_rooms[0]} to {year_name}")
                    else:
                        classRoomAssigned[year_name] = None
                        logger.debug(f"Error: No classrooms available for {year_name}")

        # Track classroom usage by day and time to prevent same classroom being used simultaneously
        classroom_occupancy = {}  # Format: {(day, time): set_of_occupied_classrooms}

        # Loop through all years
        for year_name in year_names:
            year_data = year_data_all[year_name]
            chromosome[year_name] = {}
            
            # Get lecture list and ability list for this year
            lecture_list = year_data.get("lecture_list", {})
            lecture_ability = year_data.get("lecture_ability", {})
            
            # Get available days for this year
            available_days = lectureRemainingSlots.get(year_name, [])
            
            # Get assigned classroom for this year
            assigned_classroom = classRoomAssigned.get(year_name)
            if not assigned_classroom:
                logger.debug(f"Warning: No classroom assigned for {year_name}, skipping assignments")
                continue
            
            # Loop through available days (1-indexed)
            for day_index, day_list in enumerate(available_days, 1):
                if not day_list:
                    continue
                    
                chromosome[year_name][day_index] = {}
                
                # Initialize classroom occupancy for this day if not exists
                if day_index not in classroom_occupancy:
                    classroom_occupancy[day_index] = {}
                
                # Loop through available time slots for this day
                for time in day_list:
                    practicalClash = True
                    max_attempts = 80  # Increased attempts due to additional constraints
                    currentAttempt = 0
                    time_str = str(time)  # Ensure time is string for mapping
                    
                    # Check if classroom is already occupied at this (day, time)
                    classroom_occupied = False
                    if day_index in classroom_occupancy and time in classroom_occupancy[day_index]:
                        if assigned_classroom in classroom_occupancy[day_index][time]:
                            classroom_occupied = True
                    
                    while practicalClash and currentAttempt <= max_attempts and not classroom_occupied:
                        currentAttempt += 1
                        
                        # Pick a random subject from this year
                        if not lecture_list:
                            break
                        lecture = random.choice(list(lecture_list.keys()))
                        
                        # If teacher already assigned for this subject
                        teacher = previousData.get(year_name, {}).get(lecture, None)
                        if not teacher:
                            # Pick a random teacher that can teach this subject
                            available_teachers = lecture_ability.get(lecture, [])
                            if not available_teachers:
                                continue
                            teacher = random.choice(available_teachers)
                        
                        # Check if teacher is occupied in practical at this time
                        time_slot_index = map_lectureSlotsTime_to_index[time_str]
                        teacher_serial_num = map_teachers_to_serialNum[teacher]
                        
                        occupied = check_is_faculty_occupiedInAPractical(
                            day_index, 
                            time_slot_index, 
                            teacher_serial_num, 
                            occupiedFacultyForPractical_matrix
                        )
                        
                        if occupied:
                            continue
                        
                        # Assign lecture to time slot - this is one gene
                        chromosome[year_name][day_index][time] = {
                            'lecture': lecture,
                            'teacher': teacher,
                            'classroom': assigned_classroom
                        }
                        
                        # Update classroom occupancy
                        if day_index not in classroom_occupancy:
                            classroom_occupancy[day_index] = {}
                        if time not in classroom_occupancy[day_index]:
                            classroom_occupancy[day_index][time] = set()
                        classroom_occupancy[day_index][time].add(assigned_classroom)
                        
                        # Store the subject => teacher mapping for later assignments
                        previousData[year_name][lecture] = teacher
                        practicalClash = False
                    
                    # If couldn't assign after max attempts or classroom occupied, leave as None
                    if practicalClash or classroom_occupied:
                        chromosome[year_name][day_index][time] = None
                        if classroom_occupied:
                            logger.debug(f"Classroom {assigned_classroom} occupied at Day {day_index}, Time {time} for {year_name}")

        logger.debug("\nGenerated Chromosome:")
        logger.debug("Classroom Assignments:", classRoomAssigned)
        for year_name, year_data in chromosome.items():
            assigned_count = 0
            for day, day_assignments in year_data.items():
                for time, assignment in day_assignments.items():
                    if assignment is not None:
                        assigned_count += 1
            
            logger.debug(f"{year_name}: {assigned_count} assignments across {len(year_data)} days")
            for day, day_assignments in year_data.items():
                day_assign_count = sum(1 for assignment in day_assignments.values() if assignment is not None)
                logger.debug(f"  Day {day}: {day_assign_count}/{len(day_assignments)} time slots assigned")
        
        return chromosome, classRoomAssigned

    def get_room_capacity(room_id, year_data_all):
        """Helper function to get room capacity from any year's room list"""
        for year_name, year_data in year_data_all.items():
            lecture_rooms = year_data.get("lecture_rooms_list", {})
            if room_id in lecture_rooms:
                return lecture_rooms[room_id][1]
        return 0


    class LectureGeneticAlgorithm:
        """Genetic Algorithm for lecture scheduling optimization"""
        
        def __init__(
            self,
            config,
            pop_size=30,
            generations=50,
            cxpb=0.7,
            mutpb=0.2,
            min_generations=30,
            stagnation_patience=15,
            fitness_tolerance=1e-6,
            verbose=False,
        ):
            self.config = config
            self.pop_size = pop_size
            self.generations = generations
            self.cxpb = cxpb  # Crossover probability
            self.mutpb = mutpb  # Mutation probability
            self.min_generations = min_generations
            self.stagnation_patience = stagnation_patience
            self.fitness_tolerance = fitness_tolerance
            self.verbose = verbose
            self.toolbox = None
            self.best_solution = None
            self.best_fitness = 0
            self.logbook = None
            
            self._setup_deap()
        
        def _setup_deap(self):
            """Setup DEAP genetic algorithm components"""
            # Create fitness and individual classes if not already created
            if not hasattr(creator, "FitnessMax"):
                creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            if not hasattr(creator, "Individual"):
                creator.create("Individual", dict, fitness=creator.FitnessMax)
            
            # Initialize toolbox
            self.toolbox = base.Toolbox()
            
            # Register individual and population creation
            self.toolbox.register("individual", tools.initIterate, creator.Individual,
                                lambda: self._create_individual())
            self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
            
            # Register genetic operators
            self.toolbox.register("evaluate", self._evaluate_fitness)
            self.toolbox.register("mate", self._crossover)
            self.toolbox.register("mutate", self._mutate, indpb=0.1)
            self.toolbox.register("select", tools.selTournament, tournsize=3)
        
        def _create_individual(self):
            """Create an individual chromosome"""
            lecture_chromosome = LectureChromosome(self.config)
            individual = lecture_chromosome.get_chromosome()
            self._repair_individual_counts(individual)
            return individual

        def _is_teacher_busy_in_lectures(self, individual, day, time, teacher, exclude_slot=None):
            """Check if a teacher is already assigned in lecture timetable at the same day/time."""
            for year_name, year_schedule in individual.items():
                if day not in year_schedule:
                    continue
                assignment = year_schedule[day].get(time)
                if assignment is None:
                    continue
                if exclude_slot and (year_name, day, time) == exclude_slot:
                    continue
                if assignment.get("teacher") == teacher:
                    return True
            return False

        def _pick_default_classroom(self, year_name):
            """Pick a stable classroom for a year if no assignment exists yet."""
            year_data = self.config.year_data_all.get(year_name, {})
            lecture_rooms_list = year_data.get("lecture_rooms_list", {})
            total_students = year_data.get("total_students", 0)

            suitable_rooms = [
                room_id for room_id, room_data in lecture_rooms_list.items()
                if room_data[1] >= total_students
            ]

            if suitable_rooms:
                return min(suitable_rooms, key=lambda x: abs(lecture_rooms_list[x][1] - total_students))

            return next(iter(lecture_rooms_list.keys()), None)

        def _repair_individual_counts(self, individual):
            """Repair subject counts so each year is as close as possible to exact requirements."""
            for year_name, year_data in self.config.year_data_all.items():
                year_schedule = individual.get(year_name)
                if not year_schedule:
                    continue

                lecture_list = year_data.get("lecture_list", {})
                lecture_ability = year_data.get("lecture_ability", {})

                required_counts = {
                    lecture: requirements[0]
                    for lecture, requirements in lecture_list.items()
                }

                assigned_positions = {}
                empty_slots = []
                classroom = None

                for day, day_schedule in year_schedule.items():
                    for time, assignment in day_schedule.items():
                        if assignment is None:
                            empty_slots.append((day, time))
                            continue

                        if classroom is None:
                            classroom = assignment.get("classroom")

                        lecture_name = assignment.get("lecture")
                        if lecture_name not in assigned_positions:
                            assigned_positions[lecture_name] = []
                        assigned_positions[lecture_name].append((day, time))

                if classroom is None:
                    classroom = self._pick_default_classroom(year_name)

                # 1) Remove overflow assignments first.
                for lecture_name, positions in list(assigned_positions.items()):
                    required = required_counts.get(lecture_name, 0)
                    overflow = max(0, len(positions) - required)

                    if overflow <= 0:
                        continue

                    random.shuffle(positions)
                    for _ in range(overflow):
                        if not positions:
                            break
                        day, time = positions.pop()
                        year_schedule[day][time] = None
                        empty_slots.append((day, time))

                # Refresh post-overflow counts.
                current_counts = {
                    lecture_name: len([
                        1 for _, day_schedule in year_schedule.items()
                        for _, assignment in day_schedule.items()
                        if assignment is not None and assignment.get("lecture") == lecture_name
                    ])
                    for lecture_name in required_counts.keys()
                }

                # 2) Fill missing assignments into empty slots if teacher constraints permit.
                random.shuffle(empty_slots)

                for lecture_name, required in required_counts.items():
                    missing = max(0, required - current_counts.get(lecture_name, 0))
                    if missing <= 0:
                        continue

                    available_teachers = lecture_ability.get(lecture_name, [])
                    if not available_teachers:
                        continue

                    for _ in range(missing):
                        placed = False

                        random.shuffle(empty_slots)
                        random_teachers = list(available_teachers)
                        random.shuffle(random_teachers)

                        for idx, (day, time) in enumerate(empty_slots):
                            time_slot_index = self.config.map_lectureSlotsTime_to_index[str(time)]

                            for teacher in random_teachers:
                                teacher_serial = self.config.map_teachers_to_serialNum[teacher]

                                if self.config.check_is_faculty_occupied(day, time_slot_index, teacher_serial):
                                    continue

                                if self._is_teacher_busy_in_lectures(individual, day, time, teacher):
                                    continue

                                year_schedule[day][time] = {
                                    "lecture": lecture_name,
                                    "teacher": teacher,
                                    "classroom": classroom,
                                }
                                empty_slots.pop(idx)
                                placed = True
                                break

                            if placed:
                                break

                        if not placed:
                            break


        def calculate_gap_penalty(self, binary_day_slots):

            if 1 not in binary_day_slots:
                return 0

            first = binary_day_slots.index(1)
            last = len(binary_day_slots) - 1 - binary_day_slots[::-1].index(1)

            gap_count = 0

            for i in range(first, last):
                if binary_day_slots[i] == 0:
                    gap_count += 1

            return gap_count

        def _evaluate_fitness(self, individual):
            """
            Conflict-aware fitness evaluation.
            Hard constraints are heavily penalized.
            Soft constraints guide optimization.
            """

            total_possible_slots = 0
            total_assignments = 0

            teacher_time_usage = {}   # (day, time) -> teacher
            room_time_usage = {}      # (day, time) -> classroom
            teacher_workload = {}
            subject_coverage = {}

            hard_penalty = 0
            gap_penalty = 0

            # ==================================================
            # 1️⃣ Scan entire timetable and detect conflicts
            # ==================================================
            for year_name, year_schedule in individual.items():

                subject_coverage[year_name] = {}

                for day, day_schedule in year_schedule.items():

                    daily_binary = []  # for gap calculation

                    ordered_times = sorted(
                        day_schedule.keys(),
                        key=lambda t: self.config.map_lectureSlotsTime_to_index[str(t)]
                    )

                    for time in ordered_times:
                        assignment = day_schedule[time]

                        total_possible_slots += 1

                        if assignment is None:
                            daily_binary.append(0)
                            continue

                        daily_binary.append(1)
                        total_assignments += 1

                        teacher = assignment['teacher']
                        lecture = assignment['lecture']
                        classroom = assignment['classroom']

                        key = (day, time)

                        # -------------------------------
                        # HARD 1: Teacher clash (ALL years)
                        # -------------------------------
                        if key not in teacher_time_usage:
                            teacher_time_usage[key] = {}

                        if teacher in teacher_time_usage[key]:
                            hard_penalty += 20  # stronger penalty
                        else:
                            teacher_time_usage[key][teacher] = year_name

                        # -------------------------------
                        # HARD 2: Classroom clash
                        # -------------------------------
                        if key not in room_time_usage:
                            room_time_usage[key] = {}

                        if classroom in room_time_usage[key]:
                            hard_penalty += 20
                        else:
                            room_time_usage[key][classroom] = year_name

                        # -------------------------------
                        # HARD 3: Teacher practical clash
                        # -------------------------------
                        time_slot_index = self.config.map_lectureSlotsTime_to_index[str(time)]
                        teacher_serial = self.config.map_teachers_to_serialNum[teacher]

                        if self.config.check_is_faculty_occupied(
                                day,
                                time_slot_index,
                                teacher_serial):
                            hard_penalty += 20

                        # Track workload
                        teacher_workload[teacher] = teacher_workload.get(teacher, 0) + 1

                        # Track subject coverage
                        subject_coverage[year_name][lecture] = \
                            subject_coverage[year_name].get(lecture, 0) + 1

                    # -------------------------------
                    # SOFT 1: Gap penalty per day
                    # -------------------------------
                    gap_penalty += self.calculate_gap_penalty(daily_binary)

            # ==================================================
            # 2️⃣ Soft Objective: Workload Balance
            # ==================================================
            if teacher_workload:
                workloads = list(teacher_workload.values())
                workload_std = np.std(workloads)
                workload_score = 1 / (1 + workload_std)
            else:
                workload_score = 0

            # ==================================================
            # 3️⃣ Soft Objective: Subject Requirement Matching
            # ==================================================
            requirement_score = 0
            requirement_count = 0
            over_allocation_penalty = 0

            for year_name, year_data in self.config.year_data_all.items():

                lecture_list = year_data.get("lecture_list", {})
                year_subjects = subject_coverage.get(year_name, {})

                for subject, requirements in lecture_list.items():

                    required_sessions = requirements[0]
                    actual_sessions = year_subjects.get(subject, 0)

                    if required_sessions > 0:

                        diff = actual_sessions - required_sessions

                        # Hard-ish penalty for over allocation
                        if diff > 0:
                            over_allocation_penalty += diff * 10

                        abs_diff = abs(diff)
                        requirement_score += 1 / (1 + abs_diff)
                        requirement_count += 1

            if requirement_count > 0:
                requirement_score /= requirement_count
            else:
                requirement_score = 0

            # ==================================================
            # 4️⃣ Combine Soft Objectives
            # ==================================================
            soft_score = (
                0.6 * requirement_score +
                0.1 * workload_score +
                0.3 * (1 / (1 + gap_penalty))   # smaller gaps → higher score
            )

            # ==================================================
            # 5️⃣ Apply Hard Penalties
            # ==================================================
            # total_fitness = (
            #     soft_score
            #     - (hard_penalty * 0.8)
            #     - (over_allocation_penalty * 0.5)
            # )

            # return total_fitness,
    
            if hard_penalty > 0:
                return -1000 - hard_penalty,
            else:
                return soft_score - (over_allocation_penalty * 0.1),

        
        # def _mutate(self, individual, indpb=0.1):
        #     """Mutate an individual by randomly changing some assignments"""
        #     for year_name, year_schedule in individual.items():
        #         year_data = self.config.year_data_all[year_name]
        #         lecture_list = year_data.get("lecture_list", {})
        #         lecture_ability = year_data.get("lecture_ability", {})
                
        #         for day, day_schedule in year_schedule.items():
        #             for time, assignment in day_schedule.items():
        #                 if random.random() < indpb and assignment is not None:
        #                     current_lecture = assignment['lecture']
        #                     available_teachers = lecture_ability.get(current_lecture, [])
                            
        #                     if available_teachers:
        #                         new_teacher = random.choice(available_teachers)
                                
        #                         # Check if new teacher is available
        #                         time_slot_index = self.config.map_lectureSlotsTime_to_index[time]
        #                         teacher_serial_num = self.config.map_teachers_to_serialNum[new_teacher]
                                
        #                         if not self.config.check_is_faculty_occupied(day, time_slot_index, teacher_serial_num):
        #                             individual[year_name][day][time]['teacher'] = new_teacher
            
        #     return individual,
        def _mutate(self, individual, indpb=0.1):
            """Mutate an individual by moving, swapping, or changing teachers."""
            for year_name, year_schedule in individual.items():
                if random.random() > indpb:
                    continue

                year_data = self.config.year_data_all[year_name]
                lecture_ability = year_data.get("lecture_ability", {})

                assigned_slots = []
                empty_slots = []
                for day, day_schedule in year_schedule.items():
                    for time, assignment in day_schedule.items():
                        if assignment is None:
                            empty_slots.append((day, time))
                        else:
                            assigned_slots.append((day, time))

                if not assigned_slots:
                    continue

                op_roll = random.random()

                # 1) Move a lecture to a free slot (changes time)
                if op_roll < 0.5 and empty_slots:
                    src_day, src_time = random.choice(assigned_slots)
                    dst_day, dst_time = random.choice(empty_slots)
                    assignment = year_schedule[src_day][src_time]

                    teacher = assignment.get("teacher")
                    time_slot_index = self.config.map_lectureSlotsTime_to_index[str(dst_time)]
                    teacher_serial = self.config.map_teachers_to_serialNum[teacher]

                    if not self.config.check_is_faculty_occupied(dst_day, time_slot_index, teacher_serial):
                        year_schedule[dst_day][dst_time] = assignment
                        year_schedule[src_day][src_time] = None

                # 2) Swap two lectures (changes time)
                elif op_roll < 0.8 and len(assigned_slots) >= 2:
                    (day_a, time_a), (day_b, time_b) = random.sample(assigned_slots, 2)
                    a = year_schedule[day_a][time_a]
                    b = year_schedule[day_b][time_b]

                    a_teacher = a.get("teacher")
                    b_teacher = b.get("teacher")

                    a_slot_index = self.config.map_lectureSlotsTime_to_index[str(time_b)]
                    b_slot_index = self.config.map_lectureSlotsTime_to_index[str(time_a)]

                    a_serial = self.config.map_teachers_to_serialNum[a_teacher]
                    b_serial = self.config.map_teachers_to_serialNum[b_teacher]

                    a_ok = not self.config.check_is_faculty_occupied(day_b, a_slot_index, a_serial)
                    b_ok = not self.config.check_is_faculty_occupied(day_a, b_slot_index, b_serial)

                    if a_ok and b_ok:
                        year_schedule[day_a][time_a], year_schedule[day_b][time_b] = b, a

                # 3) Change teacher for a lecture (keeps time)
                else:
                    day, time = random.choice(assigned_slots)
                    assignment = year_schedule[day][time]
                    current_lecture = assignment.get("lecture")
                    available_teachers = lecture_ability.get(current_lecture, [])

                    if available_teachers:
                        new_teacher = random.choice(available_teachers)
                        time_slot_index = self.config.map_lectureSlotsTime_to_index[str(time)]
                        teacher_serial = self.config.map_teachers_to_serialNum[new_teacher]

                        if not self.config.check_is_faculty_occupied(day, time_slot_index, teacher_serial):
                            assignment["teacher"] = new_teacher

            self._repair_individual_counts(individual)
            return individual,
        
        def _crossover(self, ind1, ind2):
            """Perform crossover between two individuals"""
            if random.random() < self.cxpb:
                for year_name in ind1.keys():
                    if year_name not in ind2:
                        continue

                    common_days = list(set(ind1[year_name].keys()) & set(ind2[year_name].keys()))
                    if not common_days:
                        continue

                    crossover_day = random.choice(common_days)
                    ind1[year_name][crossover_day], ind2[year_name][crossover_day] = \
                        ind2[year_name][crossover_day], ind1[year_name][crossover_day]

            self._repair_individual_counts(ind1)
            self._repair_individual_counts(ind2)
            
            return ind1, ind2
        
        def run(self):
            """Run the genetic algorithm"""
            logger.debug(
                "Starting Genetic Algorithm (Pop: %s, Gen: %s, MinGen: %s, Patience: %s)...",
                self.pop_size,
                self.generations,
                self.min_generations,
                self.stagnation_patience,
            )

            # Create initial population
            pop = self.toolbox.population(n=self.pop_size)

            # Add statistics tracking
            stats = tools.Statistics(lambda ind: ind.fitness.values[0])
            stats.register("avg", np.mean)
            stats.register("min", np.min)
            stats.register("max", np.max)

            # Evaluate initial population
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            fitnesses = list(map(self.toolbox.evaluate, invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            logbook = tools.Logbook()
            logbook.header = ["gen", "nevals"] + list(stats.fields)
            record = stats.compile(pop)
            logbook.record(gen=0, nevals=len(invalid_ind), **record)

            best_fitness = tools.selBest(pop, 1)[0].fitness.values[0]
            stagnant_generations = 0

            # Evolution loop with plateau-based early stopping
            for gen in range(1, self.generations + 1):
                offspring = self.toolbox.select(pop, len(pop))
                offspring = algorithms.varAnd(offspring, self.toolbox, self.cxpb, self.mutpb)

                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = list(map(self.toolbox.evaluate, invalid_ind))
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit

                pop[:] = offspring

                record = stats.compile(pop)
                logbook.record(gen=gen, nevals=len(invalid_ind), **record)

                current_best = tools.selBest(pop, 1)[0].fitness.values[0]
                if current_best > (best_fitness + self.fitness_tolerance):
                    best_fitness = current_best
                    stagnant_generations = 0
                else:
                    stagnant_generations += 1

                if gen >= self.min_generations and stagnant_generations >= self.stagnation_patience:
                    logger.debug(
                        "Stopping GA early at generation %s due to convergence plateau.",
                        gen,
                    )
                    break

            self.logbook = logbook

            # Get best individual
            self.best_solution = tools.selBest(pop, 1)[0]
            self.best_fitness = self.best_solution.fitness.values[0]
            
            logger.debug(f"\nFinal Best Fitness: {self.best_fitness:.3f}")
            logger.debug("\nEvolution Statistics:")
            logger.debug(f"Best fitness progression: {self.logbook.select('min')[-10:]}")
            logger.debug(f"Average fitness progression: {self.logbook.select('avg')[-10:]}")
            
            return self.best_solution, self.best_fitness, self.logbook
        
        def analyze_solution(self):
            """Analyze and display the best solution found"""
            if not self.best_solution:
                logger.debug("No solution available to analyze")
                return
            
            logger.debug("\n" + "="*60)
            logger.debug("BEST SOLUTION ANALYSIS")
            logger.debug("="*60)
            
            total_assignments = 0
            teacher_assignments = {}
            subject_assignments = {}
            year_assignments = {}
            
            for year_name, year_schedule in self.best_solution.items():
                year_assignments[year_name] = 0
                subject_assignments[year_name] = {}
                
                logger.debug(f"\n{year_name.upper()}:")
                logger.debug("-" * 40)
                
                for day in sorted(year_schedule.keys()):
                    day_assignments = year_schedule[day]
                    if day_assignments:
                        logger.debug(f"  Day {day}:")
                        for time in sorted(day_assignments.keys()):
                            assignment = day_assignments[time]
                            if assignment is not None:
                                total_assignments += 1
                                year_assignments[year_name] += 1
                                
                                teacher = assignment['teacher']
                                teacher_assignments[teacher] = teacher_assignments.get(teacher, 0) + 1
                                
                                subject = assignment['lecture']
                                subject_assignments[year_name][subject] = subject_assignments[year_name].get(subject, 0) + 1
                                
                                logger.debug(f"    {time}: {assignment['lecture']} by {assignment['teacher']} in Room {assignment['classroom']}")
            
            # Print summary
            logger.debug("\n" + "="*60)
            logger.debug("SUMMARY")
            logger.debug("="*60)
            logger.debug(f"Total Assignments: {total_assignments}")
            
            logger.debug("\nAssignments per Year:")
            for year_name, count in year_assignments.items():
                required = self.config.list_ofTotalLecturesPerYear.get(year_name, 0)
                percentage = (count/required*100) if required > 0 else 0
                logger.debug(f"  {year_name}: {count}/{required} ({percentage:.1f}%)")
            
            logger.debug("\nTeacher Workload:")
            for teacher, count in sorted(teacher_assignments.items(), key=lambda x: x[1], reverse=True):
                logger.debug(f"  {teacher}: {count} sessions")
            
            logger.debug("\nSubject Coverage:")
            for year_name, subjects in subject_assignments.items():
                logger.debug(f"  {year_name}:")
                lecture_list = self.config.year_data_all[year_name].get("lecture_list", {})
                for subject, required in lecture_list.items():
                    actual = subjects.get(subject, 0)
                    status = "[OK]" if actual >= required[0] else "[X]"
                    logger.debug(f"    {subject}: {actual}/{required[0]} {status}")
        
        def plot_evolution(self):
            """Plot the evolution progress"""
            if not self.logbook:
                logger.debug("No evolution data to plot")
                return
            



    # ============================ COMBINED TIMETABLE DISPLAY ============================

    def display_combined_timetable(practical_timetable, lecture_timetable, year_data_all):
        """
        Display a combined view of both practical and lecture timetables
        
        Parameters:
            practical_timetable: Dictionary with practical schedule
            lecture_timetable: Dictionary with lecture schedule (best solution from GA)
            year_data_all: Main data structure with year information
        """
        
        day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
        
        logger.debug("\n" + "="*100)
        logger.debug(" " * 30 + "*** COMPLETE WEEKLY TIMETABLE ***")
        logger.debug("="*100)
        
        for year_name in year_data_all.keys():
            logger.debug(f"\n{'='*100}")
            logger.debug(f"{' '*35}{year_name.upper().replace('_', ' ')}")
            logger.debug(f"{'='*100}")
            
            # Collect all time slots used
            all_time_slots = set()
            
            # From practicals
            if year_name in practical_timetable:
                for day, sessions_list in practical_timetable[year_name].items():
                    for sessions in sessions_list:
                        if sessions:
                            for session in sessions:
                                all_time_slots.add(session['slot'])
            
            # From lectures
            if year_name in lecture_timetable:
                for day, day_schedule in lecture_timetable[year_name].items():
                    for time in day_schedule.keys():
                        all_time_slots.add(time)
            
            # Sort time slots
            sorted_times = sorted(list(all_time_slots))
            
            # Display day by day
            for day_num in range(1, 6):
                day_name = day_names[day_num]
                
                # Check if there are any sessions this day
                has_practical = year_name in practical_timetable and day_num in practical_timetable[year_name] and practical_timetable[year_name][day_num]
                has_lecture = year_name in lecture_timetable and day_num in lecture_timetable[year_name]
                
                if not has_practical and not has_lecture:
                    continue
                
                logger.debug(f"\n{day_name:^100}")
                logger.debug("-" * 100)
                
                # Display by time slot
                for time_slot in sorted_times:
                    practical_sessions = []
                    lecture_sessions = []
                    
                    # Get practical sessions at this time
                    if has_practical:
                        for sessions in practical_timetable[year_name][day_num]:
                            if sessions:
                                for session in sessions:
                                    if session['slot'] == time_slot:
                                        practical_sessions.append(session)
                    
                    # Get lecture sessions at this time
                    if has_lecture and time_slot in lecture_timetable[year_name][day_num]:
                        lecture_assignment = lecture_timetable[year_name][day_num][time_slot]
                        if lecture_assignment is not None:
                            lecture_sessions.append(lecture_assignment)
                    
                    # Display if there's anything at this time
                    if practical_sessions or lecture_sessions:
                        time_str = f"{time_slot}" if isinstance(time_slot, (int, float)) else str(time_slot)
                        logger.debug(f"\n  [*] Time: {time_str}")
                        logger.debug("  " + "-" * 96)
                        
                        if practical_sessions:
                            logger.debug(f"  {'[PRACTICALS/LABS]:':<50}")
                            logger.debug(f"  {'Batch':<8} {'Lab':<12} {'Faculty':<10} {'Room':<10} {'Type':<15}")
                            logger.debug("  " + "-" * 96)
                            for session in practical_sessions:
                                batch = session.get('batch', 'N/A')
                                lab = session.get('lab', 'N/A')
                                faculty = session.get('faculty', 'N/A')
                                room_id = session.get('Room id', 'N/A')
                                logger.debug(f"  {batch:<8} {lab:<12} {faculty:<10} Room {room_id:<7} {'PRACTICAL':<15}")
                        
                        if lecture_sessions:
                            if practical_sessions:
                                logger.debug()  # Add spacing between practicals and lectures
                            logger.debug(f"  {'[LECTURES]:':<50}")
                            logger.debug(f"  {'Subject':<15} {'Faculty':<10} {'Classroom':<10} {'Type':<15}")
                            logger.debug("  " + "-" * 96)
                            for lecture in lecture_sessions:
                                subject = lecture.get('lecture', 'N/A')
                                teacher = lecture.get('teacher', 'N/A')
                                classroom = lecture.get('classroom', 'N/A')
                                logger.debug(f"  {subject:<15} {teacher:<10} Room {classroom:<7} {'LECTURE':<15}")
        
        logger.debug("\n" + "="*100)


    def display_combined_summary(practical_timetable, lecture_timetable, year_data_all):
        """Display summary statistics for combined timetables"""
        
        logger.debug("\n" + "="*100)
        logger.debug(" " * 35 + "*** TIMETABLE SUMMARY ***")
        logger.debug("="*100)
        
        for year_name in year_data_all.keys():
            logger.debug(f"\n{year_name.upper().replace('_', ' ')}:")
            logger.debug("-" * 100)
            
            # Count practicals
            practical_count = 0
            if year_name in practical_timetable:
                for day, sessions_list in practical_timetable[year_name].items():
                    for sessions in sessions_list:
                        if sessions:
                            practical_count += len(sessions)
            
            # Count lectures
            lecture_count = 0
            if year_name in lecture_timetable:
                for day, day_schedule in lecture_timetable[year_name].items():
                    for assignment in day_schedule.values():
                        if assignment is not None:
                            lecture_count += 1
            
            total_sessions = practical_count + lecture_count
            
            logger.debug(f"  Total Sessions: {total_sessions}")
            logger.debug(f"    • Practical/Lab Sessions: {practical_count}")
            logger.debug(f"    • Lecture Sessions: {lecture_count}")
            
            # Calculate coverage
            year_data = year_data_all[year_name]
            
            # Practical coverage
            if 'lab_list' in year_data:
                required_practicals = sum(req[0] * len(year_data.get('batches', [])) 
                                        for req in year_data['lab_list'].values())
                practical_coverage = (practical_count / required_practicals * 100) if required_practicals > 0 else 0
                logger.debug(f"    • Practical Coverage: {practical_coverage:.1f}% ({practical_count}/{required_practicals})")
            
            # Lecture coverage
            if 'lecture_list' in year_data:
                required_lectures = sum(req[0] for req in year_data['lecture_list'].values())
                lecture_coverage = (lecture_count / required_lectures * 100) if required_lectures > 0 else 0
                logger.debug(f"    • Lecture Coverage: {lecture_coverage:.1f}% ({lecture_count}/{required_lectures})")
        
        logger.debug("\n" + "="*100)


    def export_combined_timetable_to_text(practical_timetable, lecture_timetable, year_data_all, filename="combined_timetable.txt"):
        """Export combined timetable to a text file"""
        
        day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*100 + "\n")
            f.write(" " * 30 + "COMPLETE WEEKLY TIMETABLE\n")
            f.write("="*100 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*100 + "\n\n")
            
            for year_name in year_data_all.keys():
                f.write(f"\n{'='*100}\n")
                f.write(f"{' '*35}{year_name.upper().replace('_', ' ')}\n")
                f.write(f"{'='*100}\n")
                
                # Collect all time slots
                all_time_slots = set()
                
                if year_name in practical_timetable:
                    for day, sessions_list in practical_timetable[year_name].items():
                        for sessions in sessions_list:
                            if sessions:
                                for session in sessions:
                                    all_time_slots.add(session['slot'])
                
                if year_name in lecture_timetable:
                    for day, day_schedule in lecture_timetable[year_name].items():
                        for time in day_schedule.keys():
                            all_time_slots.add(time)
                
                sorted_times = sorted(list(all_time_slots))
                
                # Display day by day
                for day_num in range(1, 6):
                    day_name = day_names[day_num]
                    
                    has_practical = year_name in practical_timetable and day_num in practical_timetable[year_name] and practical_timetable[year_name][day_num]
                    has_lecture = year_name in lecture_timetable and day_num in lecture_timetable[year_name]
                    
                    if not has_practical and not has_lecture:
                        continue
                    
                    f.write(f"\n{day_name}\n")
                    f.write("-" * 100 + "\n")
                    
                    for time_slot in sorted_times:
                        practical_sessions = []
                        lecture_sessions = []
                        
                        if has_practical:
                            for sessions in practical_timetable[year_name][day_num]:
                                if sessions:
                                    for session in sessions:
                                        if session['slot'] == time_slot:
                                            practical_sessions.append(session)
                        
                        if has_lecture and time_slot in lecture_timetable[year_name][day_num]:
                            lecture_assignment = lecture_timetable[year_name][day_num][time_slot]
                            if lecture_assignment is not None:
                                lecture_sessions.append(lecture_assignment)
                        
                        if practical_sessions or lecture_sessions:
                            f.write(f"\n  Time: {time_slot}\n")
                            f.write("  " + "-" * 96 + "\n")
                            
                            if practical_sessions:
                                f.write(f"  PRACTICALS/LABS:\n")
                                for session in practical_sessions:
                                    f.write(f"    Batch {session.get('batch', 'N/A')}: {session.get('lab', 'N/A')} "
                                        f"by {session.get('faculty', 'N/A')} in Room {session.get('Room id', 'N/A')}\n")
                            
                            if lecture_sessions:
                                f.write(f"  LECTURES:\n")
                                for lecture in lecture_sessions:
                                    f.write(f"    {lecture.get('lecture', 'N/A')} by {lecture.get('teacher', 'N/A')} "
                                        f"in Room {lecture.get('classroom', 'N/A')}\n")
            
            f.write("\n" + "="*100 + "\n")
        
        logger.debug(f"\n[OK] Combined timetable exported to '{filename}'")

    def generate_teacher_serial_mapping(year_data_all):
        """
        Dynamically generate teacher ID to serial number mapping from year_data_all
        
        Extracts all unique teachers from lecture_ability and practical_ability_list
        across all years, sorts them, and assigns serial numbers.
        
        Args:
            year_data_all: Dictionary containing all year data
            
        Returns:
            dict: Mapping of teacher ID (e.g., 'T1') to serial number (1, 2, 3...)
        """
        all_teachers = set()
        
        # Extract all unique teachers from all years
        for year_name, year_data in year_data_all.items():
            # Get teachers from practical assignments
            practical_ability = year_data.get("practical_ability_list", {})
            for teachers_list in practical_ability.values():
                all_teachers.update(teachers_list)
            
            # Get teachers from lecture assignments
            lecture_ability = year_data.get("lecture_ability", {})
            for teachers_list in lecture_ability.values():
                all_teachers.update(teachers_list)
        
        # Sort teachers to ensure consistent ordering
        sorted_teachers = sorted(list(all_teachers))
        
        # Create mapping: teacher_id -> serial_number
        teacher_serial_mapping = {
            teacher: serial_num 
            for serial_num, teacher in enumerate(sorted_teachers, start=1)
        }
        
        logger.debug(f"Generated teacher mapping for {len(teacher_serial_mapping)} teachers:")
        logger.debug(teacher_serial_mapping)
        
        return teacher_serial_mapping
  


    # ========== PART 1: PRACTICAL/LAB SCHEDULING ==========
    year_data = year_data_all

    # Run feasibility analysis
    is_feasible = analyze_scheduling_feasibility(year_data)

    if not is_feasible:
        return {
            "success": False,
            "error": "Constraints are infeasible"
        }

    # Generate practical timetables
    practical_timetable, practical_occupancy = generate_complete_timetables(year_data)

    if not practical_timetable:
        return {
            "success": False,
            "error": "Practical scheduling failed"
        }

    # ========== PART 2: LECTURE SCHEDULING ==========
    map_teachers_to_serialNum = generate_teacher_serial_mapping(year_data_all)

    lecture_config = LectureSchedulingConfig(
        year_data_all,
        practical_timetable,
        practical_occupancy,
        map_teachers_to_serialNum
    )

    ga = LectureGeneticAlgorithm(
        config=lecture_config,
        pop_size=130,
        generations=180,
        cxpb=0.7,
        mutpb=0.2
    )

    best_solution, best_fitness, logbook = ga.run()

    # ========== FINAL RESULT ==========
    return {
        "success": True,
        "practical_timetable": practical_timetable,
        "lecture_timetable": best_solution,
        "fitness": best_fitness
    }
