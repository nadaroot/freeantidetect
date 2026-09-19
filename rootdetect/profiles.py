"""
Profile manager and local JSON storage for Root Detect.
"""

import os
import sys
import json
import uuid
import shutil
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from rootdetect.fingerprints import generate_random_fingerprint, sanitize_fingerprint
from rootdetect.proxy import parse_proxy_string

DEFAULT_STORAGE_DIR = Path.home() / ".rootdetect"

class ProfileManager:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            if getattr(sys, 'frozen', False):
                app_dir = Path(sys.executable).parent
            else:
                app_dir = Path(__file__).parent.parent
            local_base = app_dir / "profiles_data"
            try:
                local_base.mkdir(parents=True, exist_ok=True)
                self.base_dir = local_base
            except (PermissionError, OSError):
                self.base_dir = Path.home() / ".rootdetect"

        self.profiles_dir = self.base_dir / "profiles"
        self.config_file = self.base_dir / "profiles.json"
        
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.profiles_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            self.base_dir = Path.cwd() / "profiles_data"
            self.profiles_dir = self.base_dir / "profiles"
            self.config_file = self.base_dir / "profiles.json"
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_config()

    def _ensure_config(self):
        if not self.config_file.exists():
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({"version": 1, "profiles": []}, f, indent=2, ensure_ascii=False)

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            changed = False
            for p in data.get("profiles", []):
                if "fingerprint" in p:
                    orig = json.dumps(p["fingerprint"], sort_keys=True)
                    p["fingerprint"] = sanitize_fingerprint(p["fingerprint"])
                    if json.dumps(p["fingerprint"], sort_keys=True) != orig:
                        changed = True
            if changed:
                self._save_data(data)
            return data
        except Exception:
            return {"version": 1, "profiles": []}

    def _save_data(self, data: Dict[str, Any]):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def list_profiles(self) -> List[Dict[str, Any]]:
        return self._load_data().get("profiles", [])

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        for p in self.list_profiles():
            if p["id"] == profile_id:
                return p
        return None

    def create_profile(
        self,
        name: str,
        os_type: str = "auto",
        proxy_str: Optional[str] = None,
        notes: str = "",
        custom_fp: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        profile_id = str(uuid.uuid4())[:8]
        profile_dir = self.profiles_dir / profile_id
        user_data_dir = profile_dir / "user_data"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        fp = custom_fp if custom_fp else generate_random_fingerprint(os_type)
        
        proxy_parsed = parse_proxy_string(proxy_str) if proxy_str else None

        profile = {
            "id": profile_id,
            "name": name.strip() or f"Profile #{profile_id}",
            "created_at": int(time.time()),
            "last_launched_at": None,
            "launch_count": 0,
            "notes": notes.strip(),
            "proxy_raw": proxy_str.strip() if proxy_str else "",
            "proxy": proxy_parsed,
            "fingerprint": fp,
            "user_data_path": str(user_data_dir.resolve())
        }

        data = self._load_data()
        data["profiles"].append(profile)
        self._save_data(data)
        return profile

    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self._load_data()
        for idx, p in enumerate(data.get("profiles", [])):
            if p["id"] == profile_id:
                if "proxy_raw" in updates:
                    p["proxy_raw"] = updates["proxy_raw"]
                    p["proxy"] = parse_proxy_string(updates["proxy_raw"]) if updates["proxy_raw"] else None
                for k, v in updates.items():
                    if k not in ["id", "proxy_raw", "proxy"]:
                        p[k] = v
                data["profiles"][idx] = p
                self._save_data(data)
                return p
        return None

    def delete_profile(self, profile_id: str) -> bool:
        data = self._load_data()
        initial_len = len(data.get("profiles", []))
        data["profiles"] = [p for p in data.get("profiles", []) if p["id"] != profile_id]
        if len(data["profiles"]) < initial_len:
            self._save_data(data)
            # Remove profile folder
            p_dir = self.profiles_dir / profile_id
            if p_dir.exists():
                shutil.rmtree(p_dir, ignore_errors=True)
            return True
        return False

    def mark_launched(self, profile_id: str):
        data = self._load_data()
        for p in data.get("profiles", []):
            if p["id"] == profile_id:
                p["last_launched_at"] = int(time.time())
                p["launch_count"] = p.get("launch_count", 0) + 1
                break
        self._save_data(data)

    def export_to_file(self, filepath: str) -> bool:
        try:
            data = self._load_data()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def import_from_file(self, filepath: str) -> int:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                imported = json.load(f)
            new_profiles = imported.get("profiles", [])
            data = self._load_data()
            existing_ids = {p["id"] for p in data.get("profiles", [])}
            
            count = 0
            for np in new_profiles:
                if np.get("id") not in existing_ids:
                    # ensure directory
                    p_id = np.get("id", str(uuid.uuid4())[:8])
                    np["id"] = p_id
                    p_dir = self.profiles_dir / p_id / "user_data"
                    p_dir.mkdir(parents=True, exist_ok=True)
                    np["user_data_path"] = str(p_dir.resolve())
                    data["profiles"].append(np)
                    count += 1
            self._save_data(data)
            return count
        except Exception:
            return 0
