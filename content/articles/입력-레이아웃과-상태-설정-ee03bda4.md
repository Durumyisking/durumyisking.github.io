---
title: "입력 레이아웃과 상태 설정"
category: content/categories/topic-05-06-04-04-04.json
order: 30
---
Renderer.cpp

```c++
void SetUpState()
	// Inputlayout에서 Vertex Buffer에 들어있는 정점들이 어떤 애들일지의 구조 정보를 만든다
	// Vertexbuffer는 정점을 담고있는 자료구조일뿐
	{
		// input Layout (정점 구조 정보)
		D3D11_INPUT_ELEMENT_DESC arrLayout[2] = {}; // 우리가 vertex의 멤버로 pos, color 들고있으니까 2개만 만들자

		arrLayout[0].AlignedByteOffset = 0; // 배열의 0바이트부터 삽입하겠다.
		arrLayout[0].Format = DXGI_FORMAT_R32G32B32_FLOAT; // pos가 12바이트 짜리니까
		arrLayout[0].InputSlot = 0; // == D3D11_INPUT_PER_VERTEX_DATA 0번슬롯은 이거임
		arrLayout[0].InputSlotClass = D3D11_INPUT_PER_VERTEX_DATA;
		arrLayout[0].SemanticName = "POSITION";
		arrLayout[0].SemanticIndex = 0;

		arrLayout[1].AlignedByteOffset = 12; // 위에서 12바이트 만큼 삽입해줬으니 여기서부터 삽입할거임
		arrLayout[1].Format = DXGI_FORMAT_R32G32B32A32_FLOAT; // color가 16바이트 짜리니까
		arrLayout[1].InputSlot = 0;
		arrLayout[1].InputSlotClass = D3D11_INPUT_PER_VERTEX_DATA;
		arrLayout[1].SemanticName = "COLOR";
		arrLayout[1].SemanticIndex = 0;

		Shader->CreateInputLayout(arrLayout, 2);

	}

```

Inputlayout 생성

Shader.cpp

```c++
void CShader::CreateInputLayout(D3D11_INPUT_ELEMENT_DESC* _Desc, UINT _NumElements)
	{
		graphics::GetDevice()->CreateInputLayout(_Desc, _NumElements
			, mVSBlob->GetBufferPointer()
			, mVSBlob->GetBufferSize()
			, mInputLayout.GetAddressOf());
		// _Desc와 Compile된 VS코드의 정보가 일치하면 Inputlayout을 만든다

	}
```
