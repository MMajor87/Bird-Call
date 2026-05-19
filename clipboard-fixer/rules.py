import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))

from shared.rules import (  # noqa: F401
    Rule,
    is_link,
    clean_url,
    get_default_rules,
    _strip_utm,
    _remove_amp,
    _x_to_vxtwitter,
    _tiktok_to_tnktok,
    _facebook_to_fixacebook,
    _unwrap_facebook,
    _unwrap_google,
    _force_https,
)
