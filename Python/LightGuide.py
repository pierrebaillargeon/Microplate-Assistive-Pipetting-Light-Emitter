# to compile to deployable executable use pyinstaller LightGuide.py
import tkinter
from tkinter.filedialog import askopenfilename
from tkinter import *
import serial
import pandas as pd
from pandastable import Table

TEST = True

with open("config.txt", "r") as file:
    if file.mode == "r":
        serialPorts = file.readlines()
        COMportOne = serialPorts[0].strip('\n')
        COMportTwo = serialPorts[1].strip('\n')
        if TEST:
            print("Setting up source on port "+COMportOne)
            print("Setting up destination on port "+COMportTwo)
        else:
            sourcePanelSerialConnection = serial.Serial(COMportOne, '9600', timeout=0, stopbits=serial.STOPBITS_TWO)
            destinationPanelSerialConnection = serial.Serial(COMportTwo, '9600', timeout=0, stopbits=serial.STOPBITS_TWO)
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

def getRowNameFromWell(well):
    rowName = well[0:1]  # for row
    return rowName

def getColumnNumberFromWell(well):
    columnNumber = well[1:3]
    return columnNumber

def sendSerialCommand(wellName,destination,barcode):
    rowName = getRowNameFromWell(wellName)
    columnNumber = getColumnNumberFromWell(wellName)
    serialString = destination + " <" + rowName + "," + columnNumber + ",S," + barcode +">"
    serialString = bytes(serialString, 'us-ascii')
    print(serialString)
    if destination=="source":
        write_source(serialString)
    else:
        write_destination(serialString)

def turnPanelsOff():
    serialString = "<A,1,X,>"
    serialString = bytes(serialString, 'us-ascii')
    print(serialString)
    write_source(serialString)
    write_destination(serialString)

def parseCommands(self):

    # update the row currently highlighted in the pandastable
    pt.setSelectedRow(self.currentCsvPosition)
    #pt.setRowColors(rows=self.currentCsvPosition, clr="#95D680", cols='all')
    pt.redraw()

    # get the current source and destination wells, then send them to the sendSerialCommand for LEDs to be lit
    sourceWellName = self.csvData.at[self.currentCsvPosition, 'Source_well']
    destinationWellName = self.csvData.at[self.currentCsvPosition, 'Destination_well']
    sourceBarcode = self.csvData.at[self.currentCsvPosition,'Source_barcode']
    destinationBarcode = self.csvData.at[self.currentCsvPosition,'Destination_barcode']
    sendSerialCommand(sourceWellName, "source",sourceBarcode)
    sendSerialCommand(destinationWellName, "destination",destinationBarcode)

def onClosing():
    turnPanelsOff()
    if not TEST:
        sourcePanelSerialConnection.close()
        destinationPanelSerialConnection.close()
    print("Closing serial ports!")
    mainWindow.destroy()
    exit()

class lightPanelGUI(Frame):

    def __init__(self,master):
        self.csvData = pd.DataFrame()
        self.currentCsvPosition=0
        self.csvRecordCount=0
        self.scrollCount=1

        self.master = master
        self.master.title("Microplate Assistive Pipetting Light Emitter")
        self.master.maxsize(500,500)
        self.master.minsize(500,500)

        c = Canvas(self.master)
        c.configure(yscrollincrement='10c')

        # create all of the main containers
        top_frame = Frame(self.master, bg='grey', width=450, height=50,pady=3)

        # layout all of the main containers
        self.master.grid_rowconfigure(1,weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        top_frame.grid(row=0, sticky="ew")

        # create the widgets for the top frame
        self.fileButton = tkinter.Button(top_frame, text="Select cherrypick file", command=self.openFile)
        self.backButton = tkinter.Button(top_frame, text="Previous well", command=self.previousWell)
        self.nextButton = tkinter.Button(top_frame, text="Next well", command=self.nextWell)

        # layout the widgets in the top frame
        self.fileButton.grid(row=0, column=1)
        top_frame.grid_columnconfigure(2,weight=3)
        self.backButton.grid(row=0, column=3)
        self.nextButton.grid(row=0, column=4)


    def nextWell(self):
        # set the current row to have a grey background to indicate work on this record is complete
        pt.setRowColors(rows=self.currentCsvPosition,clr="#D3D3D3",cols='all')
        pt.redraw()
        # check to see how many times the next button has been clicked and scroll the table every two clicks
        if self.currentCsvPosition < self.csvRecordCount - 1:
            self.currentCsvPosition=self.currentCsvPosition+1
        parseCommands(self)

    def previousWell(self):
        if self.currentCsvPosition > 0:
            self.currentCsvPosition = self.currentCsvPosition - 1
        parseCommands(self)

    def openFile(self):
        global pt
        self.fileName = askopenfilename()  # show an open file dialog box and return the path to the selected file
        self.csvData = pd.read_csv(self.fileName,names=['Source_barcode','Destination_barcode','Source_well','Destination_well','Transfer_volume'],header=0)
        self.csvRecordCount=len(self.csvData.index)
        self.currentCsvPosition=0
        center = Frame(self.master, bg='gray2', width=450, height=500, pady=3)
        center.grid(row=1, sticky="nsew")
        pt = Table(center, dataframe=self.csvData, showtoolbar=False, showstatusbar=False, height=450)
        pt.adjustColumnWidths(30)
        pt.show()
        parseCommands(self)

if __name__ == '__main__':
    mainWindow = tkinter.Tk()
    lightPanelGUIinstance = lightPanelGUI(mainWindow)
    mainWindow.protocol("WM_DELETE_WINDOW", onClosing)
    mainWindow.mainloop()