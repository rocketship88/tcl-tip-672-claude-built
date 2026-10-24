@echo off
setlocal ENABLEDELAYEDEXPANSION

:: buildmerge.bat - build Tcl and Tk into ONE shared install prefix, so
:: tclsh can "package require Tk" directly (unlike build.bat, which
:: installs Tcl and Tk into separate tcl\ and tk\ subdirectories that
:: tclsh has no built-in reason to know about).
::
:: Reuses the tcl\ and tk\ source trees already extracted by
:: "build.bat unzip" - run that first if you haven't.
::
:: Usage: %~nx0 [static [clean [only]] | debug [clean [only]] | release [clean [only]]]
:: Default (no args): static build with clean
:: "clean only" performs the clean step but skips the build

cd /d "%~dp0"
set ROOTDIR=%CD%

if not "%CD%"=="%CD: =%" (
    echo ERROR: The working directory path contains spaces:
    echo   %CD%
    echo Please move the script to a directory with no spaces in the path.
    exit /b 1
)

if not defined VSCMD_ARG_TGT_ARCH (
    echo ERROR: This script must be run from a Visual Studio Native Tools Command Prompt.
    echo Please launch "x64 Native Tools Command Prompt for VS 20xx" from the Start menu.
    exit /b 1
)
if /i not "%VSCMD_ARG_TGT_ARCH%"=="x64" (
    echo ERROR: This script requires an x64 prompt, but arch is: %VSCMD_ARG_TGT_ARCH%
    echo Please launch "x64 Native Tools Command Prompt for VS 20xx" from the Start menu.
    exit /b 1
)

echo ===========================
echo Working Dir   : %CD%
echo Mode          : merged prefix
echo ===========================

set BUILDMODE=static
set DOCLEAN=1
set CLEANONLY=0

if /i "%1"=="static" (
    set BUILDMODE=static
    set DOCLEAN=0
    if /i "%2"=="clean" (
        set DOCLEAN=1
        if /i "%3"=="only" set CLEANONLY=1
    )
    goto :do_build
)
if /i "%1"=="debug" (
    set BUILDMODE=debug
    set DOCLEAN=0
    if /i "%2"=="clean" (
        set DOCLEAN=1
        if /i "%3"=="only" set CLEANONLY=1
    )
    goto :do_build
)
if /i "%1"=="release" (
    set BUILDMODE=release
    set DOCLEAN=0
    if /i "%2"=="clean" (
        set DOCLEAN=1
        if /i "%3"=="only" set CLEANONLY=1
    )
    goto :do_build
)
if "%1"=="" goto :do_build
echo ERROR: Unknown argument "%1"
echo Usage: %~nx0 [static [clean [only]] ^| debug [clean [only]] ^| release [clean [only]]]
exit /b 1

:do_build
set TCLDIR=%CD%\tcl
set TKDIR=%CD%\tk

:: Merged: both Tcl and Tk install into the SAME directory - no
:: separate tcl\/tk\ subdirs, so bin/lib are naturally shared and
:: tclsh can find Tk's pkgIndex.tcl without any extra setup.
if /i "!BUILDMODE!"=="static" (
    set INSTALLDIR=%CD%\tcltk-merged-static
    set NMAKEOPTS=OPTS=static
)
if /i "!BUILDMODE!"=="debug" (
    set INSTALLDIR=%CD%\tcltk-merged-debug
    set NMAKEOPTS=DEBUG=1
)
if /i "!BUILDMODE!"=="release" (
    set INSTALLDIR=%CD%\tcltk-merged-release
    set NMAKEOPTS=
)

if not exist "%TCLDIR%\win\makefile.vc" (
    echo ERROR: Tcl source tree not found. Run "build.bat unzip" first.
    exit /b 1
)
if not exist "%TKDIR%\win\makefile.vc" (
    echo ERROR: Tk source tree not found. Run "build.bat unzip" first.
    exit /b 1
)

echo ===========================
echo Build Mode  : !BUILDMODE! (merged prefix)
echo Install Dir : !INSTALLDIR!
echo Clean First : !DOCLEAN!
echo Clean Only  : !CLEANONLY!
echo ===========================

echo ===========================
echo Cleaning up old install folder...
echo ===========================
if exist "!INSTALLDIR!" rd /s /q "!INSTALLDIR!"

if "!DOCLEAN!"=="1" (
    echo ===========================
    echo Cleaning Tcl build artifacts...
    echo ===========================
    cd /d %TCLDIR%\win
    nmake -f makefile.vc !NMAKEOPTS! clean || goto :error

    echo ===========================
    echo Cleaning Tk build artifacts...
    echo ===========================
    cd /d %TKDIR%\win
    nmake -f makefile.vc TCLDIR=%TCLDIR% !NMAKEOPTS! clean || goto :error
)

if "!CLEANONLY!"=="1" (
    echo ===========================
    echo Clean only requested - skipping build.
    echo ===========================
    goto :eof
)

:: --- Expression substitution spelling (TCL_EXPR_SUBST_PARENS, see generic\tclParse.c) ---
:: Set EXPRSUBST=1 before running to build with the "$(expr)" trigger;
:: set EXPRSUBST=2 (or leave it unset) for the default "$((expr))" trigger.
:: Only tclParse.c uses the macro, but nmake does not notice a changed define,
:: so tclParse.obj is always deleted here to force it to be recompiled.
for /r "%TCLDIR%\win" %%F in (tclParse.obj) do if exist "%%F" del /q "%%F"
if defined EXPRSUBST (
    set CL=/DTCL_EXPR_SUBST_PARENS=!EXPRSUBST!
    echo Expression substitution: TCL_EXPR_SUBST_PARENS=!EXPRSUBST!
) else (
    echo Expression substitution: default
)

echo ===========================
echo Building Tcl ^(!BUILDMODE!, merged prefix^)...
echo ===========================
cd /d %TCLDIR%\win
nmake -f makefile.vc !NMAKEOPTS! || goto :error
nmake -f makefile.vc !NMAKEOPTS! INSTALLDIR=!INSTALLDIR! install || goto :error

echo ===========================
echo Building Tk ^(!BUILDMODE!, merged prefix^)...
echo ===========================
cd /d %TKDIR%\win
nmake -f makefile.vc TCLDIR=%TCLDIR% !NMAKEOPTS! || goto :error
nmake -f makefile.vc TCLDIR=%TCLDIR% !NMAKEOPTS! INSTALLDIR=!INSTALLDIR! install || goto :error

set TCLVERSFX=
for %%F in ("!INSTALLDIR!\bin\tclsh9*.exe") do (
    set TCLSHNAME=%%~nF
    set TCLVERSFX=!TCLSHNAME:tclsh=!
)

if /i "!BUILDMODE!"=="debug" (
    echo ===========================
    echo Copying debug symbol files ^(.pdb^) to install bin folder...
    echo ===========================
    for /d %%D in ("%TCLDIR%\win\Debug_AMD64_VC*") do set TCLDBG=%%D
    xcopy /Y /I "!TCLDBG!\tclsh!TCLVERSFX!.pdb" "!INSTALLDIR!\bin\" >nul
    xcopy /Y /I "!TCLDBG!\tcl!TCLVERSFX!.pdb"   "!INSTALLDIR!\bin\" >nul
    for /d %%D in ("%TKDIR%\win\Debug_AMD64_VC*") do set TKDBG=%%D
    xcopy /Y /I "!TKDBG!\wish!TCLVERSFX!.pdb"     "!INSTALLDIR!\bin\" >nul
    xcopy /Y /I "!TKDBG!\tcl9tk!TCLVERSFX!.pdb"   "!INSTALLDIR!\bin\" >nul
)

echo ===========================
echo Merged Tcl/Tk Build Complete ^(!BUILDMODE!^)
echo Tclsh: !INSTALLDIR!\bin\tclsh!TCLVERSFX!.exe
echo Wish : !INSTALLDIR!\bin\wish!TCLVERSFX!.exe
if /i "!BUILDMODE!"=="debug" (
    echo PDBs : copied to bin folder
)
echo.
echo Test with:
echo   !INSTALLDIR!\bin\tclsh!TCLVERSFX!.exe -c "package require Tk; puts ok"
echo ===========================
goto :eof

:error
echo Build failed. Check error above.
exit /b 1
