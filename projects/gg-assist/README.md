# Intro

- This script will wrap `google-assistant-hotword` (google-assistant library), so that:
    + Can control the onboard-LED base on status of the assistant
    + Can detect hardware issue and show to LED indicator
    + Can detect network avaibility then start the assistant
- LED pattern description:
    + White LED blinking: waiting for internet avaibility
    + White LED on: initializing
    + Teal LED on: waiting for wake word
    + GREEN LED blinking: listening for command
    + BLUE blinking: playing response sound
