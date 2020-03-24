#![windows_subsystem = "windows"]
#![feature(trait_alias)]

mod gui;

use winapi::shared::minwindef::*;
use winapi::um::winuser::*;
use gui::*;

fn main() -> Result<(), ()> {
    let class = WindowClass::new("POTIONS_BALANCE")?;
    let wndproc = &mut wndproc;
    let window = Window::new(&class, "Баланс зелий", 640, 480, wndproc)?;
    window.show(SW_SHOW);
    window.update()?;
    std::process::exit(window.run() as i32)
}

fn wndproc(window: Window, msg: UINT, _w_param: WPARAM, _l_param: LPARAM) -> Option<LRESULT> {
    match msg {
        WM_CLOSE => {
            window.destroy();
            Some(0)
        },
        WM_DESTROY => {
            unsafe { PostQuitMessage(0) };
            Some(0)
        },
        _ => None
    }
}
