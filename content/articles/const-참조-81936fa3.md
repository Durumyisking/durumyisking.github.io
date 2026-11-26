우리가 wstring 인자로 받을때 자주 사용하는 const 레퍼런스 정확히 알고가자

---

const reference는 간단하다.

참조로 받아오는데 그 원본을 변경하지 못하게 const로 받아오는 것이다.

<b>그럼 왜 우리가 wstring을 const &로 받냐</b>

- wstring은 리터럴이기 때문에 const여서 변경하려고 하면 crash가 된다.
  실수로 해당 값에 데이터를 넣는 실수를 막기 위함이다.
