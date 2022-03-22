from tkinter import *
from tkinter.filedialog import askopenfilename


window = Tk()
window.title = "Enter files"
window.geometry("300x160")
window.eval('tk::PlaceWindow . center')

files = []  # Holds the content of opened files

#######################################################################################################
def setUpAttribute():
    attributes = files[0].split()
    # print("the first thing: " + attributes[0] + "the second thing" + attributes[1] +  "the third: " +attributes[2])
    totalNumberOfAttributes = int(len(attributes)/3)
    attributeToNumber = {}
    for a in range(totalNumberOfAttributes):
        attributeToNumber[attributes[(a*3-2)]] = a + 1
        attributeToNumber[attributes[(a * 3 - 1)]] = -1 * (a + 1)
        # print(attributes[(a*3-2)])
        # print(attributes[(a*3-1)])
    # print(attributeToNumber)


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
