from tkinter import *

root = Tk()

e = Entry(root, width=75)
e.pack()


def valueEntry():
    value = e.get()
    label = Label(root, text="So this is what you entered: " + value)
    label.pack()


button = Button(root, text="Enter", command=valueEntry)
button.pack()

root.mainloop()
