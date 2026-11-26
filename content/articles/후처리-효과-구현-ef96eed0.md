렌더타겟에 모든 오브젝트를 그리고 나온 결과물을 텍스처로 만든다

그렇게 만든 텍스처에 PostEffect를 추가시킨다.

이렇게 해서 렌더링이 된 오브젝트들에 특수한 시각 효과를 줄 수가 있다.

아래는 게임에서 사용한 포스트프로세스이펙트다.

---

<details>
<summary><b>Burn/Noise 효과</b></summary>

Burn/Noise 텍스처들을 적용하고싶은 오브젝트에 추가후

텍스처 uv의 색상값에 따라서 오브젝트 텍스처의 알파값을 빼준다.

</details>

<details>
<summary><b>Wave 효과</b></summary>

```c++
float4 main(VSOut _in) : SV_Target
{
    float4 Color = (float4) 0.f;

    // 화면의 좌표를 UV좌표로 변환한다.
    float2 UV = _in.Pos.xy / Resolution;

    // wave speed는 점점 빨라진다, wave amount는 파동의 높이, distortion은 높을수록 덜 외곡된다.
    UV.x = UV.x + cos(UV.y * wave_amount + ElapsedTime * wave_speed) / wave_distortion;
    UV.y = UV.y + sin(UV.x * wave_amount + ElapsedTime * wave_speed) / wave_distortion;
     
    Color = postProcessTexture.Sample(pointSampler, UV);
    
 
    return Color;
}
```

<b>UV.x</b>

wave amount가 클수록 파장의 높이는 커진다

wave speed가 클수록 파장의 간격은 좁아진다.

wave distortion이 크면 파장의 높이는 낮아진다.

시간이 지날수록 해당 UV좌표로부터 위에있는픽셀들을 가져온다 (최대  1만큼)

근데 1이나 위에있는 픽셀을 가져오면 gap이 너무 크니까 distortion으로 조절한다.

<b>UV.y</b>

UV.x를 y축 관점에서 본 것

</details>

<details>
<summary>GreyScale(흑백) 효과</summary>

```c++
                                                 //(float3(0.21f, 0.71f, 0.07f))
float3 color = RGB;     // 이 LUMA는 ITU-R BT.601규격에 따라 정해진 luma 계수이다
float gray = dot(color, LUMA); // luma 계수와 미분한다.
Color = float4(gray, gray, gray, postProcessTexture.Sample(pointSampler, UV).a);
// rgb값을 모두 gray로 설정하고 a값은 이전의 a값을 가져온다.
```

</details>

<details>
<summary>Curve 효과</summary>

```c++
float2 curve2(float2 uv)
{
    uv -= float2(0.5f, 0.5f); // 화면의 중심으로 uv 좌표를 이동시킨다.
    uv = uv * 1.2f * (1.f / 1.2f + 2.f * uv.x * uv.x * uv.y * uv.y);
    uv += float2(0.5f, 0.5f);
    return uv;
}
```

<b>아래는 픽셀의 좌표를 재 매핑하는 코드이다.</b>

uv에서 0.5를 빼 화면 중앙쪽으로 이동시키고 숫자를 곱해서 다시 0.5를 더해

곡면 상에서 각 좌표가 평면 상에서 위치한 것보다 더 멀리 떨어진 위치에 매핑되게 한다.

```c++
uv -= float2(0.5f, 0.5f); 
uv = uv * 1.2f
uv += float2(0.5f, 0.5f);
```

<b>아래는 왜곡을 시키는 핵심 코드이다.</b>

x와 y의 절대값이 클수록 스케일링이 1.2에 가까워지고

작을수록 작은 스케일링을 가지게되어 모서리로 갈수록 스케일링이 작아진다.

따라서 중앙으로 갈수록 평면과 비슷하게 렌더링되고 모서리쪽으로 갈수록 일반 좌표보다 더 먼 곳의 픽셀을 가져오게 된다.

결과적으로 중앙이 볼록하고 모서리쪽이 작아보이는 효과를 가진다.

```c++
uv = uv * 1.2f * (1.f / 1.2f + 2.f * uv.x * uv.x * uv.y * uv.y);
```

</details>

<details>
<summary>Noise Pattern</summary>

ElapsedTime에 따라 일정한 노이즈 패턴을 return 한다.

```c++
float noise(float2 uv, Texture2D<float4> noiseTexture)
{
		// 노이즈텍스처의 좌표 가져옴 uv와 시간값을 인자로 넘겨주어 노이즈값의 변화를 만듬
    float2 offset = float2(1.0f, 2.0f * cos(ElapsedTime)) * ElapsedTime * 8.0f + uv * 1.0f; 
		// -5.5보다 작은값은 -5.5 7.5보다큰값은 7.5로 -5.5~7.5사이의 값만 나오게 제한한다. 
		// 0~1로 제한하면 화면이 아예 깔끔해진다(빼도된다), 따라서 uv의 반복을 없앨수 있다
		// 해당 함수를 사용하여 UV의 반복을 제한 할 수 있다
    offset = clamp(offset, -5.5f, 7.5f);
		// offset위치에 있는 색의 R값을 가져올것
    float s = noiseTexture.SampleLevel(pointSampler, offset, 0).x;
		// 해당 픽셀의 r값이 강하면 더 큰 값을
		// 작을수록 더 작은값을 가져온다.
    s *= s;
    return s;
}

```

</details>

<details>
<summary>Stripe</summary>

Noise Pattern을 사용해서 어느정도 렌덤성이 있는 가로줄을 생성한다.

```c++
// y 값이 start와 end사이의 값이 아니면 0을 반환한다
// 사이의 값이면 그 사이의 어느정도 비율에 위치하고 있는지를 반환한다.
float ramp(float y, float start, float end)
{
    float inside = step(start, y) - step(end, y);
    float fact = (y - start) / (end - start) * inside;
    return (1.f - fact) * inside;
}

float stripes(float2 uv, Texture2D<float4> noiseTexture)
{
													/*Noise의 주기*/     /*Noise 생성 위치*/
   float noi = noise(uv * float2(0.5f, 1.f) + float2(1.f, 3.f), noiseTexture);
	    
	 float yValue = uv.y * 4.f + ElapsedTime / 2.f + sin(ElapsedTime + sin(ElapsedTime * 0.63f));
	  
	// 해당 Yvalue가 UV상의 0.3, 0.4 사이에 있을때 유효한 값을 return한다
	 return ramp((yValue, 1.f), 0.3f, 0.4f) * noi;
}
```

</details>

<details>
<summary>Circle</summary>

```c++
float smoothCircle(float2 position, float relativeSize)
{
		// 원이 생성될 위치와 화면의 중앙 사이의 거리를 구한다.
		// 원의 일부가 화면 밖이면 렌더링 대상에서 제외
    float d = distance(center, position) * 2.0f / relativeSize;
    if (d > 1.0f)
    {
        return 0.0f;
    }
    else
    {
        return clamp(smoothness / d - smoothness, -1.0f, 1.0f);
    }
}
```

```c++
// create the grid of circles, with a bunch missing, and fanaggle the sizes a bit
float circleGrid(float2 position, float spacing, float dotSize)
{
    
    // idx => which dot we are showing in the grid.
    
    // check x and y index to see if we should draw it or not.
    float idx = floor(1.0f / spacing * position.x);
    float yIdx = floor(1.0f / spacing * position.y);

    // much higher than .06 causes the grid to be obvious
    if (rand2d(idx, yIdx, 0.06f))
    {
        return 0.0f;
    }
    
    // modify the size of the flake a bit
    float relativeSize = (0.5f + 0.5f * randF(yIdx)) * dotSize / spacing;
    
    return smoothCircle(float2(
        frac(1.0f / spacing * position.x),
        frac(1.0f / spacing * position.y + yIdx)
    ), relativeSize);
}
```

</details>

<details>
<summary>Snow 효과</summary>

```c++
float4 main(VSOut _in) : SV_Target
{      
    float4 Color = postProcessTexture.Sample(pointSampler, _in.UV); // 기존 코드
    
    float2 uvsq = float2(_in.UV.x * Resolution.x / Resolution.y, _in.UV.y);
    float amnt = 0.f;
    
    for (float i = 0.0; i < N_LAYERS; i++)
    {
        float p = 0.5f + ((i + 1.f) / N_LAYERS) * 0.4f;
        float2 fallPosition = float2(
            uvsq.x + i + p * sin(ElapsedTime / 2.f + i) / 4.f * SPEED,
            i * 3.f + uvsq.y - ElapsedTime * p / 1.f * SPEED
        );
        amnt = amnt + SNOW_ALPHA * circleGrid(fallPosition, 0.06f * p, 0.04f * p * p);
    }
    
    float4 snowColor = lerp(SNOW_COL, bg, 1.0 - amnt);
    Color.rgb = snowColor.rgb * Color.rgb; // 뷰포트 색상과 눈을 더합니다.
    
    return Color;
}
```

</details>
