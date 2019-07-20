#include <Python.h>
#include <Math.h>
#include <stdint.h>

struct Point{
	int_64t x
	int_64t y
};

struct Node{
	Point *thisCoord
	Point *nextCoord
	double dist
};

struct Route{
    int_64t length
    Node *path
};

Route tsp(const Point *data, int_64t len){
	Point *coords;
    Node *graph;
    int_64t **minTree;
    int_64t **oddVertices;

    coords = (Point *)malloc(len * sizeof(Point));
    memcpy(staticData, data, len * sizeof(Point));

	graph = (Node *)malloc(len * sizeof(Node));

	//Build the graph
	for (Node *graphref = graph, int n = 0; graphref-graph < len; graphref++, n++){
		for (Point *coordsref = coords+n; coordsref-(coords+n) < len; coordsref++){
			graphref -> thisCoord = coords+n;
			graphref -> nextCoord = coordsref;
			graphref -> dist = sqrt(pow(((coordsref -> x) - (coords+n -> x)),2) + pow(((coordsref -> y) - (coords+n -> y)),2));
		}
	}

	minTree = minimumSpanningTree(graph);

	oddVertices = findOddVertices(minTree);

	minimumWeightMatching(minTree, graph, oddVertices);

	return findEulerTour(minTree, graph);
}

/**
*   Finds the minimum spanning tree of a graph using Krustal's
*   @param graph - Some graph that exists in a 2D plane
*   @return mst - A minimum spanning tree
**/
int_64t **minimumSpanningTree(Node *graph){
    return graph;
}

int_64t **findOddVertices(int_64t **tree){
    return tree;
}

int_64t **minimumWeightMatch(int_64t **tree, int_64t **graph, int_64t **oddVertices){
    return tree;
}

Route findEulerTour(int_64t **tree, int_64t **graph){
    return tree;
}
