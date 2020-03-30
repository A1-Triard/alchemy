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
use filetime::{FileTime, set_file_mtime};
use std::io::{Read, BufWriter};
use encoding::all::WINDOWS_1251;
use encoding::Encoding;
use encoding::DecoderTrap;
use esl::{ALCH, Record, ENAM, NAME, Field, ALDT, FileMetadata, RecordFlags, FileType, TES3, HEDR, EffectIndex};
use esl::read::{Records, RecordReadMode};
use esl::code::{self, CodePage};
use either::{Right, Left};
use std::collections::{HashSet, HashMap};

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
    5, 15, 10, 15, 10,
    200, 1, 1
];

static RECOMMEND: &'static [u16] = &[
    20, 40, 80, 160, 320,
    20, 40, 80, 160, 320,
    10, 25, 45, 70, 100,
    20, 40, 80, 160, 320,
    10, 25, 45, 70, 100,
    5, 10, 17, 25, 40,
    5, 80, 45, 80, 45,
    125, 4, 5
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
        }
        window.post_wm_command(129, 0);
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
                if edit_value.is_empty() || command_id != 185 && command_id != 186 && u16::from_str(edit_value).unwrap() == 0 {
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

#[derive(Debug, Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
enum PotionLevel {
    Bargain = 0,
    Cheap = 1,
    Standard = 2,
    Quality = 3,
    Exclusive = 4
}

fn potion_level_kind(id: &str, record: &Record) -> Option<(PotionLevel,  String)> {
    let mut effects = record.fields.iter().filter(|(tag, _)| *tag == ENAM);
    let effect = if let Some((_, effect)) = effects.next() {
        effect
    } else {
        return None;
    };
    if effects.next().is_some() { return None; }
    if id.starts_with("P_") {
        if id.ends_with("_B") {
            Some((PotionLevel::Bargain, id[2 .. id.len() - 2].replace(' ', "_")))
        } else if id.ends_with("_C") {
            Some((PotionLevel::Cheap, id[2 .. id.len() - 2].replace(' ', "_")))
        } else if id.ends_with("_S") {
            Some((PotionLevel::Standard, id[2 .. id.len() - 2].replace(' ', "_")))
        } else if id.ends_with("_Q") {
            Some((PotionLevel::Quality, id[2 .. id.len() - 2].replace(' ', "_")))
        } else if id.ends_with("_E") {
            Some((PotionLevel::Exclusive, id[2 .. id.len() - 2].replace(' ', "_")))
        } else {
            None
        }
    } else {
        None
    }
}

fn potion_value(record: &Record) -> Result<u32, String> {
    let data = record.fields.iter().filter(|(tag, _)| *tag == ALDT).nth(0).ok_or_else(|| "Невалидное зелье.")?;
    if let Field::Potion(data) = &data.1 {
        Ok(data.value)
    } else {
        panic!()
    }
}

fn potion_effect(record: &Record) -> Result<EffectIndex, String> {
    let data = record.fields.iter().filter(|(tag, _)| *tag == ENAM).nth(0).unwrap();
    if let Field::Effect(data) = &data.1 {
        data.index.right().ok_or_else(|| "Невалидное зелье.".into())
    } else {
        panic!()
    }
}

fn generate_plugin(mw_path: &Path, esp_name: &OsString, values: &[u16]) -> Result<(), String> {
    let (potions, file_time) = collect_potions(mw_path)?;
    let (potions_by_kind, standard_only_potions, _) = classify_potions(potions)?;
    let level_values = find_level_values(&potions_by_kind)?;
    let mut records = Vec::new();
    records.push(Record {
        tag: TES3,
        flags: RecordFlags::empty(),
        fields: vec![
            (HEDR, Field::FileMetadata(FileMetadata {
                version: 1067869798,
                file_type: FileType::ESP,
                author: "PotionsBalance.exe".to_string(),
                description: vec!["Баланс зелий.".to_string(), format!("{:?}", values)],
                records: 0
            }))
        ]
    });
    for (_, mut potion) in standard_only_potions.into_iter() {
        if set_potion(&mut potion, &level_values, values, None)? {
            records.push(potion);
        }
    }
    for (_, potions) in potions_by_kind.into_iter() {
        for (level, (_, mut potion)) in potions.to_vec().into_iter().enumerate().filter_map(|(i, x)| x.map(|u| (i, u))) {
            if set_potion(&mut potion, &level_values, values, Some(level as u8))? {
                records.push(potion);
            }
        }
    }
    let records_count = (records.len() - 1) as u32;
    if let Field::FileMetadata(f) = &mut records[0].fields[0].1 {
        f.records = records_count;
    } else {
        panic!()
    }
    let esp_path = mw_path.join("Data Files").join(esp_name).with_extension("esp");
    {
        let mut esp = BufWriter::new(File::create(&esp_path).map_err(|e| e.to_string())?);
        code::serialize_into(&records, &mut esp, CodePage::Russian, true).map_err(|e| e.to_string())?;
    }
    set_file_mtime(&esp_path, FileTime::from_unix_time(file_time.unix_seconds() + 120, 0)).map_err(|e| e.to_string())?;
    Ok(())
}

#[derive(Debug, Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
enum EffectAttributes {
    None,
    Duration,
    Magnitude,
    DurationAndMagnitude,
    CommonDurationAndMagnitude,
}

fn effect_attributes(effect: EffectIndex) -> EffectAttributes {
    match effect {
        EffectIndex::WaterBreathing => EffectAttributes::Duration,
        EffectIndex::WaterWalking => EffectAttributes::Duration,
        EffectIndex::Invisibility => EffectAttributes::Duration,
        EffectIndex::Paralyze => EffectAttributes::Duration,
        EffectIndex::Silence => EffectAttributes::Duration,
        EffectIndex::Dispel => EffectAttributes::Magnitude,
        EffectIndex::Mark => EffectAttributes::None,
        EffectIndex::Recall => EffectAttributes::None,
        EffectIndex::DivineIntervention => EffectAttributes::None,
        EffectIndex::AlmsiviIntervention => EffectAttributes::None,
        EffectIndex::CureCommonDisease => EffectAttributes::None,
        EffectIndex::CureBlightDisease => EffectAttributes::None,
        EffectIndex::CureCorprusDisease => EffectAttributes::None,
        EffectIndex::CurePoison => EffectAttributes::None,
        EffectIndex::CureParalyzation => EffectAttributes::None,
        EffectIndex::RestoreAttribute => EffectAttributes::Magnitude,
        EffectIndex::RestoreSkill => EffectAttributes::Magnitude,
        EffectIndex::SummonScamp => EffectAttributes::Duration,
        EffectIndex::SummonClannfear => EffectAttributes::Duration,
        EffectIndex::SummonDaedroth => EffectAttributes::Duration,
        EffectIndex::SummonDremora => EffectAttributes::Duration,
        EffectIndex::SummonAncestralGhost => EffectAttributes::Duration,
        EffectIndex::SummonSkeletalMinion => EffectAttributes::Duration,
        EffectIndex::SummonLeastBonewalker => EffectAttributes::Duration,
        EffectIndex::SummonGreaterBonewalker => EffectAttributes::Duration,
        EffectIndex::SummonBonelord => EffectAttributes::Duration,
        EffectIndex::SummonWingedTwilight => EffectAttributes::Duration,
        EffectIndex::SummonHunger => EffectAttributes::Duration,
        EffectIndex::SummonGoldensaint => EffectAttributes::Duration,
        EffectIndex::SummonFlameAtronach => EffectAttributes::Duration,
        EffectIndex::SummonFrostAtronach => EffectAttributes::Duration,
        EffectIndex::SummonStormAtronach => EffectAttributes::Duration,
        EffectIndex::BoundDagger => EffectAttributes::Duration,
        EffectIndex::BoundLongsword => EffectAttributes::Duration,
        EffectIndex::BoundMace => EffectAttributes::Duration,
        EffectIndex::BoundBattleAxe => EffectAttributes::Duration,
        EffectIndex::BoundSpear => EffectAttributes::Duration,
        EffectIndex::BoundLongbow => EffectAttributes::Duration,
        EffectIndex::BoundCuirass => EffectAttributes::Duration,
        EffectIndex::BoundHelm => EffectAttributes::Duration,
        EffectIndex::BoundBoots => EffectAttributes::Duration,
        EffectIndex::BoundShield => EffectAttributes::Duration,
        EffectIndex::BoundGloves => EffectAttributes::Duration,
        EffectIndex::Corpus => EffectAttributes::Duration,
        EffectIndex::Vampirism => EffectAttributes::None,
        EffectIndex::SummonCenturionSphere => EffectAttributes::Duration,
        EffectIndex::SummonFabricant => EffectAttributes::Duration,
        EffectIndex::SummonCreature01 => EffectAttributes::Duration,
        EffectIndex::SummonCreature02 => EffectAttributes::Duration,
        EffectIndex::SummonCreature03 => EffectAttributes::Duration,
        EffectIndex::SummonCreature04 => EffectAttributes::Duration,
        EffectIndex::SummonCreature05 => EffectAttributes::Duration,
        EffectIndex::StuntedMagicka => EffectAttributes::Duration,
        EffectIndex::RestoreHealth => EffectAttributes::CommonDurationAndMagnitude,
        EffectIndex::RestoreSpellPoints => EffectAttributes::CommonDurationAndMagnitude,
        EffectIndex::RestoreFatigue => EffectAttributes::CommonDurationAndMagnitude,
        _ => EffectAttributes::DurationAndMagnitude
    }
}

fn set_potion(record: &mut Record, level_values: &[u32], values: &[u16], level: Option<u8>) -> Result<bool, String> {
    let mut changed = false;
    changed |= set_potion_value(record, level_values, values)?;
    changed |= set_potion_weight(record, values)?;
    let effect = potion_effect(record)?;
    match effect_attributes(effect) {
        EffectAttributes::None => { },
        EffectAttributes::Duration => {
            if let Some(level) = level {
                set_potion_duration(record, values[15 + level as usize]);
            } else {
                set_potion_duration(record, values[33]);
            }
        },
        EffectAttributes::Magnitude => {
            if let Some(level) = level {
                set_potion_magnitude(record, values[20 + level as usize]);
            } else {
                set_potion_magnitude(record, values[34]);
            }
        },
        EffectAttributes::DurationAndMagnitude => {
            if let Some(level) = level {
                set_potion_duration(record, values[5 + level as usize]);
                set_potion_magnitude(record, values[10 + level as usize]);
            } else {
                set_potion_duration(record, values[31]);
                set_potion_magnitude(record, values[32]);
            }
        },
        EffectAttributes::CommonDurationAndMagnitude => {
            if let Some(level) = level {
                set_potion_duration(record, values[30]);
                set_potion_magnitude(record, values[25 + level as usize]);
            } else {
                set_potion_duration(record, values[31]);
                set_potion_magnitude(record, values[32]);
            }
        }
    }
    Ok(changed)
}

fn set_potion_duration(record: &mut Record, duration: u16) {
    let data = record.fields.iter_mut().filter(|(tag, _)| *tag == ENAM).nth(0).unwrap();
    if let Field::Effect(data) = &mut data.1 {
        data.duration = duration as i32;
    } else {
        panic!()
    }
}

fn set_potion_magnitude(record: &mut Record, magnitude: u16) {
    let data = record.fields.iter_mut().filter(|(tag, _)| *tag == ENAM).nth(0).unwrap();
    if let Field::Effect(data) = &mut data.1 {
        data.magnitude_min = magnitude as i32;
        data.magnitude_max = data.magnitude_min;
    } else {
        panic!()
    }
}

fn set_potion_value(record: &mut Record, level_values: &[u32], values: &[u16]) -> Result<bool, String> {
    let mut values = values[.. 5].to_vec();
    values.sort_unstable();
    let old_value = potion_value(record)?;
    let new_value = match level_values.binary_search(&old_value) {
        Ok(i) => values[i] as u32,
        Err(i) => if i == 0 {
            (old_value as f64 * values[0] as f64 / level_values[0] as f64).round() as u32
        } else if i == 5 {
            (values[4] as f64 + (values[4] - values[3]) as f64 * (1.0 + (old_value - level_values[4]) as f64 / (level_values[4] - level_values[3]) as f64)).round() as u32
        } else {
            (values[i - 1] as f64 + (values[i] - values[i - 1]) as f64 * (old_value - level_values[i - 1]) as f64 / (level_values[i] - level_values[i - 1]) as f64).round() as u32 
        }
    };
    if new_value == old_value { return Ok(false); }
    let data = record.fields.iter_mut().filter(|(tag, _)| *tag == ALDT).nth(0).unwrap();
    if let Field::Potion(data) = &mut data.1 {
        data.value = new_value;
    } else {
        panic!()
    }
    Ok(true)
}

fn set_potion_weight(record: &mut Record, values: &[u16]) -> Result<bool, String> {
    let data = record.fields.iter_mut().filter(|(tag, _)| *tag == ALDT).nth(0).unwrap();
    if let Field::Potion(data) = &mut data.1 {
        let new_weight = ((data.weight as f64).min(values[35] as f64 * 0.01) * values[36] as f64 / values[37] as f64) as f32;
        if new_weight == data.weight { return Ok(false) };
        data.weight = new_weight;
    } else {
        panic!()
    }
    Ok(true)
}

fn find_level_values(potions: &HashMap<String, [Option<(String, Record)>; 5]>) -> Result<[u32; 5], String> {
    let mut level_values = [0; 5];
    for level in 0 .. 5 {
        let mut values = Vec::new();
        for potion in potions.iter().filter_map(|x| x.1[level].as_ref()) {
            values.push(potion_value(&potion.1)?);
        }
        values.sort_unstable();
        if values.is_empty() {
            return Err("Слишком мало зелий.".into());
        }
        level_values[level] = values[values.len() / 2];
    }
    level_values.sort_unstable();
    Ok(level_values)
}

fn classify_potions(potions: HashMap<String, Record>)
    -> Result<(HashMap<String, [Option<(String, Record)>; 5]>, Vec<(String, Record)>, Vec<(String, Record)>), String> {

    let mut potions_by_normalized_id = HashMap::new();
    for (id, record) in potions.into_iter() {
        let normalized_id = id.replace(' ', "_");
        if let Some((existing_id, _)) = potions_by_normalized_id.insert(normalized_id, (id.clone(), record)) {
            return Err(format!("Зелье \"{}\" конфликтует с зельем \"{}\".", id, existing_id));
        }
    }
    let mut potions_by_kind = HashMap::new();
    let mut other_potions = Vec::new();
    for (normalized_id, (id, record)) in potions_by_normalized_id.into_iter() {
        if let Some((level, kind)) = potion_level_kind(&normalized_id, &record) {
            let entry = potions_by_kind.entry(kind).or_insert_with(|| [None, None, None, None, None]);
            entry[level as usize] = Some((id, record));
        } else {
            other_potions.push((id, record));
        }
    }
    let mut standard_only_potions_ids = Vec::new();
    let mut standard_only_potions = Vec::new();
    for (normalized_id, levels) in potions_by_kind.iter_mut() {
        if levels[0].is_none() && levels[1].is_none() && levels[3].is_none() && levels[4].is_none() {
            standard_only_potions_ids.push(normalized_id.clone());
            standard_only_potions.push(levels[2].take().unwrap());
        }
    }
    for normalized_id in standard_only_potions_ids {
        potions_by_kind.remove(&normalized_id);
    }
    Ok((potions_by_kind, standard_only_potions, other_potions))
}

fn collect_potions(mw_path: &Path) -> Result<(HashMap<String, Record>, FileTime), String> {
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
    game_files.sort_by_key(|x| x.1.extension().and_then(|e| e.to_str()).map(|e| e.to_uppercase()));
    let mut file_time = None;
    let mut potions = HashMap::new();
    for (game_file_name, game_file_path, game_file_time) in game_files.into_iter() {
        let mut has_potions = false;
        let mut game_file = File::open(game_file_path).map_err(|x| x.to_string())?;
        let mut records = Records::new(CodePage::Russian, RecordReadMode::Lenient, 0, &mut game_file);
        let file_header = records.next().ok_or_else(|| "Невалидный файл.".to_string())?.map_err(|e| e.to_string())?;
        let (_, file_header) = file_header.fields.first().ok_or_else(|| "Невалидный файл.".to_string())?;
        if let Field::FileMetadata(file_header) = file_header {
            if file_header.author == "PotionsBalance.exe" { continue; }
        } else {
            return Err("Невалидный файл.".into());
        }
        for record in records {
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
            if record.tag != ALCH { continue; }
            let id = if let Field::StringZ(ref id) = record.fields.iter().filter(|(tag, _)| *tag == NAME).nth(0)
                .ok_or(format!("{}: alchemy record does not have an ID.", game_file_name))?.1 {
                id.string.to_uppercase()
            } else {
                panic!()
            };
            potions.insert(id, record);
            has_potions = true;
        }
        if has_potions {
            file_time = Some(game_file_time);
        }
    }
    if let Some(file_time) = file_time {
        Ok((potions, file_time))
    } else {
        Err("Зелья не найдены.".into())
    }
}
