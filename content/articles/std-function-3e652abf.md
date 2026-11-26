---
title: "std::function"
category: content/categories/topic-01-04.json
order: 30
---
함수포인터를 대체하기 위해 나온 문법 std::function(펑셔널)을 알아보자

---

펑셔널은 이름때문에 함수를 저장하는 자료형으로 사용한다고 생각할 수 있다.

하지만 정확히는 callable (함수 객체) 들을 객체의 형태로 보관할 수 있는 클래스이다.

<b>callable : c++에서 ()를 붙여 호출할 수 있는 모든 것</b>

예를들어 아래의 코드는 구조체의 오퍼레이터를 호출 한 것일 뿐이지만

펑셔널로 받을 수 있다.

```javascript
#include <iostream>


struct S {
  void operator()(int a, int b) { std::cout << "a + b = " << a + b << std::endl; }
};

int main() {
  S some_obj;
	std::function<void(char)> f2 = &some_obj(3, 5);

}
```

<b>펑셔널로 멤버함수 받기</b>

```javascript
#include <functional>
#include <iostream>
#include <string>

class A {
  int c;

 public:
  A(int c) : c(c) {}
  int some_func() { std::cout << "내부 데이터 : " << c << std::endl; }
};

int main() {
  A a(5);
  std::function<int()> f1 = a.some_func;
}
```

이럼 오류뜬다 멤버함수의 첫번째 인자는 반드시 this가 들어가있다.

우선 왜 대체하게 됐는지 알아보자

### 일반 function pointer 의 문제점.

1. 반환 값이 명시적으로 같은 타입이여야 한다.
2. 오로지 함수끼리만 호환가능.
3. 코드가 복잡해진다.

### std::function을 이용하는 것의 장점.

1. 함수 반환값이 형변환 가능한 타입이면 대입가능.
2. static 함수 포인터 말고도 functor,클래스 멤버함수 포인터, 람다함수, bind 반환값 호출 가능한 모든 대상과 호환가능.
3. 유연한 사용이 가능하다.
