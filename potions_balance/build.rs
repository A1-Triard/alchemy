use windres::Build;
use find_winsdk::{SdkInfo, SdkVersion};

fn main() {
    let sdk = SdkInfo::find(SdkVersion::Any).unwrap().unwrap();
    let windows_include = sdk.installation_folder().join("Include").join(format!("{}.0", sdk.product_version()));
    Build::new()
        .include(windows_include.join("shared"))
        .include(windows_include.join("um"))
        .compile("src/resources.rc").unwrap();
}
