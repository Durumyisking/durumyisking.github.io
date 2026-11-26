---

명시적 형 변환은 우리가 잘아는 (int), static\_cast\<int> 등등을 말한다.

묵시적 형 변환은

```c++
int a = 0;
a = 3.14f;
```

이런식으로 하는거임

묵시적 형 변환의 문제가 뭐냐하면

```c++
#include<iostream>

class Tmp {
public:
    Tmp(int num) :
        m_num(num) {
        std::cout << "Tmp 생성자 : " << m_num << std::endl;
    }

    void print() {
        std::cout << "Tmp 내부 값 : " << m_num << std::endl;
    }

private:
    int m_num;
};

void test(Tmp tmp) {
    tmp.print();
}

int main(void) {
    test(10);
}
```

이 코드는 정상적으로 작동함

함수 test의 인자는 Tmp class 타입이지만

생성자에 int를 매개로하는 생성자가 있어서

```c++
test(Tmp(10));
```

위 코드가 호출되는거임

뭐 편할수도 있긴한데 가독성면에서나 실수유발면에서나 위험한 코드로 보임

explicit은 묵시적 형 변환이 일어나는 부분에 추가해야함

그래서 생성자 앞에 추가했음

```c++
explicit  Tmp(int num) :
    m_num(num) {
    std::cout << "Tmp 생성자 : " << m_num << std::endl;
}
```

예외처리 가능!

```c++
int main(void) {
    test(10); // error! : E0415	"int"에서 "Tmp"(으)로 변환하기 위한 적절한 생성자가 없습니다.
}
```
