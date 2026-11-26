<b>윈도우API의 메인함수</b>

```c++
int APIENTRY wWinMain(_In_ HINSTANCE hInstance, // 현재 인스턴스
                     _In_opt_ HINSTANCE hPrevInstance, // 이전 인스턴스
                     _In_ LPWSTR    lpCmdLine, // 문자열 받는 포인터 변수
                     _In_ int       nCmdShow)
```

hInstance :  메모리에 올라가있는 window에 간접적으로 접근할 수 있게 해주는 핸들<br />

<b>window 생성 \~ 동작</b>

1. wmdclass 정의 : MyRegisterClass 윈도우의 속성이 되는 클래스인 wmdclass  정의
    (ex 어떻게 생겼는지 등등)

2. 메모리상에 window 할당 (CreateWindow함수)
3. showWindow함수를 통해 window 렌더링
4. windowclass를 정의할때 넣어준 함수포인터에 loop문 (wndproc 윈도우 프로시저)를 매
   프레임마다 실행

<b>window 메시지 처리</b>

- 사용자가 마우스를 클릭하거나 키보드를 누르는등의 행동을하면 messagequeue에 해당
  메시지들이 쌓임

- 쌓인 메시지들을 하나씩 GetMessage해서 Message의 타입 검사후 해당 메시지를 처리함.
- PickMessage / GetMessage
  - PickMessage
    - 메시지가 들어오기 전에는 다른 코드를 처리하다
    - 인터럽트가 걸리면 해당 인터럽트 처리 후 다시 코드 처리하러감
  - Getmessage
    - 메시지가 들어오기 전까지 프로그램이 멈춰있는다
    - 메시지가 들어오면 해당 메시지 처리후 다시 멈춤

<b>windows 구성 Lib</b>

- 메모리를 관리하고 실행시키는 kernel
- 유저 인터페이스 관리하는 User
- 화면처리와 그래픽을 담당하는 GDI로 이루어져 있다.

<b>DC 동작</b>

- Pen/Brush 핸들 선언
- GDI 오브젝트 생성
- selectObject로 hdc(윈도우 핸들이 사용중인 dc)를 세팅한다
- 사용후 기존의 obj로 되돌림
