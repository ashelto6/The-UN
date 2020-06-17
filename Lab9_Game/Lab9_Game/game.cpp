// Battleship Game Using Classes
// Antonio S.-M.
// 3/26/2020

#include "battleship.hpp"
#include <iostream>

using std::cout; using std::cin; using std::endl;

int main() {

	srand(time(nullptr));

	cout << "\nLET'S PLAY BATTLESHIP!\n";

	Fleet myFleet;

	myFleet.deployFleet();

	cout << "\nPress [v] to view ship locations after every shot! (press any key to BYPASS): ";
	char view;
	cin >> view;

	if (view == 'v' || view == 'V') {
		cout << "\nInitial Fleet";
		myFleet.printFleet();
	}

	while (myFleet.operational()) {
		Location shot;
		shot.fire();

		if (myFleet.isHitNSink(shot))
			cout << "\nThat's a Hit!";
		else
			cout << "\nThat's a miss!";

		if (view == 'v' || view == 'V')
			myFleet.printFleet();
	}

	cout << "\nGame Over! All ships have been sank!\n";
}