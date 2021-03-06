import sys
from tkinter import *
from tkinter.filedialog import askopenfilename
import os
import subprocess
import platform
import random
from PIL import Image, ImageTk

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
completePreferences = []
penaltyAmount = []
preference = 0

files = []  # Holds the content of opened files
attributeToNumber = {}  # Dictionary mapping words in atributes file to numbers for CLASP input
hcFeasibleObjects = []

option = 0
preferenceFile = 0


#######################################################################################################
def setUpAttribute():
    attributes = files[0].split()
    totalNumberOfAttributes = int(len(attributes) / 3)
    for a in range(1, totalNumberOfAttributes + 1):
        # assigning numbers to attributes. Either x or -x
        attributeToNumber[attributes[(a * 3 - 2)]] = a
        attributeToNumber[attributes[(a * 3 - 1)]] = -1 * a
    return attributeToNumber


#######################################################################################################
def setupHardConstraints():
    # conversion replaces the words in the hard constraints file with their numeric value from attributeToNumber dict
    constraints = str(files[1]).splitlines()
    newNumbers = []
    newLines = 0
    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal
    for line in constraints:
        words = line.split()
        conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        line = conversion.split()
        skip = 0
        for pos in range(len(line)):
            if skip == 1:
                skip = 0
                continue
            if line[pos] == 'NOT':
                # if there's a NOT, multiplies the next element by -1
                line[pos + 1] = -1 * int(line[pos + 1])
                newNumbers.append(line[pos + 1])
                skip = 1
                continue
            if line[pos] == 'OR':
                continue

            if line[pos] != 'NOT' and line[pos] != 'OR':
                newNumbers.append(line[pos])
        newNumbers.append(0)
        newLines += 1
        newNumbers.append('\n')

    # add penalty to list penalty amount
    # cnfstring is going to be our input for CLASP
    booleanVars = len(attributeToNumber) / 2
    finalString = "p cnf " + str(int(booleanVars)) + " " + str(newLines) + "\n"
    num2 = int(len(newNumbers))
    for num in range(num2):
        if num < num2 and [num + 1] == '\n':
            finalString += str(newNumbers[num])
            continue
        if newNumbers[num] == '\n':
            finalString += str(newNumbers[num])
            continue
        finalString += str(newNumbers[num]) + " "
        if num == num2:
                finalString += str(newNumbers[num])
    return finalString
    # add complete clasp string to completePreferences



#######################################################################################################
def claspInput():
    cmdInput = setupHardConstraints()
    # the executable for clasp should be in the same place as this program
    with open("Output.txt", "w") as text_file:
        text_file.write(str(cmdInput))
    operatingSys = platform.system()
    if operatingSys == "Darwin":
        change = "cd " + ROOT_DIR
        claspIn = change + "; ./clasp-3.3.2-x86_64-macosx -n 0 Output.txt"
        claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, shell=True, text=True)
    else:
        claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe -n 0 Output.txt')
        claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, text=True)

    for line in claspExecute.stdout.splitlines():
        if line.__contains__('SATISFIABLE'):
            continue
        elif line.__contains__('UNSATISFIABLE'):
            continue
        elif line.__contains__('UNKNOWN'):
            continue
        elif line.startswith('v'):
            hcFeasibleObjects.append(line)

#######################################################################################################
## PENALTY LOGIC ##
def setupPreferences():
    preferenceObjects = str(files[2]).splitlines()

    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal

    for line in preferenceObjects:
        words = line.split()
        newLines = 1

        preferenceconversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        tempTest = preferenceconversion.split()
        for pos in range(len(tempTest)):
            if tempTest[pos] == 'NOT':
                # if there's a NOT, multiplies the next element by -1
                tempTest[pos + 1] = -1 * int(tempTest[pos + 1])
                tempTest[pos] = " "
                # ctempTest.pop(pos)
                continue
            if tempTest[pos] == 'OR':
                # if there's an OR, does nothing and just skips
                tempTest[pos] = " "
                # tempTest.pop(pos)
                continue
            if tempTest[pos] == 'AND':
                # if there's an AND, we must start a new line in clasp
                # not sure how yet
                tempTest[pos] = '0\n'
                newLines += 1
                continue
        # add penalty to list penalty amount
        penaltyAmount.append(int(tempTest.pop()))
        # cnfstring is going to be our input for CLASP
        booleanVars = len(attributeToNumber) / 2
        cnfString = "p cnf " + str(int(booleanVars)) + " " + str(newLines) + "\n"
        for chunk in tempTest:
            if chunk == "0\n":
                cnfString += str(chunk)
            elif chunk == " ":
                continue
            else:
                cnfString += str(chunk) + ' '
        cnfString = cnfString + '0'
        # add complete clasp string to completePreferences
        completePreferences.append(cnfString)


def runningPreferences(value):
    # Start dictionary of feasible objects with a start of zero penalty 
    totalPenalty = {}
    for object in hcFeasibleObjects:
        totalPenalty[object] = 0

    counter = 0
    for claspInput in completePreferences:
        operatingSys = platform.system()
        cmdInput = claspInput
        with open("Output.txt", "w") as text_file:
            text_file.write(str(cmdInput))
        if operatingSys == "Darwin":
            change = "cd " + ROOT_DIR
            claspIn = change + "; ./clasp-3.3.2-x86_64-macosx -n 0 Output.txt"
            claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, shell=True, text=True)
        else:
            claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe -n 0 Output.txt')
            claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, text=True)
        for line in claspExecute.stdout.splitlines():
            if line.startswith('v'):
                # checks if preference objects are feasible
                if line in hcFeasibleObjects:
                    totalPenalty[line] += penaltyAmount[counter]
        counter += 1

    sortTotalPenalty = sorted(totalPenalty.items(), key=lambda x: x[1])
    # list of ordered objects from least penalty to most
    # this will get us the optimal object
    invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
    omniOptimal = []
    guiOUT = []
    for i in sortTotalPenalty:
        if i[1] == sortTotalPenalty[0][1]:
            omniOptimal.append(i)
    for entry in omniOptimal:
        toConvert = entry[0].split()[1:9]
        convertedOutput = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in toConvert)
        guiOUT.append(convertedOutput)
        guiOUT.append('\n')

    random1 = random.choice(sortTotalPenalty)
    random2 = random.choice(sortTotalPenalty)

    split1 = random1[0].split()
    split2 = random2[0].split()
    split1.remove('v')
    split2.remove('v')
    split1.remove('0')
    split2.remove('0')
    random1Convert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in split1)
    random2Convert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in split2)

    if value == 1:
        if len(hcFeasibleObjects) == 0:
            string = "No"
            return string
        else:
            string = "Yes"
            return string
    if value == 2:
        if random1[1] < random2[1]:
            string = random1Convert + "\nis better than\n" + random2Convert
            return string
        elif random1[1] > random2[1]:
            string = random2Convert + "\nis better than\n" + random1Convert
            return string
        else:
            string = random1Convert + "\nis equal to\n" + random2Convert
            return string
    if value == 3:
        string = ''.join(guiOUT[0])
        string = "Optimal Object: \n" + string
        return string
    if value == 4:
        string = ''.join(guiOUT)
        string = "Omni-Optimal objects: \n" + string 
        return string


#######################################################################################################
## POSSIBILISTIC LOGIC ##
def setupPossibilisticPreferences():

    preferenceObjects = str(files[2]).splitlines()

    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal

    for line in preferenceObjects:
        words = line.split()
        newLines = 1

        preferenceconversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        tempTest = preferenceconversion.split()
        for pos in range(len(tempTest)):
            if tempTest[pos] == 'NOT':
                # if there's a NOT, multiplies the next element by -1
                tempTest[pos + 1] = -1 * int(tempTest[pos + 1])
                tempTest[pos] = " "
                # ctempTest.pop(pos)
                continue
            if tempTest[pos] == 'OR':
                # if there's an OR, does nothing and just skips
                tempTest[pos] = " "
                # tempTest.pop(pos)
                continue
            if tempTest[pos] == 'AND':
                # if there's an AND, we must start a new line in clasp
                # not sure how yet
                tempTest[pos] = '0\n'
                newLines += 1
                continue
        # add penalty to list penalty amount
        penaltyAmount.append(float(tempTest.pop()))
        # cnfstring is going to be our input for CLASP
        booleanVars = len(attributeToNumber) / 2
        cnfString = "p cnf " + str(int(booleanVars)) + " " + str(newLines) + "\n"
        for chunk in tempTest:
            if chunk == "0\n":
                cnfString += str(chunk)
            elif chunk == " ":
                continue
            else:
                cnfString += str(chunk) + ' '
        cnfString = cnfString + '0'
        # add complete clasp string to completePreferences
        completePreferences.append(cnfString)


def runningPossibilisticPreferences(value):
    # Start dictionary of feasible objects with a start of zero penalty 
    totalTolerance = {}
    for object in hcFeasibleObjects:
        totalTolerance[object] = 1

    counter = 0
    for claspInput in completePreferences:

        cmdInput = claspInput
       
        with open("Output.txt", "w") as text_file:
            text_file.write(str(cmdInput))
        operatingSys = platform.system()
        if operatingSys == "Darwin":
            change = "cd " + ROOT_DIR
            claspIn = change + "; ./clasp-3.3.2-x86_64-macosx -n 0 Output.txt"
            claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, shell=True, text=True)
        else:
            claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe -n 0 Output.txt')
            claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, text=True)
        for line in claspExecute.stdout.splitlines():
            if line.startswith('v'):
                # checks if preference objects are feasible
                if line in hcFeasibleObjects:
                    if (1 - penaltyAmount[counter]) < totalTolerance[line]:
                        totalTolerance[line] = 1 - penaltyAmount[counter]
        counter += 1

    sortTotalTolerance = sorted(totalTolerance.items(), key=lambda x: x[1])
    # list of ordered objects from least penalty to most
    # this will get us the optimal object
    omniOptimal = []
    invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
    for i in sortTotalTolerance:
        if i[1] == sortTotalTolerance[0][1]:
            omniOptimal.append(i)
    guiOUT = []
    
    for entry in omniOptimal:
        toConvert = entry[0].split()[1:9]
        convertedOutput = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in toConvert)
        guiOUT.append(convertedOutput)
        guiOUT.append('\n')

    random1 = random.choice(sortTotalTolerance)
    random2 = random.choice(sortTotalTolerance)
 
    split1 = random1[0].split()
    split2 = random2[0].split()
    split1.remove('v')
    split2.remove('v')
    split1.remove('0')
    split2.remove('0')
    random1Convert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in split1)
    random2Convert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in split2)

    if value == 1:
        if len(hcFeasibleObjects) == 0:
            string = "No"
            return string
        else:
            string = "Yes"
            return string
    if value == 2:
        if random1[1] < random2[1]:
            string = random2Convert + "\nis better than\n" + random1Convert
            return string
        elif random1[1] > random2[1]:
            string = random1Convert + "\nis better than\n" + random2Convert
            return string
        else:
            string = random1Convert + "\nis equal to\n" + random2Convert
            return string
    if value == 3:
        string = ''.join(guiOUT[0])
        string = "Optimal Object: \n" + string
        return string
    if value == 4:
        string = ''.join(guiOUT)
        string = "Omni-Optimal objects: \n" + string 
        return string


#######################################################################################################
## QUALITATIVE CHOICE LOGIC ##

def setupQualitativePreferences(value):
    preferenceObjects = files[2].splitlines()
    totalQualitative = {}
    for feasableObject in hcFeasibleObjects:
        totalQualitative[feasableObject] = []
    inf = 99

    for preferenceObject in preferenceObjects:
        constraint = preferenceObject.split('IF')[0].strip()
        ifCase = preferenceObject.split('IF')[1].strip()
        btList = constraint.split('BT')
        strippedBTList = [s.strip() for s in btList]
        btList = strippedBTList
        for index in range(len(btList)):
            listItem = str(btList[index]).split()
            conversion = ''.join(str(attributeToNumber.get(a, a)) for a in listItem)
            conversion = conversion.replace('AND', ' ')
            btList[index] = conversion
        if ifCase != '':
            ifCase = attributeToNumber.get(ifCase)
        for feasableObject in hcFeasibleObjects:
            if ifCase != '':
                if str(ifCase) not in feasableObject.split():
                    totalQualitative[feasableObject].append(inf)
                    continue
                else:
                    satisfy = 0
                    for condition in btList:
                        attributes = len(attributeToNumber) / 2
                        lines = attributes + 1
                        claspString = "p cnf " + str(int(attributes)) + " " + str(int(lines)) + "\n"
                        claspString += str(condition) + " 0\n"
                        for pos in range(len(feasableObject) - 1):
                            if feasableObject[pos+1] == '-':
                                claspString += feasableObject[pos + 1]
                                continue
                            elif feasableObject[pos+1] == ' ':
                                continue
                            elif feasableObject[pos+1] == '0':
                                continue
                            else:
                                claspString += feasableObject[pos + 1]
                                claspString += " 0\n"
                        
                        cmdInput = claspString
                        with open("Output.txt", "w") as text_file:
                            text_file.write(str(cmdInput))
                        operatingSys = platform.system()
                        if operatingSys == "Darwin":
                            change = "cd " + ROOT_DIR
                            claspIn = change + "; ./clasp-3.3.2-x86_64-macosx Output.txt"
                            claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, shell=True, text=True)
                        else:
                            claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe Output.txt')
                            claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, text=True)
                           
                        for line in claspExecute.stdout.splitlines():
                            if line.startswith('s SATISFIABLE'):
                                if satisfy == 0:
                                    totalQualitative[feasableObject].append(btList.index(condition) + 1)
                                satisfy = 1
                                continue
                            elif line.__contains__('UNSATISFIABLE'):
                                continue
                    if satisfy == 0:
                        totalQualitative[feasableObject].append(inf)
                        continue
            else:
                satisfy = 0
                for condition in btList:
                    attributes = len(attributeToNumber) / 2
                    lines = attributes + 1
                    claspString = "p cnf " + str(int(attributes)) + " " + str(int(lines)) + "\n"
                    claspString += str(condition) + " 0\n"
                    for pos in range(len(feasableObject) - 1):
                        if feasableObject[pos + 1] == '-':
                            claspString += feasableObject[pos + 1]
                            continue
                        elif feasableObject[pos + 1] == ' ':
                            continue
                        elif feasableObject[pos + 1] == '0':
                            continue
                        else:
                            claspString += feasableObject[pos + 1]
                            claspString += " 0\n"
                    cmdInput = claspString
                    with open("Output.txt", "w") as text_file:
                        text_file.write(str(cmdInput))
                    operatingSys = platform.system()
                    if operatingSys == "Darwin":
                        change = "cd " + ROOT_DIR
                        claspIn = change + "; ./clasp-3.3.2-x86_64-macosx Output.txt"
                        claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, shell=True, text=True)
                    else:
                        claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe Output.txt')
                        claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, text=True)
                    for line in claspExecute.stdout.splitlines():
                        if line.startswith('s SATISFIABLE'):
                            if satisfy == 0:
                                totalQualitative[feasableObject].append(btList.index(condition) + 1)
                            satisfy = 1
                            continue
                        elif line.__contains__('UNSATISFIABLE'):
                            continue
                if satisfy == 0:
                    totalQualitative[feasableObject].append(inf)
                    continue

    random1 = random.choice(list(totalQualitative.keys()))
    
    random2 = random.choice(list(totalQualitative.keys()))
    
    if value == 1:
        if len(hcFeasibleObjects) == 0:
            string = "No"
            return string
        else:
            string = "Yes"
            return string
    if value == 2:
        invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])

        better1 = 0
        better2 = 0
        list1 = totalQualitative[random1]
        list2 = totalQualitative[random2]

        split1 = random1.split()
        split2 = random2.split()
        random1 = split1
        random2 = split2
        random1.remove('v')
        random2.remove('v')
        random1.remove('0')
        random2.remove('0')
        random1Convert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in random1)
        random2Convert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in random2)
        if len(list1) == len(list2) and len(list1) == sum([1 for i, j in zip(list1, list2) if i == j]):
            string = str(random1Convert) + " is equal to " + str(random2Convert)
            return string
        for pos in range(len(list1)):
            if list1[pos] < list2[pos]:
                better1 += 1
            elif list2[pos] < list1[pos]:
                better2 += 1

        if better1 == better2:
            string = str(random1Convert) + "\nis incomparable to\n" + str(random2Convert)
            return string
        if better1 > better2:
            string = str(random1Convert) + "\nis better than\n" + str(random2Convert)
            return string
        if better1 < better2:
            string = str(random2Convert) + "\nis better than\n" + str(random1Convert)
            return string

    if value == 3:
        sums = []

        for position in range(len(totalQualitative)):
            numList = totalQualitative[hcFeasibleObjects[position]]
            total = 0
            for number in numList:
                total += number
            sums.insert(position, total)
        minpos = sums.index(min(sums))
        string = "Optimal Object: \n"
        feasibleSplit = hcFeasibleObjects[minpos].split()
        feasibleSplit.remove('v')
        feasibleSplit.remove('0')
        invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
        feasibleObjectConvert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in feasibleSplit)
        string += feasibleObjectConvert
        return string
    if value == 4:
        sums = []

        for position in range(len(totalQualitative)):
            numList = totalQualitative[hcFeasibleObjects[position]]
            total = 0
            for number in numList:
                total += number
            sums.insert(position, total)

        minpos = min(sums)
        omni = [i for i, j in enumerate(sums) if j == minpos]
        string = "Omni-Optimal objects: \n"
        for item in omni:
            feasibleSplit = hcFeasibleObjects[item].split()
            feasibleSplit.remove('v')
            feasibleSplit.remove('0')
            invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
            feasibleObjectConvert = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in feasibleSplit)
            string += str(feasibleObjectConvert) + "\n"
        return string


#######################################################################################################
# FRONT END #
#######################################################################################################
window = Tk()
window.title = "Enter files"
window.geometry("260x550")
# window.eval('tk::PlaceWindow . center')

def chooseFile():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file

    with open(filename) as f:
        lines = f.read().replace(',', '')

    files.append(str(lines))


def choosePenalty():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
   
    with open(filename) as f:
        lines = f.read().replace(',', '')
    
    files.append(str(lines))
    global preferenceFile
    preferenceFile = 1


def choosePossibilistic():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    
    with open(filename) as f:
        lines = f.read().replace(',', '')
   
    files.append(str(lines))
    global preferenceFile
    preferenceFile = 2


def chooseQualitative():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    
    with open(filename) as f:
        lines = f.read().replace(',', '')
 
    files.append(str(lines))
    global preferenceFile
    preferenceFile = 3


def chooseFeasability():
    global option
    option = 1


def chooseExemplification():
    global option
    option = 2


def chooseOptimization():
    global option
    option = 3


def chooseOmni():
    global option
    option = 4


def done():
    setUpAttribute()
    claspInput()
    if preferenceFile == 1:
        setupPreferences()
    elif preferenceFile == 2:
        setupPossibilisticPreferences()

    root = Tk()
    root.title('Output')
    root.geometry("500x450")
    root.eval('tk::PlaceWindow . center')

    label = Label(root, text='')
    label.pack(pady=20)
    if preferenceFile == 1:
        if len(hcFeasibleObjects) == 0:
            label.config(text="No")
        else:
            label.config(text=runningPreferences(option))
    elif preferenceFile == 2:
        label.config(text=runningPossibilisticPreferences(option))
    elif preferenceFile == 3:
        label.config(text=setupQualitativePreferences(option))

    endButton = Button(root, text="Close and End Program", command=exit)
    endButton.pack(pady=10)

    root.mainloop()
    window.destroy()  # if pressed first, then ends whole process


# define image for canvas
imagePath1 = os.path.join(ROOT_DIR, 'GreyBG.png')  # loads images.png no matter where the project is located
bg = Image.open(imagePath1)
resizedd = bg.resize((530, 1155), Image.ANTIALIAS)
newBg = ImageTk.PhotoImage(resizedd)
# bgLabel = Label(image=newAttributeBTN)

# create canvas
myCanvas = Canvas(window, width=500, height=500, borderwidth=0, highlightthickness=0, border=0)
myCanvas.pack(fill="both", expand=True)

# set image in canvas
myCanvas.create_image(0, 0, image=newBg)

# add a label to canvas
myCanvas.create_text(50, 20, text="Constraints", font=("Batang", 11), fill="black")
myCanvas.create_text(50, 140, text="Preference", font=("Batang", 11), fill="black")
myCanvas.create_text(64, 305, text="Possible Tasks", font=("Batang", 11), fill="black")

# create images and resize them for buttons
# attributes
imagePath2 = os.path.join(ROOT_DIR, 'attributesBtn.png')
attributesImg = Image.open(imagePath2)
resized2 = attributesImg.resize((268, 38), Image.ANTIALIAS)
newAttributeBTN = ImageTk.PhotoImage(resized2)

# hard Constraint
imagePath3 = os.path.join(ROOT_DIR, 'HCBtn.png')
hardConstraintImg = Image.open(imagePath3)
resized3 = hardConstraintImg.resize((270, 38), Image.ANTIALIAS)
newHcBTN = ImageTk.PhotoImage(resized3)

# # browse
# imagePath4 = os.path.join(ROOT_DIR, 'browseBtn.png')
# browseImg = Image.open(imagePath4)
# resized = browseImg.resize((270, 50), Image.ANTIALIAS)
# newAttributeBTN = ImageTk.PhotoImage(resized)

# done
imagePath5 = os.path.join(ROOT_DIR, 'doneBtn.png')
doneImg = Image.open(imagePath5)
resized = doneImg.resize((200, 38), Image.ANTIALIAS)
newDoneBTN = ImageTk.PhotoImage(resized)

# preferences
imagePath6 = os.path.join(ROOT_DIR, 'PenaltyBtn.png')
penaltyImg = Image.open(imagePath6)
resized6 = penaltyImg.resize((270, 38), Image.ANTIALIAS)
newPenaltyBTN = ImageTk.PhotoImage(resized6)

imagePath7 = os.path.join(ROOT_DIR, 'possibilisticBtn.png')
possibilisticImg = Image.open(imagePath7)
resized7 = possibilisticImg.resize((270, 38), Image.ANTIALIAS)
newPossibilisticBTN = ImageTk.PhotoImage(resized7)

imagePath8 = os.path.join(ROOT_DIR, 'QualitativeBtn.png')
QualitativeImg = Image.open(imagePath8)
resized8 = QualitativeImg.resize((270, 38), Image.ANTIALIAS)
newQualitativeBTN = ImageTk.PhotoImage(resized8)

# types
imagePath9 = os.path.join(ROOT_DIR, 'FeasibilityBtn.png')
feasibilityImg = Image.open(imagePath9)
resized9 = feasibilityImg.resize((270, 38), Image.ANTIALIAS)
newFeasibilityBTN = ImageTk.PhotoImage(resized9)

imagePath10 = os.path.join(ROOT_DIR, 'ExemplificationBtn.png')
exemplificationImg = Image.open(imagePath10)
resized10 = exemplificationImg.resize((270, 38), Image.ANTIALIAS)
newExemplificationBTN = ImageTk.PhotoImage(resized10)

imagePath11 = os.path.join(ROOT_DIR, 'OptimizationBtn.png')
optimizationImg = Image.open(imagePath11)
resized11 = optimizationImg.resize((270, 38), Image.ANTIALIAS)
newOptimizationBTN = ImageTk.PhotoImage(resized11)

imagePath12 = os.path.join(ROOT_DIR, 'Omni-optimizzationBtn.png')
omniOptimizationImg = Image.open(imagePath12)
resized12 = omniOptimizationImg.resize((270, 38), Image.ANTIALIAS)
newOmniOptimizationBTN = ImageTk.PhotoImage(resized12)

# adding needed buttons
attributesButton = Button(window, image=newAttributeBTN, command=chooseFile, borderwidth=0, highlightthickness=0, border=0)
constraintButton = Button(window, image=newHcBTN, command=chooseFile, borderwidth=0, highlightthickness=0, border=0)
PenaltyButton = Button(window, image=newPenaltyBTN, command=choosePenalty, borderwidth=0, highlightthickness=0,border=0)
possibilisticButton = Button(window, image=newPossibilisticBTN, command=choosePossibilistic, borderwidth=0, highlightthickness=0, border=0)
qualitativeButton = Button(window, image=newQualitativeBTN, command=chooseQualitative, borderwidth=0,highlightthickness=0, border=0)
feasibilityButton = Button(window, image=newFeasibilityBTN, command=chooseFeasability, borderwidth=0, highlightthickness=0, border=0)
exemplificationButton = Button(window, image=newExemplificationBTN, command=chooseExemplification, borderwidth=0, highlightthickness=0, border=0)
optimizationButton = Button(window, image=newOptimizationBTN, command=chooseOptimization, borderwidth=0, highlightthickness=0, border=0)
omniOptimizationButton = Button(window, image=newOmniOptimizationBTN, command=chooseOmni, borderwidth=0, highlightthickness=0, border=0)

# temporary for testing
doneButton = Button(window, command=done, image=newDoneBTN, borderwidth=0, highlightthickness=0,
                    border=0)  # text="done")
doneButtonWindow = myCanvas.create_window(130, 530, anchor="center", window=doneButton)

# creating windows of buttons and adding onto canvas
attributesButtonWindow = myCanvas.create_window(130, 55, anchor="center", window=attributesButton)
constraintButtonWindow = myCanvas.create_window(130, 100, anchor="center", window=constraintButton)
penaltyButtonWindow = myCanvas.create_window(130, 175, anchor="center", window=PenaltyButton)
possibilisticButtonWindow = myCanvas.create_window(130, 220, anchor="center", window=possibilisticButton)
qualitativeButtonWindow = myCanvas.create_window(130, 265, anchor="center", window=qualitativeButton)
feasibilityButtonWindow = myCanvas.create_window(130, 335, anchor="center", window=feasibilityButton)
exemplificationButtonWindow = myCanvas.create_window(130, 380, anchor="center", window=exemplificationButton)
optimizationButtonWindow = myCanvas.create_window(130, 425, anchor="center", window=optimizationButton)
omniOptimizationButtonWindow = myCanvas.create_window(130, 470, anchor="center", window=omniOptimizationButton)

window.mainloop()
#######################################################################################################
