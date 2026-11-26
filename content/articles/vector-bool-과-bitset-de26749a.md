---
title: "vector<bool>과 bitset"
category: content/categories/topic-02-02.json
order: 60
---
<a href="https://husk321.tistory.com/366">husk321.tistory.com</a>

<b>문제점 : 연산의 추가 비용</b>

bool은 생각해보면 1bit인데 C++에서는 왜 byte단위로 사용하나?

⇒ CPU에서 처리하는 데이터의 최소 단위가 1바이트이기 때문

<b>CPU는 bit에 대해 포인터를 만들 수 없기 때문에 C++ 데이터 유형은 1바이트보다 작을 수 없다.</b>

따라서 vector\<bool>은 bool값을 저장하는 동적 배열이지만 실제로는 bit를 기반으로한 데이터구조이다. (그니까 비트처럼 쓸 수 있는데 비트는 아니고 비트처럼 쓸 수 있게 만든 데이터 구조)

<b><code>vector&lt;bool&gt;</code></b><b> 은 bool 자료형을 비트 단위로 처리할 수 있게 해준다. </b>

<details>
<summary>쉽고 재미있는 설명</summary>

8층 짜리 건물은 사실 주소가 8개인거지만 우체국에서는 층마다 다른 주소임을 인정하지 않는다.

주소는 층이 아니라 건물을 참조해야 한다.

</details>

<b><code>vector&lt;bool&gt;</code></b><b> </b>은 다른 vector와 달리 \[\]연산자로 원소 접근시 bool값이 아니라 bool의 Reference 클래스를 반환한다. 

<b><code>vector&lt;bool&gt;</code></b>은 요소를 저장할 때 비트 패킹(bit-packing)을 사용하는데, 

이는 한 바이트에 8개의 bool 값을 저장하는 방식이다. 

이 때문에 <b><code>vector&lt;bool&gt;</code></b>의 요소를 읽거나 쓸 때 비트 패킹과 언패킹(unpacking) 과정이 필요하다.

이러한 과정에서 바이트 단위로 데이터를 처리하는게 편한 CPU는 비트 단위로 데이터를 읽고 쓰게 되어, 처리 속도가 느려질 수 있다.


---

bitset\<size> 

=> size만큼의 bit를 가지는 변수를 생성한다.

배열처럼 인덱스로 변수에 접근이 가능하다.

<b>vector\<bool>보다 디버깅이 편하고 vector\<bool>의 문제도 개선 가능하다.</b>

vector 문제점 

같은 형태의 따라서 여러가지 <b>비트 연산을 할 수 있도록 여러 멤버 함수들을 지원</b>한다.

```c++
bitset<8> bit = 7; // 0000 0111;
bit[1] = 1;
bit[3] = 0; 
```

<b>vector\<bool> : 동적인 사이즈를 갖는 경우, 복잡한 비트 연산이 필요없는 경우 사용</b>

<b>bitset : 정적인 사이즈를 갖는 경우, 복잡한 비트 연산이 필요한 경우( 10진수 변환, 비트 반전) 사용</b>
