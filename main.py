from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import os
import subprocess
import platform
from PIL import Image, ImageTk

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# claspMacPath = os.path.join(ROOT_DIR, 'clasp-3.3.2-x86_64-macosx')
completePreferences = []
penaltyAmount = []
preference = 0

files = []  # Holds the content of opened files
attributeToNumber = {}  # Dictionary mapping words in atributes file to numbers for CLASP input
hcFeasibleObjects = []


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
    # TODO: add mac support here instead of new functions
    cmdInput = setupHardConstraints()
    # the executable for clasp should be in the same place as this program
    with open("Output.txt", "w") as text_file:
        text_file.write(str(cmdInput))
    claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe -n 0 Output.txt')
    # print(claspIn)
    claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, text=True)
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


def macClaspInput():
    cmdInput = setupHardConstraints()
    # the executable for clasp should be in the same place as this program
    with open("Output.txt", "w") as text_file:
        text_file.write(str(cmdInput))
    change = "cd " + ROOT_DIR
    claspIn = change + "; ./clasp-3.3.2-x86_64-macosx -n 0 Output.txt"
    claspExecute = subprocess.run(claspIn, stdout=subprocess.PIPE, shell=True, text=True)
    for line in claspExecute.stdout.splitlines():
        # print(line)
        if line.__contains__('SATISFIABLE'):
            print("Returned Satisfiable")
        elif line.__contains__('UNSATISFIABLE'):
            print("Returned Unsatisfiable")
        elif line.__contains__('UNKNOWN'):
            print("Returned Unknown")
        elif line.startswith('v'):
            hcFeasibleObjects.append(line)


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


def runningPreferences():
    # Start dictionary of feasible objects with a start of zero penalty 
    totalPenalty = {}
    for object in hcFeasibleObjects:
        totalPenalty[object] = 0
    # print(totalPenalty)

    counter = 0
    for claspInput in completePreferences:

        cmdInput = claspInput
        # print(cmdInput)
        with open("Output.txt", "w") as text_file:
            text_file.write(str(cmdInput))
        claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe -n 0 Output.txt')
        # print(claspIn)
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

    for i in sortTotalPenalty:
        # print(i[0], i[1])
        if i[1] == sortTotalPenalty[0][1]:
            omniOptimal.append(i)
    # print(omniOptimal)
    for entry in omniOptimal:
        toConvert = entry[0].split()[1:5]
        # print(toConvert)
        # invertedAttributeToNumber = {v: k for k, v in attributeToNumber.items()}
        invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
        # print(invertedAttributeToNumber)
        convertedOutput = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in toConvert)
        print(convertedOutput)
        return convertedOutput


def macRunningPreferences():
    # Start dictionary of feasible objects with a start of zero penalty
    totalPenalty = {}
    for object in hcFeasibleObjects:
        totalPenalty[object] = 0
    # print(totalPenalty)

    counter = 0
    for claspInput in completePreferences:

        cmdInput = claspInput
        with open("Output.txt", "w") as text_file:
            text_file.write(str(cmdInput))
        change = "cd " + ROOT_DIR
        claspIn = change + "; ./clasp-3.3.2-x86_64-macosx -n 0 Output.txt"
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

    for i in sortTotalPenalty:
        # print(i[0], i[1])
        if i[1] == sortTotalPenalty[0][1]:
            omniOptimal.append(i)
    # print(omniOptimal)
    for entry in omniOptimal:
        toConvert = entry[0].split()[1:5]
        # print(toConvert)
        # invertedAttributeToNumber = {v: k for k, v in attributeToNumber.items()}
        invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
        # print(invertedAttributeToNumber)
        convertedOutput = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in toConvert)
        print(convertedOutput)
        return convertedOutput


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


def runningPossibilisticPreferences():
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
        claspIn = os.path.join(ROOT_DIR, 'clasp-3.3.2-win64.exe -n 0 Output.txt')
        # print(claspIn)
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

    for entry in omniOptimal:
        toConvert = entry[0].split()[1:5]
        # print(toConvert)
        # invertedAttributeToNumber = {v: k for k, v in attributeToNumber.items()}
        invertedAttributeToNumber = dict([(value, key) for key, value in attributeToNumber.items()])
        # print(invertedAttributeToNumber)
        convertedOutput = ' '.join(str(invertedAttributeToNumber.get(int(a), a)) for a in toConvert)
        print(convertedOutput)


#######################################################################################################
## QUALITATIVE CHOICE LOGIC ##

def setupQualitativePreferences():
    # WE NEED A WAY TO KNOW WHICH PREFERENCE WE ARE WORKING WITH
    # EACH BUTTON IS LINKED TO A CERTAIN INPUT FILE FOR THIS

    # preference replaces the words in the preference file with their numeric value from attributeToNumber dict
    # preferences = files[2].split()
    # conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in preferences)
    preferenceObjects = str(files[2]).splitlines()
    ifTest = []
    # each index in array holds the clasp code per line in preference file input
    # at least that is current goal

    for line in preferenceObjects:
        words = line.split()
        newLines = 1

        preferenceconversion = ' '.join(str(attributeToNumber.get(a, a)) for a in words)
        tempTest = preferenceconversion.split()
        print("before")
        print(tempTest)
        for pos in range(len(tempTest)):
            if tempTest[pos] == 'IF':
                # if there's a NOT, multiplies the next element by -1
                ifTest.append(tempTest[pos + 1:])
                continue


#######################################################################################################
# FRONT END #
#######################################################################################################

window = Tk()
window.title = "Enter files"
window.geometry("900x500")
window.eval('tk::PlaceWindow . center')


def chooseFile():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # print("You chose: " + filename)
    with open(filename) as f:
        lines = f.read().replace(',', '')
    # print(lines)
    files.append(str(lines))


def preferenceChoice(choice):
    if choice == 1:
        return 1
    if choice == 2:
        return 2
    if choice == 3:
        return 3


def done():
    operatingSys = platform.system()
    setUpAttribute()
    if operatingSys == 'Darwin':
        macClaspInput()
    else:
        claspInput()
    setupPreferences()
    # setupPossibilisticPreferences()

    if operatingSys == 'Darwin':
        macRunningPreferences()
    else:
        runningPreferences()
        # runningPossibilisticPreferences()
    # displayOut()
    # window.destroy()  # if pressed first, then ends whole process


# define image
imagePath1 = os.path.join(ROOT_DIR, 'GreyBG.png')  # loads images.png no matter where the project is located
bg = PhotoImage(file=imagePath1)

# create canvas
myCanvas = Canvas(window, width=500, height=500)
myCanvas.pack(fill="both", expand=True)

# set image in canvas
myCanvas.create_image(0, 0, image=bg)

# add a label
myCanvas.create_text(50, 20, text="Constraints", font=("Batang", 11), fill="black")
myCanvas.create_text(50, 150, text="Preference", font=("Batang", 11), fill="black")

# create labels for botton images
# attributes
imagePath2 = os.path.join(ROOT_DIR, 'attributesBtn.png')
attributesImgPIL = Image.open(imagePath2)
attributesImg = PhotoImage(file=imagePath2)
# attributeLabel = Label(image=attributesImg)
resized = attributesImgPIL.resize((100, 100), Image.ANTIALIAS)
newAttributeBTN = ImageTk.PhotoImage(resized)
attributeLabel = Label(image=newAttributeBTN)
# hard Constraint
# imagePath3 = os.path.join(ROOT_DIR, 'HCBtn.png')
# hardConstraintImg = PhotoImage(file=imagePath3)
# hardConstraintLabel = Label(image=hardConstraintImg)
# browse
# imagePath4 = os.path.join(ROOT_DIR, 'browseBtn.png')
# browseImg = PhotoImage(file=imagePath4)
# browseLabel = Label(image=browseImg)
# done
# imagePath5 = os.path.join(ROOT_DIR, 'doneBtn.png')
# doneImg = PhotoImage(file=imagePath5)
# doneLabel = Label(image=doneImg)

# adding needed buttons
attributesButton = Button(window, image=attributesImg, command=chooseFile)
# constraintButton = Button(window, text="Select the hard constraints files", command=chooseFile)
# preferencesButton = Button(window, text="Select the preferences files", command=chooseFile)

# creating windows of buttons and adding onto canvas
# attributesButtonWindow = myCanvas.create_window(50,50, anchor="c", window=attributesButton)
# constraintButtonWindow = myCanvas.create_window(350,130, anchor="c", window=constraintButton)
# preferencesButtonWindow = myCanvas.create_window(350,160, anchor="c", window=preferencesButton)

# new
output = Entry(window)
myCanvas.create_window(712, 150, anchor="center", height=300, width=475, window=output)


# new
def displayOut():
    text = runningPreferences()
    output.insert(0, "Hello")


# add a drop down
def selected(event):
    # if clicked.get() == "Select attributes file": popup to submit then execute below code
    Browse = Button(window, text="Browse", command=chooseFile)
    doneButton = Button(window, text="Done", command=done)
    myCanvas.create_window(100, 200, anchor="center", window=Browse)
    myCanvas.create_window(250, 250, anchor="center", window=doneButton)


options = [
    "Default",
    "Attributes File",
    "Hard Constraints File",
    "Preference File"
]

# take in selected val
clicked = StringVar()
# set default val
clicked.set(options[0])

# provide a menu
ddl = OptionMenu(
    window,
    clicked,
    *options,
    command=selected
)
# putting a window on a window
ddlWindow = myCanvas.create_window(100, 190, anchor="center", window=ddl)


# new
def output():
    messagebox.showinfo(message="This works lol ")


window.mainloop()
#######################################################################################################
