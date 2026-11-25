# Discovery 001: Why `default-config.ini` Failed Verification (`Error_HostName_Message`)

- **Symptom:** After connecting the APK to `127.0.0.1:8080`, `Error_HostName_Message` (`Unable to access the configuration of current build`) showed:
  `0x00000000000000000000000000000000hs=fbe0288dcd700b55f8e8c2b080355a85659a1a01, len=301,`
  where `hs=` and `len=` matched the exact SHA-1 and byte length of `server/data/responses/default-config.ini`.
- **Root Cause (Confirmed in `libFIFAMobileNeon.so.original`):**
  - `0x53c42ac` calls `ConfigService._config_verifyFifaMobileHostNameFetch` (`0x129a57c` -> `0x118f8e8`).
  - `0x118f8e8` does **not** check an RSA/HMAC signature; it parses the INI via `0x1269058(..., "", "")` -> `0x12687f8`, then checks `0x126a744(map, "hostName")` (`0x8380030` -> `0x6862770` `"hostName"`).
  - `0x12687f8` (`0x1268a18`–`0x1268af8`) **only** loads three INI sections: `[default]`, `[platform]`, and a 6-byte device section (`0x686b02a`). `[FIFAMobileApp]` was completely ignored, leaving the map empty.
- **Fix:** Replace `[FIFAMobileApp]` with `[default]` in `server/data/responses/default-config.ini`.
- **Result:** Cleared `Error_HostName_Message` and advanced startup to `POST /g/game/batch` (`game/system/settings`).
