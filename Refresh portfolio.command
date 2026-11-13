#!/bin/zsh
cd "${0:A:h}"
python3 scripts/export_site.py && python3 scripts/check_site.py
result=$?
if [ "$result" -eq 0 ]; then
  echo "Portfolio refreshed. In GitHub Desktop, review changes, Commit to main, then Push origin."
else
  echo "Refresh failed. Start the ahmed-portfolio site in Local, then try again. Do not publish this failed refresh."
fi
read "reply?Press Return to close."
exit "$result"
