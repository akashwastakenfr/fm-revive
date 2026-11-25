# Native & Java Binary Map

Target native binary: **`libFIFAMobileNeon.so.original`** (ARM64 ELF64, NDK r18b, stripped, Build ID `5b68aef6cae0402e472aaae084aaa1367661b788`).
- `.text` VA/file offset: `0x0cf7000`, size `0x5b661a8`
- `.rodata` VA/file offset: `0x685d1b0`, size `0xa3ca50` (HXCPP string literals have an 8-byte header before char data)

## Confirmed `.text` Addresses (Stage 1: ConfigService & INI)
| Address | Symbol / Purpose |
|---|---|
| `0xd004e4`–`0xd0052c` | HXCPP static registration of `config_getFifaMobileHostNameFetchUrl*` and `config_verifyFifaMobileHostNameFetch__2` |
| `0x118ee00`–`0x118f1c4` | Builds primary URL `/config/Android/<version>/config.ini?<uint64>` |
| `0x118f484`–`0x118f800` | Builds fallback URL `/config/Android/default/config.ini?<uint64>` |
| `0x118f8e8`–`0x118fa54` | `config_verifyFifaMobileHostNameFetch__2` implementation (wrapped by `0x129a57c`) |
| `0x118fac0`–`0x118fc24` | `client_version_override` lookup & version fallback |
| `0x12687f8`–`0x1268b44` | INI section filter: accepts ONLY `[default]`, `[platform]`, and 6-byte section (`0x686b02a`) |
| `0x1268c5c` | EAIO INI wchar-to-UTF8 callback |
| `0x1268ef8`–`0x1269054` | Copies parsed maps (`[x20+0x58]`, `+0xb8`, `+0x118`) into target map |
| `0x1269058`–`0x1269154` | Top-level INI load wrapper (`0x12687f8` + `0x1268ef8`) |
| `0x126a744` | Map lookup by key (`eastl::string`), used at `0x118f99c` with `*(0x8380030)` (`"hostName"`) |
| `0x53c4278`–`0x53c439c` | `_oninitializeHostNameFetch` verification check (`[x23, #0x38]`), `HOST NAME VERIFY FAILED. url:`, `hs=`, `, len=` formatting |
| `0x53d52a0`–`0x53d5528` | `ConfigService_obj::__Field` reflection getter (`[x19, #0x38]` = `_config_verifyFifaMobileHostNameFetch`) |

## Confirmed `.text` Addresses (Stage 2: `/g/game/batch` Protobuf & Decoder)
| Address | Symbol / Purpose |
|---|---|
| `0x4b13ea4`–`0x4b142f4` | `BatchResponse::mergeFrom` (`1`: status, `2`: payload, `3`: checksum) |
| `0x4b15a74`–`0x4b15ba0` | `BatchResponseCollection::mergeFrom` (field `1` group via `vtable+0x190`) |
| `0x4c88cd8` / `0x4c89484` | Protobuf `CodedInputStream` varint/tag helpers |
| `0x4e55cd8`–`0x4e55d18` | `SystemSetting::writeTo` (`1`: name, `2`: value) |
| `0x4e572dc`–`0x4e57658` | `SystemSettings` (`1`: `settingsList`) |
| `0x4e68fdc` | Initializes byte-decoder object `[x20+8]` (enabled) & `[x20+0xc]` (multiplier) |
| `0x4e69764` (`0x4e69868`–`0x4e69884`) | Byte decoder: returns `byte` unchanged if `[x20+8]==0`, else `(multiplier * byte) & 0xff` |
| `0x56f3080`–`0x56f3350` | Live batch response loop (`0x56f30c0`: `cmp w0, #0xc8` (200); `0x56f313c`: decode payload; `0x56f3220`: invoke callback) |
| `0x56f38b4`–`0x56f3af8` | First-response 14-byte trailer stripper & `[0x886a910]` cache init |
| `0x5707720` | Static init setting `[0x886a928] = 5` |

## Confirmed `.rodata` & Relocation Addresses
- `0x6862770`: `"hostName"` (referenced via `R_AARCH64_RELATIVE` at `0x8380030`)
- `0x686298a`: `"https://fm22-configserver.prod.fuel.ddns.ea.com/config/"`
- `0x68629c4` / `0x68629d1`: `"/config.ini?"` / `"/default/config.ini?"`
- `0x686ae1d`: `"default"` (7 bytes, INI section matched at `0x1268a30`)
- `0x686d465` / `0x686d48d` / `0x686d4bc`: `config_getFifaMobileHostNameFetchUrl*` / `config_verifyFifaMobileHostNameFetch__2`
- `0x7162a0a`–`0x7162b8f`: HostName error log & localization keys (`HOST NAME VERIFY FAILED. url:`, `Error_HostName_Title`, `Error_HostName_Message`, `hs=`, `, len=`)

## Key Java Classes (`jadx-out/sources/`)
- `com.ea.gp.fifamobile.FifaMainActivity` & `com.ea.gp.fifamobile.AndroidApiUtility`
- `com.ea.ironmonkey.GameActivity` (`osiris-android` dialog lock)
- `com.ea.nimble.*` (`BaseCore`, `NimbleApplicationConfiguration`, `SynergyEnvironmentUpdater`, `SynergyEnvironmentImpl`, `EnvironmentDataContainer`)