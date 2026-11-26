---
title: "FFastArraySerializer와 Cosmetic 파츠 복제"
category: content/categories/topic-07-06-09.json
order: 20
---
## 핵심 결론

<code>FFastArraySerializer</code>는 복제되는 배열에서 전체 배열을 매번 보내는 대신, 추가/삭제/변경된 Entry만 보내기 위한 언리얼 네트워크 복제 패턴이다.

Cosmetic 파츠 시스템에서는 서버가 "이 Pawn에 어떤 파츠가 적용되어야 하는지"만 권위 있게 정하고, 각 클라이언트는 그 변경분을 받아 자기 월드에서 Cosmetic Actor를 생성하거나 제거한다.

```txt
서버
- CharacterPartList에 Entry 추가/삭제/변경
- MarkItemDirty / MarkArrayDirty로 변경 표시
- FastArrayDeltaSerialize가 변경된 Entry만 복제

클라이언트
- PostReplicatedAdd / PreReplicatedRemove / PostReplicatedChange 호출
- Entry에 맞는 ChildActorComponent와 Part Actor를 로컬 생성/제거
```

---

## 이 문서에서 말하는 서버 통신 수준

이 문서는 네트워크 기초 전체를 설명하는 문서가 아니다.

여기서 필요한 기초는 다음 정도다.

```txt
서버는 권위 있는 상태를 가진다.
클라이언트는 그 상태를 복제받아 화면에 반영한다.
Cosmetic Actor 포인터 자체를 보내는 것이 아니라, "어떤 파츠가 필요하다"는 데이터를 보낸다.
```

Cosmetic은 시각 요소지만, 멀티플레이에서는 "다른 플레이어에게 어떤 외형으로 보이는가"도 공유 상태다. 그래서 클라이언트가 마음대로 붙이는 방식이 아니라, 서버가 파츠 목록을 정하고 그 목록을 복제하는 구조가 된다.

---

## 일반 배열 복제의 한계

가장 단순한 방식은 이런 형태다.

```c++
UPROPERTY(Replicated)
TArray<FOWCharacterPart> CharacterParts;
```

이 방식은 이해하기 쉽지만, 배열 안에서 어떤 항목이 추가됐는지, 어떤 항목이 제거됐는지, 어떤 항목만 바뀌었는지를 명확한 이벤트로 다루기 어렵다.

예를 들어 현재 파츠 목록이 이렇게 있다고 하자.

```txt
0. DefaultBody
1. DefaultHair
2. DefaultLeftPistol
3. DefaultRightPistol
```

Punk 스킨을 적용하면서 Hair만 바뀌었다면 원하는 의도는 이것이다.

```txt
DefaultHair 제거
PunkHair 추가
```

하지만 일반 배열 복제만 사용하면, 클라이언트 입장에서 "배열이 바뀌었다"는 사실은 알아도 그 변경을 파츠 Actor의 생성/삭제 생명주기와 세밀하게 연결하기가 불편하다.

Cosmetic 시스템은 변경 이벤트가 중요하다.

```txt
Entry가 추가됨 -> Actor를 생성해야 함
Entry가 제거됨 -> Actor를 제거해야 함
Entry가 변경됨 -> 기존 Actor 제거 후 다시 생성해야 함
```

그래서 배열 자체와 배열 안의 항목을 분리해서 관리한다.

---

## 왜 List와 Entry로 나누는가

현재 구조는 두 역할로 나뉜다.

```txt
FOWAppliedCharacterPartEntry
- 배열 안의 한 항목
- 실제 복제될 FOWCharacterPart를 가진다
- FFastArraySerializerItem을 상속해서 복제 ID/변경 키 추적 대상이 된다

FOWCharacterPartList
- Entry 배열 전체를 소유한다
- Add/Remove/Clear 같은 변경 API를 제공한다
- FFastArraySerializer를 상속해서 배열 델타 직렬화를 담당한다
- 복제 콜백에서 Actor 생성/삭제를 실행한다
```

코드 형태는 이런 패턴이다.

```c++
USTRUCT()
struct FOWAppliedCharacterPartEntry : public FFastArraySerializerItem
{
    GENERATED_BODY()

private:
    UPROPERTY()
    FOWCharacterPart Part;

    UPROPERTY(NotReplicated)
    int32 PartHandle = INDEX_NONE;

    UPROPERTY(NotReplicated)
    TObjectPtr<UChildActorComponent> SpawnedComponent = nullptr;
};
```

```c++
USTRUCT(BlueprintType)
struct FOWCharacterPartList : public FFastArraySerializer
{
    GENERATED_BODY()

    bool NetDeltaSerialize(FNetDeltaSerializeInfo& DeltaParms)
    {
        return FFastArraySerializer::FastArrayDeltaSerialize<FOWAppliedCharacterPartEntry, FOWCharacterPartList>(Entries, DeltaParms, *this);
    }

private:
    UPROPERTY()
    TArray<FOWAppliedCharacterPartEntry> Entries;
};
```

Entry가 그냥 데이터만 가진 구조체가 아니라 <code>FFastArraySerializerItem</code>을 상속하는 점이 핵심이다. 언리얼은 이 항목별 ID와 변경 키를 이용해서 "이 배열에서 어떤 Entry가 달라졌는가"를 추적한다.

---

## 서버에서 파츠를 추가할 때

서버가 파츠를 추가하면 대략 이런 일이 일어난다.

```c++
FOWAppliedCharacterPartEntry& NewEntry = Entries.AddDefaulted_GetRef();
NewEntry.Part = NewPart;
NewEntry.PartHandle = Result.PartHandle;

MarkItemDirty(NewEntry);
```

<code>MarkItemDirty(NewEntry)</code>는 이 Entry가 새로 추가되었거나 변경되었음을 복제 시스템에 알려준다.

의미는 이렇다.

```txt
이 Entry는 다음 복제 때 클라이언트로 보내야 한다.
```

삭제할 때는 배열 구조가 바뀌므로 <code>MarkArrayDirty()</code>를 호출한다.

```c++
EntryIt.RemoveCurrent();
MarkArrayDirty();
```

즉 변경 종류에 따라 표시가 다르다.

```txt
항목 추가/항목 내용 변경 -> MarkItemDirty
항목 삭제/배열 구조 변경 -> MarkArrayDirty
```

---

## NetDeltaSerialize가 가능한 이유

<code>FOWCharacterPartList</code>는 그냥 일반 USTRUCT가 아니라 커스텀 델타 직렬화를 사용한다고 언리얼에 알려준다.

```c++
template<>
struct TStructOpsTypeTraits<FOWCharacterPartList> : public TStructOpsTypeTraitsBase2<FOWCharacterPartList>
{
    enum { WithNetDeltaSerializer = true };
};
```

이 설정 때문에 <code>CharacterPartList</code>가 복제될 때 일반 property 복제가 아니라 <code>NetDeltaSerialize</code>가 호출된다.

```c++
bool NetDeltaSerialize(FNetDeltaSerializeInfo& DeltaParms)
{
    return FFastArraySerializer::FastArrayDeltaSerialize<FOWAppliedCharacterPartEntry, FOWCharacterPartList>(Entries, DeltaParms, *this);
}
```

언리얼은 연결별로 이전에 무엇을 보냈는지 기억하고, Entry별 변경 키를 비교해서 이번에 보낼 변경분을 결정한다.

정확한 감각은 이것이다.

```txt
직렬화된 byte 배열 중간을 직접 수정해서 보내는 것이 아니다.
이전 복제 상태와 현재 상태를 비교해서, 달라진 Entry만 직렬화한다.
```

---

## 클라이언트에서 받는 콜백

FastArray는 클라이언트가 변경분을 적용한 뒤 콜백을 호출한다.

추가된 Entry는 <code>PostReplicatedAdd</code>로 들어온다.

```c++
void FOWCharacterPartList::PostReplicatedAdd(const TArrayView<int32> AddedIndices, int32 FinalSize)
{
    for (int32 Index : AddedIndices)
    {
        FOWAppliedCharacterPartEntry& Entry = Entries[Index];
        SpawnActorForEntry(Entry);
    }
}
```

제거되는 Entry는 제거 직전에 <code>PreReplicatedRemove</code>로 들어온다.

```c++
void FOWCharacterPartList::PreReplicatedRemove(const TArrayView<int32> RemovedIndices, int32 FinalSize)
{
    for (int32 Index : RemovedIndices)
    {
        FOWAppliedCharacterPartEntry& Entry = Entries[Index];
        DestroyActorForEntry(Entry);
    }
}
```

변경된 Entry는 <code>PostReplicatedChange</code>에서 처리한다.

```c++
void FOWCharacterPartList::PostReplicatedChange(const TArrayView<int32> ChangedIndices, int32 FinalSize)
{
    for (int32 Index : ChangedIndices)
    {
        FOWAppliedCharacterPartEntry& Entry = Entries[Index];
        DestroyActorForEntry(Entry);
        SpawnActorForEntry(Entry);
    }
}
```

이 콜백들이 중요한 이유는 네트워크 상태 변경과 시각 Actor 생명주기를 직접 연결할 수 있기 때문이다.

```txt
파츠 추가 복제 -> Actor 생성
파츠 제거 복제 -> Actor 제거
파츠 변경 복제 -> Actor 재생성
```

---

## Cosmetic에서 얻는 이득

Cosmetic 파츠 목록은 자주 전체가 바뀌기보다, 특정 파츠가 추가/삭제/교체되는 경우가 많다.

예를 들어 트레이서가 기본 스킨에서 Punk 스킨으로 바뀐다고 하자.

```txt
기존
- DefaultHair
- DefaultLeftPistol
- DefaultRightPistol

변경
- PunkHair
- PunkLeftPistol
- PunkRightPistol
```

FastArray를 쓰면 전체 Cosmetic 상태를 통째로 다시 보내는 대신, 실제 변경된 Entry 중심으로 보낼 수 있다.

또 다른 이득은 콜백 구조다.

```txt
서버 데이터 변경
-> 네트워크 델타 복제
-> 클라이언트 콜백
-> Actor 생성/삭제
```

이 흐름이 한 곳에 모이기 때문에 Tick에서 계속 비교하거나, UI/Controller/Pawn 여러 곳에서 "지금 붙은 Actor가 맞는지" 검사할 필요가 줄어든다.

---

## 왜 SpawnedComponent는 복제하지 않는가

<code>FOWAppliedCharacterPartEntry</code>에는 <code>SpawnedComponent</code>가 있지만 <code>NotReplicated</code>다.

```c++
UPROPERTY(NotReplicated)
TObjectPtr<UChildActorComponent> SpawnedComponent = nullptr;
```

이 값은 각 클라이언트가 자기 월드에서 만든 실제 컴포넌트 포인터다. 서버의 포인터를 클라이언트로 보내는 것이 아니다.

복제되는 것은 이것이다.

```txt
PartClass = 어떤 Actor 클래스를 만들 것인가
SocketName = 어디에 붙일 것인가
CollisionMode = 충돌을 어떻게 처리할 것인가
```

복제되지 않는 것은 이것이다.

```txt
실제로 생성된 UChildActorComponent 포인터
서버 또는 특정 클라이언트 월드 안의 Actor 인스턴스 포인터
```

이 구분이 중요하다.

서버는 "무엇을 보여야 하는가"라는 권위 데이터를 보낸다. 클라이언트는 그 데이터를 보고 "내 월드에서 어떻게 보여줄 것인가"를 실행한다.

---

## Dedicated Server에서 Actor를 만들지 않는 이유

<code>SpawnActorForEntry</code>는 Dedicated Server에서 실행되지 않도록 되어 있다.

```c++
if (ensure(OwnerComponent) && !OwnerComponent->IsNetMode(NM_DedicatedServer))
{
    // ChildActorComponent 생성
}
```

Dedicated Server는 화면을 렌더링하지 않는다. Cosmetic Actor가 순수 시각용이고 충돌도 기본적으로 <code>NoCollision</code>이라면 서버에서 만들 이유가 적다.

그래서 서버는 파츠 목록만 관리한다.

```txt
Dedicated Server
- CharacterPartList 상태 소유
- 변경분 복제
- Cosmetic Actor는 생성하지 않음

Client
- CharacterPartList 복제 수신
- 로컬에서 ChildActorComponent와 Part Actor 생성
```

이 구조는 서버 비용을 줄이고, 시각화 책임을 클라이언트로 넘긴다.

---

## 이 구조를 오버워치 예시로 보기

플레이어가 Tracer Punk 스킨을 선택했다고 하자.

서버의 선택 결과는 이런 파츠 목록이 된다.

```txt
FOWCharacterPart
- PartClass = BP_CP_Tracer_Punk_Hair
- SocketName = head

FOWCharacterPart
- PartClass = BP_CP_Tracer_Punk_LeftPistol
- SocketName = hand_l_weapon

FOWCharacterPart
- PartClass = BP_CP_Tracer_Punk_RightPistol
- SocketName = hand_r_weapon
```

서버는 이 Actor들을 직접 보여주려고 만드는 것이 아니라, <code>CharacterPartList</code>에 Entry로 추가한다.

클라이언트는 추가된 Entry를 받고 각자 자기 Pawn Mesh 소켓에 ChildActorComponent를 붙인다.

```txt
Pawn Mesh
- head socket
  - ChildActorComponent
    - BP_CP_Tracer_Punk_Hair

Pawn Mesh
- hand_l_weapon socket
  - ChildActorComponent
    - BP_CP_Tracer_Punk_LeftPistol
```

즉 네트워크로 보내는 것은 "PunkHair Actor 인스턴스"가 아니라 "PunkHair Actor 클래스를 head에 붙여야 한다"는 데이터다.

---

## 학습 포인트

이 구조를 볼 때 중요한 질문은 세 가지다.

1. 누가 권위 상태를 소유하는가?

Cosmetic 파츠 목록은 서버 권위의 <code>CharacterPartList</code>가 소유한다.

1. 누가 실제 화면 Actor를 만드는가?

각 클라이언트의 <code>FOWCharacterPartList</code> 복제 콜백이 만든다.

1. 왜 List와 Entry가 나뉘는가?

Entry는 복제 추적 단위이고, List는 델타 직렬화와 생명주기 콜백을 관리하는 컨테이너이기 때문이다.

---

## 한 줄 요약

<code>FOWCharacterPartList</code>와 <code>FOWAppliedCharacterPartEntry</code>를 나눈 이유는, Cosmetic 파츠 배열을 항목 단위로 델타 복제하고, 각 항목의 추가/삭제/변경 이벤트에 맞춰 클라이언트 로컬 Actor 생명주기를 관리하기 위해서다.
