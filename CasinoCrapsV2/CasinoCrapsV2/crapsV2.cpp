// Casino Craps Game Version 2.0

#include <vector>
#include "crapsV2.hpp"
#include <cstdlib>
#include <ctime>
#include <string>

using std::cout; using std::cin; using std::vector;

void PlayCraps::instructions() const {
	cout << "             \a                 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" << "\n"
		<< "                              ************   WELCOME TO THE SHELTON CASINO   ************" << "\n"
		<< "                              ********* STEP UP TO THE TABLE AND ROLL YOUR DICE *********" << "\n"
		<< "                              $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" << "\n"
		<< "\nHOW TO PLAY:"
		<< "\n- Must have at least 1 player.\n"
		<< "- As long as your first roll is not 2, 3, 12, 7 or 11, the number you roll is your point.\n"
		<< "- When the player wins, a chime will sound indicating the win. The player will roll for a new point.\n"
		<< "- When the player loses, a chime will sound indicating the loss.  The player will roll for a new point.\n"
		<< "\nWAYS TO WIN:"
		<< "\n1. If it is your first roll and you roll a 7 or 11.\n"
		<< "2. If you have established a point and you roll that number again before rolling a 7.\n"
		<< "\nWAYS TO LOSE:"
		<< "\n1. If it is your first roll and you roll a 2, 3, or 12.\n"
		<< "2. If you have established a point and you roll a 7 before rolling your point number again.\n"
		<< "\nNAVIGATION:"
		<< "\n- To roll, when prompted to roll enter [R]\n"
		<< "- To exit the game, when prompted to roll enter [X]\n"
		<< "- To view these instructions, when prompted to roll enter [I]\n"
		<< "\n----------------------------------------------------------------------------------------------------------------------\n";
}
void PlayCraps::setPlayer() {
	cout << "\nEnter your name: ";
	getline(cin, player_);
	cout << "\nIT'S TIME TO ROLL! GOODLUCK!\n";
}
void PlayCraps::opButton() const {
	char op;
	cout << "\nPress [R] to roll: ";
	cin >> op;

	while (op != 'R' && op != 'r') { // menu options
		if (op == 'X' || op == 'x') {
			cout << "------------------------^EXIT^------------------------\n";
			exit(0);
		}
		else if (op == 'I' || op == 'i') {
			instructions();
			cout << "\nPress [R] to roll: ";
			cin >> op;
		}
		else {
			cout << "\n\a*Invalid Entry! (Options: [R]OLL, [I]NSTRUCTIONS or E[X]IT)*\n"
				<< "\nPress [R] to roll: ";
			cin >> op;
		}
	}
}
int PlayCraps::setDice() {
	die1_ = rand() % 6 + 1;
	die2_ = rand() % 6 + 1;

	return die1_ + die2_; // (2-12)
}
void PlayCraps::setIter() {
	loser_ = find(losingNums_.begin(), losingNums_.end(), roll_);
	winner_ = find(winningNums_.begin(), winningNums_.end(), roll_);
} 
bool PlayCraps::firstRollPlay() {
	opButton();
	setRoll();
	setIter();
	printRoll();

	if (winner_ != winningNums_.end() || loser_ != losingNums_.end()) {
		if (winner_ != winningNums_.end()) {
			cout << "\aYOU WIN! You rolled a(n) " << roll_ << " on your first roll!" << "\n"
				<< "-------------------------^WIN^-------------------------\n";
		}
		else { // roll_ matches a losing number
			cout << "\aYOU LOSE! You rolled a " << roll_ << " on your first roll!" << "\n"
				<< "-------------------------^LOSS^-------------------------\n";
		}
		return true;
	}
	else { // roll_ must be == 4,5,6,8,9 or 10
		cout << "You found a point: " << roll_ << "\n"
			<< "------------------------^POINT^------------------------\n";
		setPoint();
		return false;
	}
}
bool PlayCraps::pointPlay(){
	opButton();
	setRoll();
	printRoll();
	cout << "Your point is: " << point_ << "\n";

	while (roll_ != point_ && roll_ != winningNums_[0]) { //winningNums_[0] == 7
		opButton();
		setRoll();
		printRoll();
		cout << "Your point is: " << point_ << "\n";
	}
	if (roll_ == winningNums_[0]) {
		cout << "\aYOU LOSE! You rolled a " << roll_ << "\n"
			<< "------------------------^LOSS^------------------------\n";
	}
	else if (roll_ == point_) {
		cout << "\aYOU WIN! You rolled your point: " << point_ << "\n"
			<< "------------------------^WIN^-------------------------\n";
	}
	return true;
}





