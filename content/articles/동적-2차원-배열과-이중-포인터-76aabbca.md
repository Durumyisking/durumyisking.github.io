---
title: "동적 2차원 배열과 이중 포인터"
category: content/categories/topic-01-02.json
order: 70
---
아니 메모리 연속성 있어서 싱글포인터로 되는데 왜 더블포인터 쓰는지 알아보자\~

---

<img src="../media/132809c403889bd5c1ac.png" alt="" loading="lazy" decoding="async">

그림처럼 각 행 인덱스가 가리키는 주소는 배열의 주소이다.

애초에 선언할때 행의 주소에 새로운 동적배열을 할당하는 것이기 때문

```c++
for(int i=0; i<3; i++)
	arr[i] = new int[4];
```
