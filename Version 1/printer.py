import csv
import os.path
# file fixer
filename = 'timetable.txt'
with open(filename) as file_object:
    lines = file_object.readlines()[:-8]
hehe=0
#if os.path.isfile('output.csv'):
#    os.remove('output.csv')
def printer(lst):
    global hehe
    lst=list(lst)
    with open("output.csv", "a", newline='') as fp:
        wr= csv.writer(fp)
        for line in lines:
            line=line.split('    ')
            for word in range(len(line)):
                if '-' in line[word]:
                    hehe+=1
                    dashIndex=list(line[word]).index('-')
                    line[word]=line[word][:dashIndex]
            line[-1]=line[-1] if '\n' not in line[-1] else line[-1][:-1]
            for booking in lst:
                slots=booking.split()[0].split('+')
                print(slots)
                for slot in slots:
                    if slot in line:
                        line[line.index(slot)]+=':=>'+booking[booking.index(' ')+1:]
            wr.writerow(line)
            print((line))
    print('hehe:',hehe,'len(lines):',len(lines))

#printer(('L31+L32 KARPAGAM S', 'B2+TB2 PADALA KISHOR', 'L35+L36+L39+L40+L59+L60 SRIVANI A', 'L19+L20 SHARMILA BANU K', 'A1+TA1 PREETHA EVANGELINE D', 'C1+TC1+TCC1+V2 DEEPA G', 'L15+L16 GOWSALYA M', 'G1+TG1 GOWSALYA M'))
