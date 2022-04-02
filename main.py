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
    # print(attributes)
    totalNumberOfAttributes = int(len(attributes) / 3)
    for a in range(1, totalNumberOfAttributes + 1):
        # assigning numbers to attributes. Either x or -x
        attributeToNumber[attributes[(a * 3 - 2)]] = a
        attributeToNumber[attributes[(a * 3 - 1)]] = -1 * a
        # print(attributes[(a*3-2)])
        # print(attributes[(a*3-1)])
    # print(attributeToNumber)
    return attributeToNumber


#######################################################################################################
def setupHardConstraints():
    # conversion replaces the words in the hard constraints file with their numeric value from attributeToNumber dict
    constraints = files[1].split()
    conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in constraints)
    # print(constraints)
    # print(conversion)

    newNumbers = []  # this will store an array of the numbers we get after computing though the NOTs and ORs
    conversionSplit = conversion.split()
    num = int(len(conversionSplit))
    skip = 0
    lines = 1
    for b in range(num):
        if skip == 1:
            skip = 0
            continue
        if conversionSplit[b] == 'NOT' and b > 1 and conversionSplit[b - 1] != 'OR':
            # this adds the 0 and new line to the array of numbers.
            newNumbers.append(0)
            newNumbers.append('\n')
            lines += 1
        if conversionSplit[b] == 'NOT':
            # if there's a NOT, multiplies the next element by -1, adds it to the array, then skips computing
            # the next element
            number = -1 * int(conversionSplit[b + 1])
            newNumbers.append(number)
            skip = 1
            continue
        if conversionSplit[b] == 'OR':
            # if there's an OR, does nothing and just skips
            continue
        if conversionSplit[b] != 'NOT' or conversionSplit[b] != 'OR':
            # if there's no NOT or an OR, just adds the number to the array
            newNumbers.append(int(conversionSplit[b]))

    newNumbers.append(0)  # adds a 0 to the last line
    # print(conversionSplit)
    # print(newNumbers)

    """
    # this gets the unique attributes for the first line of CLASP CNF input
    uniqueAttributes = -1  # this method counts 0 as a unique value, so we account for that by starting at -1
    uniqueList = []
    num3 = int(len(newNumbers))
    for a in range(num3):
        if newNumbers[a] != '\n' and abs(int(newNumbers[a])) not in uniqueList:
            uniqueAttributes += 1
            uniqueList.append(abs(int(newNumbers[a])))
    """

    booleanVars = len(attributeToNumber) / 2

    # final string is going to be our input for CLASP
    finalString = "p cnf " + str(int(booleanVars)) + " " + str(lines) + "\n"
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
    # print(finalString)
    return finalString


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
    # print(claspIn)

    # print(claspExecute.stdout)
    # print("executed")
    for line in claspExecute.stdout.splitlines():
        # print(line)
        if line.__contains__('SATISFIABLE'):
            print("Returned Satisfiable")
            # return 1
        elif line.__contains__('UNSATISFIABLE'):
            print("Returned Unsatisfiable")
            # return 0
        elif line.__contains__('UNKNOWN'):
            print("Returned Unknown")
            # return 2
        elif line.startswith('v'):
            hcFeasibleObjects.append(line)
    # print(hcFeasibleObjects)


#######################################################################################################
## PENALTY LOGIC ##
def setupPreferences():
    # WE NEED A WAY TO KNOW WHICH PREFERENCE WE ARE WORKING WITH
    # EACH BUTTON IS LINKED TO A CERTAIN INPUT FILE FOR THIS

    # preference replaces the words in the preference file with their numeric value from attributeToNumber dict
    # preferences = files[2].split()
    # conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in preferences)
    preferenceObjects = str(files[2]).splitlines()

    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal

    for line in preferenceObjects:
        words = line.split()
        newLines = 1

        preferenceconversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        tempTest = preferenceconversion.split()
        # print("before")
        # print(tempTest)
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
        # print(tempTest)
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
        # print(cnfString)
        # add complete clasp string to completePreferences
        completePreferences.append(cnfString)
    # print(completePreferences) 
    # print(penaltyAmount)


def runningPreferences(value):
    # Start dictionary of feasible objects with a start of zero penalty 
    totalPenalty = {}
    for object in hcFeasibleObjects:
        totalPenalty[object] = 0
    # print(totalPenalty)

    counter = 0
    for claspInput in completePreferences:
        operatingSys = platform.system()
        cmdInput = claspInput
        # print(cmdInput)
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
            # print(line)
            if line.startswith('v'):
                # checks if preference objects are feasible
                if line in hcFeasibleObjects:
                    totalPenalty[line] += penaltyAmount[counter]
        counter += 1

    # print(totalPenalty)
    sortTotalPenalty = sorted(totalPenalty.items(), key=lambda x: x[1])
    # list of ordered objects from least penalty to most
    # this will get us the optimal object

    # print(sortTotalPenalty)
    omniOptimal = []
    guiOUT = []
    for i in sortTotalPenalty:
        # print(i[0], i[1])
        if i[1] == sortTotalPenalty[0][1]:
            omniOptimal.append(i)
    # print(omniOptimal)
    for entry in omniOptimal:
        toConvert = entry[0].split()[1:9]
        # print(toConvert)
        # invertedAttributeToNumber = {v: k for k, v in attributeToNumber.items()}
        invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
        # print(invertedAttributeToNumber)
        convertedOutput = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in toConvert)
        print(convertedOutput)
        guiOUT.append(convertedOutput)

    random1 = random.choice(sortTotalPenalty)
    random2 = random.choice(sortTotalPenalty)
    print(random1)
    print(random1[1])
    print(random2)
    print(random2[1])

    if value == 1:
        print("Give feasable")
        if len(hcFeasibleObjects) == 0:
            string = "No"
            return string
        else:
            string = "Yes"
            return string
    if value == 2:
        print("Value 2")
        if random1[1] < random2[1]:
            string = "random 1 is better"
            return string
        elif random1[1] > random2[1]:
            string = "random 2 is better"
            return string
        else:
            string = "they are equal"
            return string
    if value == 3:
        print("Value 3")
        return guiOUT[0]
    if value == 4:
        print("value 4")
        return guiOUT


#######################################################################################################
## POSSIBILISTIC LOGIC ##
def setupPossibilisticPreferences():
    # WE NEED A WAY TO KNOW WHICH PREFERENCE WE ARE WORKING WITH
    # EACH BUTTON IS LINKED TO A CERTAIN INPUT FILE FOR THIS

    # preference replaces the words in the preference file with their numeric value from attributeToNumber dict
    # preferences = files[2].split()
    # conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in preferences)
    preferenceObjects = str(files[2]).splitlines()

    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal

    for line in preferenceObjects:
        words = line.split()
        newLines = 1

        preferenceconversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        tempTest = preferenceconversion.split()
        # print("before")
        # print(tempTest)
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
        # print(penaltyAmount)
        # print(tempTest)
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
        # print(cnfString)
        # add complete clasp string to completePreferences
        completePreferences.append(cnfString)
    # print(completePreferences) 
    # print(penaltyAmount)


def runningPossibilisticPreferences(value):
    # Start dictionary of feasible objects with a start of zero penalty 
    totalTolerance = {}
    for object in hcFeasibleObjects:
        totalTolerance[object] = 1
    # print(totalPenalty)

    counter = 0
    for claspInput in completePreferences:

        cmdInput = claspInput
        # print(cmdInput)
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
            # print(line)
            if line.startswith('v'):
                # checks if preference objects are feasible
                if line in hcFeasibleObjects:
                    if (1 - penaltyAmount[counter]) < totalTolerance[line]:
                        totalTolerance[line] = 1 - penaltyAmount[counter]
                        # print(penaltyAmount[counter])
                        # print(1.00 - penaltyAmount[counter])
        counter += 1

    # print(totalPenalty)
    sortTotalTolerance = sorted(totalTolerance.items(), key=lambda x: x[1])
    # list of ordered objects from least penalty to most
    # this will get us the optimal object
    # print(sortTotalTolerance)
    omniOptimal = []

    for i in sortTotalTolerance:
        # print(i[0], i[1])
        if i[1] == sortTotalTolerance[0][1]:
            omniOptimal.append(i)
    # print(omniOptimal)
    guiOUT = []
    for entry in omniOptimal:
        toConvert = entry[0].split()[1:9]
        # print(toConvert)
        # invertedAttributeToNumber = {v: k for k, v in attributeToNumber.items()}
        invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
        # print(invertedAttributeToNumber)
        convertedOutput = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in toConvert)
        print(convertedOutput)
        guiOUT.append(convertedOutput)

    random1 = random.choice(sortTotalTolerance)
    random2 = random.choice(sortTotalTolerance)
    if value == 1:
        print("Give feasable")
        if len(hcFeasibleObjects) == 0:
            string = "No"
            return string
        else:
            string = "Yes"
            return string
    if value == 2:
        print("Value 2")
        if random1[1] < random2[1]:
            string = "random 1 is better"
            return string
        elif random1[1] > random2[1]:
            string = "random 2 is better"
            return string
        else:
            string = "they are equal"
            return string
    if value == 3:
        print("Value 3")
        return guiOUT[0]
    if value == 4:
        print("value 4")
        return guiOUT



#######################################################################################################
## QUALITATIVE CHOICE LOGIC ##

def setupQualitativePreferences():
    # WE NEED A WAY TO KNOW WHICH PREFERENCE WE ARE WORKING WITH
    # EACH BUTTON IS LINKED TO A CERTAIN INPUT FILE FOR THIS

    # preference replaces the words in the preference file with their numeric value from attributeToNumber dict
    # preferences = files[2].split()
    # conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in preferences)
    preferenceObjects = str(files[2]).splitlines()
    totalQualitative = {}
    for object in hcFeasibleObjects:
        totalQualitative[object] = []
    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal

    for line in preferenceObjects:
        words = line.split()
        BTcounter = 0

        preferenceconversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        getIF = preferenceconversion.split("IF")
        # print(getIF)
        IFcase = getIF[-1] # this is the if case for the line
        # print(len(IFcase))
        # print(IFcase)
        chunks = getIF[0].split("BT") # these are the ordered BetterThan for this line
        # ISSUE WITH BT SEGMENTS THAT HAVE "AND"
        # print(chunks)

        for item in totalQualitative:
            if IFcase not in item:
                # print(IFcase)
                # print(item)
                totalQualitative[item].append("inf")
            else:
                point = 1
                for chunk in chunks:
                    if chunk in item:   # Doesn't work as wanted. Sees 7 in item with -7 in it. Thus not correct logic.
                        #print(chunk)
                        #print(item)
                        totalQualitative[item].append(point)
                        point += 1

        """
        for pos in range(len(tempTest)):
            if tempTest[pos] == 'IF':
                # if there's a NOT, multiplies the next element by -1
                # print(ifTest)   # This is to check if the if condition is true
                ifTest.append(tempTest[pos + 1:])
                temporary = tempTest[pos + 1:]
                continue
            if tempTest[pos] == 'BT':
                # if there's a NOT, multiplies the next element by -1
                BTcounter += 1
                continue"""


#######################################################################################################
# FRONT END #
#######################################################################################################
window = Tk()
window.title = "Enter files"
window.geometry("260x550")
#window.eval('tk::PlaceWindow . center')



def chooseFile():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # print("You chose: " + filename)
    with open(filename) as f:
        lines = f.read().replace(',', '')
    # print(lines)
    files.append(str(lines))

def choosePenalty():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # print("You chose: " + filename)
    with open(filename) as f:
        lines = f.read().replace(',', '')
    # print(lines)
    files.append(str(lines))
    global preferenceFile
    preferenceFile = 1

def choosePossibilistic():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # print("You chose: " + filename)
    with open(filename) as f:
        lines = f.read().replace(',', '')
    # print(lines)
    files.append(str(lines))
    global preferenceFile
    preferenceFile = 2


def chooseQualitative():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # print("You chose: " + filename)
    with open(filename) as f:
        lines = f.read().replace(',', '')
    # print(lines)
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
    setupPreferences()
    # setupPossibilisticPreferences()
    # setupQualitativePreferences()
    runningPreferences(option)
    # runningPossibilisticPreferences()
    root = Tk()
    root.title('This better work I swear')
    root.geometry("500x450")
    root.eval('tk::PlaceWindow . center')

    label = Label(root, text='')
    label.pack(pady=20)
    if preferenceFile == 1:
        label.config(text=runningPreferences(option))
    elif preferenceFile == 2:
        label.config(text=runningPossibilisticPreferences(option))
    elif preferenceFile == 3:
        label.config(text="Qualitative goes here")

    print(option)
    root.mainloop()
    # window.destroy()  # if pressed first, then ends whole process


# define image for canvas
imagePath1 = os.path.join(ROOT_DIR, 'GreyBG.png')  # loads images.png no matter where the project is located
bg = Image.open(imagePath1)
resizedd = bg.resize((530, 1155), Image.ANTIALIAS)
newBg = ImageTk.PhotoImage(resizedd)
# bgLabel = Label(image=newAttributeBTN)

# create canvas
myCanvas = Canvas(window, width=500, height=500, borderwidth=0,highlightthickness=0,border=0)
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

# # done
# imagePath5 = os.path.join(ROOT_DIR, 'doneBtn.png')
# doneImg = Image.open(imagePath5)
# resized = doneImg.resize((270, 50), Image.ANTIALIAS)
# newAttributeBTN = ImageTk.PhotoImage(resized)

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
attributesButton = Button(window, image=newAttributeBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
constraintButton = Button(window, image=newHcBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
PenaltyButton = Button(window, image=newPenaltyBTN, command=choosePenalty, borderwidth=0,highlightthickness=0,border=0)
possibilisticButton = Button(window, image=newPossibilisticBTN, command=choosePossibilistic, borderwidth=0,highlightthickness=0,border=0)
qualitativeButton = Button(window, image=newQualitativeBTN, command=chooseQualitative, borderwidth=0,highlightthickness=0,border=0)
feasibilityButton = Button(window, image=newFeasibilityBTN,command=chooseFeasability, borderwidth=0,highlightthickness=0,border=0)
exemplificationButton = Button(window,image=newExemplificationBTN, command=chooseExemplification, borderwidth=0,highlightthickness=0,border=0)
optimizationButton = Button(window,image=newOptimizationBTN, command=chooseOptimization, borderwidth=0,highlightthickness=0,border=0)
omniOptimizationButton = Button(window, image=newOmniOptimizationBTN,command=chooseOmni, borderwidth=0,highlightthickness=0,border=0)

#temporary for testing
doneButton = Button(window, command=done, text="done")
doneButtonWindow = myCanvas.create_window(130, 520, anchor="center", window=doneButton)

# creating windows of buttons and adding onto canvas
attributesButtonWindow = myCanvas.create_window(130,55, anchor="c", window=attributesButton)
constraintButtonWindow = myCanvas.create_window(130,100, anchor="c", window=constraintButton)
penaltyButtonWindow = myCanvas.create_window(130,175, anchor="c", window=PenaltyButton)
possibilisticButtonWindow = myCanvas.create_window(130,220, anchor="c", window=possibilisticButton)
qualitativeButtonWindow = myCanvas.create_window(130,265, anchor="c", window=qualitativeButton)
feasibilityButtonWindow = myCanvas.create_window(130,335, anchor="c", window=feasibilityButton)
exemplificationButtonWindow = myCanvas.create_window(130,380, anchor="c", window=exemplificationButton)
optimizationButtonWindow = myCanvas.create_window(130,425, anchor="c", window=optimizationButton)
omniOptimizationButtonWindow = myCanvas.create_window(130,470, anchor="c", window=omniOptimizationButton)

# # add a drop down
# def selected(event):
#     # if clicked.get() == "Select attributes file": popup to submit then execute below code
#     Browse = Button(window, text="Browse", command=chooseFile)
#     doneButton = Button(window, text="Done", command=done)
#     myCanvas.create_window(100, 200, anchor="center", window=Browse)
#     myCanvas.create_window(250, 250, anchor="center", window=doneButton)


# options = [
#     "Default",
#     "Attributes File",
#     "Hard Constraints File",
#     "Preference File"
# ]

# # take in selected val
# clicked = StringVar()
# # set default val
# clicked.set(options[0])

# # provide a menu
# ddl = OptionMenu(
#     window,
#     clicked,
#     *options,
#     command=selected
# )
# # putting a window for ddl on canvas
# #ddlWindow = myCanvas.create_window(100, 250, anchor="center", window=ddl)


window.mainloop()
#######################################################################################################
