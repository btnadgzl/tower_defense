from __future__ import annotations
import json
import os
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    'music_volume': 0.5,
    'sfx_volume': 0.7,
    'fullscreen': False,
    'show_fps': True,
    'difficulty': 'normal',
    'controls': {},
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def load_settings(base_dir: str) -> Dict[str, Any]:
    path = os.path.join(base_dir, 'settings.json')
    cfg: Dict[str, Any] = dict(DEFAULTS)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    mv = cfg.get('music_volume', DEFAULTS['music_volume'])
    sv = cfg.get('sfx_volume', DEFAULTS['sfx_volume'])
    cfg['music_volume'] = float(_clamp(float(mv), 0.0, 1.0))
    cfg['sfx_volume'] = float(_clamp(float(sv), 0.0, 1.0))
    cfg['fullscreen'] = bool(cfg.get('fullscreen', DEFAULTS['fullscreen']))
    cfg['show_fps'] = bool(cfg.get('show_fps', DEFAULTS['show_fps']))
    diff = str(cfg.get('difficulty', DEFAULTS['difficulty'])).lower()
    if diff not in ('easy', 'normal', 'hard'):
        diff = 'normal'
    cfg['difficulty'] = diff
    if not isinstance(cfg.get('controls'), dict):
        cfg['controls'] = {}
    return cfg

