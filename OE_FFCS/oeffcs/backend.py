from numpy.core.fromnumeric import prod
from numpy.lib.npyio import save
import pandas as pd
from django.conf import settings
from itertools import product
from .forms import ChangeStatusForm
from .models import Profile, Timetable, Entry
from collections import Counter

base_dir = str(settings.BASE_DIR).replace('\\', '/')

# Coulmn names, if needed to be changed later
COURSE_CODE = 'COURSE CODE'
COURSE_TITLE = 'COURSE TITLE'
COURSE_TYPE = 'COURSE TYPE'
SLOT = 'SLOT'
ERP_ID = 'ERP ID'
EMPLOYEE_NAME = 'EMPLOYEE NAME'

COURSE_ELA = 'ELA'
COURSE_ETH = 'ETH'

# !! Add saturday and sunday classes too !!
dict_conv = {
        'A1':['L1','L14'], 'B1':['L7','L20'], 'C1':['L13','L26'], 'D1':['L19','L3'], 'E1':['L25','L9'], 'F1':['L2','L15'],\
        'G1':['L8','L21'], 'TA1':['L27'], 'TB1':['L4'], 'TC1':['L10'], 'V1':['L16'], 'TE1':['L22'], 'TF1':['L28'], 'TG1':['L5'],\
        'TAA1':['L11'], 'V2':['L17'], 'TCC1':['L23'], 'TD1':['L29'],\
        'A2':['L31','L44'], 'B2':['L37','L50'], 'C2':['L43','L56'], 'D2':['L49','L33'], 'E2':['L55','L39'], 'F2':['L32','L45'],\
        'G2':['L38','L51'], 'TA2':['L57'], 'TB2':['L34'], 'TC2':['L40'], 'TD2':['L46'], 'TE2':['L52'], 'TF2':['L58'], 'TG2':['L35'],\
        'TAA2':['L41'], 'TBB2':['L47'], 'TCC2':['L53'], 'TDD2':['L59']
        }

morning_theory = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1','G1', 'TA1', 'TB1', 'TC1', 'V1', 'TE1', 'TF1', 'TG1', 'TAA1', 'V2', 'TCC1', 'TD1']

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
    required_columns = [COURSE_CODE, COURSE_TITLE, COURSE_TYPE, SLOT, ERP_ID, EMPLOYEE_NAME]
    dataframe = dataframe[required_columns]

    return dataframe

def convert_df_to_ds(dataframe):
    #List of subjects
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
                lab_count = get_lab_count(subject.split('(')[-1].rstrip(')'), courses[COURSE_ETH][i].split('(')[-1].rstrip(')'))
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #What do we do when lab count is 0?
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

    def add_subject(self, subject, subject_code):
        # Creating checkbox for subject
        self.form += '<input id ="' + subject_code + '" \
                type="checkbox" \
                class="subjectcheckbox'+str(self.count)+'" \
                name="'+subject_code+'" \
                value="'+subject_code+'" \
                onclick=toggleview("'+"teacherlist" + str(self.count)+'") \
                autocomplete="off">'
        
        # Creating lable for checkbox
        self.form += '<label for="'+subject_code+'"> '+subject+'</label><br>'

        # Creating span to hold and hide teacher names
        self.form += '<span style="display: none;" id="teacherlist'+str(self.count)+'">'

        # Increment count for subjects
        self.count += 1

    def add_course_type(self, course_type):
        # Adding label for course type
        # !! Inside span of subject !!
        self.form += '&emsp; <label class="coursetype">'+course_type+'</label><br>'

    def add_teacher(self, teacher, subject_code, teacher_code):
        # Adding checkbox for teacher 
        self.form += '&emsp; &emsp; <input id="'+ teacher+subject_code +'" \
                    type="checkbox" \
                    class="teachercheckbox" \
                    name="'+subject_code+'" \
                    value="'+subject_code+':'+teacher_code+'" \
                    autocomplete="off">'
        
        # Adding lable for teacher name
        self.form += '<label for="'+teacher+subject_code+'"> '+teacher+'</label><br>'

    def close_subject(self):
        # Adding a closing span tag for subject
        self.form += '</span>'

    def output(self):
        # Returning form with submit button at the end
        return self.form + '<button type="submit" form="form1" value="Submit">Submit</button>'

def convertToForm(filepath):
    # Getting datastructure from file
    finaldata = convert_df_to_ds(convert_file_to_df(filepath))
    
    # FORM object
    form2 = FORM()

    # Iterating through data
    for subject_data, course_info in finaldata.items():
        # Extract subject and subject code
        subject, code, *trash = [i.rstrip(' )') for i in subject_data.split('(')]
        # Pass to form
        form2.add_subject(subject, code)

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
                    trash, teachercode, *trash = [i.rstrip(' )') for i in teacher.split('(')]
                else:
                    teachercode = teacher.split(' (')[-1].rstrip(' )')
                # Add teacher to form
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
        filepath2 = base_dir+"/oeffcs/templates/oeffcs/testing.html"
        testfile = open(filepath2, 'w')
        testfile.write(all_text)
        testfile.close()
    return all_text

def generate_time_tables(user_object):
    saved_teachers = eval(user_object.profile.saveteachers)
    teacher_db = user_object.profile.data_file
    dataframe = convert_file_to_df(str(teacher_db))
    list_saved = list(saved_teachers.values())
    list_cleaned = []

    def get_slot_from_code(code):
        slots = {}
        course_code, teacher_code = code.split(':')
        # print(code)
        teacher_rows = dataframe.loc[(dataframe[COURSE_CODE] == course_code) & (dataframe[ERP_ID] == teacher_code)]
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

    #ALL SLOTS RECORDED
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
                subjectlst[slot] =  teachers
        merged_combo.append([key+' '+value for key,value in subjectlst.items()])
    all_combinations = list(product(*merged_combo))
    print(len(all_combinations),"Combinations found!")

    validated = []
    for i in all_combinations:
        validate_result = validate_timetable(i)
        if validate_result[0]:
            validated.append([i,validate_result])
    print(len(validated), "Combinations valid!")

    save_timetable(validated, user_object)

def validate_timetable(timetable):
    slots = []
    theory = ''
    lab = ''

    for i in timetable:
        slots.extend(i.split(' ')[0].split('+'))
    if len(slots) != len(set(slots)): return False
    slots_cleaned = []
    for i in slots:
        if i in dict_conv.keys():
            if theory != 'mixed':
                if i in morning_theory and theory == '': theory = 'morning'
                elif i not in morning_theory and theory == '': theory = 'evening'
                elif i in morning_theory and theory == 'evening': theory = 'mixed'
                elif i not in morning_theory and theory == 'morning': theory = 'mixed'
            slots_cleaned.extend(dict_conv[i])
        else: 
            if lab != 'mixed':
                inti = int(i[1:])
                if inti <= 30 and lab == '': lab = 'morning'
                elif inti > 30 and lab == '': lab = 'evening'
                elif inti <= 30 and lab == 'evening': lab = 'mixed'
                elif inti > 30 and lab == 'morning': lab = 'mixed'
            slots_cleaned.append(i)

    if len(slots_cleaned) == len(set(slots_cleaned)):
        totalcounter = Counter(slots_cleaned)
        total8 = totalcounter['L1'] + totalcounter['L7'] + totalcounter['L13'] + totalcounter['L19'] + totalcounter['L25']
        total6 = totalcounter['L35'] + totalcounter['L41'] + totalcounter['L47'] + totalcounter['L53'] + totalcounter['L59']
        total2 = totalcounter['L31'] + totalcounter['L37'] + totalcounter['L43'] + totalcounter['L49'] + totalcounter['L55']

        return (True, total8, total2, total6, theory, lab)
    else: return (False,)

def save_timetable(time_tables_data, user):
    # Save to user profile, update status number
    form = ChangeStatusForm(
        {'status_value': 2}, instance=user.profile)
    if form.is_valid():
        form.instance.user = user
        form.save()
    Timetable.objects.filter(level=user.profile).delete()
    for timetable, data in time_tables_data:
        temp_timeable = Timetable(
            level = user.profile,
             total8classes = data[1],
             total2classes = data[2],
             total6classes = data[3],
             theory_status = data[4],
             lab_status = data[5])
        temp_timeable.save()
        for entry in timetable:
            temp_entry=Entry(
                level = temp_timeable,
                slots=entry.split()[0],
                course_code=entry.split()[1].split(':')[0],
                class_code=' '.join(entry.split()[1:])
            )
            temp_entry.save()
    print('completed')

def query_database(params):
    pass