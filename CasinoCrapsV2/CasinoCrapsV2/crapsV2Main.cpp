// Casino Craps Game Version 2.0
// 4/27/2020
// Antonio Shelton

#include "crapsV2.hpp"
#include <cstdlib>
#include <ctime>

int main() {
	srand(time(nullptr));

	PlayCraps game;
	game.instructions();
	game.setPlayer();
	bool firstRoll; // loop conditional

	//do {   //UNCOMMENT TO ACTIVATE LOOP
		firstRoll = game.firstRollPlay(); 

		if (!(firstRoll))  
			firstRoll = game.pointPlay(); 
		
	//} while (firstRoll);
}