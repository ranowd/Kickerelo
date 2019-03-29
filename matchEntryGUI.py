from tkinter import *

# GUI mit dem Ziel, sowas zu erstellen "Claudius_J;Marvin_W;Rene_P;Bastian_G;2;10"

def create_4_dropdowns(options, appendList, standardOption):
	for k in range(1,5):
		k = []
		k.append(StringVar(master))
		k[0].set(options[standardOption]) # default value
		k.append(OptionMenu(master, k[0], *options))
		k[1].pack()
		dropdowns.append(k)

def cbc(tex):
	return lambda : callback(tex)

def callback(tex):
	Spieler = "{};{};{};{}".format(dropdowns[0][0].get(), dropdowns[1][0].get(), dropdowns[2][0].get(), dropdowns[3][0].get())
	Ergebnis_1 = "{};{}".format(dropdowns[4][0].get(), dropdowns[5][0].get())
	Ergebnis_2 = "{};{}".format(dropdowns[6][0].get(), dropdowns[7][0].get())
	s = "/newresult "+Spieler+Ergebnis_1+" "+Spieler+Ergebnis_2+"\n"
	tex.insert(END, s)
	tex.see(END)    


master = Tk()
master.title("ELO Telegram command generator")
frame = Frame(master)
frame.pack()

### Text Field
tex = Text(master=master)
tex.pack(side=RIGHT)

### Dropdownlists
# Define the dropdown Options
OPTIONS_Names = [
"Spieler",
"Rano",
"Jan",
"Stanko",
"Carsten"
] #etc

OPTIONS_Score = list(range(0, 11))

# Create the actual Dropdowns
dropdowns = []
create_4_dropdowns(OPTIONS_Names,dropdowns, 0)
create_4_dropdowns(OPTIONS_Score,dropdowns, 10)

# Action Button to generate string
Button = Button(frame, text="Generate Telegram Command", command=cbc(tex))
Button.pack(side=LEFT)

# Start the GUI
mainloop()	