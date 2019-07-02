
/* Arduino firmware for portable light guide     */
/* Scripps Florida                               */ 
/* Author: Pierre Baillargeon                    */
/* Correspondence: bpierre@scripps.edu           */ 
/* Date: 7/1/2019                                */ 

#include <Adafruit_NeoPixel.h>
/* This code requires the Button Arduino library v1.0.0 by Michael Adams */ 
#include <Button.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

/* The PIN variable should be set to the I/O pin that your microcontroller is using to send data to your light panel */ 
#define PIN 4
/* NUM_LEDS should be set to 96 or 384 */ 
#define NUM_LEDS 96
/* NUM_COLUMNS should be set to 12 or 24 */ 
#define NUM_COLUMNS 12
/* Valid brightness values are between 0 and 255 - do NOT set brightness above 100 unless your power supply can provide
 * adequate current for the given light panel.
 */
#define BRIGHTNESS 100

/* Set the I/O pin for your button to be used to indicate 'forward' in the program below */ 
Button forwardButton(3);
/* Set the I/O pin for your button to be used to change the main software mode below */ 
Button modeButton(2);

/* The operationMode variable is used to track which of the three main modes the device is currently in: 
 * Mode 2 is HTS demo mode, 0 is titration mode and 1 is illumination mode
 */
int operationMode=1;
/* The modeCounter variable is used to track the sub-state within each of the three main modes */ 
int modeCounter=0;

/* The randomValue, currentRow, rowEndValue, wellNumber, activePixelNumbeer, controlWell and hitIntensity variables
 * are used to in the HTS demo mode including the serpentine dispense pattern visualization.
 */
int randomValue=0; 
int currentRow=0;
int rowEndValue=0;
int wellNumber=0;
int activePixelNumber=0;
int controlWell=0;
int hitIntensity=0;

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {

  forwardButton.begin();
  modeButton.begin();

  // This is for Trinket 5V 16MHz, you can remove these three lines if you are not using a Trinket
  #if defined (__AVR_ATtiny85__)
    if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
  #endif
  // End of trinket special code
  strip.setBrightness(BRIGHTNESS);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
    
}


void loop() {

  if(modeButton.pressed()) {
    processButtonPush(1);
  }
  if(forwardButton.pressed()){
    processButtonPush(0);
  }
  
}

/* Button ID 0 is next item, button ID 1 is next mode */ 
void processButtonPush(int buttonID) {
   
   /* Check to see which button was pressed and increment the related counter */ 
   if(buttonID==0) {
     modeCounter++;
   }
   if(buttonID==1){
     if(operationMode<2){
      operationMode++;
     }
     else{
      operationMode=0;
     }
     modeCounter=0;     
   }
      
   /* Call the function responsible for updating the delay based on the operationMode and modeCounter state chart */ 
   changeState(operationMode,modeCounter);
   
}
  
void changeState(int operationState, int stateCounter) {

  if(operationState==2) {
    /* Turn on a single red LED on pixel 0 to indicate that we are in illumination mode */ 
    if(stateCounter==0) {
      clearDisplay();
      strip.setPixelColor(0,strip.Color(255,0,0)); 
      strip.show();
    }
    if(stateCounter==1) {
      /* Simulating cell dispense with serpentine pattern */ 
      for(int j = 0; j < NUM_LEDS ; j++){
        wellNumber=j+1;
        currentRow = floor((wellNumber-1)/NUM_COLUMNS);
        rowEndValue = NUM_COLUMNS * (currentRow+1);
        if(currentRow == 0 or currentRow % 2 == 0) {
          activePixelNumber = j;
        }
        else {
          activePixelNumber = (rowEndValue-wellNumber-(NUM_COLUMNS-1)) + rowEndValue;
          activePixelNumber = activePixelNumber - 1;
        }
        strip.setPixelColor(activePixelNumber,strip.Color(180,0,0)); 
        delay(50);
        strip.show();
      }
    }
    
    /* Simulating read reagent dispense with serpentine pattern */ 
    if(stateCounter==2) {       
      for(int j = 0; j < NUM_LEDS ; j++){
        wellNumber=j+1;
        currentRow = floor((wellNumber-1)/NUM_COLUMNS);
        rowEndValue = NUM_COLUMNS * (currentRow+1);
        if(currentRow == 0 or currentRow % 2 == 0) {
          activePixelNumber = j;
        }
        else {
          activePixelNumber = (rowEndValue-wellNumber-(NUM_COLUMNS-1)) + rowEndValue;
          activePixelNumber = activePixelNumber - 1;
        }
        strip.setPixelColor(activePixelNumber,strip.Color(255,255,0)); 
        delay(50);
        strip.show();  
      }     
    } 
    
    /* Simulating plate reader excitation light */ 
    else if(stateCounter==3) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(0,0,255));        
      } 
      strip.show();   
    }  

    /* Simulating plate reader emission light */ 
    else if(stateCounter==4) {    
      for(int j = 0; j < NUM_LEDS ; j++){
        randomValue=random(6);      
        controlWell=0;        
        if(j==0 || j==12 || j==24 || j==36 || j==48 || j==60 || j==72 || j==84 ) {
          controlWell=1;              
        }
        if(j==11 || j==23 || j==35 || j==47 || j==59 || j==71 || j==83 || j==95 ) {
          randomValue=-1;
        }      
        if(randomValue==1 && controlWell==0){ 
          hitIntensity=random(255);
          strip.setPixelColor(j,strip.Color(0,hitIntensity,0)); 
        }
        else if(controlWell==1){
          strip.setPixelColor(j,strip.Color(0,255,0)); 
        }
        else if(randomValue==-1){
          strip.setPixelColor(j,strip.Color(0,0,25)); 
        }
        else{
          strip.setPixelColor(j,strip.Color(0,0,255)); 
        }
      } 
      strip.show();          
    }      
    
    /* Turn all LEDs off to reset the simulation */ 
    else if(stateCounter>4){
      clearDisplay();      
      strip.show();     
      modeCounter=0;
    }
  }
  
  /* Titration demo mode */ 
  else if(operationState==0) {
     for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(0,0,0));       
     }   
    /* Turn on a single orange LED on pixel 0 to indicate that we are in illumination mode */ 
    if(stateCounter==0) {
      clearDisplay();
      strip.setPixelColor(0,strip.Color(255,165,0)); 
      strip.show();    
    }
    else {
      strip.setPixelColor(stateCounter+1,strip.Color(255,165,0));
      strip.setPixelColor(stateCounter+13,strip.Color(255,165,0));
      strip.setPixelColor(stateCounter+25,strip.Color(255,165,0));
      strip.setPixelColor(stateCounter+37,strip.Color(255,165,0));
      strip.setPixelColor(stateCounter+49,strip.Color(255,165,0));
      strip.setPixelColor(stateCounter+61,strip.Color(255,165,0));
      strip.setPixelColor(stateCounter+73,strip.Color(255,165,0));
      strip.setPixelColor(stateCounter+85,strip.Color(255,165,0));      
    }
    if(stateCounter==8) {
        modeCounter=0;
    }          
    strip.show();
  }
  
  /* Illumination mode */ 
  else if(operationState==1) {
    /* Turn on a single purple LED on pixel 0 to indicate that we are in illumination mode */  
    if(stateCounter==0){
      clearDisplay();
      strip.setPixelColor(0,strip.Color(75,0,130)); 
      strip.show();  
    }
    /* Illuminate all LEDs red */
    if(stateCounter==1) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(255,0,0));       
      } 
    }
    /* Illuminate all LEDs blue */ 
    else if(stateCounter==2) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(0,0,255));       
      } 
    }
    /* Illuminate all LEDs green */ 
    else if(stateCounter==3) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(0,255,0));       
      }   
    }
    /* Illuminate all LEDs orange */ 
    else if(stateCounter==4) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(255,165,0));       
      }     
    }
    /* Illuminate all LEDs white */ 
    else if(stateCounter==5) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(255,255,255));       
      }   
    }    
    /* Illuminate all LEDs violet */ 
    else if(stateCounter==6) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(160,32,240));       
      }   
    }    
    /* Illuminate all LEDs yellow */ 
    else if(stateCounter==7) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(255,255,0));       
      }    
    }    
    /* Illuminate all LEDs indigo */ 
    else if(stateCounter==8) {
      for(int j = 0; j < NUM_LEDS ; j++){
        strip.setPixelColor(j,strip.Color(75,0,130));       
      }              
      modeCounter=0;
    }
    strip.show();    
  }
  return;
}

void clearDisplay() {
  for(int x=0;x<NUM_LEDS;x++) {
    strip.setPixelColor(x,strip.Color(0,0,0));
  }
  return;
}
