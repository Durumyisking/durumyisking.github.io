---
title: "if constexpr"
category: content/categories/topic-01-04.json
order: 70
---
템플릿 특수화 공부하다 따라 공부해버림

---

간단하다 constexpr 변수/함수는 컴파일단계에서 계산이 가능한 값/함수임을 표시하는 키워드.

if 뒤에는 뭐가오냐? Bool값 RValue가 온다 if (세현 == 바보) <s>(false!!)</s>

그럼 그 RValue가 컴파일단계에서 계산이 가능한 값이면???<br /><b>if constexpr (컴파일 타임에 bool로 확정 가능한 조건식)</b>

```javascript
template<typename T>
void Process(다양한 파라미터, T& Value)
{
	if constexpr (TTraits<T>::bEnable)
	{
	 Value.Foo();
	}
}

template<typename T>
struct TTraits
{
    enum { bEnabled = false };
};

struct T1 {     void Foo() {} };
struct T2 {};

template<>
struct TTraits<T1>
{
    enum { bEnabled = true };
};
template<>
struct TTraits<T2>
{
    enum { bEnabled = false};
};

Process함수 호출에 대해서
Process<T1>(Value)
Process<T2>(Value) 
Process<int>(Value)

Process<T2>(Value) Process<int>(Value)도 호출하면 Process<T2> 함수 자체는 만들어진다.
다만 if constexpr(false) 내부의 Value.Foo() 코드만 버려진다.

타입 오류와 복잡한 코드의 컴파일을 컴파일단계에서 피해갈 수 있다.
=> int형으로 Value.Foo() 해버리는 상황 방지가 가능하다.
```
