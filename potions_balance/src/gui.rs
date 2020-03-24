use std::marker::PhantomData;
use std::iter::once;
use std::mem::{size_of, forget};
use std::ptr::{null, null_mut, NonNull};
use winapi::shared::minwindef::*;
use winapi::shared::windef::*;
use winapi::um::winuser::*;
use winapi::um::libloaderapi::*;
use winapi::um::errhandlingapi::*;
use std::os::raw::c_int;

pub struct Window<'a> {
    h_wnd: NonNull<HWND__>,
    phantom: PhantomData<&'a ()>,
    destroy_on_drop: bool,
}

impl<'a> Drop for Window<'a> {
    fn drop(&mut self) {
        if self.destroy_on_drop {
            unsafe {
                let ok = DestroyWindow(self.h_wnd.as_ptr());
                debug_assert!(ok != 0);
            }
        }
    }
}

pub trait WindowProc = for<'b> FnMut(Window<'b>, UINT, WPARAM, LPARAM, ) -> Option<LRESULT>;

impl<'a> Window<'a> {
    pub fn new(class: &'a WindowClass, name: &str, width: c_int, height: c_int, window_proc: &'a mut dyn WindowProc) -> Result<Window<'a>, ()> {
        let h_wnd = NonNull::new(unsafe {
            CreateWindowExW(
                WS_EX_CLIENTEDGE,
                class.atom as *const _,
                name.encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
                WS_OVERLAPPEDWINDOW,
                CW_USEDEFAULT, CW_USEDEFAULT,
                width, height,
                null_mut(),
                null_mut(),
                class.h_instance,
                Box::into_raw(Box::new(window_proc)) as *mut _
            )
        });
        if let Some(h_wnd) = h_wnd {
            Ok(Window { h_wnd, phantom: PhantomData, destroy_on_drop: true })
        } else {
            let error_code = unsafe { GetLastError() };
            message_box(&format!("Cannot create window ({}).", error_code), "Error", MB_ICONEXCLAMATION | MB_OK);
            Err(())
        }
    }

    pub fn show(&self, n_cmd_show: c_int) -> bool {
        unsafe { ShowWindow(self.h_wnd.as_ptr(), n_cmd_show) != 0 }
    }

    pub fn update(&self) -> Result<(), ()> {
        if unsafe { UpdateWindow(self.h_wnd.as_ptr()) != 0 } {
            Ok(())
        } else {
            message_box("Cannot update window.", "Error", MB_ICONEXCLAMATION | MB_OK);
            Err(())
        }
    }

    pub fn run(self) -> WPARAM {
        let h_wnd = self.h_wnd;
        forget(self);
        let mut msg = MSG {
            hwnd: null_mut(),
            message: 0,
            wParam: 0,
            lParam: 0,
            time: 0,
            pt: POINT { x: 0, y: 0 }
        };
        unsafe {
            loop {
                let res = GetMessageW(&mut msg as *mut _, h_wnd.as_ptr(), 0, 0);
                if res == 0 { break }
                if res < 0 {
                    let error_code = GetLastError();
                    message_box(&format!("Application error ({}).", error_code), "Error", MB_ICONEXCLAMATION | MB_OK);
                    break;
                }
                TranslateMessage(&msg as *const _);
                DispatchMessageW(&msg as *const _);
            }
        }
        msg.wParam
    }

    pub fn destroy(mut self) {
        self.destroy_on_drop = true;
    }
}

pub struct WindowClass {
    h_instance: HINSTANCE,
    atom: ATOM
}

impl Drop for WindowClass {
    fn drop(&mut self) {
        unsafe {
            let ok = UnregisterClassW(self.atom as usize as *const _, self.h_instance);
            debug_assert!(ok != 0);
        }
    }
}

impl WindowClass {
    pub fn new(name: &str) -> Result<WindowClass, ()> {
        unsafe extern "system" fn wndproc(h_wnd: HWND, msg: UINT, w_param: WPARAM, l_param: LPARAM) -> LRESULT {
            if msg == WM_CREATE {
                let create_struct = l_param as *const CREATESTRUCTW;
                SetWindowLongPtrW(h_wnd, GWLP_USERDATA, (*create_struct).lpCreateParams as isize);
            }
            let window_proc = GetWindowLongPtrW(h_wnd, GWLP_USERDATA) as *mut &mut dyn WindowProc;
            let res = if window_proc.is_null() {
                None
            } else {
                let window = Window { h_wnd: NonNull::new_unchecked(h_wnd), destroy_on_drop: false, phantom: PhantomData };
                let res = (*window_proc)(window, msg, w_param, l_param);
                res
            }.unwrap_or_else(|| DefWindowProcW(h_wnd, msg, w_param, l_param));
            if msg == WM_DESTROY {
                Box::from_raw(window_proc);
                SetWindowLongPtrW(h_wnd, GWLP_USERDATA, 0);
            }
            res
        }

        unsafe {
            let h_instance = GetModuleHandleW(null());
            let w = WNDCLASSEXW {
                cbSize: size_of::<WNDCLASSEXW>() as u32,
                style: 0,
                cbClsExtra: 0,
                cbWndExtra: 0,
                hInstance: h_instance,
                hIcon: LoadIconW(null_mut(), IDI_APPLICATION),
                hCursor: LoadCursorW(null_mut(), IDI_APPLICATION),
                hIconSm: LoadIconW(null_mut(), IDI_APPLICATION),
                hbrBackground: (COLOR_WINDOW + 1) as HBRUSH,
                lpszMenuName: null(),
                lpszClassName: name.encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
                lpfnWndProc: Some(wndproc),
            };
            let atom = RegisterClassExW(&w as *const _);
            if atom == 0 {
                message_box("Cannot register window class.", "Error", MB_ICONEXCLAMATION | MB_OK);
                return Err(());
            }
            Ok(WindowClass { atom, h_instance })
        }
    }
}

pub fn message_box(message: &str, caption: &str, u_type: UINT) {
    unsafe { MessageBoxW(
        null_mut(),
        message.encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
        caption.encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
        u_type
    ); }
}
