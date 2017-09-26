//***********************************************************
// C++版连点器
// 按Shift+S开启连点功能，Shift+A暂停连点功能
// 开启连点功能时，Ctrl+Z连点鼠标左键，Ctrl+X连点鼠标中键，Ctrl+C连点鼠标右键
// 按Ctrl+Shift+Space隐藏当前具有焦点的窗口，按Alt+W显示
//***********************************************************
// Version 2.0, Written by RunTimeError2

#include <Windows.h>

static bool EnableAutoClick;
static HWND HiddenWindowHwnd;

LRESULT CALLBACK WndProc(HWND,UINT,WPARAM,LPARAM);

int WINAPI WinMain(HINSTANCE hInstance,HINSTANCE hPrevInst,LPSTR lpszCmdLine,int nCmdShow) {
	HWND hwnd;
	MSG Msg;
	WNDCLASS wndclass;
	char lpszClassName[]="MyWindowClass";
	char lpszTitle[]="My Window";
	wndclass.style=CS_DBLCLKS;
	wndclass.lpfnWndProc=WndProc;
	wndclass.cbWndExtra=0;
	wndclass.cbClsExtra=0;
	wndclass.hInstance=hInstance;
	wndclass.hIcon=LoadIcon(NULL,IDI_APPLICATION);
	wndclass.hCursor=LoadCursor(NULL,IDC_ARROW);
	wndclass.hbrBackground=(HBRUSH)GetStockObject(WHITE_BRUSH);
	wndclass.lpszMenuName=NULL;
	wndclass.lpszClassName=lpszClassName;
	if(!RegisterClass(&wndclass)) {
		MessageBeep(0);
		return FALSE;
	}
	hwnd=CreateWindow(lpszClassName,lpszTitle,WS_OVERLAPPEDWINDOW,CW_USEDEFAULT,CW_USEDEFAULT,100,100,NULL,NULL,hInstance,NULL);
	UpdateWindow(hwnd);
	while(GetMessage(&Msg,NULL,0,0)) {
		TranslateMessage(&Msg);
		DispatchMessage(&Msg);
	}
	return Msg.wParam;
}

LRESULT CALLBACK WndProc(HWND hwnd,UINT message,WPARAM wParam,LPARAM lParam) {
	switch(message) {
		case WM_CREATE:
			EnableAutoClick=false;
			HiddenWindowHwnd=NULL;
			SetTimer(hwnd,1,20,NULL);
			break;
		case WM_TIMER:
			if(GetAsyncKeyState(16)<0 && GetAsyncKeyState(17)<0 && GetAsyncKeyState(18)<0 && (GetAsyncKeyState(81)<0 || GetAsyncKeyState(113)<0))
				PostQuitMessage(0);
			if(GetAsyncKeyState(16)<0 && GetAsyncKeyState(17)>=0 && GetAsyncKeyState(18)>=0 && (GetAsyncKeyState(65)<0 || GetAsyncKeyState(97)<0))
				EnableAutoClick=false;
			if(GetAsyncKeyState(16)<0 && GetAsyncKeyState(17)>=0 && GetAsyncKeyState(18)>=0 && (GetAsyncKeyState(83)<0 || GetAsyncKeyState(115)<0))
				EnableAutoClick=true;
			if((GetAsyncKeyState(90)<0 || GetAsyncKeyState(122)<0) && EnableAutoClick)
				mouse_event(MOUSEEVENTF_LEFTDOWN|MOUSEEVENTF_LEFTUP,0,0,0,0);
			if((GetAsyncKeyState(88)<0 || GetAsyncKeyState(120)<0) && EnableAutoClick)
				mouse_event(MOUSEEVENTF_MIDDLEDOWN|MOUSEEVENTF_MIDDLEUP,0,0,0,0);
			if((GetAsyncKeyState(67)<0 || GetAsyncKeyState(99)<0) && EnableAutoClick)
				mouse_event(MOUSEEVENTF_RIGHTDOWN|MOUSEEVENTF_RIGHTUP,0,0,0,0);
			if(GetAsyncKeyState(16)<0 && GetAsyncKeyState(17)<0 && GetAsyncKeyState(18)>=0 && GetAsyncKeyState(32)<0 && !HiddenWindowHwnd) {
				HiddenWindowHwnd=GetForegroundWindow();
				ShowWindow(HiddenWindowHwnd,SW_HIDE);
			}
			if(GetAsyncKeyState(16)>=0 && GetAsyncKeyState(17)>=0 && GetAsyncKeyState(18)<0 && (GetAsyncKeyState(87)<0 || GetAsyncKeyState(119)<0) && HiddenWindowHwnd) {
				ShowWindow(HiddenWindowHwnd,SW_SHOW);
				HiddenWindowHwnd=NULL;
			}
			break;
		case WM_DESTROY:
			PostQuitMessage(0);
			break;
		default:
			return DefWindowProc(hwnd,message,wParam,lParam);
	}
	return 0;
}