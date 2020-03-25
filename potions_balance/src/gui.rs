use std::marker::PhantomData;
use std::iter::once;
use std::mem::{size_of, forget};
use std::ptr::{null, null_mut, NonNull};
use winapi::shared::minwindef::*;
use winapi::shared::windef::*;
use winapi::um::winuser::*;
use winapi::um::libloaderapi::*;
use winapi::um::errhandlingapi::*;
use winapi::shared::basetsd::*;
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

pub struct WmDestroy {
    pub post_quit_message: bool
}

pub trait WindowProc {
    fn wm_close(&mut self, _window: Window) { }
    fn wm_destroy(&mut self, _wm: &mut WmDestroy) { }
    fn wm_init_dialog(&mut self, __window: Window) { }
    fn wm_command(&mut self, __window: Window, _command_id: u16) { }
}

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
    
    pub fn end_dialog(self, result: INT_PTR) {
        let ok = unsafe { EndDialog(self.h_wnd.as_ptr(), result) != 0 };
        debug_assert!(ok);
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

unsafe fn window_message(window_proc: &mut dyn WindowProc, h_wnd: HWND, msg: UINT, w_param: WPARAM, _l_param: LPARAM) -> bool {
    if msg == WM_DESTROY {
        let mut wm = WmDestroy { post_quit_message: false };
        window_proc.wm_destroy(&mut wm);
        if wm.post_quit_message {
            PostQuitMessage(0);
        }
        true
    } else {
        let window = Window { h_wnd: NonNull::new_unchecked(h_wnd), destroy_on_drop: false, phantom: PhantomData };
        match msg {
            WM_CLOSE => {
                window_proc.wm_close(window);
                true
            },
            WM_COMMAND => {
                window_proc.wm_command(window, (w_param & 0xFFFF) as u16);
                true
            },
            WM_INITDIALOG => {
                window_proc.wm_init_dialog(window);
                true
            },
            _ => false
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
            let res = if !window_proc.is_null() && window_message(*window_proc, h_wnd, msg, w_param, l_param) { 
                0
            } else {
                DefWindowProcW(h_wnd, msg, w_param, l_param)
            };
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

pub fn dialog_box(id: u16, window_proc: &mut dyn WindowProc) -> INT_PTR {
    unsafe extern "system" fn dlgproc(h_wnd: HWND, msg: UINT, w_param: WPARAM, l_param: LPARAM) -> INT_PTR {
        if msg == WM_INITDIALOG {
            SetWindowLongPtrW(h_wnd, GWLP_USERDATA, l_param);
        }
        let window_proc = GetWindowLongPtrW(h_wnd, GWLP_USERDATA) as *mut &mut dyn WindowProc;
        let res = if !window_proc.is_null() && window_message(*window_proc, h_wnd, msg, w_param, l_param) { 
            TRUE
        } else {
            FALSE
        };
        if msg == WM_DESTROY {
            Box::from_raw(window_proc);
            SetWindowLongPtrW(h_wnd, GWLP_USERDATA, 0);
        }
        res as INT_PTR
    }
    unsafe {
        DialogBoxParamW(null_mut(), id as usize as *const _, null_mut(), Some(dlgproc), Box::into_raw(Box::new(window_proc)) as LPARAM)
    }
}
