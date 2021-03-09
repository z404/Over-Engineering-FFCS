import itertools
from script import printer

datadict = {}
with open('input.txt') as file:
    data = file.readlines()
subjectname = ''
for i in data:
    if len(i.split(',')) == 1:
        subjectname = i.rstrip('\n')
    else:
        teachername,timeslot = [j.rstrip('\n') for j in i.split(',')]
        try:
            datadict[subjectname].append(timeslot+' '+teachername)
        except:
            datadict[subjectname] = [timeslot+' '+teachername]

numofsubjects = len(datadict)
subjectnames = list(datadict.keys())

totallist = [i for i in datadict.values()]
totallist = [i for i in itertools.product(*totallist)]

def check_if_valid_timetable(lst):
    classeslst = []
    new_classeslst = []
    for i in lst:
        classeslst.extend(i.split(' ')[0].split('+'))
    for i in classeslst:
        if i[0] == 'L':
            replacedict = {'L14':'A1','L15':'F1','L19':'D1','L4':'TB1','L5':'TG1','L6':'L6','L20':'B1','L21':'G1','L25':'E1','L10':'TC1',\
                            'L11':'TAA1','L12':'L12','L26':'C1','L16':'V1','L17':'V2','L18':'L18','L22':'TE1','L23':'TCC1','L24':'L24','L27':\
                            'TA1','L28':'TF1','L29':'TD1','L30':'L30','L1':'A1','L2':'F1','L3':'B1','L7':'B1','L8':'G1','L9':'E1','L13':'C1'}
            if int(i[1:])>30:
                return False, None
            else:
                if replacedict[i] in new_classeslst:
                    return False, None
                new_classeslst.append(replacedict[i])
        else:
            if i in new_classeslst:
                return False, None
            new_classeslst.append(i)
    return True,lst
    

count = 0
print(len(totallist))
for i in totallist:
    print(count)
    count+=1
    a = check_if_valid_timetable(i)
    if a[0] == True:
        with open('tt.csv','a+') as file:
            file.write(str(a[1])+'\n')
        printer(a[1])
