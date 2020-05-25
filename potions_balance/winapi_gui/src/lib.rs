#![deny(warnings)]

use std::marker::PhantomData;
use std::iter::once;
use std::mem::{size_of, forget};
use std::ptr::{null, null_mut, NonNull};
use winapi::shared::minwindef::*;
use winapi::shared::windef::*;
use winapi::um::winuser::*;
use winapi::um::libloaderapi::*;
use winapi::um::errhandlingapi::*;
use winapi::um::commdlg::*;
use winapi::shared::basetsd::*;
use std::os::raw::c_int;
use std::path::PathBuf;
use std::os::windows::ffi::{OsStringExt, OsStrExt};
use std::ffi::{OsStr, OsString};
use void::Void;
use std::fmt::{self, Display};
#[macro_use]
extern crate macro_attr;
#[macro_use]
extern crate enum_derive;
use either::{Either, Left, Right};

pub trait IsWindow {
    fn get_h_wnd(&self) -> NonNull<HWND__>;
}

pub struct Window<'a, DialogOk, DialogError> {
    h_wnd: NonNull<HWND__>,
    phantom: PhantomData<&'a (DialogOk, DialogError)>,
    destroy_on_drop: bool,
}

impl<'a, DialogOk, DialogError> IsWindow for Window<'a, DialogOk, DialogError> {
    fn get_h_wnd(&self) -> NonNull<HWND__> { self.h_wnd }
}

impl<'a, DialogOk, DialogError> Drop for Window<'a, DialogOk, DialogError> {
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
    type DialogOk;
    type DialogError;
    fn wm_create(&mut self, _window: Window<Self::DialogOk, Self::DialogError>, wm: &mut Wm) -> Result<(), Self::DialogError> { wm.handled = false; Ok(()) }
    fn wm_close(&mut self, _window: Window<Self::DialogOk, Self::DialogError>, wm: &mut Wm) { wm.handled = false; }
    fn wm_destroy(&mut self, wm: &mut WmDestroy) { wm.handled = false; }
    fn wm_init_dialog(&mut self, _window: Window<Self::DialogOk, Self::DialogError>, _wm: &mut WmInitDialog) -> Result<(), Self::DialogError> { Ok(()) }
    fn wm_command(&mut self, _window: Window<Self::DialogOk, Self::DialogError>, _command_id: u16, _notification_code: u16, wm: &mut Wm) -> Result<(), Self::DialogError> { wm.handled = false; Ok(()) }
    fn wm_timer(&mut self, _window: Window<Self::DialogOk, Self::DialogError>, _id: WPARAM) -> Result<(), Self::DialogError> { Ok(()) }
}

macro_attr! {
    #[derive(Ord, PartialOrd, Eq, PartialEq, Hash, Copy, Clone)]
    #[derive(Debug, EnumDisplay!)]
    pub enum WindowsCall {
        CreateWindowExW,
        GetMessageW,
        SetDlgItemTextW,
        SetFocus,
        PostMessageW,
        GetWindowRect,
        MoveWindow,
        RegisterClassExW,
    }
}

pub struct WindowsError {
    pub error_code: DWORD,
    pub call: WindowsCall,
}

impl Display for WindowsError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}: {}", self.call, self.error_code)
    }
}

impl<'a> Window<'a, Void, Void> {
    pub fn new(class: &'a WindowClass, name: &str, width: c_int, height: c_int, window_proc: &'a mut dyn WindowProc<DialogOk=Void, DialogError=Void>) -> Result<Window<'a, Void, Void>, WindowsError> {
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
            Err(WindowsError { call: WindowsCall::CreateWindowExW, error_code: unsafe { GetLastError() } })
        }
    }

    pub fn destroy(mut self) {
        self.destroy_on_drop = true;
    }
}

impl<'a, DialogOk, DialogError> Window<'a, DialogOk, DialogError> {
    pub fn show(&self, n_cmd_show: c_int) -> bool {
        unsafe { ShowWindow(self.h_wnd.as_ptr(), n_cmd_show) != 0 }
    }

    pub fn update(&self) {
        let ok = unsafe { UpdateWindow(self.h_wnd.as_ptr()) != 0 };
        debug_assert!(ok);
    }

    pub fn run(self) -> Result<WPARAM, WindowsError> {
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
                if res < 0 { return Err(WindowsError { call: WindowsCall::GetMessageW, error_code: GetLastError() }); }
                TranslateMessage(&msg as *const _);
                DispatchMessageW(&msg as *const _);
            }
        }
        Ok(msg.wParam)
    }

    pub fn end_dialog(self, result: Result<DialogOk, DialogError>) {
        let ok = unsafe { EndDialog(self.h_wnd.as_ptr(), Box::into_raw(Box::new(result)) as INT_PTR) != 0 };
        assert!(ok);
    }

    pub fn get_dialog_item(&self, item_id: u16) -> Option<impl AsRef<Window<Void, Void>>> {
        let h_wnd = NonNull::new(unsafe { GetDlgItem(self.h_wnd.as_ptr(), item_id as c_int) });
        h_wnd.map(|h_wnd| WindowAsRef(Window::<Void, Void> { h_wnd, destroy_on_drop: false, phantom: PhantomData }))
    }

    pub fn set_dialog_item_text_str(&self, item_id: u16, text: &str) -> Result<(), WindowsError> {
        let os_string = OsString::from_wide(&text.encode_utf16().collect::<Vec<_>>());
        self.set_dialog_item_text(item_id, &os_string)
    }
    
    pub fn set_dialog_item_text(&self, item_id: u16, text: &OsStr) -> Result<(), WindowsError> {
        let text = text.encode_wide().chain(once(0)).collect::<Vec<_>>().as_ptr();
        let ok = unsafe { SetDlgItemTextW(self.h_wnd.as_ptr(), item_id as c_int, text) != 0 };
        if ok { Ok(()) } else { Err(WindowsError { call: WindowsCall::SetDlgItemTextW, error_code: unsafe { GetLastError() } }) }
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

    pub fn set_focus(&self) -> Result<(), WindowsError> {
        let ok = unsafe { !SetFocus(self.h_wnd.as_ptr()).is_null() };
        if ok { Ok(()) } else { Err(WindowsError { call: WindowsCall::SetFocus, error_code: unsafe { GetLastError() } }) }
    }
    
    pub fn post_wm_command(&self, command_id: u16, notification_code: u16) -> Result<(), WindowsError> {
        let ok = unsafe { PostMessageW(self.h_wnd.as_ptr(), WM_COMMAND, (command_id as WPARAM) | ((notification_code as WPARAM) << 16), 0) != 0 };
        if ok { Ok(()) } else { Err(WindowsError { call: WindowsCall::PostMessageW, error_code: unsafe { GetLastError() } }) }
    }

    pub fn post_wm_user(&self, n: UINT) -> Result<(), WindowsError> {
        let ok = unsafe { PostMessageW(self.h_wnd.as_ptr(), WM_USER + n, 0, 0) != 0 };
        if ok { Ok(()) } else { Err(WindowsError { call: WindowsCall::PostMessageW, error_code: unsafe { GetLastError() } }) }
    }

    pub fn post_wm_timer(&self, id: WPARAM) -> Result<(), WindowsError> {
        let ok = unsafe { PostMessageW(self.h_wnd.as_ptr(), WM_TIMER, id, 0) != 0 };
        if ok { Ok(()) } else { Err(WindowsError { call: WindowsCall::PostMessageW, error_code: unsafe { GetLastError() } }) }
    }

    pub fn get_rect(&self) -> Result<RECT, WindowsError> {
        let mut rect = RECT { left: 0, top: 0, right: 0, bottom: 0 };
        let ok = unsafe { GetWindowRect(self.h_wnd.as_ptr(), &mut rect as *mut _) != 0 };
        if ok { Ok(rect) } else { Err(WindowsError { call: WindowsCall::GetWindowRect, error_code: unsafe { GetLastError() } }) }
    }

    pub fn move_(&self, x: c_int, y: c_int, width: c_int, height: c_int, repaint: bool) -> Result<(), WindowsError> {
        let ok = unsafe { MoveWindow(self.h_wnd.as_ptr(), x, y, width, height, if repaint { TRUE } else { FALSE }) != 0 };
        if ok { Ok(()) } else { Err(WindowsError { call: WindowsCall::MoveWindow, error_code: unsafe { GetLastError() } }) }
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

struct WindowAsRef<'a, DialogOk, DialogError>(Window<'a, DialogOk, DialogError>);

impl<'a, DialogOk, DialogError> AsRef<Window<'a, DialogOk, DialogError>> for WindowAsRef<'a, DialogOk, DialogError> {
    fn as_ref(&self) -> &Window<'a, DialogOk, DialogError> { &self.0 }
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

unsafe fn window_message<DialogOk, DialogError>(window_proc: &mut dyn WindowProc<DialogOk=DialogOk, DialogError=DialogError>, h_wnd: HWND, msg: UINT, w_param: WPARAM, _l_param: LPARAM) -> Either<bool, Option<LRESULT>> {
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
            let window: Window<DialogOk, DialogError> = Window { h_wnd: NonNull::new_unchecked(h_wnd), destroy_on_drop: false, phantom: PhantomData };
            window.end_dialog(Err(dialog_error));
        }
        result
    }
}

impl WindowClass {
    pub fn new(name: &str) -> Result<WindowClass, WindowsError> {
        unsafe extern "system" fn wndproc(h_wnd: HWND, msg: UINT, w_param: WPARAM, l_param: LPARAM) -> LRESULT {
            if msg == WM_CREATE {
                let create_struct = l_param as *const CREATESTRUCTW;
                SetWindowLongPtrW(h_wnd, GWLP_USERDATA, (*create_struct).lpCreateParams as _);
            }
            let window_proc = GetWindowLongPtrW(h_wnd, GWLP_USERDATA) as *mut &mut dyn WindowProc<DialogOk=Void, DialogError=Void>;
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
            if atom == 0 { return Err(WindowsError { call: WindowsCall::RegisterClassExW, error_code: GetLastError() }) }
            Ok(WindowClass { atom, h_instance })
        }
    }
}

pub fn message_box(owner: Option<&dyn IsWindow>, message: &str, caption: &str, u_type: UINT) {
    unsafe { MessageBoxW(
        owner.map_or(null_mut(), |x| x.get_h_wnd().as_ptr()),
        message.encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
        caption.encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr(),
        u_type
    ); }
}

pub fn dialog_box<DialogOk, DialogError>(parent: Option<&dyn IsWindow>, id: u16, window_proc: &mut dyn WindowProc<DialogOk=DialogOk, DialogError=DialogError>) -> Result<DialogOk, DialogError> {
    unsafe extern "system" fn dlgproc<DialogOk, DialogError>(h_wnd: HWND, msg: UINT, w_param: WPARAM, l_param: LPARAM) -> INT_PTR {
        if msg == WM_INITDIALOG {
            SetWindowLongPtrW(h_wnd, GWLP_USERDATA, l_param as _);
        }
        let window_proc = GetWindowLongPtrW(h_wnd, GWLP_USERDATA) as *mut &mut dyn WindowProc<DialogOk=DialogOk, DialogError=DialogError>;
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

pub fn get_open_file_name<'a, 'b>(owner: Option<&dyn IsWindow>, title: Option<&str>, filter: impl Iterator<Item=(&'a str, &'b str)>) -> Option<PathBuf> {
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
        lpstrTitle: title.map_or(null(), |x| x.encode_utf16().chain(once(0)).collect::<Vec<_>>().as_ptr()),
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
