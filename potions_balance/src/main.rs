#![windows_subsystem = "windows"]

use std::ptr::{self};
use winapi::um::winuser::MessageBoxW;

fn main() {
    let caption = "caption\0".encode_utf16().collect::<Vec<_>>();
    let message = "hello, world\0".encode_utf16().collect::<Vec<_>>();
    unsafe { MessageBoxW(ptr::null_mut(), message.as_ptr(), caption.as_ptr(), 0); }
}
