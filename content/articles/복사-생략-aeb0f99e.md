---
title: "복사 생략"
category: content/categories/topic-01-03.json
order: 110
---
---

### 복사 생략

```c++
#include <iostream>

class A {
  int data_;

 public:
  A(int data) : data_(data) { std::cout << "일반 생성자 호출!" << std::endl; }

  A(const A& a) : data_(a.data_) {
    std::cout << "복사 생성자 호출!" << std::endl;
  }
};

int main() {
  A a(1);  // 일반 생성자 호출
  A b(a);  // 복사 생성자 호출

  // 그렇다면 이것은?
  A c(A(2)); // 일반 생성자 호출
}
```

<img src="../media/a524db48d6ed5b29d4be.png" alt="" loading="lazy" decoding="async">

                     <b>                                              ??????????????</b>

예상대로라면  <code>A(2)</code> 객체를 만들면서 <b>일반 생성자를 호출</b>하고,

생성된 임시객체가 인스턴스 <code>c</code> 생성자의 인자로 들어가면서 <b>복사 생성자가 호출</b> 되어야 한다.

생각해보면 굳이 임시 객체를 한 번 만들고, 이를 복사 생성할 필요가 없다. 

어차피 임시객체 <code>A(2)</code> 로 똑같이 <code>c</code> 를 만들거면,  <code>A(2)</code>를  <code>c</code>  로 부르면 되기 때문이다.

<ul>
<li>
<code>A(2)</code>와  <code>c</code> 는 <b>동일한 포인터 주소를 사용</b>한다.
</li>
<li>
<code>A(2)</code>는 임시객체지만 자신을 참조해주는 변수 <code>c</code>가 생겨서 <b>메모리 해제가 되지 않는다.</b> 
</li>
<li>
디버그 모드에서는 일부 설정에 의해 최적화를 하지 않아 복사생략을 하지 않을 수도 있다.
</li>
</ul>

따라서 똑똑한 컴파일러는 복사 생성을 굳이 수행하지 않고, 만들어진 임시로 만들어진 <code>A(2)</code> 자체를 <code>c</code> 로 만들버린다. 

이렇게, 컴파일러 자체에서 복사를 생략해 버리는 작업을 <b><u>복사 생략(copy elision)</u></b> 이라고 합니다.

복사 생략을 하는 경우는 <b>함수의 인자</b> 뿐만 아니라 <b>함수 내부에서 생성된 객체</b>를 return할 때, 수행할 수 있다. 

(C++ 표준을 읽어보면 반드시 복사 생략을 해라 라는 식이 아니라, <i>복사 생략을 할 수 도 있다</i> 라는 뜻으로 써 있습니다.)

<aside class="callout">

C++ 17 부터 일부 경우에 대해서 (예를 들어서 함수 내부에서 객체를 만들어서 return 할 경우) 반드시 복사 생략을 해야되는 것으로 바뀌었습니다.

</aside>
