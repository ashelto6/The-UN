// Function definitions

#include "battleship.hpp"
#include <iostream>

using std::cout; using std::cin; using std::endl;

Location::Location() : x_(-1), y_('*') {}

void Location::pick() {
	x_ = rand() % fieldSize_ + 1;
	int y = rand() % fieldSize_ + 1;

	switch (y) {

	case 1:
		y_ = 'a';
		break;
	case 2:
		y_ = 'b';
		break;
	case 3:
		y_ = 'c';
		break;
	case 4:
		y_ = 'd';
		break;
	case 5:
		y_ = 'e';
		break;
	case 6:
		y_ = 'f';
		break;
	}

}

void Location::fire() {
	cout << "\nEnter the coordinates of your shot: ";

	cin >> x_ >> y_;
}

void Location::print() const {

	cout << x_ << y_;

}

bool compare(const Location& ship, const Location& shot) {
	return shot.x_ == ship.x_ &&
		shot.y_ == ship.y_;
}

Ship::Ship() : sunk_(false) {}

bool Ship::match(const Location& shot) const {
	if (compare(loc_, shot)) {
		return true;
	}
	else {
		return false;
	}
}

void Ship::sink() {
	sunk_ = true;
}

void Ship::setLocation(const Location& spot) {
	loc_ = spot;
}

void Ship::printShip() const {

	cout << "\nShip Location: ";
	loc_.print();
	if (isSunk()) {
		cout << " - This ship has been sank!";
	}
	else {
		cout << " - This ship has not been sank!";
	}
}

bool Fleet::operational() const {

	for (int i = 0; i < fleetSize_; ++i) {
		if (ships_[i].isSunk() == false)
			return true;
	}
	return false;
}

void Fleet::printFleet() const {
	int i = 0;

	while (i < fleetSize_) {
		ships_[i].printShip();
		++i;
	}
}

int Fleet::check(const Location& shot) const {
	for (int i = 0; i < fleetSize_; ++i) {
		if (ships_[i].match(shot)) {
			return i;
		}
	}
	return -1;

}

void Fleet::deployFleet() {

	int i = 0;

	while (i < fleetSize_) {
		Location position;
		position.pick();
		if (check(position) == -1) {
			ships_[i].setLocation(position);
			++i;
		}

	}
}

bool Fleet::isHitNSink(const Location& shot) {
	if (check(shot) != -1) {
		int i = check(shot);
		ships_[i].sink();
		return true;
	}
	else {
		return false;
	}
}