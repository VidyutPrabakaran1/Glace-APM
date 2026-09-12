# Install Scoop & Add the Glace APM bucket

- **1. Installing Scoop**
    Open a PowerShell Terminal and run:
    - `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
    - `Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression`

- **2. Adding the Glace APM bucket**
    - Run `scoop bucket add glace https://github.com/VidyutPrabakaran1/scoop-bucket`

To install the latest Glace APM version:
- Run `scoop install glaceapm`

To upgrade to a new version:
- Run `scoop update glaceapm`


