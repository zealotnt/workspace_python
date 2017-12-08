# Step by step guide to use the `test_baseline.py`

- Preparation:
    + Windows machine with latest SFIT installed
    + Ubuntu machine to do the validation
    + Set of PN5180 firmware on both side
    ```
    sirius_pn5180-localID1v3.05.7z
    sirius_pn5180-localID1v3.05cfg.7z
    sirius_pn5180-localID1v3.05-localID3v3.09.7z
    sirius_pn5180-localID1v3.05-remoteID2v3.09.7z
    sirius_pn5180-localID1v3.09.7z
    sirius_pn5180-localID2v3.05.7z
    sirius_pn5180-localID3forcev3.05.7z
    sirius_pn5180-localID3forcev3.05cfg.7z
    sirius_pn5180-remoteID2v3.05.7z
    sirius_pn5180-remoteID2v3.05cfg.7z
    sirius_pn5180-remoteID2v3.05-localID1v3.09.7z
    sirius_pn5180-remoteID2v3.05-remoteID4v3.09.7z
    sirius_pn5180-remoteID2v3.09.7z
    sirius_pn5180-remoteID3forcev3.05.7z
    sirius_pn5180-remoteID3v3.05.7z
    sirius_pn5180-remoteID4forcev3.05.7z
    sirius_pn5180-remoteID4forcev3.05cfg.7z
    ```

- Doit:
    There is two integration test case that we need to use this script
    + First, we need to download the `sirius's baseline` using `-c option`. (need to do this only once)
    + `Success case`, then this equation should be happen: `our baseline` + `newly-upgraded-firmware` == `sirius-new-baseline`
        * `I.` Use SFIT to upgrade firmware to Sirius
        * `II.` Use `test_baseline.py` to do the baseline validation
            - `1.` We download `sirius's baseline` copy it to `BASELINE_TARGET`
            - `2.` We copy our `BASELINE` to `BASELINE_TEMP`, we will work on this `BASELINE_TEMP` folder
            - `3.` Prepare the firmware
            - `3.1/2` Extract all firmware in `BASELINE_TEMP` and `BASELINE_TARGET`, cause we need to do the comparison on json file
            - `3.3` Extract the newly-upgraded-firmware to `BASELINE_TEMP`
            - `4.` Do the comparison, should be: `BASELINE_TEMP` == `BASELINE_TARGET`
    + `Fail case`, then we check if the `sirius's baseline` same as our `baseline`, using script's `-v option`
