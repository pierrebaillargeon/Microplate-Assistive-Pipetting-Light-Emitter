/* Arduino firmware for light pipetting guide v2 */
/* Scripps Florida                               */ 
/* Authors: Pierre Baillargeon and Kervin Coss   */
/* Correspondence: bpierre@scripps.edu           */ 
/* Date: 10/29/2018                              */ 

#include <FastLED.h>
#include "Adafruit_LiquidCrystal.h"

boolean newData = false;  //stores whether the program is presently receiving new data/input.
const byte numChars = 32; //determines the number of characters for the lists: receivedCharArray,tempStorage, rowLetter, and illuminationCommand
char receivedCharArray[numChars]; // Stores the character input received from the user

/* Components of command received over serial port - row, column and illumination command */ 
char rowLetter[numChars]= {0}; //Stores a single character, that is later used to determine the target row that the user wants to light-up
char plateBarcode[numChars];
int rowNumber;  //used to store the usable-index-number-value obtained with targetIndex, so that targetIndex can be reset to -1 so the convertRowLetterToNumber() keeps working
int columnNumber = 0; //Stores a single number, that is later used to determine the target column that the user wants to light-up
char illuminationCommand[numChars] = {0}; //Stores a single character, that is later used to determine whether the user wants to light-up a row, a column, or a single bulb 

/* Definition of I/O pin count for light guide in 384 well configuration */ 
const int numColumns = 24;
const int numRows = 16;
int pixelNumber;

CRGB leds[384];
Adafruit_LiquidCrystal lcd(0);

void setup() {
  
  FastLED.addLeds<NEOPIXEL, 6>(leds, 384); 
  
  Serial.begin(500000);
  /* Print instructions to serial port; useful for debugging or reminding users what the command format is */   
  Serial.println(F("Enter data the following format: <A,1,S,Barcode>"));
  Serial.println(F("First parameter is row letter, second parameter is column, third parameter is illumination command."));
  Serial.println(F("Valid row and columns are plate density dependent."));
  Serial.println(F("Valid illumination commands are: S - illuminate single well, R - illuminate entire row, C - illuminate entire column."));  
  Serial.println(); 

  
 // illuminationTest();
  clearDisplay();  

  // set up the LCD's number of rows and columns: 
  // Print a message to the LCD.
  lcd.begin(16, 2);  
  lcd.print(F("Barcode:"));
  lcd.setBacklight(HIGH);
  
}


void loop() {

  delay(100); // delay for 1/10 of a second
// 
  recvWithStartEndMarkers();
  
  if (newData == true) {
    /* Parse the data received over the serial port into its constituent parts [row, column, illumination command] */ 
    parseData();
    /* Return the parsed data back to the serial port - useful for debugging & confirmation to user */ 
    displayParsedCommand();
    /* Convert the row letter to a number */ 
    rowNumber = convertRowLetterToNumber(rowLetter);
    /* Clear the display from the previous command */     
    //clearDisplay();
    /* Execute the new command */ 
    parseIlluminationCommand(String(illuminationCommand));
    /* Set newData to false to indicate that we have processed this command */ 
    newData = false;
  }  
}

/* Receive incoming serial data and store in receivedCharArray array */ 
void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte indexListCounter = 0;
  char startMarker = '<';
  char endMarker = '>';
  char receivedCharacter;

  while (Serial.available() > 0 && newData == false) {
    receivedCharacter = Serial.read();
    if (recvInProgress == true) {
      if (receivedCharacter != endMarker) {
        receivedCharArray[indexListCounter] = receivedCharacter;
        indexListCounter++;
        if (indexListCounter >= numChars) {
          indexListCounter = numChars - 1;
        }
      }
      else {
        receivedCharArray[indexListCounter] = '\0'; // terminate the string
        recvInProgress = false;
        indexListCounter = 0;
        newData = true;
      }
    }
    else if (receivedCharacter == startMarker) {
      recvInProgress = true;
    }
  }
}

/* Parse incoming serial data */ 
void parseData() {      

    char * strtokIndx; // this is used by strtok() as an index
    strtokIndx = strtok(receivedCharArray,",");      // get the first part - the string
    strcpy(rowLetter, strtokIndx); // copy it to rowLetter       
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    columnNumber = atoi(strtokIndx);// convert this part to an integer    
    strtokIndx = strtok(NULL,",");      // get the first part - the string    
    strcpy(illuminationCommand, strtokIndx); // copy it to illuminationCommand
    strtokIndx = strtok(NULL,",");      // get the plate barcode
    strcpy(plateBarcode, strtokIndx); // copy it to illuminationCommand
}

/* Displays the parsed information to the serial terminal; useful for debugging communication issues */ 
void displayParsedCommand() {
    Serial.print(F("Column:"));
    Serial.println(columnNumber);
    Serial.print(F("Row:"));
    Serial.println(rowLetter);
    Serial.print(F("Command:"));
    Serial.println(illuminationCommand);    
    lcd.setCursor(0, 1);
    lcd.print(String(plateBarcode));
}

/* Turns off all LEDs */ 
void clearDisplay(){     
  FastLED.clear();
  FastLED.show();
  Serial.println(F("Display cleared."));    
} 

/* Turns on all LEDs for a given row */ 
void illuminateRow(int row){   
  Serial.print(F("Row:"));
  Serial.println(row);           
  for (int column=1;column=<numColumns;column++){
    setLED(row, column, CRGB::White);
  }           
  //FastLED.show();
}

/* Turns on all LEDs for a given column */ 
void illuminateColumn(int column){       
  Serial.print(F("Column:"));
  Serial.println(column);
  for(int row=0;row<numRows;row++) {
    setLED(row, column, CRGB::White);
  }           
  //FastLED.show();
}

/* Turns on an individual LED for a given row and column */ 
void illuminateWell(int row, int column){
//  Serial.print(F("Pixel #:"));
//  Serial.println(pixelNumber);
  setLED(row, column, CRGB::White);
  FastLED.show();           
}

/* Determine which illumination command has been received and call the corresponding illumination function */ 
void parseIlluminationCommand(String illuminationCommand){
  /* Clear the display */ 
  if(illuminationCommand == "X"){
    clearDisplay();
  }
  /* Light up a single column */ 
  else if(illuminationCommand == "C"){
    illuminateColumn(columnNumber);
  }
  /* Light up a single row */ 
  else if(illuminationCommand == "R"){
    illuminateRow(rowNumber);
  }
  /* Light up a single LED */ 
  else if(illuminationCommand == "S"){    
    illuminateWell(rowNumber, columnNumber);
  }
  /* Turn off a single row */ 
  else if(illuminationCommand == "CR"){    
    clearRow(rowNumber);
  }  
  /* Turn off a column row */ 
  else if(illuminationCommand == "CC"){    
    clearColumn(columnNumber);
  }    
  /* Update display */ 
  else if(illuminationCommand == "U"){    
    updateDisplay();
  }    
  else{
    Serial.println(F("ERROR Appropriate value not received."));    
  }
}

/* Convert the row letter to a number value */ 
int convertRowLetterToNumber(char rowLetterReceived[0]){
  /* The character A is represented by the integer value 65, subtract that and you have the integer value of the row number */ 
  rowNumber = rowLetterReceived[0] - 65;
  return rowNumber;
}

/* Function to to illuminate one row at a time, useful to run at startup to identify dead LEDs */ 
void illuminationTest() {
  for(int x=0;x<384;x++) {
    leds[x] = CRGB::White;    
  }
  FastLED.show();
}



/* Turns off all LEDs for a given row */ 
void clearRow(int row){       
  Serial.print(F("Clearing row:"));
  Serial.println(row);   
  for(int column=1;column=<numColumns;column++) {
    setLED(row, column, CRBG::Black);
  }             
}

/* Command for updating the display */ 
void updateDisplay() {
  FastLED.show();
}


/* Turns off all LEDs for a given column */ 
void clearColumn(int column){       
  Serial.print(F("Clearing column:"));
  Serial.println(column);
  for(int row=0;row<numRows;row++) {
    setLED(row, column, CRBG::Black);
  }           
  //FastLED.show();
}

void setLED(int row, int column, CRGB color){
  leds[row*numColumns + (column-1)] = color;
}
