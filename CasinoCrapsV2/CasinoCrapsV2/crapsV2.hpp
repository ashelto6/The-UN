// Casino Craps Game Version 2.0

#pragma once
#include <vector>
#include <iostream>
#include <algorithm>

using std::string; using std::vector;

#ifndef CRAPSV2_HPP
#define CRAPSV2_HPP

class PlayCraps {
public:
	PlayCraps() : player_("Player"), die1_(-1), die2_(-1), roll_(-1), point_(-1) {}; // void con: init player_, die1_, die2_, roll_ and point_
	void instructions() const; // Instructs player how the game works
	void setPlayer(); // assigns player_ the player's chosen name
	void opButton() const; // performs an operation based on user's entry if the entry is != 'r' || 'R'
	int setDice(); // assigns random integers between (1-6) to die1_ and die2_, returns die1_ + die2_ (a number 2-12)
	void printRoll() const {std::cout<<"\nRoll: "<<die1_<<" "<<die2_<<"\n";} // prints player's roll, format: die1_ " " die2_	
	bool firstRollPlay(); // GamePlay for first roll, returns true if player wins/loses, false if a pointNum is rolled
	void setPoint() {point_ = roll_;} // assigns roll_ value to point_
	void setIter(); // iterators are assigned return values of find() algorithm
	void setRoll() {roll_ = setDice();} // return value of method 'setDice()' is assigned to roll_
	bool pointPlay(); // GamePlay for once player finds point, returns true once player wins or loses
private:
	string player_;
	int die1_, die2_, roll_, point_;
	vector<int> winningNums_{7,11}; 	vector<int>::iterator winner_;
	vector<int> losingNums_{2,3,12};	vector<int>::iterator loser_;
};

#endif CRAPSV2_HPP
