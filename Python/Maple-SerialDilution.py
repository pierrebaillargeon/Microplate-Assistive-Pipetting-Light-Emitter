# to compile to deployable executable use pyinstaller Maple-SerialDilution.py
import tkinter
from tkinter import *
import serial
import string
import time

alphabet = list(string.ascii_uppercase)
last_received = ''

file = open("C:\PipettingLightGuide\config.txt","r")
if file.mode == "r":
    serialPorts = file.readlines()
    COMportOne = serialPorts[0].strip('\n')
    sourcePanelSerialConnection = serial.Serial(COMportOne, '500000', timeout=0, stopbits=serial.STOPBITS_ONE)

else:
    print("Error reading serial ports config file.")

def getRowNameFromWell(well):
    rowName = well[0:1]  # for row
    return rowName

def getColumnNumberFromWell(well):
    columnNumber = well[1:3]
    return columnNumber

# read data from serial port
def readSerial():
    dataFromSerial = sourcePanelSerialConnection.read(2000)
    #print(dataFromSerial)

def sendSerialCommand(value,command):

    #rowName = getRowNameFromWell(wellName)
    #columnNumber = getColumnNumberFromWell(wellName)
    serialString = "<" + value + "," +  value + "," + command + ",Titration>\r\n"
    serialString = bytes(serialString, 'us-ascii')
    print(serialString)
    #if destination=="source":
    sourcePanelSerialConnection.write(serialString)
    time.sleep(.15)

    readSerial()

def turnPanelsOff():
    serialString = "<A,1,X,>"
    serialString = bytes(serialString, 'us-ascii')
    print(serialString)
    sourcePanelSerialConnection.write(serialString)

def parseCommands(self):

    # send the command to clear existing LEDs
    sendSerialCommand("1", "X")

    startValueList = self.startValues.get().split(',')
    #print(startValueList)
    rowMaskList = self.maskValues.get().split('-')
    #print(rowMaskList)
    #print(self.titrationMode.get())

    if(self.titrationMode.get()=="By column"):
        sendCommand="C"
        startMaskValue = alphabet.index(rowMaskList[0])
        endMaskValue = alphabet.index(rowMaskList[1])
    else:
        sendCommand="R"
        startMaskValue = int(rowMaskList[0])
        endMaskValue = int(rowMaskList[1])

    for value in startValueList:
        if(self.titrationMode.get()=="By column"):
            sendSerialCommand(value,sendCommand)
        else:
            sendSerialCommand(value, sendCommand)

    # define the upper bound for the mask
    selectedDensity = self.plateDensitySelection.get()
    selectedTitrationMode = self.titrationMode.get()
    if (selectedDensity == "96 well"):
        if (selectedTitrationMode == "By column"):
            upperMaskBoundary = 8
            lowerMaskBoundary = 0
        else:
            upperMaskBoundary = 12
            lowerMaskBoundary = 1
    else:
        if (selectedTitrationMode == "By column"):
            upperMaskBoundary = 16
            lowerMaskBoundary = 0
        else:
            upperMaskBoundary = 25
            lowerMaskBoundary = 1


    for z in range(lowerMaskBoundary, upperMaskBoundary):
        if(self.titrationMode.get()=="By column"):
            letterValue = alphabet[z]
            if(z < startMaskValue):
                sendSerialCommand(letterValue,"CR")
            if (z > endMaskValue):
                sendSerialCommand(letterValue, "CR")
        else:
            if (z < startMaskValue):
                sendSerialCommand(str(z), "CC")
            if (z > endMaskValue):
                sendSerialCommand(str(z), "CC")

    # send the command to toggle LEDs on for previous LED instructions sent
    sendSerialCommand(value, "U")


def onClosing():
    turnPanelsOff()
    # sourcePanelSerialConnection.close()
    print("Closing serial ports!")
    mainWindow.destroy()
    exit()

class lightPanelGUI(Frame):

    def __init__(self,master):

        self.master = master
        self.master.title("Microplate Assistive Pipetting Light Emitter")
        self.master.maxsize(425,300)
        self.master.minsize(425,300)

        c = Canvas(self.master)
        c.configure(yscrollincrement='10c')

        # layout all of the main containers


        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.titrationMode = StringVar(value="By column")
        self.titrationMode.set('By column')
        self.plateDensitySelection = StringVar()
        self.startValues = StringVar()
        self.startValues.set("3,13")
        self.maskValues = StringVar()
        self.maskValues.set("A-P")
        self.plateDensitySelection.set('384 well')
        self.plateDensityOptions = {'384 well', '96 well'}
        self.nextButtonText = tkinter.StringVar(value="Next column")
        self.previousButtonText = tkinter.StringVar(value="Previous column")
        self.startValuesText=tkinter.StringVar(value="Start column(s)")
        self.maskText=tkinter.StringVar(value="Row mask")

        # create the widgets
        self.titrationModeColumn = tkinter.Radiobutton(self.master, text="By column", variable=self.titrationMode, value='By column', padx=0, pady=0, command=self.columnSelection)
        self.titrationModeRow = tkinter.Radiobutton(self.master, text="By row", variable=self.titrationMode, value='By row', padx=0, pady=0, command=self.rowSelection)
        self.backButton = tkinter.Button(self.master, textvariable=self.previousButtonText, command=self.previousSelection)
        self.nextButton = tkinter.Button(self.master, textvariable=self.nextButtonText, command=self.nextSelection)
        self.plateDensityDropdown = tkinter.OptionMenu(self.master, self.plateDensitySelection, *self.plateDensityOptions, command=self.updateParameters)
        self.startValuesEntry = tkinter.Entry(self.master, textvariable=self.startValues, width=4)
        self.maskEntry = tkinter.Entry(self.master, textvariable=self.maskValues, width=4)


        Label(self.master, text="Titration Mode", font="Helvetica 18 bold").grid(row=0, column=0, sticky=W, padx=20, pady=0)
        self.titrationModeColumn.grid(row=1, column=0, sticky=W, padx=30, pady=0)
        self.titrationModeRow.grid(row=2, column=0, sticky=W, padx=30, pady=0)
        self.nextButton.grid(row=1, column=3, padx=(0, 10), pady=0)
        self.backButton.grid(row=1, column=4, padx=(0,10), pady=0)
        Label(self.master, text="Plate Density", font="Helvetica 18 bold").grid(row=3, column=0, sticky=W, padx=20, pady=(10,0))
        self.plateDensityDropdown.grid(row=4, column=0, sticky=W, padx=30, pady=0)
        Label(self.master, textvariable=self.startValuesText, font="Helvetica 18 bold").grid(row=5, column=0, sticky=W, padx=20, pady=(10,0))
        self.startValuesEntry.grid(row=6, column=0, sticky=W, padx=30, pady=0)
        Label(self.master, textvariable=self.maskText, font="Helvetica 18 bold").grid(row=7, column=0, sticky=W, padx=20, pady=(10,0))
        self.maskEntry.grid(row=8, column=0, sticky=W, padx=30, pady=(0,10))

        time.sleep(2)
        readSerial()
        # send the initial command to light up the panel with the default parameters
        parseCommands(self)

    def columnSelection(self):
        self.nextButtonText.set("Next column")
        self.previousButtonText.set("Previous column")
        self.startValuesText.set("Start column(s)")
        self.maskText.set("Row mask")
        self.updateParameters(self)

    def rowSelection(self):
        self.nextButtonText.set("Next row")
        self.previousButtonText.set("Previous row")
        self.startValuesText.set("Start row(s)")
        self.maskText.set("Column mask")
        self.updateParameters(self)

    def updateParameters(self, parameters):
        selectedDensity = self.plateDensitySelection.get()
        selectedTitrationMode = self.titrationMode.get()
        if(selectedDensity == "96 well"):
            if(selectedTitrationMode == "By column"):
                self.startValues.set("2,7")
                self.maskValues.set("A-H")
            else:
                self.startValues.set("B,E")
                self.maskValues.set("1-12")
        else:
            if (selectedTitrationMode == "By column"):
                self.startValues.set("3,13")
                self.maskValues.set("A-P")
            else:
                self.startValues.set("C,F")
                self.maskValues.set("1-24")

        parseCommands(self)

    def nextSelection(self):
        startValueList = self.startValues.get().split(',')
        selectedDensity = self.plateDensitySelection.get()
        if(selectedDensity == '384 well'):
            upperColumnLimit=24
            upperRowLimit=15
        else:
            upperColumnLimit=12
            upperRowLimit=7
        if (self.titrationMode.get() == "By column"):
            if (int(startValueList[1]) < upperColumnLimit):
                lowerStartValue = int(startValueList[0]) + 1
                upperStartValue = int(startValueList[1]) + 1
                newStartValue = str(lowerStartValue) + "," + str(upperStartValue)
                self.startValues.set(newStartValue)
        else:
            if (alphabet.index(startValueList[1]) < upperRowLimit):
                lowerStartValue = alphabet[alphabet.index(startValueList[0]) + 1]
                upperStartValue = alphabet[alphabet.index(startValueList[1]) + 1]
                newStartValue = str(lowerStartValue) + "," + str(upperStartValue)
                self.startValues.set(newStartValue)

        parseCommands(self)

    def previousSelection(self):

        startValueList = self.startValues.get().split(',')
        if (self.titrationMode.get() == "By column"):
            if (int(startValueList[0]) > 1):
                lowerStartValue = int(startValueList[0]) - 1
                upperStartValue = int(startValueList[1]) - 1
                newStartValue = str(lowerStartValue) + "," + str(upperStartValue)
                self.startValues.set(newStartValue)
        else:
            if (alphabet.index(startValueList[0]) > 0):
                lowerStartValue = alphabet[alphabet.index(startValueList[0]) - 1]
                upperStartValue = alphabet[alphabet.index(startValueList[1]) - 1]
                newStartValue = str(lowerStartValue) + "," + str(upperStartValue)
                self.startValues.set(newStartValue)

        parseCommands(self)

if __name__ == '__main__':
    mainWindow = tkinter.Tk()
    lightPanelGUIinstance = lightPanelGUI(mainWindow)
    mainWindow.protocol("WM_DELETE_WINDOW", onClosing)
    mainWindow.mainloop()