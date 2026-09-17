versione='1.0.0'
# Module: default (entry point)
# Lite: nessun self-update da server remoto, solo avvio launcher locale.

import sys
import xbmcgui

if sys.argv[2] == "":
    pass

try:
    import launcher
    launcher.run()
except Exception as err:
    import traceback
    traceback.print_exc()
    dialog = xbmcgui.Dialog()
    dialog.ok("AnimeLite", "Errore: {0}".format(err))
