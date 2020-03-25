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
        match command_id {
            129 => {
                window.set_dialog_item_text(150, "5");
                window.set_dialog_item_text(151, "15");
                window.set_dialog_item_text(152, "35");
                window.set_dialog_item_text(153, "80");
                window.set_dialog_item_text(154, "175");
                window.set_dialog_item_text(160, "8");
                window.set_dialog_item_text(165, "5");
                window.set_dialog_item_text(161, "15");
                window.set_dialog_item_text(166, "8");
                window.set_dialog_item_text(162, "30");
                window.set_dialog_item_text(167, "10");
                window.set_dialog_item_text(163, "45");
                window.set_dialog_item_text(168, "15");
                window.set_dialog_item_text(164, "60");
                window.set_dialog_item_text(169, "20");
                window.set_dialog_item_text(170, "8");
                window.set_dialog_item_text(171, "15");
                window.set_dialog_item_text(172, "30");
                window.set_dialog_item_text(173, "45");
                window.set_dialog_item_text(174, "60");
                window.set_dialog_item_text(180, "5");
                window.set_dialog_item_text(181, "8");
                window.set_dialog_item_text(182, "10");
                window.set_dialog_item_text(183, "15");
                window.set_dialog_item_text(184, "20");
            },
            130 => {
                window.set_dialog_item_text(150, "20");
                window.set_dialog_item_text(151, "40");
                window.set_dialog_item_text(152, "80");
                window.set_dialog_item_text(153, "160");
                window.set_dialog_item_text(154, "320");
                window.set_dialog_item_text(160, "20");
                window.set_dialog_item_text(165, "10");
                window.set_dialog_item_text(161, "40");
                window.set_dialog_item_text(166, "25");
                window.set_dialog_item_text(162, "80");
                window.set_dialog_item_text(167, "45");
                window.set_dialog_item_text(163, "160");
                window.set_dialog_item_text(168, "70");
                window.set_dialog_item_text(164, "320");
                window.set_dialog_item_text(169, "100");
                window.set_dialog_item_text(170, "20");
                window.set_dialog_item_text(171, "40");
                window.set_dialog_item_text(172, "80");
                window.set_dialog_item_text(173, "160");
                window.set_dialog_item_text(174, "320");
                window.set_dialog_item_text(180, "10");
                window.set_dialog_item_text(181, "25");
                window.set_dialog_item_text(182, "45");
                window.set_dialog_item_text(183, "70");
                window.set_dialog_item_text(184, "100");
            }
            _ => { }
        }
    }
}
