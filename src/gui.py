from tkinter import *
import main

version = 0.3

window = Tk()
window.title(f"configtool v{version}")
window.minsize(width=500, height=800)


label = Label(
    text="THIS DOES NOT YET WORK;\nTHE CONVERTING, SHORTENING, VEGAS WEIGHTS,\nETC HAVE NOT BEEN IMPLEMENTED",
)
label.config(font=("Arial", 20))
label.pack()


text = Text(height=30, width=30)
text.pack()


def get_text():
    print(text.get("1.0", END))


button = Button(text="convert", command=get_text)
button.pack()

window.mainloop()
