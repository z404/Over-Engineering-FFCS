from numpy.core.fromnumeric import prod
from numpy.lib.npyio import save
import pandas as pd
from django.conf import settings
from itertools import product

base_dir = str(settings.BASE_DIR).replace('\\', '/')

def convert_file_to_df(filepath):
    dataframe = pd.read_excel(base_dir+"/media/"+filepath)
    dataframe.fillna(method="ffill", inplace=True)

    # THE CODE HERE IS SPECIFIC TO LAST YEAR'S STRUCTURE
    # WHEN THE NEW SHEET COMES, MODIFY THIS PART OF CODE TO CHANGE READ STRUCTURE
    # FOR NOW, WE ARE USING MID SLOT DETAILS, AS IT HAS TEACHER'S NAMES

    # CONVERT DATAFRAME INTO DATASTRUCTURE: {"<COURSE NAME>;<COURSE CODE>": {<COURSE TYPE>: ["<TEACHER NAMES>;<ERP ID>"]}}
    # print(dataframe.head())

    dataframe.drop(["CLASS ID", "EMPLOYEE SCHOOL"], axis=1, inplace=True)
    # print(dataframe.tail())
    return dataframe

def convertToForm(filepath):
    dataframe = convert_file_to_df(filepath)
    subjects = dataframe['COURSE TITLE'].unique()

    totaldictionary = {}

    for index, row in dataframe.iterrows():
        course_title = row['COURSE TITLE'] + ' (' + row['COURSE CODE']+')'
        employee_name = row['EMPLOYEE NAME'] + ' (' + row['ERP ID']+')'
        if course_title not in totaldictionary.keys():
            totaldictionary.update(
                {course_title: {row['COURSE TYPE']: [employee_name]}})
        elif row['COURSE TYPE'] not in totaldictionary[course_title].keys():
            totaldictionary[course_title].update(
                {row['COURSE TYPE']: [employee_name]})
        else:
            if employee_name not in totaldictionary[course_title][row['COURSE TYPE']]:
                totaldictionary[course_title][row['COURSE TYPE']].append(
                    employee_name)

    # REMOVE ELA FROM ANY THAT HAVE ETH
    # print(totaldictionary)
    def get_lab_count(subject, teacher):
        shortened = dataframe.loc[(dataframe['COURSE CODE'] == subject) & (dataframe['COURSE TYPE'] == 'ELA') & (dataframe['ERP ID'] == teacher)]
        return len(shortened)

    finaldata = {}
    for subject, courses in totaldictionary.items():
        print()
        course_types = list(courses.keys())
        if course_types == ['ELA', 'ETH'] or course_types == ['ETH', 'ELA']:
            theory = courses['ETH']
            lab = courses['ELA']
            for i in range(len(theory)):
                lab_count = get_lab_count(subject.split('(')[-1].rstrip(')'), theory[i].split('(')[-1].rstrip(')'))
                theory[i] = theory[i] + \
                    ' (' + str(lab_count) + ' Lab class(es))'
            finaldata.update({subject: {'ETH': theory}})
        else:
            finaldata.update({subject: courses})
    # print(finaldata)

    # DATASTRUCTURE IS READY, RENDER FORM
    form = ""
    count = 1
    for key, val in finaldata.items():
        subject, code, *trash = [i.rstrip(' )') for i in key.split('(')]
        form += '<input type="checkbox" class="subjectcheckbox'+str(count)+'" name="'+code+'" value="' +\
            code+'" onclick=toggleview("'+"teacherlist" + \
            str(count)+'") autocomplete="off">'
        form += '<label for="'+code+'"> '+subject+'</label><br>'
        form += '<span style="display: none;" id="teacherlist'+str(count)+'">'
        for c_type, teacherlist in val.items():
            form += '&emsp; <label class="coursetype">'+c_type+'</label><br>'
            for teacher in teacherlist:
                if 'APT' not in teacher:
                    teachername, teachercode, *trash = [i.rstrip(' )') for i in teacher.split('(')]
                else:
                    teachercode = teacher.split(' (')[-1].rstrip(' )')
                form += '&emsp; &emsp; <input type="checkbox" class="teachercheckbox" \
                    name="'+code+'" value="'+code+':'+teachercode+'" autocomplete="off">'
                form += '<label for="'+code+'"> '+teacher+'</label><br>'
        form += '</span>'
        count += 1
    form += '<button type="submit" form="form1" value="Submit">Submit</button>'

    return form


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
        teacher_rows = dataframe.loc[(dataframe['COURSE CODE'] == course_code) & (dataframe['ERP ID'] == teacher_code)]
        for index, row in teacher_rows.iterrows():
            try:
                slots[row['COURSE TYPE']].append(row['SLOT'])
            except:
                slots[row['COURSE TYPE']] = [row['SLOT']]
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

    print(total_combo)
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