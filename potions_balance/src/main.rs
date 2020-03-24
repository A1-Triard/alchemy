#![windows_subsystem = "windows"]
#![feature(trait_alias)]

mod gui;

use winapi::um::winuser::*;
use gui::*;

fn main() -> Result<(), ()> {
    let class = WindowClass::new("POTIONS_BALANCE")?;
    let main_window_proc = &mut MainWindowProc;
    let window = Window::new(&class, "Баланс зелий", 640, 480, main_window_proc)?;
    window.show(SW_SHOW);
    window.update()?;
    std::process::exit(window.run() as i32)
}

struct MainWindowProc;

impl WindowProc for MainWindowProc {
    fn wm_close(&mut self, window: Window) {
        window.destroy();
    }

    fn wm_destroy(&mut self, wm: &mut WmDestroy) { 
        wm.post_quit_message = true;
    }
}
