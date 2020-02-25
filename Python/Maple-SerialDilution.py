# to compile to deployable executable use pyinstaller Maple-SerialDilution.py
import string
import time
from tkinter import *
import serial

import SerialUtils

DRY_RUN = False

alphabet = list(string.ascii_uppercase)
last_received = ''

with open("config.txt", "r") as file:
    serialPorts = file.readlines()
    COMPortOne = serialPorts[0].strip()
    if DRY_RUN:
        sourcePanelSerialConnection = None
        print("Setting up source on port " + COMPortOne)
    else:
        sourcePanelSerialConnection = serial.Serial(COMPortOne, '38400', parity=serial.PARITY_NONE,
                                                    stopbits=serial.STOPBITS_ONE)


def send_serial_command(value, command):
    if value.isdecimal():
        SerialUtils.send_serial_command(sourcePanelSerialConnection, command, row="A", column=value)
    else:
        SerialUtils.send_serial_command(sourcePanelSerialConnection, command, row=value, column="1")


def on_closing():
    SerialUtils.close_connection([sourcePanelSerialConnection])
    print("Closing serial ports!")
    mainWindow.destroy()
    exit()


class LightPanelGUI(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.master = master
        self.master.title("Microplate Assistive Pipetting Light Emitter")
        self.master.maxsize(425, 300)
        self.master.minsize(425, 300)

        c = Canvas(self.master)
        c.configure(yscrollincrement='10c')

        # layout all of the main containers

        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.titrationMode = StringVar(value="By column")
        self.titrationMode.set('By column')
        self.plateDensitySelection = StringVar()
        self.startValues = StringVar()
        self.startValues.set("2,7")
        self.maskValues = StringVar()
        self.maskValues.set("A-H")
        self.plateDensitySelection.set('96 well')
        self.plateDensityOptions = {'384 well', '96 well'}
        self.nextButtonText = StringVar(value="Next column")
        self.previousButtonText = StringVar(value="Previous column")
        self.startValuesText = StringVar(value="Start column(s)")
        self.maskText = StringVar(value="Row mask")

        # create the widgets
        self.titrationModeColumn = Radiobutton(self.master, text="By column", variable=self.titrationMode,
                                               value='By column', padx=0, pady=0, command=self.column_selection)
        self.titrationModeRow = Radiobutton(self.master, text="By row", variable=self.titrationMode,
                                            value='By row', padx=0, pady=0, command=self.row_selection)
        self.backButton = Button(self.master, textvariable=self.previousButtonText,
                                 command=self.previous_selection)
        self.nextButton = Button(self.master, textvariable=self.nextButtonText, command=self.next_selection)
        self.plateDensityDropdown = OptionMenu(self.master, self.plateDensitySelection,
                                               *self.plateDensityOptions, command=lambda _: self.update_parameters())
        self.startValuesEntry = Entry(self.master, textvariable=self.startValues, width=4)
        self.maskEntry = Entry(self.master, textvariable=self.maskValues, width=4)

        Label(self.master, text="Titration Mode", font="Helvetica 18 bold").grid(row=0, column=0, sticky=W, padx=20,
                                                                                 pady=0)
        self.titrationModeColumn.grid(row=1, column=0, sticky=W, padx=30, pady=0)
        self.titrationModeRow.grid(row=2, column=0, sticky=W, padx=30, pady=0)
        self.nextButton.grid(row=1, column=3, padx=(0, 10), pady=0)
        self.backButton.grid(row=1, column=4, padx=(0, 10), pady=0)
        Label(self.master, text="Plate Density", font="Helvetica 18 bold").grid(row=3, column=0, sticky=W, padx=20,
                                                                                pady=(10, 0))
        self.plateDensityDropdown.grid(row=4, column=0, sticky=W, padx=30, pady=0)
        Label(self.master, textvariable=self.startValuesText, font="Helvetica 18 bold").grid(row=5, column=0, sticky=W,
                                                                                             padx=20, pady=(10, 0))
        self.startValuesEntry.grid(row=6, column=0, sticky=W, padx=30, pady=0)
        Label(self.master, textvariable=self.maskText, font="Helvetica 18 bold").grid(row=7, column=0, sticky=W,
                                                                                      padx=20, pady=(10, 0))
        self.maskEntry.grid(row=8, column=0, sticky=W, padx=30, pady=(0, 10))

        time.sleep(2)
        # send the initial command to light up the panel with the default parameters
        self.parse_commands()

    def column_selection(self):
        self.nextButtonText.set("Next column")
        self.previousButtonText.set("Previous column")
        self.startValuesText.set("Start column(s)")
        self.maskText.set("Row mask")
        self.update_parameters()

    def row_selection(self):
        self.nextButtonText.set("Next row")
        self.previousButtonText.set("Previous row")
        self.startValuesText.set("Start row(s)")
        self.maskText.set("Column mask")
        self.update_parameters()

    def update_parameters(self):
        selected_density = self.plateDensitySelection.get()
        selected_titration_mode = self.titrationMode.get()
        if selected_density == "96 well":
            if selected_titration_mode == "By column":
                self.startValues.set("2,7")
                self.maskValues.set("A-H")
            else:
                self.startValues.set("B,E")
                self.maskValues.set("1-12")
        else:
            if selected_titration_mode == "By column":
                self.startValues.set("3,13")
                self.maskValues.set("A-P")
            else:
                self.startValues.set("C,F")
                self.maskValues.set("1-24")

        self.parse_commands()

    def next_selection(self):
        start_value_list = self.startValues.get().split(',')
        selected_density = self.plateDensitySelection.get()
        if selected_density == '384 well':
            upper_column_limit = 24
            upper_row_limit = 15
        else:
            upper_column_limit = 12
            upper_row_limit = 7
        if self.titrationMode.get() == "By column":
            if int(start_value_list[1]) < upper_column_limit:
                lower_start_value = int(start_value_list[0]) + 1
                upper_start_value = int(start_value_list[1]) + 1
                new_start_value = str(lower_start_value) + "," + str(upper_start_value)
                self.startValues.set(new_start_value)
        else:
            if alphabet.index(start_value_list[1]) < upper_row_limit:
                lower_start_value = alphabet[alphabet.index(start_value_list[0]) + 1]
                upper_start_value = alphabet[alphabet.index(start_value_list[1]) + 1]
                new_start_value = str(lower_start_value) + "," + str(upper_start_value)
                self.startValues.set(new_start_value)

        self.parse_commands()

    def previous_selection(self):
        start_value_list = self.startValues.get().split(',')
        if self.titrationMode.get() == "By column":
            if int(start_value_list[0]) > 1:
                lower_start_value = int(start_value_list[0]) - 1
                upper_start_value = int(start_value_list[1]) - 1
                new_start_value = str(lower_start_value) + "," + str(upper_start_value)
                self.startValues.set(new_start_value)
        else:
            if alphabet.index(start_value_list[0]) > 0:
                lower_start_value = alphabet[alphabet.index(start_value_list[0]) - 1]
                upper_start_value = alphabet[alphabet.index(start_value_list[1]) - 1]
                new_start_value = str(lower_start_value) + "," + str(upper_start_value)
                self.startValues.set(new_start_value)

        self.parse_commands()

    def parse_commands(self):
        # send the command to clear existing LEDs
        send_serial_command("1", "clear")

        start_value_list = self.startValues.get().split(',')
        # print(start_value_list)
        mask_list = self.maskValues.get().split('-')
        # print(mask_list)
        # print(self.titrationMode.get())

        if self.titrationMode.get() == "By column":
            send_command = "column_on"
            start_mask_value = alphabet.index(mask_list[0])
            end_mask_value = alphabet.index(mask_list[1])
        else:
            send_command = "row_on"
            start_mask_value = int(mask_list[0])
            end_mask_value = int(mask_list[1])

        for value in start_value_list:
            send_serial_command(value, send_command)

        # define the upper bound for the mask
        selected_density = self.plateDensitySelection.get()
        selected_titration_mode = self.titrationMode.get()
        if selected_density == "96 well":
            if selected_titration_mode == "By column":
                upper_mask_boundary = 8
                lower_mask_boundary = 0
            else:
                upper_mask_boundary = 13
                lower_mask_boundary = 1
        else:
            if selected_titration_mode == "By column":
                upper_mask_boundary = 16
                lower_mask_boundary = 0
            else:
                upper_mask_boundary = 25
                lower_mask_boundary = 1

        for z in range(lower_mask_boundary, upper_mask_boundary):
            if self.titrationMode.get() == "By column":
                letter_value = alphabet[z]
                if z < start_mask_value:
                    send_serial_command(letter_value, "row_off")
                if z > end_mask_value:
                    send_serial_command(letter_value, "row_off")
            else:
                if z < start_mask_value:
                    send_serial_command(str(z), "column_off")
                if z > end_mask_value:
                    send_serial_command(str(z), "column_off")

        # send the command to toggle LEDs on for previous LED instructions sent
        # send_serial_command("1", "U")


if __name__ == '__main__':
    mainWindow = Tk()
    lightPanelGUIInstance = LightPanelGUI(mainWindow)
    mainWindow.protocol("WM_DELETE_WINDOW", on_closing)
    mainWindow.mainloop()
