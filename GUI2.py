from tkinter import *
import tkinter.font

# GUI Def
window = Tk()
window.title("Hi I'm a window")
myFont = tkinter.font.Font(family='Helvetica, size = 12, weight = bold')


# events
def menu_event(number):
    print("menu" + str(number))


def exit_program():
        print("Bye")
        window.destroy()


# widgets
sz_menu_height = 9
sz_menu_width = 2*sz_menu_height
btn_menu_1 = Button(window, text="Menu 1", font=myFont, bg='blue', height=sz_menu_height, width=sz_menu_width, command=menu_event("1"))
btn_menu_2 = Button(window, text="Menu 2", font=myFont, bg='blue', height=sz_menu_height, width=sz_menu_width, command=menu_event(2))
btn_menu_3 = Button(window, text="Menu 3", font=myFont, bg='blue', height=sz_menu_height, width=sz_menu_width, command=menu_event(3))
btn_menu_4 = Button(window, text="Menu 4", font=myFont, bg='blue', height=sz_menu_height, width=sz_menu_width, command=menu_event(4))
btn_menu_1.pack()
btn_menu_2.pack()
btn_menu_3.pack()
btn_menu_4.pack()

btn_exit = Button(window, text="Exit", font=myFont, bg='red', height=1, width=24, command=exit_program)
btn_exit.pack()



# mainloop
window.mainloop()
#window.protocol("WM_DELETE_WINDOW", exitProgramm())