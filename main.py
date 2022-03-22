from tkinter import *
from tkinter.filedialog import askopenfilename

window = Tk()
window.title = "Enter files"
window.geometry("300x160")
window.eval('tk::PlaceWindow . center')

files = []  # Holds the content of opened files
attributeToNumber = {}


#######################################################################################################
def setUpAttribute():
    attributes = files[0].split()
    totalNumberOfAttributes = int(len(attributes) / 3)
    for a in range(totalNumberOfAttributes):
        attributeToNumber[attributes[(a * 3 - 2)]] = a + 1
        attributeToNumber[attributes[(a * 3 - 1)]] = -1 * (a + 1)
        # print(attributes[(a*3-2)])
        # print(attributes[(a*3-1)])
    # print(attributeToNumber)
    return attributeToNumber


def setupHardConstraints():
    attributes = files[1].split()
    conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in attributes)
    # print(attributes)
    # print(conversion)
    lines = 1
    newNumbers = []
    conversionSplit = conversion.split()
    num = int(len(conversionSplit))
    skip = 0
    for b in range(num):
        if skip == 1:
            skip = 0
            continue
        if conversionSplit[b] == 'NOT' and b > 1 and conversionSplit[b - 1] != 'OR':
            # this adds the 0 and new line to the array of numbers
            newNumbers.append(0)
            newNumbers.append('\n')
            lines += 1
        if conversionSplit[b] == 'NOT':
            # if there's a NOT, multiplies the next element by -1 then skips that number
            number = -1 * int(conversionSplit[b + 1])
            newNumbers.append(number)
            skip = 1
            continue
        if conversionSplit[b] == 'OR':
            # if there's an OR, does nothing and just skips
            continue
        if conversionSplit[b] != 'NOT' or conversionSplit[b] != 'OR':
            # if there's no NOT, just adds the number to the array
            newNumbers.append(int(conversionSplit[b]))

    newNumbers.append(0)  # adds a 0 to the last line
    # print(conversionSplit)
    # print(newNumbers)

    # this gets the unique values for the first line of CNF input
    uniqueAttributes = -1
    uniqueList = []
    num3 = int(len(newNumbers))
    for a in range(num3):
        if newNumbers[a] != '\n' and abs(int(newNumbers[a])) not in uniqueList:
            uniqueAttributes += 1
            uniqueList.append(a)

    finalString = "p cnf " + str(uniqueAttributes) + " " + str(lines) + "\n"
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
    print(finalString)


def chooseFile():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # print("You chose: " + filename)
    with open(filename) as f:
        lines = f.read().replace(',', '')
    # print(lines)
    files.append(str(lines))


def done():
    # print("You pressed done, here are the results")
    # print("First file: " + str(files[0]) + " Second File: " + str(files[1]) + " Third File: " + str(files[2]))
    # function to do calculations should go here
    setUpAttribute()
    setupHardConstraints()
    window.destroy()  # if pressed first, then ends whole process


# this seems to be working
attributesButton = Button(window, text="Select attributes file", command=chooseFile)
attributesButton.pack()
constraintButton = Button(window, text="Select the hard constraints files", command=chooseFile)
constraintButton.pack()
preferencesButton = Button(window, text="Select the preferences files", command=chooseFile)
preferencesButton.pack()
endButton = Button(window, text="Done", command=done)
endButton.pack(pady=20)

window.mainloop()

# Start to convert the example attribute file into CNF
#######################################################################################################


# Start to convert the example constraints file into CNF
#######################################################################################################

# Start to convert the example preferences file into CNF
#######################################################################################################
