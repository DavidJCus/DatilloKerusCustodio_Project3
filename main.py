from tkinter import *
from tkinter.filedialog import askopenfilename

root = Tk()


def chooseFile():
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    print("You chose: " + filename)


def done():
    # function to do calculations should go here
    root.destroy()  # if pressed first, then ends whole process


# this seems to be working
button = Button(root, text="Select attributes file", command=chooseFile)
button.pack()
button2 = Button(root, text="Select the hard constraints", command=chooseFile)
button2.pack()
endButton = Button(root, text="Done", command=done)
endButton.pack(pady=20)

root.mainloop()

"""
use this to function to get contents of a file into a variable, maybe an array of content? lines[i]

with open(filename) as f:
    lines = f.readlines()
"""
