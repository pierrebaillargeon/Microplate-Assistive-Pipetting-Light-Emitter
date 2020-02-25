# to compile to deployable executable use pyinstaller LightGuide.py
import tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename
import serial

import pandas as pd
from pandastable import Table

import SerialUtils

DRY_RUN = False
COLUMNS = ['Source_barcode', 'Destination_barcode', 'Source_well', 'Destination_well', 'Transfer_volume']

with open("config.txt", "r") as file:
    if file.mode == "r":
        serialPorts = file.readlines()
        COMPortOne = serialPorts[0].strip()
        COMPortTwo = serialPorts[1].strip()
        if DRY_RUN:
            print("Setting up source on port " + COMPortOne)
            sourcePanelSerialConnection = None
            print("Setting up destination on port " + COMPortTwo)
            destinationPanelSerialConnection = None
        else:
            sourcePanelSerialConnection = serial.Serial(COMPortOne, '38400', parity=serial.PARITY_NONE,
                                                        stopbits=serial.STOPBITS_ONE)
            destinationPanelSerialConnection = serial.Serial(COMPortTwo, '38400', parity=serial.PARITY_NONE,
                                                             stopbits=serial.STOPBITS_ONE)
    else:
        print("Error reading serial ports config file.")


def send_serial_command(well_name, to_source):
    SerialUtils.send_serial_command(sourcePanelSerialConnection if to_source else destinationPanelSerialConnection,
                                    "well_on", well_name=well_name)


def clear_panels():
    SerialUtils.clear_panels([sourcePanelSerialConnection, destinationPanelSerialConnection])


def on_closing():
    SerialUtils.close_connection([sourcePanelSerialConnection, destinationPanelSerialConnection])
    print("Closing serial ports!")
    mainWindow.destroy()
    exit()


class LightPanelGUI(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.csvData = pd.DataFrame()
        self.currentCsvPosition = 0
        self.csvRecordCount = 0
        self.scrollCount = 1
        self.fileName = ""
        self.pt = None

        self.master = master
        self.master.title("Microplate Assistive Pipetting Light Emitter")
        self.master.maxsize(500, 500)
        self.master.minsize(500, 500)

        c = Canvas(self.master)
        c.configure(yscrollincrement='10c')

        # create all of the main containers
        top_frame = Frame(self.master, bg='grey', width=450, height=50, pady=3)

        # layout all of the main containers
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        top_frame.grid(row=0, sticky="ew")

        # Create container for table
        self.center = Frame(self.master, bg='gray2', width=450, height=500, pady=3)
        self.center.grid(row=1, sticky="nsew")

        # create the widgets for the top frame
        self.fileButton = tkinter.Button(top_frame, text="Select cherrypick file", command=self.open_file)
        self.backButton = tkinter.Button(top_frame, text="Previous well", command=self.previous_well)
        self.nextButton = tkinter.Button(top_frame, text="Next well", command=self.next_well)

        # layout the widgets in the top frame
        self.fileButton.grid(row=0, column=1)
        top_frame.grid_columnconfigure(2, weight=3)
        self.backButton.grid(row=0, column=3)
        self.nextButton.grid(row=0, column=4)

    def next_well(self):
        # set the current row to have a grey background to indicate work on this record is complete
        self.pt.setRowColors(rows=self.currentCsvPosition, clr="#D3D3D3", cols='all')
        self.pt.redraw()

        if self.currentCsvPosition < self.csvRecordCount - 1:
            self.currentCsvPosition = self.currentCsvPosition + 1
        self.parse_commands()

    def previous_well(self):
        if self.currentCsvPosition > 0:
            self.currentCsvPosition = self.currentCsvPosition - 1
        self.parse_commands()

    def open_file(self):
        self.fileName = askopenfilename()  # show an open file dialog box and return the path to the selected file
        self.csvData = pd.read_csv(self.fileName, names=COLUMNS, header=0)
        self.csvRecordCount = len(self.csvData.index)
        self.currentCsvPosition = 0
        self.pt = Table(self.center, dataframe=self.csvData, showtoolbar=False, showstatusbar=False, height=450)
        self.pt.adjustColumnWidths(30)
        self.pt.show()
        self.parse_commands()

    def parse_commands(self):
        # update the row currently highlighted in the pandastable
        self.pt.setSelectedRow(self.currentCsvPosition)
        # pt.setRowColors(rows=self.currentCsvPosition, clr="#95D680", cols='all')
        self.pt.redraw()

        # get the current source and destination wells, then send them to the send_serial_command for LEDs to be lit
        source_well_name = self.csvData.at[self.currentCsvPosition, 'Source_well']
        destination_well_name = self.csvData.at[self.currentCsvPosition, 'Destination_well']
        source_barcode = self.csvData.at[self.currentCsvPosition, 'Source_barcode']
        destination_barcode = self.csvData.at[self.currentCsvPosition, 'Destination_barcode']

        clear_panels()
        send_serial_command(source_well_name, True)
        send_serial_command(destination_well_name, False)


if __name__ == '__main__':
    mainWindow = tkinter.Tk()
    lightPanelGUIInstance = LightPanelGUI(mainWindow)
    mainWindow.protocol("WM_DELETE_WINDOW", on_closing)
    mainWindow.mainloop()
