[https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-intersectrect](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-intersectrect)

- 두 <b><span>RECT</span></b>가 겹쳐있을때 겹친 영역의 <b><span>RECT</span></b>를 반환한다.

```c++
BOOL IntersectRect(
  [out] LPRECT     lprcDst,
  [in]  const RECT *lprcSrc1,
  [in]  const RECT *lprcSrc2
);
```
