---
title: "COM 인터페이스와 ComPtr"
category: content/categories/topic-05-06.json
order: 30
---
---

<b>COM 오브젝트 (directX에서 사용하는 인터페이스들)</b>에 대해 사용하는 <b>스마트 포인터</b>이다.

(이거 쓰라고 권장되어있는거다. 안써도 되긴 하는데 일단 쓰자)

```javascript
Microsoft::WRL::ComPtr<ID3D11Device> device; // COM interface
ComPtr<ID3D11Device> m_d3dDevice;

device.As(&m_d3dDevice); (As를 사용해서 포인터 복사)
```
