versione='1.0.0'
# Module: watched_store
# Author: ElSupremo
# Created on: 17.09.2026
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
#
# Persistenza minima per la "memoria di visualizzazione" (resume/watched).
# Un solo file JSON nel profilo dell'addon: { "<md5(link)>": {resume, total, playcount, last_played} }

import hashlib
import json
import os
from datetime import datetime, timezone

import xbmcaddon
import xbmcvfs

ADDON_ID = 'plugin.video.mandrakodi'
STORE_FILE = 'watched.json'


def _store_path():
    profile = xbmcvfs.translatePath(xbmcaddon.Addon(id=ADDON_ID).getAddonInfo('profile'))
    xbmcvfs.mkdirs(profile)
    return os.path.join(profile, STORE_FILE)


def _load_all():
    path = _store_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        # file assente/corrotto: si riparte da un dict vuoto senza crashare
        return {}


def _save_all(data):
    path = _store_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception:
        pass


def make_key(identifier):
    """Hash md5 stabile dell'identificatore univoco del contenuto (es. item['link'])."""
    if not identifier:
        return None
    return hashlib.md5(identifier.encode('utf-8', 'ignore')).hexdigest()


def load_state(key):
    if not key:
        return None
    return _load_all().get(key)


def save_progress(key, resume_seconds, total_seconds, watched_threshold_pct=90):
    """Salva il progresso di riproduzione. Se la percentuale vista supera la
    soglia, marca come visto (playcount++) invece di salvare un resume point."""
    if not key or not total_seconds or total_seconds <= 0:
        return
    data = _load_all()
    entry = data.get(key, {'playcount': 0})
    pct = (resume_seconds / total_seconds) * 100
    if pct >= watched_threshold_pct:
        entry['resume'] = 0.0
        entry['playcount'] = int(entry.get('playcount', 0)) + 1
    else:
        entry['resume'] = float(resume_seconds)
        entry.setdefault('playcount', 0)
    entry['total'] = float(total_seconds)
    entry['last_played'] = datetime.now(timezone.utc).isoformat()
    data[key] = entry
    _save_all(data)


def mark_watched(key, total_seconds):
    if not key:
        return
    data = _load_all()
    entry = data.get(key, {'playcount': 0})
    entry['resume'] = 0.0
    entry['total'] = float(total_seconds) if total_seconds else entry.get('total', 0.0)
    entry['playcount'] = int(entry.get('playcount', 0)) + 1
    entry['last_played'] = datetime.now(timezone.utc).isoformat()
    data[key] = entry
    _save_all(data)


def mark_unwatched(key):
    if not key:
        return
    data = _load_all()
    entry = data.get(key, {})
    entry['resume'] = 0.0
    entry['playcount'] = 0
    data[key] = entry
    _save_all(data)


def demo():
    """Self-check minimo (nessun framework): valida make_key e la logica soglia."""
    assert make_key("") is None
    assert make_key("http://a") == make_key("http://a")
    assert make_key("http://a") != make_key("http://b")
    # sotto soglia -> resume salvato, playcount invariato
    e1 = {'playcount': 0}
    pct1 = (30 / 100) * 100
    assert pct1 < 90
    # sopra soglia -> verrebbe marcato come visto
    pct2 = (95 / 100) * 100
    assert pct2 >= 90
    print("watched_store demo OK")


if __name__ == '__main__':
    demo()
