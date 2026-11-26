---
title: "HLSL 셰이더 파일"
category: content/categories/topic-05-06-04-04-04-02.json
order: 20
---
셰이더 언어인 HLSL을 사용해서 만듬

언어인데 막 개복잡한게 아니라 그냥 구조체처럼 쓸 수 있나봄

<b>ShaderFiles</b>

PSTriangle.hlsli

```c++
struct VTX_IN // 우린 w값 안쓸거니까 input은 vector3으로
{
    float3 vPos : POSITION; // 오른쪽에 오는놈은 시멘틱이라고 해요
                            // 태그같은거임
    float4 vColor : COLOR;
    
};

struct VTX_OUT
{
    float4 vPos : SV_Position; // 하지만 인자로는 vector4받음
    float4 vColor : COLOR;
};

float4 main(VTX_IN _in)
{
    VTX_OUT output = (VTX_OUT) 0.0f; // 초기화
    output.vPos = float4(_in.vPos, 1.f); // float 3까지는 vpos쓰고 w로는 1.f 쓸거임
    output.vColor = _in.vColor;

	return output; // 얘를 레스터라이저에 보내줌
}
```

PSTriangle.hlsli

```c++
struct VTX_OUT
{
    float4 vPos : SV_Position;
    float4 vColor : COLOR;
};

float4 main(VTX_OUT _in) : SV_Target // VS에서 VTX_OUT을 return했으니 얘가 인자로 받음
{
    return _in.vColor;
}
```
