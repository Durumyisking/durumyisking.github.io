그래픽 파이프라인에서 데이터를 읽고쓰는데 사용되는 두 버퍼들의 차이점을 알아보자

---

<b>ConstantBuffer</b>

- <b>장점</b>
  - 매우 빠른 GPU 접근 속도
- <b>단점</b>
  - 상수 버퍼라서 GPU내에서 수정이 불가능하다.

  int 1024

<b>StructuredBuffer</b>

- <b>장점</b>
  - CPU와 GPU 모두에서 수정이 가능하기 때문에 더 많은 유연성을 제공한다.
  - 대규모 데이터 처리에 유용하다.
- <b>단점</b>
  - ConstantBuffer보다 전송 비용이 높다.
  - 일부 데이터를 CPU에서 수정하고 GPU에서만 읽는 경우
    데이터 동기화 문제가 발생할 수 있다.

따라서 ConstantBuffer는 작은 양의 상수 데이터에 유용하며, StructuredBuffer는 대규모 데이터 처리에 유용합니다.
