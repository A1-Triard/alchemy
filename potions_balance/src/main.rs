#![windows_subsystem = "windows"]
#![feature(trait_alias)]

mod gui;

use winapi::shared::basetsd::INT_PTR;
use winapi::um::winuser::*;
use gui::*;

fn main() {
    let main_dialog_proc = &mut MainWindowProc;
    dialog_box(1, main_dialog_proc);
}

struct MainWindowProc;

impl WindowProc for MainWindowProc {
    fn wm_close(&mut self, window: Window) {
        window.destroy();
    }

    fn wm_command(&mut self, window: Window, command_id: u16) {
        if command_id as i32 == IDOK || command_id as i32 == IDCANCEL {
            window.end_dialog(command_id as INT_PTR);
        }
    }
}
