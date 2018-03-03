/*
 * This is a sample of Logic mainly to test the interfaces
 * It creates a 'record file' containing all the arguments
 *
 * RunTimeError2, 2018-3-3
 */
#include <fstream>
#include <iostream>
using namespace std;

int main(int argc, char **argv) {
	ofstream outfile;
	cout << "Logic Launched!" << endl;
	outfile.open("gamerecord.txt");
	outfile << "AI list:" << endl;
	for(int i = 1; i < argc; i++)
		outfile << argv[i] << endl;
	outfile << "Here ends the file.\nOnly for a test :)\n";
	outfile.close();
	return 0;
}
