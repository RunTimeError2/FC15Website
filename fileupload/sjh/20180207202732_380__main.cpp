#include <iostream>
#include <cstdlib>
#include <ctime>
using namespace std;

#define MAXN 1000
#define MAXNUM 10000

//≤Â»Î≈≈–Ú
void insertSort(int data[], int l, int r) {
	int tmp = 0;
	for (int i = l + 1; i <= r; i++)
		if (data[i] < data[i - 1]) {
			tmp = data[i];
			int j = i - 1;
			while (j >= 0 && data[j] > tmp) {
				data[j + 1] = data[j];
				j--;
			}
			data[j + 1] = tmp;
		}
}

//—°‘Ò≈≈–Ú
void selectionSort(int data[], int l, int r) {
	int j, tmp, pos;
	for (int i = l; i <= r; i++) {
		pos = i;
		for (j = i; j <= r; j++)
			pos = (data[j] < data[pos]) ? j : pos;
		tmp = data[pos];
		data[pos] = data[i];
		data[i] = tmp;
	}
}

//√∞≈›≈≈–Ú
void bubbleSort(int data[], int l, int r) {
	bool flag = true;
	for (int i = r - 1; i >= l && flag; i--) {
		flag = false;
		for (int j = l; j <= i; j++)
			if (data[j] > data[j + 1]) {
				int tmp = data[j];
				data[j] = data[j + 1];
				data[j + 1] = tmp;
				flag = true;
			}
	}
}

//œ£∂˚≈≈–Ú
void shellSort(int data[], int l, int r) {
	int step = 0;
	int auxiliary = 0;
	int count = r - l + 1;
	for (step = count / 2; step > 0; step /= 2)
		for (int i = l + step; i <= r; i++)
			if (data[i] < data[i - step]) {
				auxiliary = data[i];
				int j = i - step;
				while (j >= l && data[j] > auxiliary) {
					data[j + step] = data[j];
					j -= step;
				}
				data[j + step] = auxiliary;
			}
}

//øÏÀŸ≈≈–Ú
void quickSort(int data[], int l, int r) {
	if (l < r) {
		int pivotL = l, pivotR = r, x = data[l]; //data[l] can be changed
		while (pivotL < pivotR) {
			while (pivotL<pivotR && data[pivotR]>x)
				pivotR--;
			if (pivotL < pivotR)
				data[pivotL++] = data[pivotR];
			while (pivotL < pivotR && data[pivotL] < x)
				pivotL++;
			if (pivotL < pivotR)
				data[pivotR--] = data[pivotL];
		}
		data[pivotL] = x;
		quickSort(data, l, pivotL - 1);
		quickSort(data, pivotL + 1, r);
	}
}

//πÈ≤¢≈≈–Ú
void arrayMerge(int data[], int p, int q, int r) {
	int n1 = q - p + 1;
	int n2 = r - q;
	int *L = new int[n1];
	int *R = new int[n2];
	for (int i = 0; i < n1; i++)
		L[i] = data[p + i];
	for (int i = 0; i < n2; i++)
		R[i] = data[q + 1 + i];
	int i = 0, j = 0;
	for (int k = p; k <= r; k++)
		data[k] = (L[i] <= R[j]) ? ((i < n1) ? L[i++] : R[j++]) : ((j < n2) ? R[j++] : L[i++]);
	delete[] L;
	delete[] R;
}

void mergeSort(int data[], int p, int r) {
	if (p < r) {
		int q = (int)(p + r) / 2;
		mergeSort(data, p, q);
		mergeSort(data, q + 1, r);
		arrayMerge(data, p, q, r);
	}
}

//ª˘ ˝≈≈–Ú
static const int RADIX[6] = { 1,10,100,1000,10000,1000000 };
#define GETRADIX(x,n) ((x)%(RADIX[(n)])/(RADIX[(n)-1]))

void radixSort(int *arr, int l, int r) {
	for (int k = 1; k <= 5; k++) {
		int count[10]{ 0 };
		int *ans = new int[r - l + 1];
		for (int i = l; i <= r; i++)
			count[GETRADIX(arr[i], k)]++;
		for (int i = 1; i < 10; i++)
			count[i] += count[i - 1];
		for (int i = r; i >= l; i--) {
			ans[count[GETRADIX(arr[i], k)] - 1] = arr[i];
			count[GETRADIX(arr[i], k)]--;
		}
		for (int i = l; i <= r; i++)
			arr[i] = ans[i];
		delete[] ans;
	}
}

int main() {
	srand((unsigned int)time(NULL));
	int n = 20;
	int data[MAXN];
	for (int i = 0; i < n; i++) {
		data[i] = rand() % MAXNUM;
		cout << data[i] << " ";
	}
	cout << endl;
	//insertSort(data, 0, n - 1);
	//selectionSort(data, 0, n - 1);
	//bubbleSort(data, 0, n - 1);
	//shellSort(data, 0, n - 1);
	//quickSort(data, 0, n - 1);
	//mergeSort(data, 0, n - 1);
	radixSort(data, 0, n - 1);
	for (int i = 0; i < n; i++)
		cout << data[i] << " ";
	cout << endl;
	cin.get();
	return 0;
}