# to compile to deployable executable use pyinstaller LightGuide.py
import tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename

import pandas as pd
import serial
from pandastable import Table

TEST = True
COLUMNS = ['Source_barcode', 'Destination_barcode', 'Source_well', 'Destination_well', 'Transfer_volume']

with open("config.txt", "r") as file:
    if file.mode == "r":
        serialPorts = file.readlines()
        COMPortOne = serialPorts[0].strip()
        COMPortTwo = serialPorts[1].strip()
        if TEST:
            print("Setting up source on port " + COMPortOne)
            print("Setting up destination on port " + COMPortTwo)
        else:
            sourcePanelSerialConnection = serial.Serial(COMPortOne, '9600', timeout=0, stopbits=serial.STOPBITS_TWO)
            destinationPanelSerialConnection = serial.Serial(COMPortTwo, '9600', timeout=0,
                                                             stopbits=serial.STOPBITS_TWO)
    else:
        print("Error reading serial ports config file.")


def write_source(bytestring):
    if TEST:
        print("Sending bytestring to source: " + str(bytestring))
    else:
        sourcePanelSerialConnection.write(bytestring)


def write_destination(bytestring):
    if TEST:
        print("Sending bytestring to destination: " + str(bytestring))
    else:
        destinationPanelSerialConnection.write(bytestring)


def get_row_name_from_well(well):
    row_name = well[0:1]  # for row
    return row_name


def get_column_number_from_well(well):
    column_number = well[1:3]
    return column_number


def send_serial_command(well_name, to_source, barcode):
    row_name = get_row_name_from_well(well_name)
    column_number = get_column_number_from_well(well_name)
    serial_string = "<" + row_name + "," + column_number + ",S," + barcode + ">"
    serial_string = bytes(serial_string, 'us-ascii')
    print(serial_string)
    if to_source:
        write_source(serial_string)
    else:
        write_destination(serial_string)


def turn_panels_off():
    serial_string = "<A,1,X,>"
    serial_string = bytes(serial_string, 'us-ascii')
    print(serial_string)
    write_source(serial_string)
    write_destination(serial_string)


def on_closing():
    turn_panels_off()
    if not TEST:
        sourcePanelSerialConnection.close()
        destinationPanelSerialConnection.close()
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
        send_serial_command(source_well_name, True, source_barcode)
        send_serial_command(destination_well_name, False, destination_barcode)


if __name__ == '__main__':
    mainWindow = tkinter.Tk()
    lightPanelGUIInstance = LightPanelGUI(mainWindow)
    mainWindow.protocol("WM_DELETE_WINDOW", on_closing)
    mainWindow.mainloop()
