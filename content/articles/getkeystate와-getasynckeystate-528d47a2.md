왜 Getkeystate를 안쓰고 Asynckeystate를 사용할까?? 왜 사용하는지 어떻게 사용하는지 알아보자.

---

`GetKeyState`의 반환 상태는 스레드가 메시지 큐에서 키 메시지를 읽을 때 갱신된다. 키보드 메시지를 처리하면서 그 메시지가 생성된 시점의 키 상태를 확인하는 데 사용할 수 있다.

`GetAsyncKeyState`의 반환값에서 최상위 비트는 호출 시점에 키가 눌려 있는지를 나타낸다. 프레임마다 현재 상태를 확인하려면 이 비트를 검사한다.

최하위 비트의 최근 입력 여부는 다른 애플리케이션의 호출에도 영향을 받는다. 짧은 입력까지 처리해야 한다면 키 메시지를 보고 상태 변화를 기록한다.

[GetKeyState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeystate) · [GetAsyncKeyState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate)
