@echo off
setlocal

:: test.bat - build tcltest and run the expression-substitution related tests.
:: Place in tcl\win and run from an x64 Native Tools Command Prompt.
::
:: Usage: test.bat 1|2 [static|debug|release] [full|pattern]
::   1 = test the build where the trigger is  $(expr)
::   2 = test the build where the trigger is  $((expr))   (the default spelling)
::   second argument = build mode, default static (same as buildmerge.bat)
::
:: Default: runs parse*.test (parse, parseOld, parseExpr) and compile.test.
::   third argument  full          = run the whole test suite (takes several minutes)
::   third argument  subst*.test   = run just the test files that match that pattern
::   Example: test.bat 2 static full
:: Only tclParse.c depends on the spelling, so tclParse.obj is deleted first to
:: make sure it is recompiled with the requested setting. Your installed
:: tcltk-merged-* folders are not touched.

cd /d "%~dp0"

if "%1"=="1" goto :argok
if "%1"=="2" goto :argok
echo Usage: %~nx0 1^|2 [static^|debug^|release] [full^|pattern]
echo   1 = $^(expr^) spelling, 2 = $^(^(expr^)^) spelling
exit /b 1

:argok
if not exist makefile.vc (
    echo ERROR: makefile.vc not found. Put this file in tcl\win.
    exit /b 1
)
where nmake >nul 2>&1
if errorlevel 1 (
    echo ERROR: nmake not found. Run this from an x64 Native Tools Command Prompt.
    exit /b 1
)

set MODEOPTS=OPTS=static
if /i "%2"=="static"  set MODEOPTS=OPTS=static
if /i "%2"=="debug"   set MODEOPTS=DEBUG=1
if /i "%2"=="release" set MODEOPTS=

:: setlocal above means CL does not leak into your console afterwards.
set CL=/DTCL_EXPR_SUBST_PARENS=%1

echo ===========================
echo TCL_EXPR_SUBST_PARENS=%1   nmake options: %MODEOPTS%
echo ===========================

del /s /q tclParse.obj >nul 2>&1

set TESTRC=0
if /i "%3"=="full" (
    nmake -f makefile.vc test %MODEOPTS%
    if errorlevel 1 set TESTRC=1
    goto :done
)
if not "%3"=="" (
    nmake -f makefile.vc test %MODEOPTS% TESTPAT=%3
    if errorlevel 1 set TESTRC=1
    goto :done
)
nmake -f makefile.vc test %MODEOPTS% TESTPAT=parse*.test
if errorlevel 1 set TESTRC=1
nmake -f makefile.vc test %MODEOPTS% TESTPAT=compile.test
if errorlevel 1 set TESTRC=1

:done

echo ===========================
if "%TESTRC%"=="0" (
    echo The test runs finished with exit code 0. Check the Failed counts above.
) else (
    echo At least one test run reported a problem - see the output above.
)
echo ===========================
exit /b %TESTRC%
