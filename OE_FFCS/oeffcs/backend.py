from os import stat
from django.shortcuts import render
from numpy.core.fromnumeric import prod
from numpy.lib.npyio import save
import pandas as pd
from django.conf import settings
from itertools import product
from .forms import ChangeStatusForm, ChangeFiltersForm, ChangeTimetableNumber
from .models import Profile, Timetable, Entry
from collections import Counter
import time
from discord_logger import DiscordLogger
from discord_logger import DiscordLogger
from ipware import get_client_ip
from django.db import transaction, DatabaseError, IntegrityError

options_info = {
    "application_name": "OEFFCS LOGGER",
    "service_name": "Backend logger",
    "service_icon_url": "https://cdn.discordapp.com/attachments/853138859772215299/865220535964925952/unknown.png",
    "display_hostname": False,
    "default_level": "info",
}
options_success = {
    "application_name": "OEFFCS LOGGER",
    "service_name": "Backend logger",
    "service_icon_url": "https://cdn.discordapp.com/attachments/853138859772215299/865220535964925952/unknown.png",
    "display_hostname": False,
    "default_level": "success",
}
options_error = {
    "application_name": "OEFFCS LOGGER",
    "service_name": "Backend logger",
    "service_icon_url": "https://cdn.discordapp.com/attachments/853138859772215299/865220535964925952/unknown.png",
    "display_hostname": False,
    "default_level": "error",
}

lowlevellog_info = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/865251088046489630/OQlPSvuqHFdTepq37bm0q4cffe8HrA3CzjlqH-0NZDuCZnmztyTYtYdD9DzVFqGatTN", **options_info)
highlevellog_info = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/865266449731420241/enyFO8HDsx3gQwvXYcrUZ2WilDkSKm3EnfjmEpknR4yFOtyYAnqK1fczycvzPPN2ihg", **options_info)
lowlevellog_success = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/865251088046489630/OQlPSvuqHFdTepq37bm0q4cffe8HrA3CzjlqH-0NZDuCZnmztyTYtYdD9DzVFqGatTN", **options_success)
highlevellog_success = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/865266449731420241/enyFO8HDsx3gQwvXYcrUZ2WilDkSKm3EnfjmEpknR4yFOtyYAnqK1fczycvzPPN2ihg", **options_success)
lowlevellog_error = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/865251088046489630/OQlPSvuqHFdTepq37bm0q4cffe8HrA3CzjlqH-0NZDuCZnmztyTYtYdD9DzVFqGatTN", **options_error)
highlevellog_error = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/865266449731420241/enyFO8HDsx3gQwvXYcrUZ2WilDkSKm3EnfjmEpknR4yFOtyYAnqK1fczycvzPPN2ihg", **options_error)

options = {
    "application_name": "OEFFCS LOGGER",
    "service_name": "Backend logger",
    "service_icon_url": "https://cdn.discordapp.com/attachments/853138859772215299/865220535964925952/unknown.png",
    "display_hostname": False,
    "default_level": "info",
}

logger = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/865251088046489630/OQlPSvuqHFdTepq37bm0q4cffe8HrA3CzjlqH-0NZDuCZnmztyTYtYdD9DzVFqGatTNx", **options)
logger.construct(title="Log", description="Service restarted!")
response = logger.send()

base_dir = str(settings.BASE_DIR).replace('\\', '/')

# Coulmn names, if needed to be changed later
COURSE_CODE = 'COURSE CODE'
COURSE_TITLE = 'COURSE TITLE'
COURSE_TYPE = 'COURSE TY'
SLOT = 'SLOT'
ERP_ID = 'ERP ID'
EMPLOYEE_NAME = 'EMPLOYEE NAME'

COURSE_ELA = 'ELA'
COURSE_ETH = 'ETH'

people_status = {}

# !! Add saturday and sunday classes too !!
dict_conv = {
    'A1': ['L1', 'L14'], 'B1': ['L7', 'L20'], 'C1': ['L13', 'L26'], 'D1': ['L19', 'L3'], 'E1': ['L25', 'L9'], 'F1': ['L2', 'L15'],
    'G1': ['L8', 'L21'], 'TA1': ['L27'], 'TB1': ['L4'], 'TC1': ['L10'], 'V1': ['L16'], 'TE1': ['L22'], 'TF1': ['L28'], 'TG1': ['L5'],
    'TAA1': ['L11'], 'V2': ['L17'], 'TCC1': ['L23'], 'TD1': ['L29'],
    'A2': ['L31', 'L44'], 'B2': ['L37', 'L50'], 'C2': ['L43', 'L56'], 'D2': ['L49', 'L33'], 'E2': ['L55', 'L39'], 'F2': ['L32', 'L45'],
    'G2': ['L38', 'L51'], 'TA2': ['L57'], 'TB2': ['L34'], 'TC2': ['L40'], 'TD2': ['L46'], 'TE2': ['L52'], 'TF2': ['L58'], 'TG2': ['L35'],
    'TAA2': ['L41'], 'TBB2': ['L47'], 'TCC2': ['L53'], 'TDD2': ['L59']
}

morning_theory = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'TA1',
                  'TB1', 'TC1', 'V1', 'TE1', 'TF1', 'TG1', 'TAA1', 'V2', 'TCC1', 'TD1']


def convert_file_to_df(filepath):
    # REQUIRED COLUMNS IN THE DATASET ARE:
    # COURSE CODE
    # COURSE TITLE
    # COURSE TYPE
    # SLOT
    # ERP ID
    # EMPLOYEE NAME

    # Reading the dataset from file
    dataframe = pd.read_excel(base_dir+"/media/"+filepath)

    # Filling previous entries into NAN values
    dataframe.fillna(method="ffill", inplace=True)
    # print(dataframe.head())

    # Dropping unrequired columns
    required_columns = [COURSE_CODE, COURSE_TITLE,
                        COURSE_TYPE, SLOT, ERP_ID, EMPLOYEE_NAME]
    dataframe = dataframe[required_columns]
    erpid = list(dataframe[ERP_ID])
    for i in range(len(erpid)):
        try:
            erpid[i] = str(int(erpid[i]))
        except:
            pass
    dataframe[ERP_ID] = erpid
    return dataframe


def convert_df_to_ds(dataframe):
    # List of subjects
    subjects = dataframe[COURSE_TITLE].unique()

    # CONVERT DATAFRAME INTO DATASTRUCTURE: {"<COURSE NAME>;<COURSE CODE>": {<COURSE TYPE>: ["<TEACHER NAMES>;<ERP ID>"]}}
    # Total dictionary is in the above format
    totaldictionary = {}

    # Iterating through the dataframe
    for index, row in dataframe.iterrows():
        # Extracting title and name of teacher, along with course code and teacher ID
        course_title = row[COURSE_TITLE] + ' (' + row[COURSE_CODE]+')'
        employee_name = row[EMPLOYEE_NAME] + ' (' + row[ERP_ID]+')'

        # If subject hasn't been seen before, add the new subject, along with the course type
        if course_title not in totaldictionary.keys():
            totaldictionary.update(
                {course_title: {row[COURSE_TYPE]: [employee_name]}})
        # Else if course type hasn't been seen before, add the new course type to the subject dictionary
        elif row[COURSE_TYPE] not in totaldictionary[course_title].keys():
            totaldictionary[course_title].update(
                {row[COURSE_TYPE]: [employee_name]})
        # If both subject and type has been seen, append teacher name to teacher list
        else:
            if employee_name not in totaldictionary[course_title][row[COURSE_TYPE]]:
                totaldictionary[course_title][row[COURSE_TYPE]].append(
                    employee_name)

    # REMOVE ELA FROM ANY THAT HAVE ETH
    # Function to get lab count from eacher for subject
    def get_lab_count(subject, teacher):
        # Remove all other data except that teacher and that subject and lab classes and return length
        return len(dataframe.loc[(dataframe[COURSE_CODE] == subject) & (dataframe[COURSE_TYPE] == COURSE_ELA) & (dataframe[ERP_ID] == teacher)])

    # Building final datastructure after removing lab classes
    finaldata = {}

    # Iterating through each subject
    for subject, courses in totaldictionary.items():
        # If course has ETH and ELA
        if sorted(list(courses.keys())) == sorted([COURSE_ELA, COURSE_ETH]):
            # Iterating through theory and searching for lab classes
            for i in range(len(courses[COURSE_ETH])):
                # Getting lab count
                lab_count = get_lab_count(subject.split(
                    '(')[-1].rstrip(')'), courses[COURSE_ETH][i].split('(')[-1].rstrip(')'))
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # What do we do when lab count is 0?
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                # Adding lab count to teacher name
                courses[COURSE_ETH][i] = courses[COURSE_ETH][i] + \
                    ' (' + str(lab_count) + ' Lab class(es))'
            # Update the datastructure with new data
            finaldata.update({subject: {COURSE_ETH: courses[COURSE_ETH]}})
        else:
            # Not a ELA course, just uppend and move on
            finaldata.update({subject: courses})

    return finaldata
    # print(finaldata)


class FORM:
    # Form variable to store form
    form = ''
    # count variable to store count
    count = 1

    def add_subject(self, subject, subject_code, check_status="unchecked", user_object=''):
        # Creating checkbox for subject
        self.form += '<div class="custom-control custom-switch"><input id ="' + subject_code + '" \
                type="checkbox" \
                class="custom-control-input subjectcheckbox'+str(self.count)+'" \
                name="'+subject_code+'" \
                value="'+subject_code+'" \
                onclick=toggleview("'+"teacherlist" + str(self.count)+'","' + subject_code + '") \
                autocomplete="off" '+check_status+'>'

        # Creating lable for checkbox
        self.form += '<label class="custom-control-label" for="' + \
            subject_code+'"> '+subject_code+' '+subject+'</label>'

        try:
            course_type_data = eval(user_object.profile.course_type)
            crstype = course_type_data[subject_code]
            if crstype == 'PC':
                self.form += '''<select name="'''+subject_code+'''classification" class="form-select" aria-label="Default select example">
                            <option value="PC" selected>Programme Core</option>
                            <option value="PE">Programme Elective</option>
                            <option value="UC">University Core</option>
                            <option value="UE">University Elective</option>
                            </select>
                            </div>'''
            elif crstype == 'PE':
                self.form += '''<select name="'''+subject_code+'''classification" class="form-select" aria-label="Default select example">
                            <option value="PC">Programme Core</option>
                            <option value="PE" selected>Programme Elective</option>
                            <option value="UC">University Core</option>
                            <option value="UE">University Elective</option>
                            </select>
                            </div>'''
            elif crstype == 'UC':
                self.form += '''<select name="'''+subject_code+'''classification" class="form-select" aria-label="Default select example">
                            <option value="PC">Programme Core</option>
                            <option value="PE">Programme Elective</option>
                            <option value="UC" selected>University Core</option>
                            <option value="UE">University Elective</option>
                            </select>
                            </div>'''
            else:
                self.form += '''<select name="'''+subject_code+'''classification" class="form-select" aria-label="Default select example">
                            <option value="PC">Programme Core</option>
                            <option value="PE">Programme Elective</option>
                            <option value="UC">University Core</option>
                            <option value="UE" selected>University Elective</option>
                            </select>
                            </div>'''
        except (SyntaxError, KeyError):
            self.form += '''<select name="'''+subject_code+'''classification" class="form-select" aria-label="Default select example">
                            <option selected disabled hidden>Course Category</option>
                            <option value="PC">Programme Core</option>
                            <option value="PE">Programme Elective</option>
                            <option value="UC">University Core</option>
                            <option value="UE">University Elective</option>
                            </select>
                            </div>'''

        # Creating span to hold and hide teacher names
        self.form += '<span style="display: none;" id="teacherlist' + \
            str(self.count)+'">'

        # Increment count for subjects
        self.count += 1

    def add_course_type(self, course_type):
        # Adding label for course type
        # !! Inside span of subject !!
        self.form += '&emsp; <label class="coursetype">'+course_type+'</label><br>'

    def add_teacher(self, teacher, subject_code, teacher_code, check_status="unchecked"):
        # Adding checkbox for teacher
        self.form += '<div class="form-check">&emsp; &emsp; \
                    <input id="' + teacher+subject_code + '" \
                    type="checkbox" \
                    class="teachercheckbox form-check-input" \
                    name="'+subject_code+'" \
                    value="'+subject_code+':'+teacher_code+'" \
                    autocomplete="off" '+check_status+'>'

        # Adding lable for teacher name
        self.form += '<label for="'+teacher+subject_code+'" class="form-check-label"\
            style="margin-bottom:4px;"> '+teacher+'</label></div>'

    def close_subject(self):
        # Adding a closing span tag for subject
        self.form += '</span>'

    def output(self):
        # Returning form with submit button at the end
        return self.form + '<button type="submit" form="form1" class="btn btn-primary btn-block w-50" value="Submit">Submit</button>'


def convertToForm(user):
    # Getting datastructure from file
    finaldata = convert_df_to_ds(
        convert_file_to_df(str(user.profile.data_file)))
    status_value = user.profile.status_value
    if status_value >= 2:
        saved_previous_teachers = user.profile.saveteachers
    else:
        saved_previous_teachers = ''

    # FORM object
    form2 = FORM()

    # asdf

    # Iterating through data
    for subject_data, course_info in finaldata.items():
        # Extract subject and subject code
        subject, code, *trash = [i.rstrip(' )')
                                 for i in subject_data.split('(')]
        # Pass to form
        if code in saved_previous_teachers:
            form2.add_subject(subject, code, "checked", user_object=user)
        else:
            form2.add_subject(subject, code, user_object=user)

        # Iterating through course data
        for c_type, teacherlist in course_info.items():
            # Add course to form
            form2.add_course_type(c_type)

            # Extract teacher code from teachers name
            for teacher in teacherlist:
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # Special Case for STS, need to generalize
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                if 'APT' not in teacher:
                    trash, teachercode, * \
                        trash = [i.rstrip(' )') for i in teacher.split('(')]
                else:
                    teachercode = teacher.split(' (')[-1].rstrip(' )')
                # Add teacher to form
                if code+':'+teachercode in saved_previous_teachers:
                    form2.add_teacher(teacher, code, teachercode, "checked")
                else:
                    form2.add_teacher(teacher, code, teachercode)
        # Finish subject
        form2.close_subject()

    # Return form data
    return form2.output()


def timetable_to_html_str(lst):
    def conventional(slot: str) -> str:
        return '<td class="normal">'+slot+'</td>'

    def activated(slotinfo: str) -> str:
        return '<td class="normal active">'+slotinfo+'</td>'

    filepath = base_dir+"/oeffcs/templates/oeffcs/timetable.html"
    with open(filepath, 'r') as obj:
        all_text = obj.read()
        # print(all_text)
        # print(lst)
        for enrollment in lst:
            slots_in_enrollment = enrollment.split()[0].split('+')
            enrollment_data = " ".join(enrollment.split()[1:])
            # print(slots_in_enrollment)
            for slot in slots_in_enrollment:
                all_text = all_text.replace(conventional(slot), activated(
                    slot+'<br>'+enrollment_data))
        # print("For loops completed\n*******\n")  # +all_text
    return all_text


def generate_time_tables(user_object):
    people_status[str(user_object.username)] = {}
    people_status[str(user_object.username)]['valid_timetables'] = 0
    people_status[str(user_object.username)]['valid_status'] = False
    # print(people_status)
    saved_teachers = eval(user_object.profile.saveteachers)
    teacher_db = user_object.profile.data_file
    dataframe = convert_file_to_df(str(teacher_db))
    list_saved = list(saved_teachers.values())
    # list_cleaned = [[j] for i in list_saved for j in i if ":" in j]
    list_cleaned = []

    def get_slot_from_code(code):
        slots = {}
        course_code, teacher_code = code.split(':')
        # print(code)
        teacher_rows = dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (
            dataframe[ERP_ID] == teacher_code)]
        for index, row in teacher_rows.iterrows():
            try:
                slots[row[COURSE_TYPE]].append(row[SLOT])
            except:
                slots[row[COURSE_TYPE]] = [row[SLOT]]
        combinations = product(*list(slots.values()))
        combined = []
        for i in combinations:
            combined.append("+".join(i) + ' ' + code)
        return combined

    for i in list_saved:
        list_cleaned.append([j for j in i if ':' in j])
    total_combo = []
    for subject in list_cleaned:
        subject_slots = []
        for teacher in subject:
            subject_slots.extend(get_slot_from_code(teacher))
        total_combo.append(subject_slots)
    # ALL SLOTS RECORDED
    # print(total_combo)

    # trial = [i[0] for i in total_combo]
    # timetable_to_html_str(trial)

    # print(total_combo)
    merged_combo = []
    for i in total_combo:
        subjectlst = {}
        for j in i:
            slot = j.split(' ')[0]
            teachers = " ".join(j.split(" ")[1:])
            if slot in subjectlst.keys():
                subjectlst[slot] += ' ' + teachers
            else:
                subjectlst[slot] = teachers
        merged_combo.append(
            [key+' '+value for key, value in subjectlst.items()])

    all_combinations = product(*merged_combo)
    # print("Combinations found!")
    lowlevellog_info.construct(title="Process Log", description=user_object.username +
                               " generated combinations! Calculating number of valid timetables")
    lowlevellog_info.send()
    # Calculating total number of combos
    total = 1
    for i in merged_combo:
        total = len(i)*total
    people_status[str(user_object.username)]['total_timetables'] = total
    people_status[str(user_object.username)]['completed_timetables'] = 0
    form = ChangeStatusForm(
        {'status_value': -5}, instance=user_object.profile)
    if form.is_valid():
        form.instance.user = user_object
        form.save()
    Timetable.objects.filter(level=user_object.profile).delete()
    count = 0
    for i in all_combinations:
        validate_result = validate_timetable(i)
        if validate_result[0]:
            count += 1
            save_timetable_indivisual([i, validate_result], user_object, count)
            people_status[str(user_object.username)]['valid_timetables'] += 1
        people_status[str(user_object.username)]['completed_timetables'] += 1
    people_status[str(user_object.username)]['valid_status'] = True
    lowlevellog_info.construct(
        title="Process Log", description=user_object.username+" generated "+str(count)+" valid timetables!")
    lowlevellog_info.send()
    # print(count, "Combinations valid!")
    form = ChangeStatusForm(
        {'status_value': 2}, instance=user_object.profile)
    if form.is_valid():
        form.instance.user = user_object
        form.save()
    no_of_timetables = count
    form = ChangeTimetableNumber(
        {'timetable_count': no_of_timetables}, instance=user_object.profile)
    if form.is_valid():
        form.instance.user = user_object
        form.save()

    # save_timetable(validated, user_object)


def validate_timetable(timetable):
    slots = []
    theory = ''
    lab = ''

    for i in timetable:
        slots.extend(i.split(' ')[0].split('+'))
    # remove all occurances of NIL from slots
    slots = [i for i in slots if i != 'NIL']
    if len(slots) != len(set(slots)):
        return (False, 0, 0, 0, 'none', 'none')
    print(slots)

    if 'D1' in slots and 'L4' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TB1' in slots and 'L5' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TG1' in slots and 'L6' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'E1' in slots and 'L10' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TC1' in slots and 'L11' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TAA1' in slots and 'L12' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'F1' in slots and 'L16' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'V1' in slots and 'L17' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'V2' in slots and 'L18' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'G1' in slots and 'L22' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TE1' in slots and 'L23' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TCC1' in slots and 'L24' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'TA1' in slots and 'L28' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TF1' in slots and 'L29' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TD1' in slots and 'L30' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    #######################################
    if 'D2' in slots and 'L34' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TB2' in slots and 'L35' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TG2' in slots and 'L36' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'E2' in slots and 'L40' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TC2' in slots and 'L41' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TAA2' in slots and 'L42' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'F2' in slots and 'L46' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TD2' in slots and 'L47' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TBB2' in slots and 'L48' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'G2' in slots and 'L52' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TE2' in slots and 'L53' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TCC2' in slots and 'L54' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    if 'TA2' in slots and 'L58' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TF2' in slots and 'L59' in slots:
        return (False, 0, 0, 0, 'none', 'none')
    if 'TDD2' in slots and 'L60' in slots:
        return (False, 0, 0, 0, 'none', 'none')

    slots_cleaned = []
    for i in slots:
        if i == 'NIL':
            continue
        if i in dict_conv.keys():
            if theory != 'mixed':
                if i in morning_theory and theory == '':
                    theory = 'morning'
                elif i not in morning_theory and theory == '':
                    theory = 'evening'
                elif i in morning_theory and theory == 'evening':
                    theory = 'mixed'
                elif i not in morning_theory and theory == 'morning':
                    theory = 'mixed'
            slots_cleaned.extend(dict_conv[i])
        else:
            if lab != 'mixed':

                inti = int(i[1:])
                if inti <= 30 and lab == '':
                    lab = 'morning'
                elif inti > 30 and lab == '':
                    lab = 'evening'
                elif inti <= 30 and lab == 'evening':
                    lab = 'mixed'
                elif inti > 30 and lab == 'morning':
                    lab = 'mixed'
            slots_cleaned.append(i)

    if len(slots_cleaned) == len(set(slots_cleaned)):
        totalcounter = Counter(slots_cleaned)
        total8 = totalcounter['L1'] + totalcounter['L7'] + \
            totalcounter['L13'] + totalcounter['L19'] + totalcounter['L25']
        total6 = totalcounter['L35'] + totalcounter['L41'] + \
            totalcounter['L47'] + totalcounter['L53'] + totalcounter['L59']
        total2 = totalcounter['L31'] + totalcounter['L37'] + \
            totalcounter['L43'] + totalcounter['L49'] + totalcounter['L55']

        return (True, total8, total2, total6, theory, lab)
    else:
        return (False, 0, 0, 0, 'none', 'none')


def save_timetable_indivisual(timetable_data, user, count):
    temp_timeable = Timetable(
        level=user.profile,
        total8classes=timetable_data[1][1],
        total2classes=timetable_data[1][2],
        total6classes=timetable_data[1][3],
        theory_status=timetable_data[1][4],
        lab_status=timetable_data[1][5],
        ttid=str(user)+str(count),
        nickname='Timetable '+str(count))
    temp_timeable.save()
    with transaction.atomic():
        for entry in timetable_data[0]:
            temp_entry = Entry(
                level=temp_timeable,
                slots=entry.split()[0],
                course_code=entry.split()[1].split(':')[0],
                class_code=' '.join(entry.split()[1:])
            )
            temp_entry.save()


def save_timetable(time_tables_data, user):
    # Save to user profile, update status number
    form = ChangeStatusForm(
        {'status_value': 2}, instance=user.profile)
    if form.is_valid():
        form.instance.user = user
        form.save()
    Timetable.objects.filter(level=user.profile).delete()
    no_of_timetables = len(time_tables_data)
    form = ChangeTimetableNumber(
        {'timetable_count': no_of_timetables}, instance=user.profile)
    if form.is_valid():
        form.instance.user = user
        form.save()
    count = 1
    for timetable, data in time_tables_data:
        temp_timeable = Timetable(
            level=user.profile,
            total8classes=data[1],
            total2classes=data[2],
            total6classes=data[3],
            theory_status=data[4],
            lab_status=data[5],
            ttid=str(user)+str(count),
            nickname='Timetable '+str(count))
        count += 1
        temp_timeable.save()
        for entry in timetable:
            temp_entry = Entry(
                level=temp_timeable,
                slots=entry.split()[0],
                course_code=entry.split()[1].split(':')[0],
                class_code=' '.join(entry.split()[1:])
            )
            temp_entry.save()
    print('completed')


def query_database(params, user):
    time_of_day = params['pre-post-lunch']
    # print(params)
    # params might be different due to form validation of Slot field
    # Considering slot as string for now
    # Converting string to list
    slots = [i.strip() for i in params['slots'].split(',')]

    if time_of_day == 'none':
        objects = Timetable.objects.filter(level=user.profile,
                                           total8classes__lte=params['8-classes'],
                                           total6classes__lte=params['6-classes'],
                                           total2classes__lte=params['2-classes'])
    else:
        if 'pre-theory' == time_of_day:
            objects = Timetable.objects.filter(level=user.profile,
                                               total8classes__lte=params['8-classes'],
                                               total6classes__lte=params['6-classes'],
                                               total2classes__lte=params['2-classes'],
                                               theory_status='morning')
        elif 'pre-lab' == time_of_day:
            objects = Timetable.objects.filter(level=user.profile,
                                               total8classes__lte=params['8-classes'],
                                               total6classes__lte=params['6-classes'],
                                               total2classes__lte=params['2-classes'],
                                               lab_status='morning')
        elif 'post-theory' == time_of_day:
            objects = Timetable.objects.filter(level=user.profile,
                                               total8classes__lte=params['8-classes'],
                                               total6classes__lte=params['6-classes'],
                                               total2classes__lte=params['2-classes'],
                                               theory_status='evening')
        elif 'post-lab' == time_of_day:
            objects = Timetable.objects.filter(level=user.profile,
                                               total8classes__lte=params['8-classes'],
                                               total6classes__lte=params['6-classes'],
                                               total2classes__lte=params['2-classes'],
                                               lab_status='evening')
        elif 'pre-theory-post-lab' == time_of_day:
            objects = Timetable.objects.filter(level=user.profile,
                                               total8classes__lte=params['8-classes'],
                                               total6classes__lte=params['6-classes'],
                                               total2classes__lte=params['2-classes'],
                                               lab_status='evening',
                                               theory_status='morning')
        elif 'pre-lab-post-theory' == time_of_day:
            objects = Timetable.objects.filter(level=user.profile,
                                               total8classes__lte=params['8-classes'],
                                               total6classes__lte=params['6-classes'],
                                               total2classes__lte=params['2-classes'],
                                               lab_status='morning',
                                               theory_status='evening')
    if slots != ['']:
        for i in slots:
            objects = objects.exclude(level=user.profile,
                                      entry__slots__contains=i)
    return objects


def show_selected_data(user_profile):
    file_path = str(user_profile.data_file).lstrip('exceldata/')
    try:
        selected_teachers = eval(user_profile.saveteachers)
    except:
        selected_teachers = {}
    selected_teachers_cleaned = {}
    for course, teachers in selected_teachers.items():
        if course not in teachers:
            # return render(request, 'oeffcs/pickteachers.html',
            #               {'teacherdata': ret, 'errordisplay': 'How did you even get this error?'})
            continue
        elif len(teachers) == 1:
            pass
        else:
            selected_teachers_cleaned.update(
                {course: [i for i in teachers if i != course]})

    retdict = {}
    status_value = user_profile.status_value
    if not(status_value >= 1):
        retdict['exceldata'] = 'You haven\'t uploaded a file yet!'
    else:
        # Add link to download excel sheet
        retdict['exceldata'] = '<b>File path: </b> '+file_path

    if status_value >= 2:
        retdict['teacherdata'] = '<table id="Teachertable" class="table table-bordered table-hover table-sm table-dark">\
                                <thead>\
                                    <tr>\
                                    <th scope="col">##</th>\
                                    <th scope="col">Employee Name</th>\
                                    <th scope="col">ERP</th>\
                                    <th scope="col">Slot</th>\
                                    <th scope="col">Subject</th>\
                                    </tr>\
                                </thead><tbody>'
        tabspace = '&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;'
        dataframe = convert_file_to_df(str(user_profile.data_file))
        count = 1
        for i, j in selected_teachers_cleaned.items():
            teacherstring = ''
            for teacher in j:
                if ' ' in teacher:
                    teachers = teacher.split(' ')
                else:
                    teachers = [teacher]
                for teacher in teachers:
                    course_code, erpid = teacher.split(':')
                    slots = ", ".join(dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (
                        dataframe[ERP_ID] == erpid)][SLOT].unique())
                    name = dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (
                        dataframe[ERP_ID] == erpid)][EMPLOYEE_NAME].unique()[0]
                    cname = dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (
                        dataframe[ERP_ID] == erpid)][COURSE_TITLE].unique()[0]
                    teacherstring += '<tr>\
                                            <th scope="row">'+str(count)+'</th>\
                                            <td>'+name+'</td>\
                                            <td>'+erpid+'</td>\
                                            <td>'+slots+'</td>\
                                            <td>'+cname+'</td>\
                                        </tr>'
                    count += 1
            retdict['teacherdata'] += teacherstring

        retdict['teacherdata'] += '</tbody></table>'
        total_timetables = user_profile.timetable_count
        retdict['teacherdata'] += '&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;Total number of valid timetables calculated: ' + \
            str(total_timetables)

    else:
        retdict['teacherdata'] = 'You haven\'t chosen any teachers yet!'

    tick_excel = '<span class="badge bg-success rounded-pill"><i class="fa fa-check" aria-hidden="true"></i></span>' \
        if status_value >= 1 else '<span class="badge bg-danger rounded-pill"><i class="fas fa-times"></i></span>'
    tick_teachers = '<span class="badge bg-success rounded-pill"><i class="fa fa-check" aria-hidden="true"></i></span>' \
        if status_value >= 2 else '<span class="badge bg-danger rounded-pill"><i class="fas fa-times"></i></span>'
    tick_filters = '<span class="badge bg-success rounded-pill"><i class="fa fa-check" aria-hidden="true"></i></span>' \
        if status_value >= 3 else '<span class="badge bg-danger rounded-pill"><i class="fas fa-times"></i></span>'
    tick_timetables = '<span class="badge bg-success rounded-pill"><i class="fa fa-check" aria-hidden="true"></i></span>' \
        if status_value >= 4 else '<span class="badge bg-danger rounded-pill"><i class="fas fa-times"></i></span>'
    tick_priority = '<span class="badge bg-success rounded-pill"><i class="fa fa-check" aria-hidden="true"></i></span>' \
        if status_value >= 5 else '<span class="badge bg-danger rounded-pill"><i class="fas fa-times"></i></span>'
    retdict['status_details'] = '<ul class="list-group px-5">\
                                    <li class="list-group-item d-flex justify-content-between align-items-center py-1 bg-dark text-light">\
                                        Uploaded Excel Sheet'+tick_excel+'\
                                    </li>\
                                    <li class="list-group-item d-flex justify-content-between align-items-center py-1 bg-dark text-light">\
                                        Chose Teachers'+tick_teachers+'\
                                    </li>\
                                    <li class="list-group-item d-flex justify-content-between align-items-center py-1 bg-dark text-light">\
                                        Chose Filters'+tick_filters+'\
                                    </li>\
                                    <li class="list-group-item d-flex justify-content-between align-items-center py-1 bg-dark text-light">\
                                        Shortlisted Timetables'+tick_timetables+'\
                                    </li>\
                                    <li class="list-group-item d-flex justify-content-between align-items-center py-1 bg-dark text-light">\
                                        Generated final priority list'+tick_priority+'\
                                    </li>\
                                </ul>'

    retdict['filters'] = ''
    if status_value >= 3:
        saved_filters = eval(user_profile.savefilters)
        # print(user_profile.savefilters)
        theory_pref, lab_pref = "Mixed", "Mixed"
        if 'pre-theory' in saved_filters['pre-post-lunch'][0]:
            theory_pref = "Morning"
        if 'post-theory' in saved_filters['pre-post-lunch'][0]:
            theory_pref = "Evening"
        if 'pre-lab' in saved_filters['pre-post-lunch'][0]:
            lab_pref = "Morning"
        if 'post-lab' in saved_filters['pre-post-lunch'][0]:
            lab_pref = "Evening"
        retdict['filters'] = '<table class="table table-sm table-bordered table-hover table-dark">\
                                <thead>\
                                    <tr>\
                                    <th scope="col">##</th>\
                                    <th scope="col">Field</th>\
                                    <th scope="col">Value</th>\
                                    </tr>\
                                </thead><tbody>\
                                    <tr>\
                                        <th scope="row">1</th>\
                                        <td>Theory preference</td>\
                                        <td>'+theory_pref+'</td>\
                                    </tr>\
                                    <tr>\
                                        <th scope="row">2</th>\
                                        <td>Lab preference</td>\
                                        <td>'+lab_pref+'</td>\
                                    </tr>\
                                    <tr>\
                                        <th scope="row">3</th>\
                                        <td>Max 8 o\'clock classes</td>\
                                        <td>'+saved_filters['8-classes'][0]+'</td>\
                                    </tr>\
                                    <tr>\
                                        <th scope="row">4</th>\
                                        <td>Max 2 o\'clock classes</td>\
                                        <td>'+saved_filters['2-classes'][0]+'</td>\
                                    </tr>\
                                        <tr>\
                                        <th scope="row">5</th>\
                                        <td>Max 6 o\'clock classes</td>\
                                        <td>'+saved_filters['6-classes'][0]+'</td>\
                                    </tr>\
                                    </tr>\
                                        <tr>\
                                        <th scope="row">6</th>\
                                        <td>Slots Ignored</td>\
                                        <td>'+saved_filters['slots'][0]+'</td>\
                                    </tr></tbody></table>'
    else:
        retdict['filters'] = 'You haven\'t chosen any filters yet!'

    try:
        ttid = eval(user_profile.save_order)['ttid'].strip()
        data = eval(user_profile.save_order)['data']
        ds = convert_df_to_ds_2(data, ttid)
        renderstr = ''
        count = 0
        for i in ds:
            crstype = i[0]
            crstitle = i[1]
            crsdata = i[2:]
            renderstr += '<table class="table table-sm table-bordered table-hover table-dark">\
                                    <thead>\
                                        <tr>\
                                        <th scope="col">##</th>\
                                        <th scope="col">Teacher Name</th>\
                                        <th scope="col">ERP ID</th>\
                                        <th scope="col">Slot</th>\
                                        <th scope="col">Course</th>\
                                        </tr>\
                                    </thead><tbody>'
            for j in crsdata:
                count += 1
                renderstr += '<tr>\
                                <th scope="row">'+str(count)+'</th>\
                                <td>'+j['name']+'</td>\
                                <td>'+j['erpid']+'</td>\
                                <td>'+j['slot']+'</td>\
                                <td>'+crstitle+' ('+crstype+')</td>\
                            </tr>'
            renderstr += '</tbody></table>'
        retdict['saved_teacher_list'] = renderstr
    except (SyntaxError, IndexError):
        retdict['saved_teacher_list'] = 'You haven\'t generated a teacher list yet!'

    return retdict


def savefilters(save_dict, user_object):
    # print(save_dict)
    form = ChangeFiltersForm(
        {'savefilters': str(save_dict)}, instance=user_object.profile)
    if form.is_valid():
        form.instance.user = user_object
        form.save()
    form = ChangeStatusForm(
        {'status_value': 3}, instance=user_object.profile)
    if form.is_valid():
        form.instance.user = user_object
        form.save()


def rectifyfiltersave(filter):
    new_filter = {}
    for i, j in eval(filter).items():
        new_filter.update({i: j[0]})
    return new_filter


def getselectedtt(user_object):
    saved_filters = rectifyfiltersave(user_object.profile.savefilters)
    query_data = query_database(saved_filters, user_object)
    return query_data


def get_teacher_data(user_object, teacher, count, slots, clean='no'):
    teacherstring = ''
    dataframe = convert_file_to_df(str(user_object.profile.data_file))
    teachers = teacher.split(' ')
    teacher_dict = {}
    for teacher in teachers:
        course_code, erpid = teacher.split(':')
        name = dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (
            dataframe[ERP_ID] == erpid)][EMPLOYEE_NAME].unique()[0]
        cname = dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (
            dataframe[ERP_ID] == erpid)][COURSE_TITLE].unique()[0]
        teacherstring += '<tr>\
                                <td>'+str(count)+'</td>\
                                <td>'+name+'</td>\
                                <td>'+course_code+'</td>\
                                <td>'+erpid+'</td>\
                                <td>'+slots+'</td>\
                                <td>'+cname+'</td>\
                            </tr>'
        teacher_dict.update({teacher: {'name': name, 'course_code': course_code,
                                       'erpid': erpid, 'slots': slots, 'cname': cname}})
    if clean == 'yes':
        return teacher_dict
    return teacherstring


def get_timetable_data_by_id(user_object, table_id, first='first'):
    returndata = {}
    timetable = Timetable.objects.filter(ttid=table_id)
    if len(timetable) != 1:
        return None
    else:
        timetable_lst = []
        entries = Entry.objects.filter(level=timetable[0])
        returndata['information_table'] = '<table id="Teachertable" class="table table-bordered table-hover table-sm table-dark">\
                                <tbody>\
                                    <tr>\
                                    <th scope="col">##</th>\
                                    <th scope="col">Employee Name</th>\
                                    <th scope="col">Course Code</th>\
                                    <th scope="col">ERP</th>\
                                    <th scope="col">Slot</th>\
                                    <th scope="col">Subject</th>\
                                    </tr>'
        # </thead><tbody>'
        count = 1
        returndata['information_dict'] = {}
        for i in entries:
            timetable_lst.append(i.slots+" "+i.course_code)
            returndata['information_table'] += get_teacher_data(
                user_object, i.class_code, count, i.slots)
            returndata['information_dict'].update(get_teacher_data(
                user_object, i.class_code, count, i.slots, 'yes'))
            count += 1
        returndata['information_table'] += '</tbody></table>'
        if first == 'first':
            returndata['render_timetable'] = timetable_to_html_str(
                timetable_lst)
        else:
            print("This got triggered?")
            returndata['render_timetable'] = timetable_lst
            del returndata['information_table']
        returndata['nickname'] = timetable[0].nickname
        return returndata
        # return timetable[0].ttid


def apicall_changenick_by_id(user_object, table_index, new_nick):
    selected_timetables = getselectedtt(user_object)
    timetable = selected_timetables[table_index]
    timetable.nickname = new_nick
    timetable.save(update_fields=['nickname'])
    return timetable.ttid


def apicall_changepriority_by_id(user_object, table_index, new_priority):
    selected_timetables = getselectedtt(user_object)
    timetable = selected_timetables[table_index]
    timetable.priority = new_priority
    timetable.save(update_fields=['priority'])
    return timetable.ttid

# render next timetable


def apicall_render_next(user_object, index_number, first="second"):
    returndata = {'index': index_number}

    selected_timetables = getselectedtt(user_object)
    returndata.update({'total': len(selected_timetables)})
    list_of_selected_timetables = [i.nickname for i in selected_timetables]
    if first == 'first':
        returndata['timetable_list'] = '<table id="timetablelist" class="table table-dark"><tbody style="width: 100%; display: table;">'
        index = 0
        for i in selected_timetables:
            if i.priority == 5:
                returndata['timetable_list'] += f'<tr id = "{index}" data-index="{index}" data-priority="{str(i.priority)}" onclick = "timetableChange()"><td id = \
                    "{"""nickname-"""+str(index)}" class="{"current" if index == 0 else ""}"><span id="displayNickname'+str(index)+'">'+f'#{index+1}: '+i.nickname +\
                    '</span><span id="displayPriority' + \
                    str(index)+'"><span class="badge badge-pill badge-success float-right">' + \
                    str(i.priority)+'</span></span></td></tr>'
            elif i.priority == 4:
                returndata['timetable_list'] += f'<tr id = "{index}" data-index="{index}" data-priority="{str(i.priority)}" onclick = "timetableChange()"><td id = \
                    "{"""nickname-"""+str(index)}" class="{"current" if index == 0 else ""}"><span id="displayNickname'+str(index)+'">'+f'#{index+1}: '+i.nickname +\
                    '</span><span id="displayPriority' + \
                    str(index)+'"><span class="badge badge-pill badge-primary float-right">' + \
                    str(i.priority)+'</span></span></td></tr>'
            elif i.priority == 3:
                returndata['timetable_list'] += f'<tr id = "{index}" data-index="{index}" data-priority="{str(i.priority)}" onclick = "timetableChange()"><td id = \
                    "{"""nickname-"""+str(index)}" class="{"current" if index == 0 else ""}"><span id="displayNickname'+str(index)+'">'+f'#{index+1}: '+i.nickname +\
                    '</span><span id="displayPriority' + \
                    str(index)+'"><span class="badge badge-pill badge-info float-right">' + \
                    str(i.priority)+'</span></span></td></tr>'
            elif i.priority == 2:
                returndata['timetable_list'] += f'<tr id = "{index}" data-index="{index}" data-priority="{str(i.priority)}" onclick = "timetableChange()"><td id = \
                    "{"""nickname-"""+str(index)}" class="{"current" if index == 0 else ""}"><span id="displayNickname'+str(index)+'">'+f'#{index+1}: '+i.nickname +\
                    '</span><span id="displayPriority' + \
                    str(index)+'"><span class="badge badge-pill badge-warning float-right">' + \
                    str(i.priority)+'</span></span></td></tr>'
            elif i.priority == 1:
                returndata['timetable_list'] += f'<tr id = "{index}" data-index="{index}" data-priority="{str(i.priority)}" onclick = "timetableChange()"><td id = \
                    "{"""nickname-"""+str(index)}" class="{"current" if index == 0 else ""}"><span id="displayNickname'+str(index)+'">'+f'#{index+1}: '+i.nickname +\
                    '</span><span id="displayPriority' + \
                    str(index)+'"><span class="badge badge-pill badge-danger float-right">' + \
                    str(i.priority)+'</span></span></td></tr>'
            elif i.priority == 0:
                returndata['timetable_list'] += f'<tr id = "{index}" data-index="{index}" data-priority="{str(i.priority)}" onclick = "timetableChange()"><td id = \
                    "{"""nickname-"""+str(index)}" class="{"current" if index == 0 else ""}"><span id="displayNickname'+str(index)+'">'+f'#{index+1}: '+i.nickname +\
                    '</span><span id="displayPriority'+str(index)+'"><span class="badge badge-pill badge-danger float-right">\
                <i class="fa fa-trash" aria-hidden="true"></i></span></span></td></tr>'
            index += 1
        returndata['timetable_list'] += '</tbody></table>'

    index_number = index_number % len(list_of_selected_timetables)
    if first == 'first':
        timetable_by_index = get_timetable_data_by_id(
            user_object, selected_timetables[index_number].ttid)
    else:
        timetable_by_index = get_timetable_data_by_id(
            user_object, selected_timetables[index_number].ttid, 'second')
    returndata['nickname_render'] = selected_timetables[index_number].nickname
    returndata.update(timetable_by_index)
    return returndata


def sort_by_priority(element):
    return element.priority


def get_timetable_popup(user_object, ttid, nickname):
    ret_string = '''
    <a class="btn btn-info text-white" data-ttid="'''+ttid+'''" onclick="toggle_modal(myModal'''+ttid+''')" id="myBtn'''+ttid+'''">Show Timetable</a>
    <!-- The Modal -->
    <div id="myModal'''+ttid+'''" class="modal">

    <!-- Modal content -->
    <div class="modal-content">
        
        <div class="modal-header">
        
        <h2>'''+nickname+'''</h2>
        <span id="myModal'''+ttid+'''close" class="close">&times;</span>
        </div>
        <div class="modal-body">
        '''+f"<span id='{ttid}main'></span>\
            <span id='{ttid}info'></span> "+'''
        </div>
    </div>

    </div>'''
    return ret_string


def backend_genteachlist(user_object):
    all_timetables = getselectedtt(user_object)
    render_string = '''
    <table class="table">
    <tbody>
        <tr>
        <th scope="col">#</th>
        <th scope="col">Timetable Nickname</th>
        <th scope="col">Timetable</th>
        <th scope="col">Prioriry</th>
        <th scope="col">Generate List</th>
        </tr>
    '''
    all_timetables = sorted(all_timetables, key=sort_by_priority, reverse=True)
    count = 1
    for i in all_timetables:
        if i.priority != 0:
            if i.priority == 1:
                prstr = '<span class="badge badge-pill badge-danger">1</span>'
            elif i.priority == 2:
                prstr = '<span class="badge badge-pill badge-warning">2</span>'
            elif i.priority == 3:
                prstr = '<span class="badge badge-pill badge-info">3</span>'
            elif i.priority == 4:
                prstr = '<span class="badge badge-pill badge-primary">4</span>'
            elif i.priority == 5:
                prstr = '<span class="badge badge-pill badge-success">5</span>'
            render_string += '''
            <tr>
            <th scope="row">'''+str(count)+'''</th>
            <td>'''+i.nickname+'''</td>
            <td>'''+get_timetable_popup(user_object, i.ttid, i.nickname)+'''</td>
            <td>'''+prstr+'''</td>
            <td><a class="btn btn-primary text-white" data-ttid="'''+i.ttid+'''" onclick="showTimetable()" id="GoBtn'''+i.ttid+'''">Show List</a></td>
            </tr>
            '''
            count += 1
    render_string += '</tbody>'
    return {"display_table": render_string}


def apicall_timetable_boilerplate() -> str:
    filepath = base_dir+"/oeffcs/templates/oeffcs/timetable.html"
    with open(filepath, 'r') as obj:
        all_text = obj.read()
        return {
            "timetable": all_text
        }


def display_teacher_list_temp(user_object, ttid):
    timetable = get_timetable_data_by_id(user_object, ttid)
    info_dict = timetable['information_dict']
    # print(info_dict)
    # try:
    #     ds2 = eval(user_object.profile.save_order)
    #     ds2 = convert_df_to_ds_2(ds2['data'], ds2['ttid'])
    #     info_dict2 = {}
    #     for i in ds2:
    #         course_name, course_code = " ".join(i[1].split('(')[:-1]), i[1].split('(')[-1].replace(')','')
    #         print(course_code, course_name)
    #         data = i[2:]
    #         for i in data:
    #             temp = {}
    #             temp['name'] = i['name']
    #             temp['course_code'] = course_code
    #             temp['erpid'] = i['erpid']
    #             temp['slots'] = i['slot']
    #             temp['cname'] = course_name
    #             info_dict2.update({course_code+':'+i['erpid']:temp})
    #     print(info_dict2)

    #     info_dict = info_dict2
    # except SyntaxError:
    #     pass
    render_dict = {}
    for i, data in info_dict.items():
        if i.split(":")[0] in render_dict.keys():
            render_dict[i.split(":")[0]] += '<tr>\
                                <td>'+data['name']+'</td>\
                                <td>'+data['course_code']+'</td>\
                                <td>'+data['erpid']+'</td>\
                                <td>'+data['slots']+'</td>\
                                <td>'+data['cname']+'</td>\
                            </tr>'
        else:
            render_dict[i.split(":")[0]] = '<tr>\
                                <td>'+data['name']+'</td>\
                                <td>'+data['course_code']+'</td>\
                                <td>'+data['erpid']+'</td>\
                                <td>'+data['slots']+'</td>\
                                <td>'+data['cname']+'</td>\
                            </tr>'
    for i in render_dict.keys():
        render_dict[i] = '<table class="table table-bordered table-hover table-sm table-dark">\
                                <thead>\
                                    <tr>\
                                    <th scope="col">Employee Name</th>\
                                    <th scope="col">Course Code</th>\
                                    <th scope="col">ERP</th>\
                                    <th scope="col">Slot</th>\
                                    <th scope="col">Subject</th>\
                                    </tr></thead><tbody class="moovable" id="tbody'+i+'">' + render_dict[i] + '</tbody></table>'

    final_render = '<div class="thunder">'
    for i in render_dict.values():
        final_render = final_render+i
    final_render = final_render + '</div>'
    return {'render_timetable': timetable['render_timetable'], 'render_demo': final_render, "ttid": ttid, 'nickname': timetable['nickname']}
    # return {'ttid':ttid,'render_demo':final_render}


def convert_df_to_ds_2(data, ttid):
    ttid = ttid.strip()
    # data = eval(user_object.profile.save_order)['data']
    # ttid = eval(user_object.profile.save_order)['ttid']
    author_object = Timetable.objects.filter(ttid=ttid)[0].level.user
    entry = Entry.objects.filter(level=Timetable.objects.filter(ttid=ttid)[0])
    dataframe = convert_file_to_df(str(author_object.profile.data_file))
    listofdict = []
    course_type_stuff = author_object.profile.course_type
    for i in data:
        course_list = []
        coursecode = i[0]
        teachers = i[1]
        # this needs to be an indivisual table
        newdataframe = dataframe.query('`'+COURSE_CODE+'` == "'+coursecode+'"')
        for j in teachers:
            j = j.strip()
            temp = {}
            temp['erpid'] = j
            temp['slot'] = entry.filter(
                class_code__contains=coursecode+":"+j)[0].slots
            temp['name'] = dataframe.query(
                '`'+COURSE_CODE+'` == "'+coursecode+'" and `'+ERP_ID+'` == "'+j+'"').iloc[0][EMPLOYEE_NAME]
            temp['chosen'] = 'C'
            course_list.append(temp)
        listofdict.append([eval(course_type_stuff)[i[0]],
                           newdataframe[COURSE_TITLE].unique()[0] + ' (' + newdataframe[COURSE_CODE].unique()[0] + ')'] + course_list)
    return listofdict


def apicall_finalpage(user_object):
    def get_slot_from_code(code):
        slots = {}
        course_code, teacher_code = code.split(':')
        # print(code)
        teacher_rows = dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (
            dataframe[ERP_ID] == teacher_code)]
        for index, row in teacher_rows.iterrows():
            try:
                slots[row[COURSE_TYPE]].append(row[SLOT])
            except:
                slots[row[COURSE_TYPE]] = [row[SLOT]]
        combinations = product(*list(slots.values()))
        combined = []
        for i in combinations:
            combined.append("+".join(i) + ' ' + code)
        return combined
    data = eval(user_object.profile.save_order)['data']
    ttid = eval(user_object.profile.save_order)['ttid']
    author_object = Timetable.objects.filter(ttid=ttid.strip())[0].level.user
    entry = Entry.objects.filter(
        level=Timetable.objects.filter(ttid=ttid.strip())[0])
    dataframe = convert_file_to_df(str(author_object.profile.data_file))
    course_type_stuff = author_object.profile.course_type
    listofdict = []
    for i in data:
        course_list = []
        coursecode = i[0]
        teachers = i[1]
        # this needs to be an indivisual table

        newdataframe = dataframe.query('`'+COURSE_CODE+'` == "'+coursecode+'"')
        for j in teachers:
            temp = {}
            temp['erpid'] = j
            temp['slot'] = entry.filter(
                class_code__contains=coursecode+":"+j)[0].slots
            temp['name'] = dataframe.query(
                '`'+COURSE_CODE+'` == "'+coursecode+'" and `'+ERP_ID+'` == "'+j+'"').iloc[0][EMPLOYEE_NAME]
            temp['chosen'] = 'C'
            course_list.append(temp)
            # NIL

        donelist = []
        for data in newdataframe.iterrows():
            if coursecode+':'+data[1][ERP_ID] not in donelist:
                slots = [i.split(' ')[0] for i in get_slot_from_code(
                    coursecode+':'+data[1][ERP_ID])]
                donelist.append(coursecode+':'+data[1][ERP_ID])
                for slot in slots:
                    if (data[1][ERP_ID] in [i['erpid'] for i in course_list] and slot in [i['slot'] for i in course_list]):
                        if [i['erpid'] for i in course_list].index(data[1][ERP_ID]) == [i['slot'] for i in course_list].index(slot):
                            pass
                        else:
                            temp = {}
                            temp['erpid'] = data[1][ERP_ID]
                            temp['slot'] = slot
                            temp['name'] = data[1][EMPLOYEE_NAME]
                            temp['chosen'] = 'R'
                            course_list.append(temp)
                    else:
                        temp = {}
                        temp['erpid'] = data[1][ERP_ID]
                        temp['slot'] = slot
                        temp['name'] = data[1][EMPLOYEE_NAME]
                        temp['chosen'] = 'R'
                        course_list.append(temp)
        listofdict.append([eval(course_type_stuff)[
                          i[0]], newdataframe[COURSE_TITLE].unique()[0] + ',' + coursecode] + course_list)

    new_datastructure = []
    for subject in listofdict:
        course_type = subject[0]
        course_name = subject[1]
        data = subject[2:]
        c_courses = []
        r_courses = []
        for teacher in data:
            if teacher['chosen'] == 'C':
                if teacher['slot'] not in [i['slot'] for i in c_courses]:
                    # index = [i['slot'] for i in c_courses].index(teacher['slot'])
                    temp = {}
                    temp['erpid'] = [teacher['erpid']]
                    temp['slot'] = teacher['slot']
                    temp['name'] = [teacher['name']]
                    temp['chosen'] = 'C'
                    c_courses.append(temp)
                else:
                    index = [i['slot']
                             for i in c_courses].index(teacher['slot'])
                    # print(temp['erpid'])
                    c_courses[index]['erpid'].append(teacher['erpid'])
                    c_courses[index]['name'].append(teacher['name'])
                    # print(c_courses[index]['erpid'])
            else:
                if teacher['slot'] not in [i['slot'] for i in r_courses]:
                    # index = [i['slot'] for i in c_courses].index(teacher['slot'])
                    temp = {}
                    temp['erpid'] = [teacher['erpid']]
                    temp['slot'] = teacher['slot']
                    temp['name'] = [teacher['name']]
                    temp['chosen'] = 'R'
                    r_courses.append(temp)
                else:
                    index = [i['slot']
                             for i in r_courses].index(teacher['slot'])
                    # print(temp['erpid'])
                    r_courses[index]['erpid'].append(teacher['erpid'])
                    r_courses[index]['name'].append(teacher['name'])
                    # print(c_courses[index]['erpid'])
        new_datastructure.append(
            [course_type, course_name] + c_courses + r_courses)
    print(new_datastructure)
    return new_datastructure
