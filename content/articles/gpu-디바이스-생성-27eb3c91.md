GPU devcie 객체 생성

```c++
HWND hwnd = application.GetHwnd(); // 윈도우 핸들 얻어옴

		// Device, Device Context
		UINT DeviceFlag = D3D11_CREATE_DEVICE_DEBUG; // 디버그모드로 만들거임 릴리즈모드는 0
		D3D_FEATURE_LEVEL FeatureLevel = (D3D_FEATURE_LEVEL)0;

		// 그냥 bool 형 반환값과 같음 SUCCEEDED / FAILED로 나뉨
		// 함수 반환 성공하면 suc 아니면 fail 나옴
		HRESULT hr = D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, DeviceFlag
			, nullptr, 0, D3D11_SDK_VERSION, mDevice.GetAddressOf()
			, &FeatureLevel, mContext.GetAddressOf());
```
