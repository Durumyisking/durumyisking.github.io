---
title: "RAII와 스마트 포인터"
category: content/categories/topic-01-02.json
order: 90
---
shared\_ptr, weak\_ptr, unique\_ptr

스마트포인터는 메모리 해제를 자동으로 해주어 사고를 미연에 방지한다.

---

포인터를 사용하려면 두가지 문제에 대해 신경써야한다.

### 자원 관리의 중요성

C++에서는 gc안쓰니까 (있긴하답니다) 메모리 누수가 일어나지 않게 관리해야 한다.

C++ 에는 <b>RAII (Resouce Acquisition Is Initialization (자원의 획득은 초기화다))</b>이 있다.

이를 통해 자원 관리를 스택에 할당한 객체를 통해 수행할 수있다.

- 함수 스택에 정의된 객체들은 scope가 끝날때 모두 소멸자가 호출된다.

포인터들은 객체가 아니기 때문에 scope가 끝나도 소멸자가 호출되지가 않는다.

스마트 포인터는 포인터들을 ‘<b>객체</b>’로 만들어 scope가 끝났을때 소멸자가 호출되도록 하는 것이다.

```c++
#include <iostream>
#include <memory>

class Dog
{
public:
	Dog(int age) : mAge{ age }
	{
		std::cout << "Dog constructor" << std::endl;
	}
	~Dog()
	{
		std::cout << "Dog destructor" << std::endl;
	}
private:
	int mAge;
};

int main()
{
	std::unique_ptr<Dog> dogPtr = std::make_unique<Dog>(9);
    
	return 0;
}
```

요런식으로 하면 main 함수 끝날때 자동으로 해제된다.

### 해제된 메모리 재 참조

```c++
Data* data = new Data();
Date* data2 = data;

// data 의 입장 : 사용 다 했으니 소멸시켜야지.
delete data;

// ...

// data2 의 입장 : 나도 사용 다 했으니 소멸시켜야지
delete data2;
```

대표적인 double free 버그이다.

위 코드는 Data포인터에 대한 소유권이 data인지 data2인지 명확하지가 않다.

해당 문제를 해결하기 위해 나온 스마트포인터가 unique\_ptr이다.

<details>
<summary>unique\_ptr</summary>

유니크 포인터는 한 포인터에 대한 소유권을 독점할 수 있게 해준다.(<b>Exclusive Ownership</b>)

```c++
int main()
{
    std::unique_ptr<Cat> catPtr = std::make_unique<Cat>();
    std::unique_ptr<Cat> catPtr1 = catPtr; //ERROR
}
```

해당 코드는 catPtr을 독점화 해서 다른 포인터가 소유권을 갖지 못하게 한다.

(unique\_ptr의 내부에는 복사생성자에 delete 키워드가 있어서 복사생성을 막아놓았다)

근데 이동생성자는 안막혀있어서 소유권 옮기고 싶으면 std::move쓰면된다.

```c++
int main()
{
    std::unique_ptr<Cat> catPtr = std::make_unique<Cat>();
    std::unique_ptr<Cat> catPtr1 = std::move(catPtr); // 원본은 nullptr이 된다!
}
```

<b>unique\_ptr 함수 인자로 사용</b>

```c++
void do_something(std::unique_ptr<A>& ptr) { ptr->do_sth(3); }

int main() {
  std::unique_ptr<A> pa(new A());
  do_something(pa);
}
```

위 코드는 함수 인자로 unique\_ptr의 참조를 받고있다.

do\_something 함수 한정이지만

```c++
std::unique_ptr<A> pa(new A());
std::unique_ptr<A>& ptr = pa;
```

이 코드랑 다를바가 없다 ⇒ 유일한 소유권을 가지는 코드가 아니게 된다.

그래서 우리는 unique\_ptr을 함수 인자로 전달할때는 객체 형식이 아닌 포인터로만 전달해주면 된다.

```c++
void do_something(A* ptr) { ptr->do_sth(3); }

int main() {
  std::unique_ptr<A> pa(new A());
  do_something(pa.get());
}
```

<b>Container에 unique\_ptr 넣기</b>

```c++
std::vector<std::unique_ptr<A>> vec;
std::unique_ptr<A> pa(new A());

vec.push_back(pa);  // 복사생성이 안되니까 안됨 ㅇㅇ
```

```c++
std::vector<std::unique_ptr<A>> vec;
std::unique_ptr<A> pa(new A());

vec.push_back(std::move(pa));  
vec.emplace_back(pa);  
이거 2개를 씁시다잉
```

아마도 unique ptr은 객체를 하나만 만들고싶을때 쓸거같다 (싱글톤 등등)

생각해봤는데  오토체스의 position (한칸엔 하나만 들갈수있으니까) 에서도 사용할듯

</details>

<details>
<summary>shared\_ptr</summary>

shared\_ptr은 unique\_ptr과 달리 exclusive ownership을 가지지 않고 shared ownership을 가진다.

따라서

```c++
std::shared_ptr<T> p = std::make_shared<T>
std::shared_ptr<T> q = p;
```

이거 된다.

일반포인터와 다르게 쉐어드 포인터는 메모리 공간 안에서 몇개의 포인터가 객체를 가리키고있는지 카운팅한다.

<b>참조 인지</b>

- 포인터 B가 포인터 A를 참조하면
  포인터 A의 Reference(Strong) Count가 증가한다.

  (Strong Count는 포인터를 참조할때마다 1씩 증가한다)

  포인터 A를 참조하는 포인터들을 Delete해줄때마다 Strong Count가 1씩감소하고

  0이되었을때 자기 자신(포인터 A)를 Delete한다.

  <b>Weak Count</b>

  - Weak Pointer가 가리키는 경우 Weak Count가 올라가지만 WeakCount는 메모리 해제에는 관여하지 않는다.

이런 shared\_ptr도 leak의 가능성이 있다.

```c++
class Cat
{
public:
	Cat(std::string name) : mName{ name }
	{
		std::cout << mName << " cat constructor" << std::endl;
	}
	~Cat()
	{
		std::cout << mName << " cat destructor" << std::endl;
	}
	std::shared_ptr<Cat> mVar;
    
private:
	std::string mName;
};

int main()
{
	std::shared_ptr<Cat> kitty = std::make_shared<Cat>("kitty");
	kitty->mVar = kitty;
	std::cout << kitty.use_count() << std::endl;
}
```

당근빳다 바보같은 코드지만.. 원리를 알아보자

main 종료시 kitty 사라짐 → Count 2에서 1로 줌 하지만 mVar이 kitty를 가리키고 있어서

strong count가 1인상태로 프로세스가 종료된다.

실제로는 아래와 같은 문제가 자자하다

```c++
#include <iostream>
#include <memory>

class Cat
{
public:
	Cat(std::string name) : mName{ name }
	{
		std::cout << mName << " cat constructor" << std::endl;
	}
	~Cat()
	{
		std::cout << mName << " cat destructor" << std::endl;
	}
	std::shared_ptr<Cat> mVar;
private:
	std::string mName;
};

int main()
{
	std::shared_ptr<Cat> kitty = std::make_shared<Cat>("kitty");
	std::shared_ptr<Cat> nabi = std::make_shared<Cat>("nabi");

	kitty->mVar = nabi;
	nabi->mVar = kitty;

	std::cout << "kitty count : " << kitty.use_count() << std::endl;
	std::cout << "nabi count : " << nabi.use_count() << std::endl;
}
```

흔한 순환참조이다.

둘 다 Strong Count 1로 끝난다

</details>

순환참조 문제를 해결하기 위해 weak\_ptr이 있다.

<details>
<summary>weak\_ptr</summary>

weak\_ptr로 받은 포인터는 lock()함수를 사용하여 shared\_ptr형으로 변경해야한다.

우선은 weak가 shared를 참조하는 코드를 보자

```c++
class Cat
{
public:
    Cat(std::string name) : mName{ name }
    {
        std::cout << mName << " cat constructor" << std::endl;
    }
    virtual void speak() const
    {
        std::cout << "Hi?" << std::endl;
    }
    ~Cat()
    {
        std::cout << mName << " cat destructor" << std::endl;
    }
    std::shared_ptr<Cat> mVar;
private:
    std::string mName;
};


int main()
{
    std::shared_ptr<Cat> kitty = std::make_shared<Cat>("kitty");
    std::weak_ptr<Cat> weak_kitty = kitty;
    //weak pointer 선언 및 shared pointer kitty참조
    std::cout << "count : " << kitty.use_count() << std::endl;
    
    return 0;
}
```

이렇게 참조하면 kitty의 Strong count는 1 weak count는 2가된다.

```c++
	std::shared_ptr<Cat> kitty = std::make_shared<Cat>("kitty");
  std::weak_ptr<Cat> weak_kitty = kitty;
  
  if(const auto shared_kitty = weak_kitty.lock())
  {
      shared_kitty->speak();
  }
  else
  {
      std::cout << "pointing nothing\n";
  }
```

만약 kitty가 해제가 되지 않았으면 lock은 kitty의 인스턴스 포인터를 반환해준다.

if문 scope안에서 kitty의 SC는 2로증가하고 shared\_kitty가 scope를 벗어남에 따라 1로 다시 감소한다.

weak\_ptr사용해서 위의 순환참조 문제 해결

```c++
class Cat
{
public:
	Cat(std::string name) : mName{ name }
	{
		std::cout << mName << " cat constructor" << std::endl;
	}
	~Cat()
	{
		std::cout << mName << " cat destructor" << std::endl;
	}
	std::weak_ptr<Cat> mVar;
private:
	std::string mName;
};

int main()
{
	std::shared_ptr<Cat> kitty = std::make_shared<Cat>("kitty");
	std::shared_ptr<Cat> nabi = std::make_shared<Cat>("nabi");

	kitty->mVar = nabi;
	nabi->mVar = kitty;

	std::cout << "kitty count : " << kitty.use_count() << std::endl;
	std::cout << "nabi count : " << nabi.use_count() << std::endl;
}
```

서로 참조해도 SC는 안올라가고 WC만 올라갔기때문에 메모리 해제가 잘된다.

</details>


---

- <b>사용 방법</b>

  기본 선언

  ```c++
  #include <memory>

  int main() 
  {
      // 1. 객체를 생성하면서 shared_prt에 매핑해준다.
      std::shared_ptr<int> ptr1(new int(42));

      // 2. make_shared 함수를 사용하여 shared_ptr을 생성한다. // 이 방법이 선호되는듯 함
      std::shared_ptr<int> ptr2 = std::make_shared<int>(42);

      return 0;
  }
  ```

  객체 공유

  ```c++
  #include <iostream>
  #include <memory>

  class MyClass {
  public:
      MyClass() {
          std::cout << "MyClass 생성자 호출" << std::endl;
      }
      ~MyClass() {
          std::cout << "MyClass 소멸자 호출" << std::endl;
      }
  };

  int main() {
     // 1. 객체를 생성하면서 shared_prt에 매핑해준다.
      std::shared_ptr<MyClass> ptr1(new MyClass);

      // 2. make_shared 함수를 사용하여 shared_ptr을 생성한다. // 이 방법이 선호되는듯 함
      std::shared_ptr<MyClass> ptr2(ptr1);

      // ptr1을 해제한다.
      ptr1.reset();

      // ptr1이 해제되었으므로 ptr2만 객체를 참조하고 있다.
      std::cout << "ptr1이 해제되었으므로 ptr2만 객체를 참조합니다." << std::endl;
      std::cout << "ptr2.use_count(): " << ptr2.use_count() << std::endl; // 1

      return 0;
  }
  ```

침습형 shared\_ptr 공부하기
