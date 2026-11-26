---
title: "Attribute"
category: content/categories/topic-07-05.json
order: 70
---
---

우리가 평소에 사용하는 공격범위, 체력, 스테미너 등등 게임에 있어서 사용할 변수들? 이라고 보면된다.

### Attribute Set

- 단일 어트리뷰트 데이터인 GameplayAttributeData의 묶음
- <b>주요함수</b>
  - PreAttributeChange : 어트리뷰트 변경 전 호출
  - PostAttributeChange : 어트리뷰트 변경 후에 호출
  - PreGameplayEffectExecute : 게임플레이 이펙트 적용 전에 호출
  - PostGameplayEffectExecute : 게임플레이 이펙트 적용 후에 호출
- <b>어트리뷰트 세트 접근자 매크로</b>
  - 많이 수행되는 기능에 대해 매크로를 만들어 제공함
- AttributeSet를 ASC에 수동으로 등록할 필요 없다<br />같은 액터에 있는 UAttributeSet타입 객체 찾아서 등록한다.

### GameplayAttributeData

- 기본적으로 2가지 값으로 구성<br />BaseValue : 기본 값 (영구히 적용되는 고정 스탯 값을 관리하는데 사용<br />CurrentValue : 변동 값. 버프(Buff) 등으로 임시적으로 변동된 값을 관리하는데 사용

---

별거 없다 아래와 같은식으로 게임할때 쓸 정보들 만든다

```c++

// MyAttributeSet.h
UCLASS()
class ARENABATTLEGAS_API UABCharacterAttributeSet : public UAttributeSet
{
	GENERATED_BODY()
public:
	UABCharacterAttributeSet();

protected:
	UPROPERTY(BlueprintReadOnly, Category="Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData AttackRange;
	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxAttackRange;

	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData AttackRadius;
	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxAttackRadius;

	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData AttackRate;
	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxAttackRate;

	UPROPERTY(BlueprintReadOnly, Category = "Health", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData Health;

	UPROPERTY(BlueprintReadOnly, Category = "Health", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxHealth;

};

```

어트리뷰트들이 잔뜩 생기는데 이것들의 Base/Current 값에 대해 대해 GetterSetter 만들면 고역일 것이다.<br />다행히도 언리얼에서 편하게 하라고 매크로 만들어뒀다.

```c++
#define ATTRIBUTE_ACCESSORS(ClassName, PropertyName) \
	GAMEPLAYATTRIBUTE_PROPERTY_GETTER(ClassName, PropertyName) \ 
	GAMEPLAYATTRIBUTE_VALUE_GETTER(PropertyName) \
	GAMEPLAYATTRIBUTE_VALUE_SETTER(PropertyName) \
	GAMEPLAYATTRIBUTE_VALUE_INITTER(PropertyName)

	/*
	GAMEPLAYATTRIBUTE_PROPERTY_GETTER 어트리뷰트의 타입? 해당 어트리뷰트가 특정 어트리뷰트인지 구별하는데 사용
	GAMEPLAYATTRIBUTE_VALUE_GETTER CurrentValue가져옴
	GAMEPLAYATTRIBUTE_VALUE_SETTER Base(영구한)값 Set하는 매크로
	GAMEPLAYATTRIBUTE_VALUE_INITTER Base/CurrentValue를 같은값으로 설정해줌
	*/


UCLASS()
class ARENABATTLEGAS_API UABCharacterAttributeSet : public UAttributeSet
{
	GENERATED_BODY()
public:
	UABCharacterAttributeSet();

	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, AttackRange);
	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, MaxAttackRange);
	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, AttackRadius);
	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, MaxAttackRadius);
	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, AttackRate);
	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, MaxAttackRate);
	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, Health);
	ATTRIBUTE_ACCESSORS(UABCharacterAttributeSet, MaxHealth);

protected:
	UPROPERTY(BlueprintReadOnly, Category="Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData AttackRange;
	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxAttackRange;

	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData AttackRadius;
	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxAttackRadius;

	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData AttackRate;
	UPROPERTY(BlueprintReadOnly, Category = "Attack", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxAttackRate;

	UPROPERTY(BlueprintReadOnly, Category = "Health", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData Health;

	UPROPERTY(BlueprintReadOnly, Category = "Health", Meta = (AllowPrivateAccess = true))
	FGameplayAttributeData MaxHealth;

};

```

매크로를 추가했으면

이런 함수들이 추가되어있어서 바로 사용 가능하다.

```c++
	InitHealth(GetMaxHealth());
```

---

아래와 같이 ASC를 사용중인 클래스에 Attribue를 멤버로 추가하고

CreateDefaultSubobject로 객체를 생성해준다

```c++
UCLASS()
class ARENABATTLEGAS_API AABGASPlayerState : public APlayerState, public IAbilitySystemInterface
{
	GENERATED_BODY()
	
public:
	AABGASPlayerState()
	{
		ASC = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("ASC"));
		AttributeSet = CreateDefaultSubobject<UABCharacterAttributeSet>(TEXT("AttributeSet"));
	}

protected:
	UPROPERTY(EditAnywhere)
	TObjectPtr<class UAbilitySystemComponent> ASC;
	UPROPERTY(EditAnywhere)
	TObjectPtr<class UABCharacterAttributeSet> AttributeSet;
};

```

우리가 AttributeSet을 ASC에다가 직접 Set 해주지 않아도

```c++
//UAbilitySystemComponent.cpp
void UAbilitySystemComponent::InitializeComponent()
{
	Super::InitializeComponent();
	
	.... // 생략
	
	// Owner의 Object들을 가져온다음에
	// Attribue가 있으면 Spawn 시킨다.
	TArray<UObject*> ChildObjects;
	GetObjectsWithOuter(Owner, ChildObjects, false, RF_NoFlags, EInternalObjectFlags::Garbage);

	for (UObject* Obj : ChildObjects)
	{
		UAttributeSet* Set = Cast<UAttributeSet>(Obj);
		if (Set)  
		{
			SpawnedAttributes.AddUnique(Set);
		}
	}

	SetSpawnedAttributesListDirty();
}

```

해당 어트리뷰트 셋은 <br />아래 코드를 참고하여 어디서든 불러올 수 있다.

```c++
	UAbilitySystemComponent* ASC = 
			UAbilitySystemBlueprintLibrary::GetAbilitySystemComponent(Character);
	if (!ASC)
	{
		return FGameplayAbilityTargetDataHandle();
	}
	const UABCharacterAttributeSet* AttributeSet = ASC->GetSet<UABCharacterAttributeSet >();
	if (!AttributeSet)
	{
		return FGameplayAbilityTargetDataHandle();
	}
```

어트리뷰트 변경되기전 이런식으로 후처리를 해 줄 수 있다.

```c++
void UABCharacterAttributeSet::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)
{
	if (Attribute == GetHealthAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0, GetMaxHealth());
	}
}

```
