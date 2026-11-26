<b>특별 키워드</b>

<ul>
<li>
auto : 인텔리전스가 자동으로 데이터타입을 유추해서 사용함 

( int num = 5000 → auto num = 5000 )
</li>
<li>
decltype : 데이터 타입을 추론해줌

( decltype(num) num2 → int num2 ) 

</li>
</ul>

<b>namespace 키워드</b>

라이브러리를 만듬 (라이브러리 : 특정 함수나 변수들을 정리해둔 폴더라고 보면됨)

namespace 이름

\{

int iData = 10;

\}

이렇게 선언하면 이름::iData로 사용 가능

우리가 사용하는 cout/cin은 std(standard) 라이브러리에 존재

<b>using 키워드</b>

using namespace 라이브러리명

라이브러리를 ::으로 참조하지 않고 항상 참조하겠다라는 뜻

<b>typedef 키워드</b>

자료형 이름을 재정의함 → 별명을 만들어준다.

typedef unsigned int UINT ⇒ unsigned int 를 UINT키워드로도 사용하겠다는 뜻

<b>static\_cast / dynamic\_cast</b>

(자료형)변수 ⇒ 이렇게 캐스팅하면 C스타일 캐스팅으로 예외작업이 좀 덜되어있음

⇒ 그래서 우리는 <b>static\_cast\<자료형>(변수) </b>를 사용한다.

<b>Dynamic\_cast </b>부모자식관계에서 형 변환 일어날때 사용한다. 더 안전하다고함
