```c++
void CGraphicDevice::Clear()
	{
		// 배경색
		FLOAT backgroundColor[4] = { 0.2f, 0.2f, 0.2f, 1.f };
		// 렌더타겟뷰 클리어
		mContext->ClearRenderTargetView(mRenderTargetView.Get(), backgroundColor);
		// depthstencilview도 클리어
		mContext->ClearDepthStencilView(mDepthStencilView.Get(), D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL, 1.f, 0); // 깊이버퍼도 클리어 해줘야해
	}
```
