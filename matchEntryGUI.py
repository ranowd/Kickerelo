from tkinter import *
from players import options

# GUI mit dem Ziel, sowas zu erstellen "Claudius_J;Marvin_W;Rene_P;Bastian_G;2;10"

def create_4_dropdowns(options, appendList, standardOption):
	for k in range(1,5):
		k = []
		k.append(StringVar(master))
		k[0].set(options[standardOption]) # default value
		k.append(OptionMenu(master, k[0], *options))
		k[1].pack()
		appendList.append(k)

def create_textfields(fieldTitle, appendList):
	i=0
	for k in range(1,(len(fieldTitle)+1)):
		k = []
		k.append(Label(frame2, text=fieldTitle[i]).grid(row=i))
		k.append(Entry(frame2))
		k[1].grid(row=i, column=1)
		k[1].insert(END,'-1')
		appendList.append(k)
		i+=1

def cbc(tex, option):
	return lambda : callback(tex, option)

def callback(tex, option):
	if option == 1:
		Spieler = "{};{};{};{}".format(dropdowns[0][0].get(), dropdowns[1][0].get(), dropdowns[2][0].get(), dropdowns[3][0].get())
		Ergebnis_1 = "{};{}".format(dropdowns[4][0].get(), dropdowns[5][0].get())
		Ergebnis_2 = "{};{}".format(dropdowns[6][0].get(), dropdowns[7][0].get())
		s = "/newresult "+Spieler+Ergebnis_1+" "+Spieler+Ergebnis_2+"\n"
	if option == 2:
		s =  "/editPlayer {} {} {} {} {} {}\n".format(dropdowns[0][0].get(), textFields[0][1].get(), textFields[1][1].get(), textFields[2][1].get(), textFields[3][1].get(), textFields[4][1].get())
	tex.insert(END, s)
	tex.see(END)


master = Tk()
master.title("ELO Telegram command generator")
frame = Frame(master)
frame.pack()

frame2 = Frame(master)
frame2.pack(side=RIGHT)
### Text Field
tex = Text(master=master)
tex.pack(side=RIGHT)

### Dropdownlists
# Define the dropdown Options
OPTIONS_Names = options#etc

OPTIONS_Score = list(range(0, 11))

# Create the actual Dropdowns
dropdowns = []
create_4_dropdowns(OPTIONS_Names,dropdowns, 0)
create_4_dropdowns(OPTIONS_Score,dropdowns, 10)

# UNDER CONSTRUCTION TEXT FIELDS
textFields = []
titles = ["username","pseudo","role","status","team"]
# Label(frame2, text="First Name").grid(row=0)
# Label(frame2, text="Last Name").grid(row=1)

# e1 = Entry(frame2)
# e2 = Entry(frame2)

# e1.grid(row=0, column=1)
# e2.grid(row=1, column=1)

create_textfields(titles,textFields) # 5 textfields

# Action Buttons to generate strings
Button1 = Button(frame, text="New Results Command", command=cbc(tex, 1))
Button2 = Button(frame, text="Edit Player Info Command", command=cbc(tex, 2))
Button1.pack(side=LEFT)
Button2.pack(side=RIGHT)

# Start the GUI
mainloop()
