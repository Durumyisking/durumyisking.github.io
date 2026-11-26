---
title: "버퍼 로드"
category: content/categories/topic-05-06-04-04-04.json
order: 40
---
Renderer.cpp

```c++
void LoadBuffer()
	{
		Mesh = new CMesh(); // 임시
		mpos = new Vector4(); // 임시
		CResources::Insert<CMesh>(L"RectMesh", Mesh); // 임시

		Mesh->CreateVertexBuffer(arrVertex, arrVertex.size()); // arrVertex정보로 메시의 Vertexbuffer생성

		std::vector<UINT> vecIdx = {}; // IdxBuffer에서 사용할 벡터 생성

		vecIdx.push_back(0);
		vecIdx.push_back(1);
		vecIdx.push_back(2);
		vecIdx.push_back(0);
		vecIdx.push_back(2);
		vecIdx.push_back(3);

		Mesh->CreateIndexBuffer(vecIdx.data(), vecIdx.size()); // 위의 정보로 메시의 Idxbuffer 생성

		// Const Buffer
		Mesh->CreateConstantBuffer(arrVertex.size()); // 

		*mpos = { 0.f, 0.f, 0.f, 0.f }; // 임시 : 상수버퍼에 전달할 transposition 정보
	}
```
