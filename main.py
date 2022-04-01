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
# FRONT END #
#######################################################################################################

window = Tk()
window.title = "Enter files"
window.geometry("1000x800")
#window.eval('tk::PlaceWindow . center')


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


# def done():
#     operatingSys = platform.system()
#     setUpAttribute()
#     if operatingSys == 'Darwin':
#         macClaspInput()
#     else:
#         claspInput()
#     setupPreferences()
#     # setupPossibilisticPreferences()
#     # setupQualitativePreferences()

#     if operatingSys == 'Darwin':
#         macRunningPreferences()
#     else:
#         runningPreferences()
#         # runningPossibilisticPreferences()
#     # displayOut()

#     root = Tk()
#     root.title('This better work I swear')
#     root.geometry("500x450")
#     root.eval('tk::PlaceWindow . center')

#     label = Label(root, text='')
#     label.pack(pady=20)

#     label.config(text=runningPreferences())

#     root.mainloop()
#     # window.destroy()  # if pressed first, then ends whole process


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
myCanvas.create_text(50, 20, text="Constraints", font=("Batang", 10), fill="black")
myCanvas.create_text(50, 140, text="Preference", font=("Batang", 10), fill="black")
myCanvas.create_text(63, 300, text="Possible Tasks", font=("Batang", 10), fill="black")

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
PenaltyButton = Button(window, image=newPenaltyBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
possibilisticButton = Button(window, image=newPossibilisticBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
qualitativeButton = Button(window, image=newQualitativeBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
feasibilityButton = Button(window, image=newFeasibilityBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
exemplificationButton = Button(window, image=newExemplificationBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
optimizationButton = Button(window, image=newOptimizationBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)
omniOptimizationButton = Button(window, image=newOmniOptimizationBTN, command=chooseFile, borderwidth=0,highlightthickness=0,border=0)

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
#     # Browse = Button(window, text="Browse", command=chooseFile)
#     doneButton = Button(window, text="Done", command=quit)
#     # myCanvas.create_window(100, 200, anchor="center", window=Browse)
#     myCanvas.create_window(130, 450, anchor="center", window=doneButton)
    
# options = [
#     "Default",
#     "Feasibility",
#     "Exemplification",
#     "Optimization",
#     "Omni-optimization"
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
# ddlWindow = myCanvas.create_window(130, 390, anchor="center", window=ddl)

# new
def output():
    messagebox.showinfo(message="This works lol ")

window.mainloop()
#######################################################################################################
