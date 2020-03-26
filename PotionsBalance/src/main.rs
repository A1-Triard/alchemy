#![windows_subsystem = "windows"]
#![feature(trait_alias)]

mod gui;

use gui::*;
use std::iter::once;
use std::str::FromStr;
use winapi::um::winuser::*;
use std::ffi::OsString;
use std::path::{Path, PathBuf};
use ini::Ini;
use std::fs::{self, File};
use filetime::FileTime;
use std::io::Read;
use encoding::all::WINDOWS_1251;
use encoding::Encoding;
use encoding::DecoderTrap;
use esl::{ALCH};
use esl::read::{Records, RecordReadMode};
use esl::code::CodePage;
use either::{Right, Left};

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
                    if mw_path.is_empty() {
                        message_box(Some(&window), "Необходимо указать расположение папки с игрой.", "Ошибка", MB_ICONWARNING | MB_OK);
                        window.get_dialog_item(132).unwrap().as_ref().set_focus();
                    } else {
                        let mw_path = PathBuf::from(mw_path);
                        let esp_name = window.get_dialog_item_text(134, 256);
                        let values = (0..STANDARD.len()).map(|i| u16::from_str(window.get_dialog_item_text(150 + i as u16, 4).to_str().unwrap()).unwrap()).collect::<Vec<_>>();
                        if let Err(e) = generate_plugin(&mw_path, &esp_name, &values) {
                            message_box(Some(&window), &e, "Ошибка", MB_ICONERROR | MB_OK);
                        } else {
                            message_box(Some(&window), &format!("Плагин {}.esp готов к использованию.", esp_name.to_string_lossy()), "Сделано", MB_ICONINFORMATION | MB_OK);
                        }
                    }
                },
                _ => { }
            }
        }
    }
}

fn generate_plugin(mw_path: &Path, esp_name: &OsString, values: &[u16]) -> Result<(), String> {
    let mut ini = Vec::new();
    File::open(mw_path.join("Morrowind.ini").as_path()).and_then(|mut x| x.read_to_end(&mut ini)).map_err(|x| x.to_string())?;
    let ini = WINDOWS_1251.decode(&ini, DecoderTrap::Strict).map_err(|x| x.to_string())?;
    let ini = Ini::load_from_str(&ini).map_err(|x| x.to_string())?;
    let game_files_section = ini.section(Some("Game Files")).ok_or("В Morrowind.ini отсутствует секция [Game Files].")?;
    let mut game_files = Vec::with_capacity(game_files_section.len());
    for (_, name) in game_files_section.iter() {
        let path = mw_path.join("Data Files").join(name);
        let metadata = fs::metadata(path.as_path()).map_err(|x| x.to_string())?;
        let time = FileTime::from_last_modification_time(&metadata);
        game_files.push((name, path, time));
    }
    game_files.sort_by_key(|x| x.2);
    for (game_file_name, game_file_path, _) in game_files.into_iter() {
        for record in Records::new(CodePage::Russian, RecordReadMode::Lenient, 0, &mut File::open(game_file_path).map_err(|x| x.to_string())?) {
            let record = match record {
                Err(error) => match error.source() {
                    Right(error) => return Err(format!("{}: {}", game_file_name, error)),
                    Left(error) => if error.record_tag() == ALCH {
                        return Err(format!("{}: {}", game_file_name, error));
                    } else {
                        continue;
                    }
                },
                Ok(record) => record
            };
        }
    }
    Ok(())
}