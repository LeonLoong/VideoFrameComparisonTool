@echo off

if not exist "C:\%HOMEPATH%\Demo\Program\Demo_CheckFrameTool\" mkdir C:\%HOMEPATH%\Demo\Program\Demo_CheckFrameTool\
robocopy "A:\Demo\Global\Other\Demo_CheckFrameTool\Demo_CheckFrameTool" "C:\%HOMEPATH%\Demo\Program\Demo_CheckFrameTool" /mir
goto CopyShortcut


:CopyShortcut
C:
cd C:\%HOMEPATH%\Demo\Program\Demo_CheckFrameTool
copy Demo_CheckFrameTool.lnk C:\Users\%USERNAME%\Desktop