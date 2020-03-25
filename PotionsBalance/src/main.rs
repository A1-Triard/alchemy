#![windows_subsystem = "windows"]
#![feature(trait_alias)]

mod gui;

use gui::*;
use std::iter::once;
use std::str::FromStr;
use winapi::um::winuser::*;
use std::ffi::OsString;

fn main() {
    let main_dialog_proc = &mut MainWindowProc { edit_original_value: None };
    dialog_box(1, main_dialog_proc);
}

static STANDARD: &'static [u16] = &[
    5, 15, 35, 80, 175,
    8, 15, 30, 45, 60,
    5, 8, 10, 15, 20,
    8, 15, 30, 45, 60,
    5, 8, 10, 15, 20,
    1, 2, 10, 20, 40,
    5, 15, 10, 15, 10
];

static RECOMMEND: &'static [u16] = &[
    20, 40, 80, 160, 320,
    20, 40, 80, 160, 320,
    10, 25, 45, 70, 100,
    20, 40, 80, 160, 320,
    10, 25, 45, 70, 100,
    5, 10, 17, 25, 40,
    5, 80, 45, 80, 45
];

struct MainWindowProc {
    edit_original_value: Option<OsString>,
}

impl WindowProc for MainWindowProc {
    fn wm_close(&mut self, window: Window) {
        window.destroy();
    }

    fn wm_init_dialog(&mut self, window: Window) {
        window.set_dialog_item_limit_text(132, 255);
        window.set_dialog_item_limit_text(134, 255);
        window.set_dialog_item_text_str(134, "PotionsBalance");
        for (i, v) in STANDARD.iter().enumerate() {
            window.set_dialog_item_limit_text(150 + i as u16, 3);
            window.set_dialog_item_text_str(150 + i as u16, &v.to_string());
        }
    }
    
    fn wm_command(&mut self, window: Window, command_id: u16, notification_code: u16) {
        match notification_code {
            EN_SETFOCUS => {
                debug_assert!(self.edit_original_value.is_none());
                self.edit_original_value = Some(window.get_dialog_item_text(command_id, 4));
            },
            EN_KILLFOCUS => {
                let edit_original_value = self.edit_original_value.take().unwrap();
                let edit_value = window.get_dialog_item_text(command_id, 4);
                let edit_value = edit_value.to_str().unwrap();
                if edit_value.is_empty() || u16::from_str(edit_value).unwrap() == 0 {
                    window.set_dialog_item_text(command_id, &edit_original_value);
                }
            },
            _ => match command_id {
                129 => {
                    for (i, v) in STANDARD.iter().enumerate() {
                        window.set_dialog_item_text_str(150 + i as u16, &v.to_string());
                    }
                },
                130 => {
                    for (i, v) in RECOMMEND.iter().enumerate() {
                        window.set_dialog_item_text_str(150 + i as u16, &v.to_string());
                    }
                },
                133 => {
                    if let Some(file) = get_open_file_name(Some(&window), Some("Morrowind.ini"), once(("Morrowind.ini", "Morrowind.ini"))) {
                        window.set_dialog_item_text(132, &file.parent().unwrap().as_os_str());
                    }
                },
                127 => {
                    let mw_path = window.get_dialog_item_text(132, 256);
                    let esp_name = window.get_dialog_item_text(134, 256);
                    let values = (0 .. STANDARD.len()).map(|i| u16::from_str(window.get_dialog_item_text(150 + i as u16, 4).to_str().unwrap()).unwrap()).collect::<Vec<_>>();
                },
                _ => { }
            }
        }
    }
}
