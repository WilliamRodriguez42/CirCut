#ifndef POINT_H
#define POINT_H
#endif
/**
 * Represents the x,y, and z coordinates of a given point
 */
struct Point{
	int64_t x
	int64_t y
};

/**
 * Compares two struct Points for equivalency
 * @param a  a reference to a Point
 * @param b	 a reference to a Point
 * @return whether the comparison is equal (true) or not equal (false)
 */
bool operator==(Point& a, Point& b) const{
	if(a.x == b.x && a.y == b.y)return true;
	else return false;
}
