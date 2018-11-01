/* Arduino firmware for light pipetting guide   */
/* Scripps Florida                              */ 
/* Authors: Pierre Baillargeon and Kervin Coss  */
/* Correspondence: bpierre@scripps.edu          */ 
/* Date: 8/7/2018                               */ 

boolean newData = false;  //stores whether the program is presently receiving new data/input.
const byte numChars = 32; //determines the number of characters for the lists: receivedCharArray,tempStorage, rowLetter, and illuminationCommand
char receivedCharArray[numChars]; // Stores the character input received from the user

/* Components of command received over serial port - row, column and illumination command */ 
char rowLetter[numChars] = {0}; //Stores a single character, that is later used to determine the target row that the user wants to light-up
int rowNumber;  //used to store the usable-index-number-value obtained with targetIndex, so that targetIndex can be reset to -1 so the convertRowLetterToNumber() keeps working
int columnNumber = 0; //Stores a single number, that is later used to determine the target column that the user wants to light-up
char illuminationCommand[numChars] = {0}; //Stores a single character, that is later used to determine whether the user wants to light-up a row, a column, or a single bulb 

/* Definition of I/O pin count for light guide in 96 well configuration */ 
const int numColumns = 24;
const int numRows = 16;

/* Mapping of Arduino mega I/O to pins on the light guide for 96 well configuration */ 
/* uint8_t colPins[numColumns] = {A15,A14,A13,A12,A11,A10,A9,A8,A7,A6,A5,A4}; //Declare column pins */ 
/* uint8_t rowPins[numRows] = {53,51,49,47,45,43,41,39};//Declare row pins */ 
  
/* Mapping of Arduino mega I/O to pins on the light guide for 384 well configuration */ 
uint8_t colPins[numColumns] = {38,40,42,44,46,48,50,52,A15,A14,A13,A12,A11,A10,A9,A8,A7,A6,A5,A4,A3,A2,A1,A0}; //Declare column pins 
uint8_t rowPins[numRows] = {53,51,49,47,45,43,41,39,37,35,33,31,29,27,25,23}; //Declare row pins  
 

void setup() {

  Serial.begin(9600);
  /* Print instructions to serial port; useful for debugging or reminding users what the command format is */   
  Serial.println("Enter data the following format: <A,1,S>");
  Serial.println("First parameter is row letter, second parameter is column, third parameter is illumination command.");
  Serial.println("Valid row and columns are plate density dependent.");
  Serial.println("Valid illumination commands are: S - illuminate single well, R - illuminate entire row, C - illuminate entire column.");  
  Serial.println(); 
  
  for(int i=0;i<numRows;i++) {   //delcare the row pins, so that they can be called in an array form
    pinMode(rowPins[i],OUTPUT);
  }
  for(int i=0;i<numColumns;i++) {//delcare the column pins, so that they can be called in an array form
    pinMode(colPins[i],OUTPUT);   
  }
  
  clearDisplay();  
  illuminationTest();
  clearDisplay();  
  
  /* Delete the rows below to clean up code once buttons are resolved */ 
  pinMode(12, OUTPUT);
  pinMode(6, INPUT_PULLUP);
  pinMode(13, OUTPUT);
  pinMode(7, INPUT_PULLUP);
}


void loop() {
  
  String inByte = "next";
  if (digitalRead(6) == LOW && digitalRead(7) == LOW) {   
    Serial.write("stop\r\n"); // send the data back in a new line so that it is not all one long line
  }
  if (digitalRead(6) == LOW) {
    Serial.write("next\r\n"); // send the data back in a new line so that it is not all one long line
  }  
  if (digitalRead(7) == LOW) {
    Serial.write("last\r\n"); // send the data back in a new line so that it is not all one long line
  }

  delay(100); // delay for 1/10 of a second
 
  recvWithStartEndMarkers();
  
  if (newData == true) {
    /* Parse the data received over the serial port into its constituent parts [row, column, illumination command] */ 
    parseData();
    /* Return the parsed data back to the serial port - useful for debugging & confirmation to user */ 
    displayParsedCommand();
    /* Convert the row letter to a number */ 
    rowNumber = convertRowLetterToNumber(rowLetter);
    /* Clear the display from the previous command */ 
    clearDisplay();
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
}

/* Displays the parsed information to the serial terminal; useful for debugging communication issues */ 
void displayParsedCommand() {
    Serial.print("Column:");
    Serial.println(columnNumber);
    Serial.print("Row:");
    Serial.println(rowLetter);
    Serial.print("Command: ");
    Serial.println(illuminationCommand);
    Serial.println();
}

/* Turns off all LEDs */ 
void clearDisplay(){     
  for(int i=0;i<numColumns;i++) {   
    digitalWrite(colPins[i],LOW);
  }
  for(int i=0;i<numRows;i++) {
    digitalWrite(rowPins[i],HIGH);   
  }
} 

/* Turns on all LEDs for a given row */ 
void illuminateRow(int row){              
  digitalWrite(rowPins[row],LOW);
  for (int column=0;column<numColumns;column++){
    digitalWrite(colPins[column],HIGH);
  }           
}

/* Turns on all LEDs for a given column */ 
void illuminateColumn(int column){            
  digitalWrite(colPins[column-1],HIGH);
  for(int row=0;row<numRows;row++) {
    digitalWrite(rowPins[row],LOW);     
  }           
}

/* Turns on an individual LED for a given row and column */ 
void illuminateWell(int c, int r){
  digitalWrite(colPins[c-1],HIGH);
  digitalWrite(rowPins[r],LOW);           
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
    illuminateWell(columnNumber,rowNumber);
  }
  else{
    Serial.println("ERROR Appropriate value not received.");
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
  for(int x=0;x<numRows;x++) {
    illuminateRow(x);
    delay(500);
    clearDisplay();
  }
}

