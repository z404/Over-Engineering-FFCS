import pandas as pd
from django.conf import settings

base_dir = str(settings.BASE_DIR).replace('\\', '/')


def convertToForm(filepath):
    dataframe = pd.read_excel(base_dir+"/media/"+filepath)
    print(base_dir+"/media/"+filepath)
    dataframe.fillna(method="ffill", inplace=True)

    # THE CODE HERE IS SPECIFIC TO LAST YEAR'S STRUCTURE
    # WHEN THE NEW SHEET COMES, MODIFY THIS PART OF CODE TO CHANGE READ STRUCTURE
    # FOR NOW, WE ARE USING MID SLOT DETAILS, AS IT HAS TEACHER'S NAMES

    # CONVERT DATAFRAME INTO DATASTRUCTURE: {"<COURSE NAME>;<COURSE CODE>": {<COURSE TYPE>: ["<TEACHER NAMES>;<ERP ID>"]}}
    # print(dataframe.head())

    dataframe.drop(["CLASS ID", "EMPLOYEE SCHOOL"], axis=1, inplace=True)
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
    finaldata = {}
    for subject, courses in totaldictionary.items():
        course_types = list(courses.keys())
        if course_types == ['ELA', 'ETH'] or course_types == ['ETH', 'ELA']:
            theory = courses['ETH']
            lab = courses['ELA']
            for i in range(len(theory)):
                theory[i] = theory[i] + \
                    ' (' + str(lab.count(theory[i])) + ' Lab class(es))'
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
                teachername, teachercode, * \
                    trash = [i.rstrip(' )') for i in teacher.split('(')]
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
    print(filepath)
    with open(filepath, 'r') as obj:
        all_text = obj.read()
        # print(all_text)
        print(lst)
        for enrollment in lst:
            slots_in_enrollment = enrollment.split()[0].split('+')
            enrollment_data = " ".join(enrollment.split()[1:])
            print(slots_in_enrollment)
            for slot in slots_in_enrollment:
                all_text = all_text.replace(conventional(slot), activated(
                    slot+'<br>'+enrollment_data))
        print("For loops completed\n*******\n")  # +all_text
        filepath2 = base_dir+"/oeffcs/templates/oeffcs/testing.html"
        testfile = open(filepath2, 'w')
        testfile.write(all_text)
        testfile.close()
    return all_text
