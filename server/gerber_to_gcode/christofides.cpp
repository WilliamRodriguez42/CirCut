/*
 * A C++ Python module that uses Christofides algorithm to create a Euler tour of a set of data points
 * This approximates a solution to the Travelling Salesman Problem
 *
 * Based on work by William Rodriguez <williamjr@ufl.edu>
 *
 * @author Austin Kee <austinjkee@ufl.edu>
 */
#include <Python.h>
#include <iostream>
#include <stdlib.h>
#include <Math.h>
#include <stdint.h>
#include <stdbool.h>
#include <limits.h>
#include <Point.h>

struct Route{
	Point *coords
	int64_t* *vertices
	int64_t len
};

/**
 * Allocates a two dimensional array of any type within a linearly addressable space.
 * Can only create a square matrix.
 * @param graph a reference to a double pointer whose contents will be assigned
 * @param len a reference to the desired height and width of the matrix
 */
template <typename T>
void matrixAlloc(T**& graph, int64_t& len){
	//graph = (T**)malloc((len * sizeof(T*)) + (len * len *sizeof(T)));  // Allocate the space
	graph = (T**) calloc(len*(sizeof(T*)/sizeof(T)) + (len*len), sizeof(T));  // Allocate the space
	T* ptr = (int64_t*)(graph + len); // ptr is now pointing to the first element in of 2D array
	for(T** graphref = graph; (*graphref = ptr); ptr+=len, graphref++); // for loop to point rows pointer to appropriate location in 2D array
}


/**
 * Calculates the distance between the points
 * @param a  a reference to a pointer to a Point
 * @param b	 a reference to a pointer to a Point
 * @return the distance between the points as a double
 */
double distance(Point* a, Point* b){
	return sqrt(pow((a->x - b->x), 2) + pow((a->y - b->y), 2));
}

/**
 *
 */
Route* tsp(const Point* data, int64_t len){
	Point* const coords = (Point* )malloc(len * sizeof(Point));
	int64_t** graph;

    //copy the original data to a new set of addresses
    //	to prevent accidental deletion of data by the original owner
    memcpy(coords, data, len * sizeof(Point));

    //allocate a square matrix of dimensions len*len to graph
    //note that the function allocates a matrix that can be accessed as if it's a single array
    matrixAlloc(graph, len);

    //Build the graph
    buildGraph(graph, coords, len);

	minTree = minimumSpanningTree(graph, len);

	oddVertices = findOddVertices(minTree);

	minimumWeightMatching(minTree, graph, oddVertices);

	return findEulerTour(minTree, graph);
}

/**
 *  Builds a graph containing distance data from each point.
 *  Points are designated an index based on their position in the coords array;
 *  the first coord is graph node 1, the second coord is graph node 2, etc.
 *
 *  @param graph The graph container to populate with data
 *  @param coords The reference to the coordinates in the graph
 *  @param len	The number of points
 */
void buildGraph(int64_t** graph, Point* coords, int64_t& len){
	//for pointA in the set
	for(Point* pointA = coords; pointA < coords+len; pointA++, graph++){
		//find the distance from point to all other points
		//	remembering the shortest distance and respective point
		double shortestDist = DBL_MAX;  //set to largest possible value so that the first comparison will always be saved
		int64_t index;  //define the index
		//for pointB larger than pointA in the set
		for(Point* pointB = pointA+1; pointB < coords+len; pointB++){
			//if the distance from pointA to pointB is less than the current shortest distance
			if((double thisDist = distance(pointA, pointB)) >= shortestDist){
				shortestDist = thisDist;  //set the distance
				index = coords - pointB;  //set
			}
		}
		//save the shortest distance
		*((*graph) + (index))= shortestDist;
	}
}

/**
 *   Finds the minimum spanning tree of a graph using Krustal's
 *   @param graph - Some graph that exists in a 2D plane
 *   @return mst - A minimum spanning tree
 */
Node* *minimumSpanningTree(int64_t** graph, int64_t len){
	double leastDist=0;
	double thisDist=0;

	Node* *tree;
	tree = (Node* *)malloc(len * sizeof(Node*))

	int64_t leastIndex=0;
	int64_t thisIndex=0;
	for (int64_t n = 0; n<len; n++){
		for (int64_t i = 0; i<len; i++){
			thisIndex = n*len + i;
			thisDist = graph + thisIndex -> dist;
			if(i==0 || thisDist < leastDist){
				leastDist=thisDist;
				leastIndex=thisIndex
			}
		}
		(tree + n)* = graph + leastIndex;
	}

    return tree;
}

int64_t **findOddVertices(int64_t **tree){
    return tree;
}

int64_t **minimumWeightMatch(int64_t **tree, int64_t **graph, int64_t **oddVertices){
    return tree;
}

Route findEulerTour(int64_t **tree, int64_t **graph){
    return tree;
}
