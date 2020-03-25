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

static STANDARD: &'static [u16] = &[
    5, 15, 35, 80, 175,
    8, 15, 30, 45, 60,
    5, 8, 10, 15, 20,
    8, 15, 30, 45, 60,
    5, 8, 10, 15, 20,
    1, 2, 10, 20, 40,
    5
];

static RECOMMEND: &'static [u16] = &[
    20, 40, 80, 160, 320,
    20, 40, 80, 160, 320,
    10, 25, 45, 70, 100,
    20, 40, 80, 160, 320,
    10, 25, 45, 70, 100,
    5, 10, 17, 25, 40,
    5
];

struct MainWindowProc;

impl WindowProc for MainWindowProc {
    fn wm_close(&mut self, window: Window) {
        window.destroy();
    }

    fn wm_init_dialog(&mut self, window: Window) {
        window.set_dialog_item_text(134, "PotionsBalance");
        for (i, v) in STANDARD.iter().enumerate() {
            window.set_dialog_item_text(150 + i as u16, &v.to_string());
        }
    }
    fn wm_command(&mut self, window: Window, command_id: u16) {
        match command_id {
            129 => {
                for (i, v) in STANDARD.iter().enumerate() {
                    window.set_dialog_item_text(150 + i as u16, &v.to_string());
                }
            },
            130 => {
                for (i, v) in RECOMMEND.iter().enumerate() {
                    window.set_dialog_item_text(150 + i as u16, &v.to_string());
                }
            }
            _ => { }
        }
    }
}
