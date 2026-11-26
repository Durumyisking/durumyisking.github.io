---

### Winsock2 초기화와 해제

<b>WSAStartup</b>

```c++
int WSAStartup(
        WORD      wVersionRequired, // 프로그래머가 사용할 윈속의 버전 (보통2.2 사용)
  [out] LPWSADATA lpWSAData // WSADATA라는 구조체 변수의 주소 값 전
);
```

<b>첫 번째 인자</b>에 버전 2.2를 넣고 싶으면 0x0202를 넣으면 된다.

(WORD 자료형은 2바이트고 16bit니까 ㅇㅇ 16진수에서는 한자리가 4비트잖아)

(1바이트를 main 버전, 나머지 1바이트를 sub 버전으로 봄)

그런데 바이트단위로 버전 넣어주기 번거로우니까 MAKEWORD(2, 2)로 처리하면 된다.

<b>두 번째 인자 </b>LPWSADATA는 WSADATA의 포인터 형이다. WSADATA를 따로 프로그램에서 사용하지는 않지만 윈속을 초기화 하기 위해서는 반드시 필요하니까 변수 하나 넘겨주자.

넣어준 WSADATA에는 라이브러리의 정보가 채워진다.

<b>WSACleanup</b>

```c++
int WSAAPI WSACleanup();
```

성공시 0, 실패시 SOCKET\_ERROR가 반환된다.

SOCKET\_ERROR이 반환되었을때 [WSAGetLastError](https://learn.microsoft.com/ko-kr/windows/desktop/api/winsock/nf-winsock-wsagetlasterror)를 호출하여 특정 오류 번호를 검색할 수 있다.

WSACleanup 호출 이후에는 윈속 관련 함수 호출이 불가능해진다.

원칙상은 윈속 관련 함수 호출이 필요 없을때 호출하는게 맞는데 그냥 프로그램 종료직전에 호출한다.

### 소켓 관련 함수
