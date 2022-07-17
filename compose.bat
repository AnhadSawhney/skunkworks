FOR %%a IN (ezgif\*.*) DO magick composite logo_inverted.png %%a -compose difference -gravity center out\%%a
::%%a
