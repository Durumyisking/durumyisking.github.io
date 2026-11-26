그러게요 왜? 쓸까요?

---

당연\~하지만 Memory Leak이 발생하지 않게 하기 위함이다.

하지만 이는 70점 짜리 답변이라고 하는데

면접관님들은 소멸자의 호출 여부를 말하면 더 기뻐하신다고 하신다.

아래는 virtual 소멸자를 사용하지 않았을때의 오류이다

```c++
{ // 정상적인 소멸자 호출로 메모리 릭이 발생하지 않는다.
    Monster* p = new Monster();
    delete p;
}

// 멤버로 int값 하나만 가지고 Chair
{ // ~Chair(); 가 호출되지않지만 릭 발생 안함.
    Abstract* p = new Chair();
    delete p;
}

// sharedptr 멤버를 가지고 있는 Monster
{ // ~Monster(); 가 호출되지도 않고, 메모리릭도 발생!
    Abstract* p = new Monster();
    delete p;
}

```

멤버중에 동적할당한 멤버를 가지고 있는 자식클래스는 소멸자를 호출 할 때 부모의 소멸자만 부르기  때문에 자식클래스에 있는 멤버는 delete 되지 않아서 메모리 릭이 발생한다
