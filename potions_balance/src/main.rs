#![windows_subsystem = "windows"]
#![feature(trait_alias)]

mod gui;

use winapi::shared::basetsd::INT_PTR;
use winapi::um::winuser::*;
use gui::*;

fn main() -> Result<(), ()> {
    let main_dialog_proc = &mut MainDialogProc;
    dialog_box(1, main_dialog_proc);
    let class = WindowClass::new("POTIONS_BALANCE")?;
    let main_window_proc = &mut MainWindowProc;
    let window = Window::new(&class, "Баланс зелий", 640, 480, main_window_proc)?;
    window.show(SW_SHOW);
    window.update()?;
    std::process::exit(window.run() as i32)
}

struct MainDialogProc;

impl WindowProc for MainDialogProc {
    fn wm_command(&mut self, window: Window, command_id: u16) {
        if command_id as i32 == IDOK || command_id as i32 == IDCANCEL {
            window.end_dialog(command_id as INT_PTR);
        }
    }
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
