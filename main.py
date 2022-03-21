from tkinter import *
from tkinter.filedialog import askopenfilename

window = Tk()
window.title = "Enter files"
window.geometry("300x160")
window.eval('tk::PlaceWindow . center')

files = []


def chooseFile():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    print("You chose: " + filename)
    with open(filename) as f:
        lines = f.readlines()
    print(lines)
    files.append(lines)


def done():
    print("You pressed done, here are the results")
    # print("First file: " + str(files[0]) + " Second File: " + str(files[1]) + " Third File: " + str(files[2]))
    # function to do calculations should go here
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

"""
use this to function to get contents of a file into a variable, maybe an array of content? lines[i]

with open(filename) as f:
    lines = f.readlines()
"""
