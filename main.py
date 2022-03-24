from tkinter import *
from tkinter.filedialog import askopenfilename

window = Tk()
window.title = "Enter files"
window.geometry("300x160")
window.eval('tk::PlaceWindow . center')

files = []  # Holds the content of opened files
attributeToNumber = {}  # Dictionary mapping words in atributes file to numbers for CLASP input


#######################################################################################################
def setUpAttribute():
    attributes = files[0].split()
    #print(attributes)
    totalNumberOfAttributes = int(len(attributes) / 3)
    for a in range(1, totalNumberOfAttributes + 1):
        # assigning numbers to attributes. Either x or -x
        attributeToNumber[attributes[(a * 3 - 2)]] = a
        attributeToNumber[attributes[(a * 3 - 1)]] = -1 * (a)
        #print(attributes[(a*3-2)])
        #print(attributes[(a*3-1)])
    #print(attributeToNumber)
    return attributeToNumber

#######################################################################################################
def setupHardConstraints():
    # conversion replaces the words in the hard constraints file with their numeric value from attributeToNumber dict
    constraints = files[1].split()
    conversion = ' '.join(str(attributeToNumber.get(a, a)) for a in constraints)
    #print(constraints)
    #print(conversion)

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
    #print(conversionSplit)
    #print(newNumbers)

    # this gets the unique attributes for the first line of CLASP CNF input
    uniqueAttributes = -1  # this method counts 0 as a unique value, so we account for that by starting at -1
    uniqueList = []
    num3 = int(len(newNumbers))
    print(num3)
    for a in range(num3):
        if newNumbers[a] != '\n' and abs(int(newNumbers[a])) not in uniqueList:
            uniqueAttributes += 1
            uniqueList.append(abs(int(newNumbers[a])))

    # final string is going to be our input for CLASP
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

#define image
bg = PhotoImage(file="C:\\Users\\James\\Documents\\AI\\Python_Project3\\AI_Project3KerusCustodio\\images.png")

#create canvas
myCanvas = Canvas(window, width=700, height=400)
myCanvas.pack(fill="both", expand=True)

#set image in canvas 
myCanvas.create_image(0,0, image=bg, anchor="nw")

#add a label
myCanvas.create_text(100,20, text="Select an option", font=("Times new roman",24), fill="white")

# this seems to be working
# attributesButton = Button(window, text="Select attributes file", command=chooseFile)
# attributesButton.pack()
# constraintButton = Button(window, text="Select the hard constraints files", command=chooseFile)
# constraintButton.pack()
# preferencesButton = Button(window, text="Select the preferences files", command=chooseFile)
# preferencesButton.pack()
# endButton = Button(window, text="Done", command=done)
# endButton.pack(pady=20)

window.mainloop()

# Start to convert the example attribute file into CNF
#######################################################################################################

# Start to convert the example constraints file into CNF
#######################################################################################################

# Start to convert the example preferences file into CNF
#######################################################################################################
