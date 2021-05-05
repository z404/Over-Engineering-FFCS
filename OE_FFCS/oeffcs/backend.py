import pandas as pd


def convertToForm(filepath):
    dataframe = pd.read_excel("media/"+filepath)
    dataframe.fillna(method = "ffill", inplace = True)
    
    #THE CODE HERE IS SPECIFIC TO LAST YEAR'S STRUCTURE
    #WHEN THE NEW SHEET COMES, MODIFY THIS PART OF CODE TO CHANGE READ STRUCTURE
    #FOR NOW, WE ARE USING MID SLOT DETAILS, AS IT HAS TEACHER'S NAMES

    #CONVERT DATAFRAME INTO DATASTRUCTURE: {"<COURSE NAME>;<COURSE CODE>": {<COURSE TYPE>: ["<TEACHER NAMES>;<ERP ID>"]}}
    #print(dataframe.head())
    
    dataframe.drop(["CLASS ID", "EMPLOYEE SCHOOL"], axis = 1, inplace = True)
    subjects = dataframe['COURSE TITLE'].unique()

    totaldictionary = {}

    for index, row in dataframe.iterrows():
        course_title = row['COURSE TITLE'] +' ('+ row['COURSE CODE']+')'
        employee_name = row['EMPLOYEE NAME'] + ' ('+ row['ERP ID']+')'
        if course_title not in totaldictionary.keys():
            totaldictionary.update({course_title:{row['COURSE TYPE']:[employee_name]}})
        elif row['COURSE TYPE'] not in totaldictionary[course_title].keys():
            totaldictionary[course_title].update({row['COURSE TYPE']:[employee_name]})
        else:
            if employee_name not in totaldictionary[course_title][row['COURSE TYPE']]:
                totaldictionary[course_title][row['COURSE TYPE']].append(employee_name)
            
    #DATASTRUCTURE IS READY, RENDER FORM
    form = ""
    count = 1
    for key,val in totaldictionary.items():
        subject, code, *trash = [i.rstrip(' )') for i in key.split('(')]
        form+='<input type="checkbox" class="subjectcheckbox'+str(count)+'" name="'+code+'" value="'+\
            code+'" onclick=toggleview("'+"teacherlist"+str(count)+'")>'
        form+='<label for="'+code+'"> '+subject+'</label><br>'
        form+='<span style="display: none;" id="teacherlist'+str(count)+'">'
        for c_type, teacherlist in val.items():
            form+='&emsp; <label class="coursetype">'+c_type+'</label><br>'
            for teacher in teacherlist:
                teachername, teachercode, *trash = [i.rstrip(' )') for i in teacher.split('(')]
                form+='&emsp; &emsp; <input type="checkbox" class="teachercheckbox" name="'+code+'" value="'+code+':'+teachercode+'">'
                form+='<label for="'+code+'"> '+teacher+'</label><br>'
        form+='</span>'
        count += 1
    form+='<button type="submit" form="form1" value="Submit">Submit</button>'

    return form
