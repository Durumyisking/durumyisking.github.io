---
title: "스왑 체인과 RTV 생성"
category: content/categories/topic-05-06-04-04.json
order: 20
---
SwapChain 초기화 및 객체 생성

```c++
// SwapChain
		// DESC = description의 약자로 해당 객체를 사용하여 설정을 해줄 수 있음
		DXGI_SWAP_CHAIN_DESC swapChainDesc = {};

		swapChainDesc.OutputWindow = hwnd; // 렌더될 윈도우의 핸들
		swapChainDesc.Windowed = true; // 창모드 전체화면
		swapChainDesc.BufferCount = 2; // 사용할 렌더링 버퍼개수

		swapChainDesc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT; // 버퍼 렌더타겟으로 쓸거임
		swapChainDesc.BufferDesc.Width = application.GetWidth();
		swapChainDesc.BufferDesc.Height = application.GetHeight();
		swapChainDesc.BufferDesc.Format = DXGI_FORMAT::DXGI_FORMAT_R8G8B8A8_UNORM; // 컬러 포멧 타입
		swapChainDesc.BufferDesc.RefreshRate.Numerator = 240; // 프레임 비율 분자
		swapChainDesc.BufferDesc.RefreshRate.Denominator = 1; // 프레임 비율 분모
		swapChainDesc.BufferDesc.Scaling = DXGI_MODE_SCALING_UNSPECIFIED;
		swapChainDesc.BufferDesc.ScanlineOrdering = DXGI_MODE_SCANLINE_ORDER_UNSPECIFIED;

		/*
			sample description은 Direct3D의 멀티 샘플링 속성을 정의한다. 
			멀티 샘플링은 렌더된 픽셀들의 평균 샘플을 사용하여 최종 컬러를 좀더 부드럽게 하는 기술이다.
			샘플러와 관련된게 맞다.
		*/
		swapChainDesc.SampleDesc.Count = 1;
		swapChainDesc.SampleDesc.Quality = 0;

		if (!CreateSwapChain(&swapChainDesc)) // SwapChain 생성
			return;


// func createswapchain
bool CGraphicDevice::CreateSwapChain(DXGI_SWAP_CHAIN_DESC* _Desc)
	{
		Microsoft::WRL::ComPtr<IDXGIDevice> pDXGIDevice = nullptr;
		Microsoft::WRL::ComPtr<IDXGIAdapter> pDXGIAdapter = nullptr;
		Microsoft::WRL::ComPtr<IDXGIFactory> pDXGIFactory = nullptr;

		if (FAILED(mDevice->QueryInterface(__uuidof(IDXGIDevice), (void**)pDXGIDevice.GetAddressOf())))
			return false;

		if (FAILED(pDXGIDevice->GetParent(__uuidof(IDXGIAdapter), (void**)pDXGIAdapter.GetAddressOf())))
			return false;

		if (FAILED(pDXGIAdapter->GetParent(__uuidof(IDXGIFactory), (void**)pDXGIFactory.GetAddressOf())))
			return false;

		if (FAILED(pDXGIFactory->CreateSwapChain(mDevice.Get(), _Desc, mSwapChain.GetAddressOf())))
			return false;

		return true;
	}
```

SwapChain에 있는 renderingbuffer중 1개를 RTV로 지정할 것임

```c++
// Get rendertarget for swapchain
		hr = mSwapChain->GetBuffer(0, __uuidof(ID3D11Texture2D), (void**)mRenderTarget.GetAddressOf());

// Create Rendertarget View : 렌더타겟에 접근하기위한 Rendertarget View 생성
		hr = mDevice->CreateRenderTargetView(mRenderTarget.Get(), nullptr, mRenderTargetView.GetAddressOf());
```
