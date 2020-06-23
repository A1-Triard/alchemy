#![feature(never_type)]
#![deny(warnings)]

use std::marker::PhantomData;
use std::iter::once;
use std::mem::{size_of, forget};
use std::ptr::{null, null_mut, NonNull};
use winapi::shared::minwindef::*;
use winapi::shared::windef::*;
use winapi::um::winuser::*;
use winapi::um::libloaderapi::*;
use winapi::um::commdlg::*;
use winapi::shared::basetsd::*;
use std::os::raw::c_int;
use std::path::PathBuf;
use std::os::windows::ffi::{OsStringExt, OsStrExt};
use std::ffi::{OsStr, OsString};
use either::{Either, Left, Right};
use winapi::um::libloaderapi::LoadStringW;
use winapi::um::winnt::LPWSTR;
use std::slice::{self};
use std::io::{self};

pub trait IsWindow {
    fn get_h_wnd(&self) -> NonNull<HWND__>;
}

pub trait DialogResult {
    type Error;
}

impl<DialogOk, DialogError> DialogResult for Result<DialogOk, DialogError> {
    type Error = DialogError;
}

impl DialogResult for ! {
    type Error = !;
}

pub struct Window<'a, DialogResult> {
    h_wnd: NonNull<HWND__>,
    phantom: PhantomData<&'a DialogResult>,
    destroy_on_drop: bool,
}

impl<'a, DialogResult> IsWindow for Window<'a, DialogResult> {
    fn get_h_wnd(&self) -> NonNull<HWND__> { self.h_wnd }
}

impl<'a, DialogResult> Drop for Window<'a, DialogResult> {
    fn drop(&mut self) {
        if self.destroy_on_drop {
            unsafe {
                let ok = DestroyWindow(self.h_wnd.as_ptr());
                debug_assert!(ok != 0);
            }
        }
    }
}

pub struct Wm {
    pub handled: bool
}

pub struct WmDestroy {
    pub handled: bool,
    pub post_quit_message: bool
}

pub struct WmInitDialog {
    pub set_keyboard_focus: bool
}

pub trait WindowProc {
    type DialogResult: DialogResult;
    fn wm_create(&mut self, _window: Window<Self::DialogResult>, wm: &mut Wm) -> Result<(), <Self::DialogResult as DialogResult>::Error> { wm.handled = false; Ok(()) }
    fn wm_close(&mut self, _window: Window<Self::DialogResult>, wm: &mut Wm) { wm.handled = false; }
    fn wm_destroy(&mut self, wm: &mut WmDestroy) { wm.handled = false; }
    fn wm_init_dialog(&mut self, _window: Window<Self::DialogResult>, _wm: &mut WmInitDialog) -> Result<(), <Self::DialogResult as DialogResult>::Error> { Ok(()) }
    fn wm_command(&mut self, _window: Window<Self::DialogResult>, _command_id: u16, _notification_code: u16, wm: &mut Wm) -> Result<(), <Self::DialogResult as DialogResult>::Error> { wm.handled = false; Ok(()) }
    fn wm_timer(&mut self, _window: Window<Self::DialogResult>, _id: WPARAM) -> Result<(), <Self::DialogResult as DialogResult>::Error> { Ok(()) }
}

impl<'a> Window<'a, !> {
    pub fn new(class: &'a WindowClass, name: impl AsRef<str>, width: c_int, height: c_int, window_proc: &'a mut dyn WindowProc<DialogResult=!>) -> io::Result<Window<'a, !>> {
        let h_wnd = NonNull::new(unsafe {
            CreateWindowExW(
                WS_EX_CLIENTEDGE,
                class.atom as *const _,
                name.as_ref().encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
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
            Err(io::Error::last_os_error())
        }
    }

    pub fn destroy(mut self) {
        self.destroy_on_drop = true;
    }

    pub fn run(self) -> io::Result<WPARAM> {
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
                if res < 0 { return Err(io::Error::last_os_error()); }
                TranslateMessage(&msg as *const _);
                DispatchMessageW(&msg as *const _);
            }
        }
        Ok(msg.wParam)
    }
}

impl<'a, DialogOk, DialogError> Window<'a, Result<DialogOk, DialogError>> {
    pub fn end_dialog(self, result: Result<DialogOk, DialogError>) {
        let ok = unsafe { EndDialog(self.h_wnd.as_ptr(), Box::into_raw(Box::new(result)) as INT_PTR) != 0 };
        assert!(ok);
    }
}

impl<'a, DialogResult> Window<'a, DialogResult> {
    pub fn show(&self, n_cmd_show: c_int) -> bool {
        unsafe { ShowWindow(self.h_wnd.as_ptr(), n_cmd_show) != 0 }
    }

    pub fn update(&self) {
        let ok = unsafe { UpdateWindow(self.h_wnd.as_ptr()) != 0 };
        debug_assert!(ok);
    }

    pub fn get_dialog_item(&self, item_id: u16) -> Option<impl AsRef<Window<!>>> {
        let h_wnd = NonNull::new(unsafe { GetDlgItem(self.h_wnd.as_ptr(), item_id as c_int) });
        h_wnd.map(|h_wnd| WindowAsRef(Window::<!> { h_wnd, destroy_on_drop: false, phantom: PhantomData }))
    }

    pub fn set_dialog_item_text_str(&self, item_id: u16, text: &str) -> io::Result<()> {
        let os_string = OsString::from_wide(&text.encode_utf16().collect::<Vec<_>>());
        self.set_dialog_item_text(item_id, &os_string)
    }
    
    pub fn set_dialog_item_text(&self, item_id: u16, text: &OsStr) -> io::Result<()> {
        let text = text.encode_wide().chain(once(0)).collect::<Vec<_>>().as_ptr();
        let ok = unsafe { SetDlgItemTextW(self.h_wnd.as_ptr(), item_id as c_int, text) != 0 };
        if ok { Ok(()) } else { Err(io::Error::last_os_error()) }
    }
    
    pub fn get_dialog_item_text(&self, item_id: u16, max_len: u16) -> OsString {
        let mut text = Vec::with_capacity(max_len as usize);
        text.resize(max_len as usize, 0);
        let res = unsafe { GetDlgItemTextW(self.h_wnd.as_ptr(), item_id as c_int, text.as_mut_ptr(), text.len() as i32) };
        OsString::from_wide(&text[..res as usize])
    }

    pub fn set_dialog_item_limit_text(&self, item_id: u16, limit: u16) {
        unsafe { SendDlgItemMessageW(self.h_wnd.as_ptr(), item_id as c_int, EM_LIMITTEXT as u32, limit as usize, 0); }
    }

    pub fn set_focus(&self) -> io::Result<()> {
        let ok = unsafe { !SetFocus(self.h_wnd.as_ptr()).is_null() };
        if ok { Ok(()) } else { Err(io::Error::last_os_error()) }
    }
    
    pub fn post_wm_command(&self, command_id: u16, notification_code: u16) -> io::Result<()> {
        let ok = unsafe { PostMessageW(self.h_wnd.as_ptr(), WM_COMMAND, (command_id as WPARAM) | ((notification_code as WPARAM) << 16), 0) != 0 };
        if ok { Ok(()) } else { Err(io::Error::last_os_error()) }
    }

    pub fn post_wm_timer(&self, id: WPARAM) -> io::Result<()> {
        let ok = unsafe { PostMessageW(self.h_wnd.as_ptr(), WM_TIMER, id, 0) != 0 };
        if ok { Ok(()) } else { Err(io::Error::last_os_error()) }
    }

    pub fn get_rect(&self) -> io::Result<RECT> {
        let mut rect = RECT { left: 0, top: 0, right: 0, bottom: 0 };
        let ok = unsafe { GetWindowRect(self.h_wnd.as_ptr(), &mut rect as *mut _) != 0 };
        if ok { Ok(rect) } else { Err(io::Error::last_os_error()) }
    }

    pub fn move_(&self, x: c_int, y: c_int, width: c_int, height: c_int, repaint: bool) -> io::Result<()> {
        let ok = unsafe { MoveWindow(self.h_wnd.as_ptr(), x, y, width, height, if repaint { TRUE } else { FALSE }) != 0 };
        if ok { Ok(()) } else { Err(io::Error::last_os_error()) }
    }
}

pub struct Monitor {
    pub h_monitor: NonNull<HMONITOR__>
}

impl Monitor {
    pub fn from_window(window: &dyn IsWindow, flags: DWORD) -> Monitor {
        let h_monitor = NonNull::new(unsafe { MonitorFromWindow(window.get_h_wnd().as_ptr(), flags) }).unwrap();
        Monitor { h_monitor }
    }
    
    pub fn get_info(&self) -> MONITORINFO {
        let mut info = MONITORINFO {
            cbSize: size_of::<MONITORINFO>() as u32,
            rcMonitor: RECT { left: 0, top: 0, right: 0, bottom: 0 },
            rcWork: RECT { left: 0, top: 0, right: 0, bottom: 0 },
            dwFlags: 0
        };
        let ok = unsafe { GetMonitorInfoW(self.h_monitor.as_ptr(), &mut info as *mut _) != 0 };
        assert!(ok);
        info
    }
}

struct WindowAsRef<'a, DialogResult>(Window<'a, DialogResult>);

impl<'a, DialogResult> AsRef<Window<'a, DialogResult>> for WindowAsRef<'a, DialogResult> {
    fn as_ref(&self) -> &Window<'a, DialogResult> { &self.0 }
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

unsafe fn window_message<DialogResult: crate::DialogResult>(window_proc: &mut dyn WindowProc<DialogResult=DialogResult>, h_wnd: HWND, msg: UINT, w_param: WPARAM, _l_param: LPARAM) -> Either<bool, Option<LRESULT>> {
    if msg == WM_DESTROY {
        let mut wm = WmDestroy { post_quit_message: false, handled: true };
        window_proc.wm_destroy(&mut wm);
        if wm.post_quit_message {
            PostQuitMessage(0);
        }
        if wm.handled { Right(Some(0)) } else { Right(None) }
    } else {
        let window = Window { h_wnd: NonNull::new_unchecked(h_wnd), destroy_on_drop: false, phantom: PhantomData };
        let (result, dialog_error) = if msg == WM_INITDIALOG {
            let mut wm = WmInitDialog { set_keyboard_focus: true };
            let dialog_error = window_proc.wm_init_dialog(window, &mut wm).err();
            (Left(wm.set_keyboard_focus), dialog_error)
        } else {
            let mut wm = Wm { handled: true };
            let (result, dialog_error) = match msg {
                WM_CREATE => window_proc.wm_create(window, &mut wm).err().map_or((Right(0), None), |d| (Right(-1), Some(d))),
                WM_CLOSE => { window_proc.wm_close(window, &mut wm); (Right(0), None) },
                WM_COMMAND => (Right(0), window_proc.wm_command(window, (w_param & 0xFFFF) as u16, ((w_param >> 16) & 0xFFFF) as u16, &mut wm).err()),
                WM_TIMER => (Right(0), window_proc.wm_timer(window, w_param).err()),
                _ => { wm.handled = false; (Right(0), None) }
            };
            (if wm.handled { result.map_right(Some) } else { Right(None) }, dialog_error)
        };
        if let Some(dialog_error) = dialog_error {
            let window: Window<Result<!, DialogResult::Error>> = Window { h_wnd: NonNull::new_unchecked(h_wnd), destroy_on_drop: false, phantom: PhantomData };
            window.end_dialog(Err(dialog_error));
        }
        result
    }
}

impl WindowClass {
    pub fn new(name: &str) -> io::Result<WindowClass> {
        unsafe extern "system" fn wndproc(h_wnd: HWND, msg: UINT, w_param: WPARAM, l_param: LPARAM) -> LRESULT {
            if msg == WM_CREATE {
                let create_struct = l_param as *const CREATESTRUCTW;
                SetWindowLongPtrW(h_wnd, GWLP_USERDATA, (*create_struct).lpCreateParams as _);
            }
            let window_proc = GetWindowLongPtrW(h_wnd, GWLP_USERDATA) as *mut &mut dyn WindowProc<DialogResult=!>;
            let result = if !window_proc.is_null() {
                window_message(*window_proc, h_wnd, msg, w_param, l_param).right_or_else(|x| Some(if x { TRUE } else { FALSE } as LRESULT))
            } else {
                None
            };
            let result = result.unwrap_or_else(|| DefWindowProcW(h_wnd, msg, w_param, l_param));
            if msg == WM_DESTROY {
                Box::from_raw(window_proc);
                SetWindowLongPtrW(h_wnd, GWLP_USERDATA, 0);
            }
            result
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
            if atom == 0 { return Err(io::Error::last_os_error()) }
            Ok(WindowClass { atom, h_instance })
        }
    }
}

pub fn message_box(owner: Option<&dyn IsWindow>, message: impl AsRef<str>, caption: impl AsRef<str>, u_type: UINT) {
    unsafe { MessageBoxW(
        owner.map_or(null_mut(), |x| x.get_h_wnd().as_ptr()),
        message.as_ref().encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
        caption.as_ref().encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
        u_type
    ); }
}

pub fn dialog_box<DialogOk, DialogError>(parent: Option<&dyn IsWindow>, id: u16, window_proc: &mut dyn WindowProc<DialogResult=Result<DialogOk, DialogError>>) -> Result<DialogOk, DialogError> {
    unsafe extern "system" fn dlgproc<DialogOk, DialogError>(h_wnd: HWND, msg: UINT, w_param: WPARAM, l_param: LPARAM) -> INT_PTR {
        if msg == WM_INITDIALOG {
            SetWindowLongPtrW(h_wnd, GWLP_USERDATA, l_param as _);
        }
        let window_proc = GetWindowLongPtrW(h_wnd, GWLP_USERDATA) as *mut &mut dyn WindowProc<DialogResult=Result<DialogOk, DialogError>>;
        let result = !window_proc.is_null() &&
            window_message(*window_proc, h_wnd, msg, w_param, l_param).left_or_else(|x| x.is_some());
        if msg == WM_DESTROY {
            Box::from_raw(window_proc);
            SetWindowLongPtrW(h_wnd, GWLP_USERDATA, 0);
        }
        (if result { TRUE } else { FALSE }) as INT_PTR
    }
    
    unsafe {
        *Box::from_raw(DialogBoxParamW(null_mut(), id as usize as *const _, parent.map_or(null_mut(), |x| x.get_h_wnd().as_ptr()), Some(dlgproc::<DialogOk, DialogError>), Box::into_raw(Box::new(window_proc)) as LPARAM) as *mut _)
    }
}

pub fn get_open_file_name<'a, 'b, T: AsRef<str>>(owner: Option<&dyn IsWindow>, title: Option<T>, filter: impl Iterator<Item=(&'a str, &'b str)>) -> Option<PathBuf> {
    let filter = filter
        .flat_map(|(x, y)| once(x).chain(once(y)))
        .flat_map(|x| x.encode_utf16().map(|x| { assert_ne!(x, 0); x }).chain(once(0)))
        .chain(once(0))
        .collect::<Vec<_>>();
    let mut file = Vec::with_capacity(256);
    file.resize(256, 0);
    let mut args = OPENFILENAMEW {
        lStructSize: size_of::<OPENFILENAMEW>() as u32,
        hwndOwner: owner.map_or(null_mut(), |x| x.get_h_wnd().as_ptr()),
        hInstance: null_mut(),
        lpstrFilter: filter.as_ptr(),
        lpstrCustomFilter: null_mut(),
        nMaxCustFilter: 0,
        nFilterIndex: 0,
        lpstrFile: file.as_mut_ptr(),
        nMaxFile: file.len() as u32,
        lpstrFileTitle: null_mut(),
        nMaxFileTitle: 0,
        lpstrInitialDir: null(),
        lpstrTitle: title.map_or(null(), |x| x.as_ref().encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr()),
        Flags: OFN_DONTADDTORECENT | OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST | OFN_LONGNAMES,
        nFileOffset: 0,
        nFileExtension: 0,
        lpstrDefExt: null(),
        lCustData: 0,
        lpfnHook: None,
        lpTemplateName: null(),
        pvReserved: null_mut(),
        dwReserved: 0,
        FlagsEx: 0
    };

    let selected = unsafe { GetOpenFileNameW(&mut args as *mut _) != 0 };
    if selected {
        Some(OsString::from_wide(&file).into())
    } else {
        None
    }
}

pub fn load_string(id: UINT) -> io::Result<String> {
    let h_instance = unsafe { GetModuleHandleW(null()) };
    let mut ptr: LPWSTR = null_mut();
    let len = unsafe { LoadStringW(h_instance, id, &mut ptr as *mut _ as LPWSTR, 0) };
    if len < 0 { return Err(io::Error::last_os_error()) }
    if len == 0 { return Ok(String::new()) }
    let resource = unsafe { slice::from_raw_parts(ptr, len as usize) };
    let resource = if let Some(end) = resource.iter().position(|&x| x == 0) {
        &resource[.. end]
    } else {
        resource
    };
    String::from_utf16(resource).map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))
}
