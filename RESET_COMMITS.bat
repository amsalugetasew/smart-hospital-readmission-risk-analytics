@echo off
cls
echo ================================================================================
echo  RESET UNPUSHED COMMITS (Remove commits with API key)
echo ================================================================================
echo.

echo This will:
echo   1. Remove all unpushed commits
echo   2. Keep all your file changes
echo   3. Allow you to make fresh commits without the API key
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/3] Checking current git status...
git status
echo.

echo [2/3] Resetting to last pushed commit (keeping all changes)...
echo.
git reset --soft origin/main
echo.
echo Done! All commits removed, but files are still changed.
echo.

echo [3/3] Current status (files are staged and ready to commit):
git status
echo.

echo ================================================================================
echo  SUCCESS! Commits removed.
echo ================================================================================
echo.
echo Next steps:
echo   1. Review the staged files: git status
echo   2. Unstage files if needed: git reset HEAD filename
echo   3. Make fresh commits: git add . ^&^& git commit -m "Your message"
echo   4. Push: git push
echo.
pause
