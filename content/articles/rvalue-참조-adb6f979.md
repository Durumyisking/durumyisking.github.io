---
title: "rvalue 참조"
category: content/categories/topic-01-03.json
order: 100
---
c++ 11의 핵심 기능 우측값 참조에 대해 알아보자\~

---

<b>R\_Value Reference</b>

우리는 좌측값을 받아올때랑 우측값을 받아올때 연산이 다름

int x = 500;

int i = 300; // 우측값 받아옴 복사 없음

int i = x; // 좌측값 받아옴 x를 복사해서 i에 줌

만약 클래스에서 생성자를 호출할때. 

이미 생성된 변수 a를 이용해 b를 만든다고 할 때 myclass 값을 매번 새로 생성하는 것은 메모리 낭비이다.

```c++
class myclass
{
	myclass(myclass& other)
	{
		str = other.str;
	}

	String str;
}

int main()
{
	myclass a();
	myclass b(a); // a를 복사해서 새로운 객체를 만든 후 b에 전달 메모리 낭비!

}
```

새로운 myclass을 담을 메모리를 할당하는 대신, 포인터를 전달함으로써 효율적으로 값을 옮기며 클래스 객체를 생성할 수 있는데, 이때 이동 생성자를 사용한다. 이동 생성자는 아래와 같은 형식을 가진다.

```c++
myclass(myclass&& other) noexcept // exception 발생해도 작업 안멈춰서 값이 안깨짐
	{
		str = other.str;
	}
```

<b>move함수</b>

- move함수의 이름은 move지만
- 사실 인자로 받은 객체를 우측값으로 변환해서 return하는것이다. ⇒ 그냥 타입 변환임

<b>좌측값 참조를 사용하면</b>

```c++
template <typename T>
void swap(const T& a, const T& b) {
    T tmp(a);
    a = b;
    b = tmp;
}
```

T에서 a를 호출하는 과정에서 복사 생성자가 호출된다.

여기서 tmp은 이 함수가 종료되면 사라지는 임시객체임 ⇒ <b>비효율적 + 연산많음</b>

위 코드에서 tmp는 재사용되지도 않고 다른 대입 및 복사 연산자의 target으로만 이용됨

<b>그래서 우리는 move 함수를 사용해 값을 ‘이동’만 시킬거임</b>

```c++
template <class T>
void swap(T& a, T& b) {
  T tmp(std::move(a));
  a = std::move(b);
  b = std::move(tmp);
}

X a, b;
swap(a, b);
```

위와 같은 방식으로 swap 함수를 구현하면, swap이 실제로 행해지는 과정에서 이동 생성자가 호출된다. move는 좌측값을 우측값 레퍼런스처럼 사용할 수 있도록 타입 캐스팅을 해 준다. 

- move 함수 - rvalue ref
  move함수는 rvalue ref에서 사용한다

  즉 문맥에 따라서 우리가 참조할 친구가 명시적일때 move를 쓴다는 것

- forward 함수 - universal ref
  forward함수는 universal ref에서 사용한다

  즉 문맥에 따라서 우리가 참조할 친구의 자료형이 명시적이지 않거나 template 등으로 가변적인 친구일때 사용한다.

  즉 forward는 lvalue일때 rvalue일때 모두 사용이 가능한데

  우리가 lvalue로 쓸때는 lvalue에 맞게 캐스팅하고 rvalue로 쓸때는 rvalue에 맞게 캐스팅하면 됨
