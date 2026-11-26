---
title: "클래스"
category: content/categories/topic-01-03.json
order: 20
---
### 클래스

```c++
class MyClass
{
	public:
		int iData;        // 외부에서 접근 가능

	private:
		int iPrivateData; // 외부에서 접근 불가
}

int main()
{
	Myclass myclass = new MyClass();
	myclass->iData // 가능
	myclass->iPrivateData // 불가능
}
```

<b>접근제한 지정자</b>

- <b>public (구조체는 Default로 public 되어있다)</b>
  - 전체 공개
  - 외부에서 접근 가능
- <b>private </b>
  - 감추고 싶은 항목 비공개
  - 클래스 외부에서 접근 불가능
- protected
  <ul>
  <li>
  상속받은 
  </li>
  </ul>

<b>멤버변수/함수</b>

- <b>클래스 내에 선언된 변수와 함수</b>를 멤버변수/함수라고 부름
- 외부에서 객체로 접근을 하면 자기 자신의 멤버에 접근하는것임

<b>this포인터</b>

- 객체 내에서 자기 자신을 가리키는 포인터
- 객체 내에서 멤버에 접근할때 사실 전부 앞에 this→가 붙어있음
- 사실은 <b>int\* const this</b> 라서 this자체를 수정이 불가능하다.

```c++
class MyClass
{
	public:
		int iData;

	public:
		void func()
		{
			iData = 2;
			this->iData = 2;
			// 이 두 코드는 같은뜻
		}
}
```

<b>생성자/소멸자</b>

생성자를 사용해서 초기화 및 초기작업을 편하게 할 수 있다.

- 생성자
  - 클래스를 생성해 메모리를 할당하고나면 반드시 무적권 호출되는 함수
  - 생성자 코드블럭 안에서 값을 대입해주는건 진정한 초기화가 아님
    우리는 멤버를 만들면서 바로 값을 세팅해주는 이니셜라이저를 사용해서 초기화를 시켜줄것

  - 디폴트생성자
    - 사실 우리가 생성자를 직접 생성해주지 않아도 내부에서 기본 생성자가 생성되어 있음
      (딱히 역할은 없음ㅋ) ⇒ 소멸자도 이하 동문

    - 디폴트생성자만 사용하고 싶을때
      ```c++
      Node() = default; // 를 클래스 내에 넣어두면됨 근데 잘 안씀 ㅋ
      ```
- 소멸자
  - 객체가 메모리에서 해제될때 반드시 실행되는 함수

  ```c++
  class MyClass
  {
  	public:
  		// 1생성자
  		MyClass()
  				: iData(10) // Member initiallizer
  				, chName('b')  // 먼저 실행
  		{
  			iData2 = 10
  			chName2 = a;
  		}
  		// 2생성자 오버로딩
  		MyClass(int _iData)
  				: iData(_iData) // Member initiallizer
  				, chName('b')  // 먼저 실행
  		{		}
  		// 복사생성자 -> 사실 디폴트로 존재함
  		MyClass(MyClass& _MyClassDest)
  				: this.iData(_MyClassDest->iData)
  				, this.chName(_MyClassDest->chName)
  		{
  		}

  		// 소멸자
  		~MyClass()
  		{
  			iData = 0;
  			chName('\0');
  			// 선언한 함수 나갈때 실행
  		}
  	public:
  		int iData, iData2;
  		char chName, chName2;

  	public:
  		void func()
  		{

  		}
  }

  int main()
  {
  	MyClass Node1; // Node1의 1번 생성자 호출
  	MyClass Node2(5); // Node2의 2번 생성자 호출

  	cout << Node2.iData;

  	MyClass* pNode1 = new Node(); // pNode1의 생성자 호출
  	MyClass* pNode2 = new Node(5); // pNode2의 2번생성자 호출

  	// 동적할당한 클래스는 delete로 메모리 해제할때 소멸자 호출됨
  	delete pNode2; // 이때 pNode2의 소멸자 호출
  	delete pNode1; // 이때 pNode1의 소멸자 호출

  	return 0; // Node 2번생성자 호출 이후 Node의 1번 생성자 호출
  }
  ```

<b>Header / Class 분할구현</b>

- <b>Header</b>에는 사용할 변수나 함수들을 <b>선언</b>만 해둡니다
- <b>Class</b>에서 <b>구현</b>을 합니다.

<b>Player.h</b>

```c++
#include <iostream>
#include "status.h" // 객체의 상태를 가지는 구조체를 가진 header

class CPlayer
{
public:
	CPlayer(int _iLevel);

private:
	Status status;

public:
	void PrintLevel();
	void SetLevel(int _iLevel);
};
```

<b>Player.cpp</b>

```c++
#include "Player.h"


CPlayer::CPlayer(int _iLevel)
	: status({5, 5 ,5, _iLevel})
{
}

void CPlayer::PrintLevel()
{
	std::cout << status.iLevel << std::endl;
}

void CPlayer::SetLevel(int _iLevel)
{
	this->status.iLevel = _iLevel;
}
```

<b>main.cpp</b>

```c++
// #include <iostream> Player.h가 iostream을 가지고 있기 때문에 필요 없음
#include "Player.h"

using namespace std;

int main()
{
	CPlayer player(5);
	player.PrintLevel();
	player.SetLevel(22);
	player.PrintLevel();

	return 0;
}
```

<b>전방선언</b>

과도한 include 남발로 include loop속에 갇힐수가 있음

ex) player가 monster include, monster가 player include

그럴때 Header에 전방선언 사용 (그 클래스가 존재한다는것만 알고있게 하는것)

### <b>\*include는 cpp에서\*</b>

Header에서는 어차피 그 클래스를 사용을 안할꺼기 때문에

선언을 위해 그런 글씨를 가진 자료형이 있다는것만 알려주는것

<b>Player.h</b>

```c++
#include <iostream>
#include "status.h" // 객체의 상태를 가지는 구조체를 가진 header

class CMonster; // CMonster가 뭔지 사실은 전~혀모름
								// 그냥 CMonster이라는 글씨를 가진 8바이트짜리 자료형이 있다는거만 인식

class CPlayer
{
public:
	CPlayer(int _iLevel);

private:
	Status status;

public:
	void Fight(CMonster _Monster); // 선언가능
	void Skill(CMonster _Monster)
	{
			_Monster.hp -= 10; // 불가능 // _Monster가 hp를 가지고 있는지 모름
	}
};
```

<b>Player.cpp</b>

```c++
#include "Player.h"
#include "Monster.h" // Monster를 직접 사용하기 위해 include함

CPlayer::CPlayer(int _iLevel)
	: status({5, 5 ,5, _iLevel})
{
}

void Fight(CMonster _Monster)
{
		battle(_Monster); 
}
void Skill(CMonster _Monster)
{
		_Monster.hp -= 10; // 가능 include 해주었기 때문
}
```

<b>inline 함수 - 최적화 방법</b>

```c++
inline void PrintHp();  
							// 자주쓰는 함수를 여기에 inline함수로 선언해주면 좋음
							// inline 키워드를 붙이면 빌드단계에서 함수를 사용한곳 안에 구현부코드 자체가 들어감
							// 그래서 그냥 헤더나 클래스같은거 안거치고 바로 함수를 사용하는것
							// 좋은 최적화 방법임
```
