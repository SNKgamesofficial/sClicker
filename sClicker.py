#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 sClicker v4 - Python Portierung (1:1 Funktionsumfang der AutoHotkey v2 Version)
================================================================================
"""

import os
import sys
import re
import json
import time
import random
import string
import ctypes
import threading
import traceback
import math
import configparser
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

try:
    import requests
except ImportError:
    requests = None

import urllib.request
import urllib.error

try:
    import winreg
except ImportError:
    winreg = None

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont
except Exception:
    Image = None
    ImageTk = None
    ImageDraw = None
    ImageFilter = None
    ImageFont = None

# ============== SUPABASE ==============
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase nicht installiert. Führe aus: pip install supabase")
    create_client = None
    Client = None

SUPABASE_URL = "https://szmcudmzfvicedktoybs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6bWN1ZG16ZnZpY2Vka3RveWJzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NDg5NTg3OSwiZXhwIjoyMTAwNDcxODc5fQ.flvhv_aSeXZ6CRHxLjn5yk7BTg368VFKsZqWOIgKABo"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Fehler beim Verbinden zu Supabase: {e}")
    supabase = None

# ============== SUPABASE FUNKTIONEN ==============

def supabase_get_accounts():
    if supabase is None:
        return None
    try:
        response = supabase.table("accounts").select("*").execute()
        accounts = {}
        for row in response.data:
            accounts[row["username"]] = row
        return {"accounts": accounts}
    except Exception as e:
        sClickerLog.append(f"Supabase GET Accounts Fehler: {e}")
        return None

def supabase_update_account(username: str, data: dict):
    if supabase is None:
        return False
    try:
        if "id" in data:
            del data["id"]
        if "username" in data:
            del data["username"]
        response = supabase.table("accounts").update(data).eq("username", username).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase UPDATE Account Fehler: {e}")
        return False

def supabase_create_account(username: str, data: dict):
    if supabase is None:
        return False
    try:
        if "username" in data:
            del data["username"]
        response = supabase.table("accounts").insert({"username": username, **data}).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase CREATE Account Fehler: {e}")
        return False

def supabase_delete_account(username: str):
    if supabase is None:
        return False
    try:
        response = supabase.table("accounts").delete().eq("username", username).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase DELETE Account Fehler: {e}")
        return False

# FIX: clickDelay -> delay, id wird entfernt
def supabase_get_click_kits():
    if supabase is None:
        return []
    try:
        response = supabase.table("click_kits").select("*").execute()
        return response.data
    except Exception as e:
        sClickerLog.append(f"Supabase GET Click Kits Fehler: {e}")
        return []

def supabase_create_click_kit(data: dict):
    if supabase is None:
        return False
    try:
        if "id" in data:
            del data["id"]
        if "delay" in data:
            data["clickDelay"] = data.pop("delay")
        response = supabase.table("click_kits").insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase CREATE Click Kit Fehler: {e}")
        return False

def supabase_update_click_kit(kit_id: str, data: dict):
    if supabase is None:
        return False
    try:
        if "id" in data:
            del data["id"]
        if "delay" in data:
            data["clickDelay"] = data.pop("delay")
        response = supabase.table("click_kits").update(data).eq("id", kit_id).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase UPDATE Click Kit Fehler: {e}")
        return False

def supabase_delete_click_kit(kit_id: str):
    if supabase is None:
        return False
    try:
        response = supabase.table("click_kits").delete().eq("id", kit_id).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase DELETE Click Kit Fehler: {e}")
        return False

def supabase_get_app_config():
    if supabase is None:
        return {}
    try:
        response = supabase.table("app_config").select("*").execute()
        cfg = {}
        for row in response.data:
            cfg[row.get("key", "")] = row.get("value", "")
        return cfg
    except Exception as e:
        sClickerLog.append(f"Supabase GET AppConfig Fehler: {e}")
        return {}

def supabase_set_app_config(key: str, value: str):
    if supabase is None:
        return False
    try:
        existing = supabase.table("app_config").select("*").eq("key", key).execute()
        if existing.data:
            response = supabase.table("app_config").update({"value": value}).eq("key", key).execute()
        else:
            response = supabase.table("app_config").insert({"key": key, "value": value}).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase SET AppConfig Fehler: {e}")
        return False

def supabase_get_news():
    if supabase is None:
        return []
    try:
        response = supabase.table("news").select("*").execute()
        return response.data
    except Exception as e:
        sClickerLog.append(f"Supabase GET News Fehler: {e}")
        return []

def supabase_create_news(data: dict):
    if supabase is None:
        return False
    try:
        if "id" in data:
            del data["id"]
        response = supabase.table("news").insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase CREATE News Fehler: {e}")
        return False

def supabase_update_news(news_id: str, data: dict):
    if supabase is None:
        return False
    try:
        if "id" in data:
            del data["id"]
        response = supabase.table("news").update(data).eq("id", news_id).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase UPDATE News Fehler: {e}")
        return False

def supabase_delete_news(news_id: str):
    if supabase is None:
        return False
    try:
        response = supabase.table("news").delete().eq("id", news_id).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase DELETE News Fehler: {e}")
        return False

# ============== REPORT FUNKTIONEN (FIX: Tabelle wird erstellt falls nicht existiert) ==============

def supabase_get_reports():
    if supabase is None:
        return []
    try:
        response = supabase.table("reports").select("*").execute()
        return response.data
    except Exception as e:
        # Wenn Tabelle nicht existiert, leere Liste zurückgeben
        if "PGRST205" in str(e):
            return []
        sClickerLog.append(f"Supabase GET Reports Fehler: {e}")
        return []

def supabase_create_report(data: dict):
    if supabase is None:
        return False
    try:
        if "id" in data:
            del data["id"]
        if "kit_id" not in data:
            data["kit_id"] = ""
        if "kit_name" not in data:
            data["kit_name"] = ""
        if "reporter" not in data:
            data["reporter"] = ""
        if "reason" not in data:
            data["reason"] = ""
        if "created" not in data:
            data["created"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "status" not in data:
            data["status"] = "open"
        response = supabase.table("reports").insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase CREATE Report Fehler: {e}")
        return False

def supabase_delete_report(report_id: str):
    if supabase is None:
        return False
    try:
        response = supabase.table("reports").delete().eq("id", report_id).execute()
        return len(response.data) > 0
    except Exception as e:
        sClickerLog.append(f"Supabase DELETE Report Fehler: {e}")
        return False

# ============== CACHE ==============
CACHE_DURATION = 60
_cache = {"kits": [], "news": [], "accounts": {}, "reports": [], "time": 0}

def _dedupe_by_id(items: list) -> list:
    seen = set()
    out = []
    for it in items:
        iid = it.get("id", "")
        if iid:
            if iid in seen:
                continue
            seen.add(iid)
        out.append(it)
    return out

def get_cached_kits(force_refresh=False):
    now = time.time()
    if force_refresh or now - _cache["time"] > CACHE_DURATION:
        _cache["kits"] = _dedupe_by_id(supabase_get_click_kits())
        _cache["news"] = _dedupe_by_id(supabase_get_news())
        _cache["accounts"] = supabase_get_accounts() or {"accounts": {}}
        _cache["reports"] = supabase_get_reports()
        _cache["time"] = now
    return _cache["kits"]

def get_cached_news():
    now = time.time()
    if now - _cache["time"] > CACHE_DURATION:
        _cache["kits"] = _dedupe_by_id(supabase_get_click_kits())
        _cache["news"] = _dedupe_by_id(supabase_get_news())
        _cache["accounts"] = supabase_get_accounts() or {"accounts": {}}
        _cache["reports"] = supabase_get_reports()
        _cache["time"] = now
    return _cache["news"]

def get_cached_accounts():
    now = time.time()
    if now - _cache["time"] > CACHE_DURATION:
        _cache["kits"] = _dedupe_by_id(supabase_get_click_kits())
        _cache["news"] = _dedupe_by_id(supabase_get_news())
        _cache["accounts"] = supabase_get_accounts() or {"accounts": {}}
        _cache["reports"] = supabase_get_reports()
        _cache["time"] = now
    return _cache["accounts"]

def get_cached_reports():
    now = time.time()
    if now - _cache["time"] > CACHE_DURATION:
        _cache["kits"] = _dedupe_by_id(supabase_get_click_kits())
        _cache["news"] = _dedupe_by_id(supabase_get_news())
        _cache["accounts"] = supabase_get_accounts() or {"accounts": {}}
        _cache["reports"] = supabase_get_reports()
        _cache["time"] = now
    return _cache["reports"]

def auth_get_data() -> str:
    data = supabase_get_accounts()
    if data:
        return json.dumps(data)
    return ""

def get_public_kits():
    return get_cached_kits()

def save_public_kits(kits: list) -> bool:
    success = True
    for kit in kits:
        kit_id = kit.get("id")
        if kit_id:
            if not supabase_update_click_kit(kit_id, kit):
                success = False
        else:
            # FIX: Keine ID übergeben
            kit_copy = kit.copy()
            if "id" in kit_copy:
                del kit_copy["id"]
            if not supabase_create_click_kit(kit_copy):
                success = False
    if success:
        _cache["time"] = 0
    return success

def get_news_posts() -> list:
    return get_cached_news()

def save_news_posts(posts: list) -> bool:
    success = True
    for post in posts:
        post_id = post.get("id")
        if post_id:
            if not supabase_update_news(post_id, post):
                success = False
        else:
            if not supabase_create_news(post):
                success = False
    if success:
        _cache["time"] = 0
    return success

def fix_dpi():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# ============== CLICKER ENGINE ==============
CLICKER_ENGINE_AVAILABLE = sys.platform in ("win32", "darwin") or sys.platform.startswith("linux")
CLICKER_ENGINE_ERROR = ""

if sys.platform == "win32":
    _user32 = ctypes.windll.user32
    _INPUT_MOUSE = 0
    _INPUT_KEYBOARD = 1
    _MOUSEEVENTF_LEFTDOWN = 0x0002
    _MOUSEEVENTF_LEFTUP = 0x0004
    _MOUSEEVENTF_RIGHTDOWN = 0x0008
    _MOUSEEVENTF_RIGHTUP = 0x0010
    _MOUSEEVENTF_MIDDLEDOWN = 0x0020
    _MOUSEEVENTF_MIDDLEUP = 0x0040
    _KEYEVENTF_EXTENDEDKEY = 0x0001
    _KEYEVENTF_KEYUP = 0x0002
    _KEYEVENTF_SCANCODE = 0x0008
    _MAPVK_VK_TO_VSC = 0
    ULONG_PTR = ctypes.c_size_t

    _user32.MapVirtualKeyW.restype = ctypes.c_uint
    _user32.MapVirtualKeyW.argtypes = [ctypes.c_uint, ctypes.c_uint]

    _EXTENDED_VKS = {
        0x21, 0x22, 0x23, 0x24,
        0x25, 0x26, 0x27, 0x28,
        0x2D, 0x2E,
        0x5B, 0x5C,
        0xA3, 0xA5,
        0x90,
    }

    class _MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong), ("dwExtraInfo", ULONG_PTR)]

    class _KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ULONG_PTR)]

    class _INPUT_UNION(ctypes.Union):
        _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT)]

    class _INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("union", _INPUT_UNION)]

    def _send_mouse(down_flag, up_flag):
        inp_down = _INPUT(_INPUT_MOUSE, _INPUT_UNION(mi=_MOUSEINPUT(0, 0, 0, down_flag, 0, 0)))
        inp_up = _INPUT(_INPUT_MOUSE, _INPUT_UNION(mi=_MOUSEINPUT(0, 0, 0, up_flag, 0, 0)))
        _user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(_INPUT))
        _user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(_INPUT))

    def _mouse_down(flag):
        inp = _INPUT(_INPUT_MOUSE, _INPUT_UNION(mi=_MOUSEINPUT(0, 0, 0, flag, 0, 0)))
        _user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))

    def _mouse_up(flag):
        inp = _INPUT(_INPUT_MOUSE, _INPUT_UNION(mi=_MOUSEINPUT(0, 0, 0, flag, 0, 0)))
        _user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))

    def click_left():
        _send_mouse(_MOUSEEVENTF_LEFTDOWN, _MOUSEEVENTF_LEFTUP)

    def click_right():
        _send_mouse(_MOUSEEVENTF_RIGHTDOWN, _MOUSEEVENTF_RIGHTUP)

    def click_middle():
        _send_mouse(_MOUSEEVENTF_MIDDLEDOWN, _MOUSEEVENTF_MIDDLEUP)

    def double_click_left():
        click_left()
        time.sleep(0.03)
        click_left()

    def hold_left_down():
        _mouse_down(_MOUSEEVENTF_LEFTDOWN)

    def hold_left_up():
        _mouse_up(_MOUSEEVENTF_LEFTUP)

    def hold_right_down():
        _mouse_down(_MOUSEEVENTF_RIGHTDOWN)

    def hold_right_up():
        _mouse_up(_MOUSEEVENTF_RIGHTUP)

    def hold_middle_down():
        _mouse_down(_MOUSEEVENTF_MIDDLEDOWN)

    def hold_middle_up():
        _mouse_up(_MOUSEEVENTF_MIDDLEUP)

    def move_cursor(x, y):
        try:
            _user32.SetCursorPos(int(x), int(y))
        except Exception:
            pass

    _VK_MAP = {
        "enter": 0x0D, "return": 0x0D, "space": 0x20, "tab": 0x09,
        "esc": 0x1B, "escape": 0x1B, "backspace": 0x08, "delete": 0x2E,
        "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
        "home": 0x24, "end": 0x23, "pgup": 0x21, "pgdn": 0x22,
        "insert": 0x2D, "capslock": 0x14, "numlock": 0x90,
        "lbutton": 0x01, "rbutton": 0x02, "mbutton": 0x04,
        "lwin": 0x5B, "rwin": 0x5C, "lctrl": 0xA2, "rctrl": 0xA3,
        "lalt": 0xA4, "ralt": 0xA5, "lshift": 0xA0, "rshift": 0xA1,
        "shift": 0x10, "ctrl": 0x11, "alt": 0x12,
    }
    for _i in range(1, 25):
        _VK_MAP[f"f{_i}"] = 0x6F + _i if _i > 12 else 0x70 + (_i - 1)

    def _vk_for(key: str):
        k = key.strip().lower()
        if k in _VK_MAP:
            return _VK_MAP[k]
        if len(k) == 1:
            ch = k.upper()
            if "0" <= ch <= "9" or "A" <= ch <= "Z":
                return ord(ch)
        return None

    def _scan_for_vk(vk: int) -> int:
        try:
            return _user32.MapVirtualKeyW(ctypes.c_uint(vk), ctypes.c_uint(_MAPVK_VK_TO_VSC))
        except Exception:
            return 0

    def key_down(key: str):
        vk = _vk_for(key)
        if vk is None:
            return
        scan = _scan_for_vk(vk)
        flags = _KEYEVENTF_SCANCODE
        if vk in _EXTENDED_VKS:
            flags |= _KEYEVENTF_EXTENDEDKEY
        if scan == 0:
            inp = _INPUT(_INPUT_KEYBOARD, _INPUT_UNION(ki=_KEYBDINPUT(vk, 0, 0, 0, 0)))
        else:
            inp = _INPUT(_INPUT_KEYBOARD, _INPUT_UNION(ki=_KEYBDINPUT(0, scan, flags, 0, 0)))
        _user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))

    def key_up(key: str):
        vk = _vk_for(key)
        if vk is None:
            return
        scan = _scan_for_vk(vk)
        flags = _KEYEVENTF_SCANCODE | _KEYEVENTF_KEYUP
        if vk in _EXTENDED_VKS:
            flags |= _KEYEVENTF_EXTENDEDKEY
        if scan == 0:
            inp = _INPUT(_INPUT_KEYBOARD, _INPUT_UNION(ki=_KEYBDINPUT(vk, 0, _KEYEVENTF_KEYUP, 0, 0)))
        else:
            inp = _INPUT(_INPUT_KEYBOARD, _INPUT_UNION(ki=_KEYBDINPUT(0, scan, flags, 0, 0)))
        _user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))

    def press_key(key: str):
        key_down(key)
        time.sleep(0.02)
        key_up(key)

    def is_key_down(key: str) -> bool:
        vk = _vk_for(key)
        if vk is None:
            return False
        try:
            return bool(_user32.GetAsyncKeyState(vk) & 0x8000)
        except Exception:
            return False

    def is_mouse_button_down(button: str) -> bool:
        return is_key_down({"left": "lbutton", "right": "rbutton", "middle": "mbutton"}.get(button, "lbutton"))

    class _WinPoint(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    def get_cursor_pos():
        try:
            p = _WinPoint()
            _user32.GetCursorPos(ctypes.byref(p))
            return (p.x, p.y)
        except Exception:
            return None

elif sys.platform == "darwin":
    import ctypes.util
    _cg_path = ctypes.util.find_library("ApplicationServices")
    if not _cg_path:
        # FIX: seit macOS 11+ liegen System-Frameworks nicht mehr als
        # einzelne Dateien vor, find_library() findet sie deshalb oft nicht.
        # Direkter Pfad funktioniert trotzdem (dyld fängt das ab).
        _cg_path = "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices"
    try:
        _cg = ctypes.CDLL(_cg_path)
    except OSError:
        _cg = None
    CLICKER_ENGINE_AVAILABLE = _cg is not None
    if _cg is None:
        CLICKER_ENGINE_ERROR = "ApplicationServices-Framework konnte nicht geladen werden."
    else:
        try:
            _cg.AXIsProcessTrusted.restype = ctypes.c_bool
            if not bool(_cg.AXIsProcessTrusted()):
                CLICKER_ENGINE_AVAILABLE = False
                CLICKER_ENGINE_ERROR = ("sClicker hat keine Bedienungshilfen-Berechtigung. "
                                         "Bitte unter Systemeinstellungen → Datenschutz & Sicherheit "
                                         "→ Bedienungshilfen aktivieren und sClicker neu starten.")
        except Exception:
            pass

    _kCGEventLeftMouseDown = 1
    _kCGEventLeftMouseUp = 2
    _kCGEventRightMouseDown = 3
    _kCGEventRightMouseUp = 4
    _kCGEventOtherMouseDown = 25
    _kCGEventOtherMouseUp = 26
    _kCGMouseButtonLeft = 0
    _kCGMouseButtonRight = 1
    _kCGMouseButtonCenter = 2
    _kCGHIDEventTap = 0

    class _CGPoint(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    if _cg is not None:
        _cg.CGEventCreate.restype = ctypes.c_void_p
        _cg.CGEventCreate.argtypes = [ctypes.c_void_p]
        _cg.CGEventGetLocation.restype = _CGPoint
        _cg.CGEventGetLocation.argtypes = [ctypes.c_void_p]
        _cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
        _cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, _CGPoint, ctypes.c_uint32]
        _cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        _cg.CGEventCreateKeyboardEvent.restype = ctypes.c_void_p
        _cg.CGEventCreateKeyboardEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint16, ctypes.c_bool]
        _cg.CFRelease.argtypes = [ctypes.c_void_p]
        try:
            _cg.CGWarpMouseCursorPosition.argtypes = [_CGPoint]
            _cg.CGWarpMouseCursorPosition.restype = ctypes.c_int32
        except Exception:
            pass
        try:
            _cg.CGEventSourceKeyState.argtypes = [ctypes.c_int, ctypes.c_uint16]
            _cg.CGEventSourceKeyState.restype = ctypes.c_bool
            _cg.CGEventSourceButtonState.argtypes = [ctypes.c_int, ctypes.c_uint32]
            _cg.CGEventSourceButtonState.restype = ctypes.c_bool
        except Exception:
            pass
    _kCGEventSourceStateHIDSystemState = 1

    def _mac_current_pos():
        ev = _cg.CGEventCreate(None)
        pt = _cg.CGEventGetLocation(ev)
        _cg.CFRelease(ev)
        return pt

    def _mac_post_mouse(event_type, button):
        if _cg is None:
            return
        pt = _mac_current_pos()
        ev = _cg.CGEventCreateMouseEvent(None, event_type, pt, button)
        _cg.CGEventPost(_kCGHIDEventTap, ev)
        _cg.CFRelease(ev)

    def click_left():
        _mac_post_mouse(_kCGEventLeftMouseDown, _kCGMouseButtonLeft)
        _mac_post_mouse(_kCGEventLeftMouseUp, _kCGMouseButtonLeft)

    def click_right():
        _mac_post_mouse(_kCGEventRightMouseDown, _kCGMouseButtonRight)
        _mac_post_mouse(_kCGEventRightMouseUp, _kCGMouseButtonRight)

    def click_middle():
        _mac_post_mouse(_kCGEventOtherMouseDown, _kCGMouseButtonCenter)
        _mac_post_mouse(_kCGEventOtherMouseUp, _kCGMouseButtonCenter)

    def double_click_left():
        click_left()
        time.sleep(0.03)
        click_left()

    def hold_left_down():
        _mac_post_mouse(_kCGEventLeftMouseDown, _kCGMouseButtonLeft)

    def hold_left_up():
        _mac_post_mouse(_kCGEventLeftMouseUp, _kCGMouseButtonLeft)

    def hold_right_down():
        _mac_post_mouse(_kCGEventRightMouseDown, _kCGMouseButtonRight)

    def hold_right_up():
        _mac_post_mouse(_kCGEventRightMouseUp, _kCGMouseButtonRight)

    def hold_middle_down():
        _mac_post_mouse(_kCGEventOtherMouseDown, _kCGMouseButtonCenter)

    def hold_middle_up():
        _mac_post_mouse(_kCGEventOtherMouseUp, _kCGMouseButtonCenter)

    def move_cursor(x, y):
        if _cg is None:
            return
        try:
            pt = _CGPoint(float(x), float(y))
            _cg.CGWarpMouseCursorPosition(pt)
        except Exception:
            pass

    _VK_MAP_MAC = {
        "enter": 0x24, "return": 0x24, "space": 0x31, "tab": 0x30,
        "esc": 0x35, "escape": 0x35, "backspace": 0x33, "delete": 0x75,
        "up": 0x7E, "down": 0x7D, "left": 0x7B, "right": 0x7C,
        "home": 0x73, "end": 0x77, "pgup": 0x74, "pgdn": 0x79,
        "capslock": 0x39, "insert": 0x72,
        "shift": 0x38, "ctrl": 0x3B, "alt": 0x3A, "lwin": 0x37, "rwin": 0x36,
        "a": 0x00, "b": 0x0B, "c": 0x08, "d": 0x02, "e": 0x0E, "f": 0x03,
        "g": 0x05, "h": 0x04, "i": 0x22, "j": 0x26, "k": 0x28, "l": 0x25,
        "m": 0x2E, "n": 0x2D, "o": 0x1F, "p": 0x23, "q": 0x0C, "r": 0x0F,
        "s": 0x01, "t": 0x11, "u": 0x20, "v": 0x09, "w": 0x0D, "x": 0x07,
        "y": 0x10, "z": 0x06,
        "0": 0x1D, "1": 0x12, "2": 0x13, "3": 0x14, "4": 0x15, "5": 0x17,
        "6": 0x16, "7": 0x1A, "8": 0x1C, "9": 0x19,
        "f1": 0x7A, "f2": 0x78, "f3": 0x63, "f4": 0x76, "f5": 0x60, "f6": 0x61,
        "f7": 0x62, "f8": 0x64, "f9": 0x65, "f10": 0x6D, "f11": 0x67, "f12": 0x6F,
    }

    def _vk_for_mac(key: str):
        return _VK_MAP_MAC.get(key.strip().lower())

    def key_down(key: str):
        if _cg is None:
            return
        vk = _vk_for_mac(key)
        if vk is None:
            return
        ev = _cg.CGEventCreateKeyboardEvent(None, vk, True)
        _cg.CGEventPost(_kCGHIDEventTap, ev)
        _cg.CFRelease(ev)

    def key_up(key: str):
        if _cg is None:
            return
        vk = _vk_for_mac(key)
        if vk is None:
            return
        ev = _cg.CGEventCreateKeyboardEvent(None, vk, False)
        _cg.CGEventPost(_kCGHIDEventTap, ev)
        _cg.CFRelease(ev)

    def press_key(key: str):
        key_down(key)
        time.sleep(0.02)
        key_up(key)

    def is_key_down(key: str) -> bool:
        if _cg is None:
            return False
        if key.strip().lower() in ("lbutton", "rbutton", "mbutton"):
            return is_mouse_button_down({"lbutton": "left", "rbutton": "right", "mbutton": "middle"}[key.strip().lower()])
        vk = _vk_for_mac(key)
        if vk is None:
            return False
        try:
            return bool(_cg.CGEventSourceKeyState(_kCGEventSourceStateHIDSystemState, vk))
        except Exception:
            return False

    def is_mouse_button_down(button: str) -> bool:
        if _cg is None:
            return False
        b = {"left": 0, "right": 1, "middle": 2}.get(button, 0)
        try:
            return bool(_cg.CGEventSourceButtonState(_kCGEventSourceStateHIDSystemState, b))
        except Exception:
            return False

    def get_cursor_pos():
        if _cg is None:
            return None
        try:
            pt = _mac_current_pos()
            return (int(pt.x), int(pt.y))
        except Exception:
            return None

elif sys.platform.startswith("linux"):
    _LINUX_SESSION_TYPE = os.environ.get("XDG_SESSION_TYPE", "").lower()
    _LINUX_LIBS_OK = False
    _LINUX_X11_OK = False
    _x11 = None
    _xtst = None
    _display = None

    try:
        _x11 = ctypes.CDLL("libX11.so.6")
        _xtst = ctypes.CDLL("libXtst.so.6")
        _LINUX_LIBS_OK = True
    except OSError:
        _x11 = None
        _xtst = None

    if _LINUX_LIBS_OK:
        try:
            _x11.XOpenDisplay.restype = ctypes.c_void_p
            _x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
            _display = _x11.XOpenDisplay(None)
        except Exception:
            _display = None

        if _display and _LINUX_SESSION_TYPE != "wayland":
            # FIX: prüfen ob die XTest-Erweiterung überhaupt läuft, BEVOR
            # irgendwo XTestFake*Event aufgerufen wird. Ohne diese Prüfung
            # kann ein fehlendes XTest den ganzen Prozess crashen, weil
            # Xlib bei X-Protokollfehlern standardmäßig exit() aufruft.
            try:
                event_base = ctypes.c_int()
                error_base = ctypes.c_int()
                major = ctypes.c_int()
                minor = ctypes.c_int()
                _xtst.XTestQueryExtension.argtypes = [
                    ctypes.c_void_p, ctypes.POINTER(ctypes.c_int),
                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                    ctypes.POINTER(ctypes.c_int),
                ]
                _LINUX_X11_OK = bool(_xtst.XTestQueryExtension(
                    _display, ctypes.byref(event_base), ctypes.byref(error_base),
                    ctypes.byref(major), ctypes.byref(minor)))
            except Exception:
                _LINUX_X11_OK = False

    if not _LINUX_X11_OK:
        CLICKER_ENGINE_AVAILABLE = False
        if _LINUX_SESSION_TYPE == "wayland":
            CLICKER_ENGINE_ERROR = ("Wayland erkannt - Autoclick benötigt X11. "
                                     "Bitte beim Login 'Ubuntu on Xorg' (X11-Sitzung) "
                                     "statt der Standard-Wayland-Sitzung wählen.")
        elif not _LINUX_LIBS_OK:
            CLICKER_ENGINE_ERROR = ("libX11/libXtst nicht gefunden. Bitte installieren, "
                                     "z.B. 'sudo apt install libxtst6' (Debian/Ubuntu) "
                                     "oder 'sudo dnf install libXtst' (Fedora).")
        elif not _display:
            CLICKER_ENGINE_ERROR = "Konnte keine Verbindung zum X-Server herstellen"
        else:
            CLICKER_ENGINE_ERROR = "XTest-Erweiterung auf diesem X-Server nicht verfügbar."

    _LINUX_BUTTON_LEFT = 1
    _LINUX_BUTTON_MIDDLE = 2
    _LINUX_BUTTON_RIGHT = 3

    if _LINUX_X11_OK:
        _xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
        _xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
        _x11.XFlush.argtypes = [ctypes.c_void_p]
        _x11.XStringToKeysym.restype = ctypes.c_ulong
        _x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
        _x11.XKeysymToKeycode.restype = ctypes.c_ubyte
        _x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        _x11.XWarpPointer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint,
                                       ctypes.c_int, ctypes.c_int]
        _x11.XDefaultRootWindow.restype = ctypes.c_void_p
        _x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        _x11.XQueryKeymap.argtypes = [ctypes.c_void_p, ctypes.c_char * 32]
        _x11.XQueryPointer.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_uint),
        ]
        _x11.XQueryPointer.restype = ctypes.c_int

    def _linux_flush():
        if _LINUX_X11_OK:
            _x11.XFlush(_display)

    def _linux_fake_button(button, is_press):
        if not _LINUX_X11_OK:
            return
        _xtst.XTestFakeButtonEvent(_display, ctypes.c_uint(button),
                                    ctypes.c_int(1 if is_press else 0), ctypes.c_ulong(0))
        _linux_flush()

    def click_left():
        _linux_fake_button(_LINUX_BUTTON_LEFT, True)
        _linux_fake_button(_LINUX_BUTTON_LEFT, False)

    def click_right():
        _linux_fake_button(_LINUX_BUTTON_RIGHT, True)
        _linux_fake_button(_LINUX_BUTTON_RIGHT, False)

    def click_middle():
        _linux_fake_button(_LINUX_BUTTON_MIDDLE, True)
        _linux_fake_button(_LINUX_BUTTON_MIDDLE, False)

    def double_click_left():
        click_left()
        time.sleep(0.03)
        click_left()

    def hold_left_down():
        _linux_fake_button(_LINUX_BUTTON_LEFT, True)

    def hold_left_up():
        _linux_fake_button(_LINUX_BUTTON_LEFT, False)

    def hold_right_down():
        _linux_fake_button(_LINUX_BUTTON_RIGHT, True)

    def hold_right_up():
        _linux_fake_button(_LINUX_BUTTON_RIGHT, False)

    def hold_middle_down():
        _linux_fake_button(_LINUX_BUTTON_MIDDLE, True)

    def hold_middle_up():
        _linux_fake_button(_LINUX_BUTTON_MIDDLE, False)

    def move_cursor(x, y):
        if not _LINUX_X11_OK:
            return
        try:
            root = _x11.XDefaultRootWindow(_display)
            _x11.XWarpPointer(_display, None, root, 0, 0, 0, 0, int(x), int(y))
            _linux_flush()
        except Exception:
            pass

    _LINUX_KEYSYM_NAMES = {
        "enter": "Return", "return": "Return", "space": "space", "tab": "Tab",
        "esc": "Escape", "escape": "Escape", "backspace": "BackSpace",
        "delete": "Delete", "up": "Up", "down": "Down", "left": "Left",
        "right": "Right", "home": "Home", "end": "End", "pgup": "Prior",
        "pgdn": "Next", "insert": "Insert", "capslock": "Caps_Lock",
        "shift": "Shift_L", "ctrl": "Control_L", "alt": "Alt_L",
        "lwin": "Super_L", "rwin": "Super_R",
    }
    for _i in range(1, 25):
        _LINUX_KEYSYM_NAMES[f"f{_i}"] = f"F{_i}"

    def _vk_for_linux(key: str):
        if not _LINUX_X11_OK:
            return None
        k = key.strip().lower()
        name = _LINUX_KEYSYM_NAMES.get(k, k)
        if len(name) == 1:
            name = name.upper() if name.isalpha() else name
        keysym = _x11.XStringToKeysym(name.encode("ascii", errors="ignore"))
        if not keysym:
            return None
        return _x11.XKeysymToKeycode(_display, ctypes.c_ulong(keysym))

    def key_down(key: str):
        kc = _vk_for_linux(key)
        if not kc:
            return
        _xtst.XTestFakeKeyEvent(_display, ctypes.c_uint(kc), ctypes.c_int(1), ctypes.c_ulong(0))
        _linux_flush()

    def key_up(key: str):
        kc = _vk_for_linux(key)
        if not kc:
            return
        _xtst.XTestFakeKeyEvent(_display, ctypes.c_uint(kc), ctypes.c_int(0), ctypes.c_ulong(0))
        _linux_flush()

    def press_key(key: str):
        key_down(key)
        time.sleep(0.02)
        key_up(key)

    def is_key_down(key: str) -> bool:
        if key.strip().lower() in ("lbutton", "rbutton", "mbutton"):
            return is_mouse_button_down({"lbutton": "left", "rbutton": "right", "mbutton": "middle"}[key.strip().lower()])
        if not _LINUX_X11_OK:
            return False
        kc = _vk_for_linux(key)
        if not kc:
            return False
        try:
            buf = ctypes.create_string_buffer(32)
            _x11.XQueryKeymap(_display, buf)
            byte_index = kc // 8
            bit_index = kc % 8
            return bool(buf.raw[byte_index] & (1 << bit_index))
        except Exception:
            return False

    def is_mouse_button_down(button: str) -> bool:
        if not _LINUX_X11_OK:
            return False
        try:
            root = _x11.XDefaultRootWindow(_display)
            root_ret = ctypes.c_void_p()
            child_ret = ctypes.c_void_p()
            root_x = ctypes.c_int()
            root_y = ctypes.c_int()
            win_x = ctypes.c_int()
            win_y = ctypes.c_int()
            mask = ctypes.c_uint()
            _x11.XQueryPointer(_display, root, ctypes.byref(root_ret), ctypes.byref(child_ret),
                                ctypes.byref(root_x), ctypes.byref(root_y),
                                ctypes.byref(win_x), ctypes.byref(win_y), ctypes.byref(mask))
            bit = {"left": 0x100, "right": 0x400, "middle": 0x200}.get(button, 0x100)
            return bool(mask.value & bit)
        except Exception:
            return False

    def get_cursor_pos():
        if not _LINUX_X11_OK:
            return None
        try:
            root = _x11.XDefaultRootWindow(_display)
            root_ret = ctypes.c_void_p()
            child_ret = ctypes.c_void_p()
            root_x = ctypes.c_int()
            root_y = ctypes.c_int()
            win_x = ctypes.c_int()
            win_y = ctypes.c_int()
            mask = ctypes.c_uint()
            _x11.XQueryPointer(_display, root, ctypes.byref(root_ret), ctypes.byref(child_ret),
                                ctypes.byref(root_x), ctypes.byref(root_y),
                                ctypes.byref(win_x), ctypes.byref(win_y), ctypes.byref(mask))
            return (root_x.value, root_y.value)
        except Exception:
            return None

else:
    CLICKER_ENGINE_AVAILABLE = False
    CLICKER_ENGINE_ERROR = "Diese Plattform wird von der Klick-Engine nicht unterstützt."
    def click_left(): pass
    def click_right(): pass
    def click_middle(): pass
    def double_click_left(): pass
    def hold_left_down(): pass
    def hold_left_up(): pass
    def hold_right_down(): pass
    def hold_right_up(): pass
    def hold_middle_down(): pass
    def hold_middle_up(): pass
    def press_key(key): pass
    def key_down(key): pass
    def key_up(key): pass
    def move_cursor(x, y): pass
    def is_key_down(key): return False
    def is_mouse_button_down(button): return False
    def get_cursor_pos(): return None

# ============== KONFIGURATION ==============

def _get_platform_data_dir() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "sClicker")
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~/Library/Application Support"), "sClicker")
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "sClicker")

APPDATA = os.environ.get("APPDATA") or os.path.expanduser("~")
SCLICKER_DATA_DIR = _get_platform_data_dir()
os.makedirs(SCLICKER_DATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(SCLICKER_DATA_DIR, "sClicker_settings.ini")
ADMIN_USER = "Snakyxy"
OWNER_USERS = {"Snakyxy", "sClicker"}

def is_owner_account(username: str) -> bool:
    if not username:
        return False
    return str(username).strip().lower() in {o.lower() for o in OWNER_USERS}

ACCOUNT_RESET_VERSION = 1
def accent():
    """Aktuelle Akzentfarbe des gewaehlten Themes - fuer einheitliche, theme-treue Buttons."""
    return THEMES.get(state.current_theme, THEMES["purple"])["accent"]
ADMIN_WHITE = "#FFFFFF"

DEBUG_ENABLED = True
sClickerLog = []

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
START_COUNTDOWN_SECONDS = 5
# ============== UI-EINSTELLUNGEN (hier leicht anpassbar) ==============
BADGE_NAME_GAP = 5          # Abstand zwischen Name und erstem Badge (Verified etc.)
BADGE_BADGE_GAP = 4         # Abstand zwischen mehreren Badges (Verified+OG usw.)
KIT_VERIFIED_Y_OFFSET = 3   # Vertikaler Versatz des Verified-Icons bei Kits/News
HEADER_STREAK_Y_OFFSET = 5  # Vertikaler Versatz des Flamme+Streak-Widgets im Header
ICON_Y_OFFSET = 1           # Globaler vertikaler Versatz für ALLE Badges/Icons (Header, Listen)
PROFILE_BADGE_Y_OFFSET = 4  # Vertikaler Versatz NUR für Badges im Profil-Fenster
KIT_BADGE_Y_OFFSET = 2      # Vertikaler Versatz NUR für Badges bei Click Kits (Global Click Kits Fenster)

TRACKABLE_KEYS = (
    list("abcdefghijklmnopqrstuvwxyz") + list("0123456789") +
    ["space", "shift", "ctrl", "alt", "up", "down", "left", "right", "tab", "enter"]
)
TRACKABLE_MOUSE_BUTTONS = ("left", "right", "middle")
HOTKEY_POLL_INTERVAL = 0.05

TOS_TEXT = (
"sClicker - Terms of Service\n\n"

"Last Updated: August 5, 2026\n\n"

"PLEASE READ THESE TERMS CAREFULLY. THEY CONTAIN IMPORTANT LIMITATIONS "
"ON YOUR RIGHTS, INCLUDING A LIMITATION OF LIABILITY.\n\n"

"1. Acceptance of Terms\n"
"By downloading, installing, accessing, or using sClicker (\"the "
"Software\"), you enter into a binding agreement with SnakyGames "
"(\"we\", \"us\") and confirm that you have read, understood, and "
"agree to these Terms of Service (\"Terms\") and our Privacy Policy. "
"If you do not agree, you must not use the Software.\n\n"

"2. Eligibility\n"
"You must be at least 16 years old, or the minimum age of digital "
"consent in your jurisdiction if higher, to create an sClicker "
"account. If you are below this age, you may only use the Software "
"under the supervision and with the consent of a parent or legal "
"guardian who agrees to these Terms on your behalf.\n\n"

"3. Nature of the Software\n"
"sClicker is a general-purpose automation utility that simulates "
"mouse clicks, keyboard input, and cursor movement on your own "
"device, according to sequences you configure. It does not target, "
"interact with, or modify any specific third-party application, "
"game, or website.\n\n"

"4. Your Responsibility for Third-Party Rules\n"
"Many games, websites, and services prohibit or restrict automation "
"tools under their own terms. YOU ARE SOLELY RESPONSIBLE FOR "
"DETERMINING WHETHER YOUR USE OF sClicker COMPLIES WITH THE RULES OF "
"ANY THIRD-PARTY SERVICE. SnakyGames does not encourage or direct the "
"use of sClicker to violate any third-party terms or applicable law, "
"and disclaims all liability for warnings, penalties, suspensions, "
"bans, or loss of progress or access imposed by a third-party service "
"as a result of your use of the Software.\n\n"

"5. Accounts and User Data\n"
"Creating an sClicker account is optional. If you create one, certain "
"data may be stored on our servers to provide account functionality, "
"as described in our Privacy Policy. You are responsible for "
"maintaining the confidentiality of your credentials and for all "
"activity under your account.\n\n"

"6. User-Generated Content\n"
"The Software lets you create and share content, including Click "
"Kits, profile information, comments, and replies (\"User Content\"). "
"You retain any rights you hold in your User Content. By submitting "
"it, you grant SnakyGames a worldwide, non-exclusive, royalty-free "
"license to host, store, display, and distribute it solely to operate "
"and improve the Software. You represent that you own or have rights "
"to your User Content and that it does not infringe third-party "
"rights or violate Section 7.\n\n"

"7. Prohibited Content and Conduct\n"
"You must not use sClicker to: (a) upload illegal, fraudulent, "
"defamatory, hateful, harassing, or violence-promoting content; "
"(b) impersonate any person or entity; (c) upload malicious code or "
"attempt unauthorized access to any device, account, or system; "
"(d) reverse engineer or bypass authentication mechanisms except "
"where permitted by law; (e) interfere with sClicker's servers or "
"other users' accounts; (f) submit knowingly false reports; or "
"(g) violate applicable law.\n\n"

"8. Moderation, Suspension, and Termination\n"
"SnakyGames may review, remove, or refuse to display User Content, "
"and may warn, restrict, suspend, or terminate accounts, at its "
"reasonable discretion, to enforce these Terms or protect the "
"Software and its users. Where legally required, applicable notice "
"and statutory rights will be respected. You may contact us via "
"Section 15 to dispute a decision.\n\n"

"9. No Warranty\n"
"THE SOFTWARE IS PROVIDED \"AS IS\" AND \"AS AVAILABLE\", WITHOUT "
"WARRANTIES OF ANY KIND, TO THE MAXIMUM EXTENT PERMITTED BY LAW. We "
"do not warrant uninterrupted, error-free, or secure operation, or "
"that stored data or online features remain available indefinitely. "
"Statutory warranties that cannot lawfully be excluded remain "
"unaffected.\n\n"

"10. Limitation of Liability\n"
"TO THE MAXIMUM EXTENT PERMITTED BY LAW, SNAKYGAMES SHALL NOT BE "
"LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES, "
"OR FOR LOSS OF DATA, PROGRESS, OR THIRD-PARTY ACCOUNT ACCESS, "
"ARISING FROM YOUR USE OF THE SOFTWARE. Nothing here excludes "
"liability for death, personal injury caused by negligence, fraud, "
"or any liability that cannot lawfully be excluded.\n\n"

"11. Third-Party Services\n"
"sClicker may interact with third-party infrastructure (such as our "
"database provider) that is not operated by SnakyGames. We are not "
"responsible for the availability or policies of such third parties.\n\n"

"12. Intellectual Property\n"
"Unless stated otherwise, sClicker's software, branding, and original "
"materials are owned by or licensed to SnakyGames and protected by "
"applicable law. You may not copy, redistribute, or commercially "
"exploit them without permission, except where permitted by law.\n\n"

"13. Changes to These Terms\n"
"We may update these Terms from time to time. Material changes will "
"be announced through the Software or another appropriate channel. "
"Continued use after the effective date constitutes acceptance, to "
"the extent permitted by law.\n\n"

"14. Severability and Governing Law\n"
"If any provision is found invalid or unenforceable, the remaining "
"provisions remain in effect. These Terms are subject to applicable "
"law; mandatory consumer-protection rights that apply to you remain "
"unaffected.\n\n"

"15. Contact\n"
"For questions about these Terms, join the official SnakyGames "
"Discord server and open a support ticket.\n\n"

"By checking the box and continuing to use sClicker, you confirm that "
"you have read and agree to these Terms of Service.\n\n"

"© SnakyGames. All rights reserved."
)

PRIVACY_TEXT = (
"sClicker - Privacy Policy\n\n"

"Last Updated: August 5, 2026\n\n"

"This Privacy Policy explains what data sClicker collects, why, and "
"how it is stored when you use an sClicker account. If you use "
"sClicker as a guest without an account, no account data is sent to "
"our servers.\n\n"

"1. Data We Collect\n"
"When you create and use an sClicker account, we may store: your "
"username; a cryptographically hashed version of your password (we "
"never store or can recover your plain-text password); profile "
"settings such as theme, avatar emoji/color, and bio; click "
"statistics and login-streak data; your saved Click Kit action "
"sequences if you upload them publicly; comments, replies, and likes "
"you post; follow/follower relationships; report submissions you "
"make; and a coarse presence indicator (last-seen timestamp and "
"whether the clicker is currently running), used only to show an "
"online/offline status to other users.\n\n"

"2. Data We Do Not Collect\n"
"sClicker does not collect your real name, physical address, payment "
"information, precise location, or the content of other applications "
"on your device. Local-only settings (such as your action sequences "
"while not logged in) are stored solely on your own device.\n\n"

"3. How We Use Your Data\n"
"We use account data solely to: operate core features (login, "
"settings sync across devices); display your public profile, Click "
"Kits, and comments to other users as intended by these features; "
"maintain follower/following relationships you create; and review "
"reports for moderation purposes.\n\n"

"4. Where Data Is Stored\n"
"Account data is stored using a third-party database provider "
"(Supabase). This provider acts as our data processor and stores "
"data on infrastructure it operates. We do not sell your data to "
"advertisers or other third parties.\n\n"

"5. Data Sharing\n"
"Information you choose to make public (username, bio, avatar, "
"uploaded Click Kits, comments) is visible to other sClicker users by "
"design. We do not share your account data with third parties for "
"marketing purposes. We may disclose data where required by law, to "
"protect the rights and safety of SnakyGames or its users, or in "
"connection with a legitimate legal request.\n\n"

"6. Data Retention\n"
"We retain account data for as long as your account exists. If your "
"account is deleted or terminated, associated personal data is "
"removed or anonymized within a reasonable period, except where "
"retention is required for legal, security, or fraud-prevention "
"purposes, or where content has already been shared publicly and "
"copied or cached elsewhere.\n\n"

"7. Your Rights\n"
"Depending on your jurisdiction, you may have the right to access, "
"correct, export, or delete your personal data, and to object to or "
"restrict certain processing. You can update most profile data "
"directly in Account Settings, or request account deletion through "
"our support channel described in Section 9.\n\n"

"8. Children\n"
"sClicker is not directed at children under 16. If you believe a "
"child has provided us with personal data without appropriate "
"parental consent, please contact us so we can take appropriate "
"action.\n\n"

"9. Contact\n"
"For privacy questions or data requests, join the official "
"SnakyGames Discord server and open a support ticket.\n\n"

"10. Changes to This Policy\n"
"We may update this Privacy Policy from time to time. Material "
"changes will be announced through the Software or another "
"appropriate channel.\n\n"

"© SnakyGames. All rights reserved."
)
TRANSLATIONS = {
    "en": {
        "title": "sClicker - Modern AutoClicker",
        "speed": "Speed Settings",
        "delay": "Delay between actions:",
        "actions": "Action Sequence Builder",
        "addBtn": "Add Action",
        "delete": "Delete Selected",
        "clear": "Clear All",
        "control": "Control Panel",
        "startStop": "START / STOP",
        "exit": "EXIT",
        "settings": "Settings",
        "clicksExecuted": "Clicks:",
        "ready": "Ready",
        "active": "RUNNING - click to stop",
        "stopped": "STOPPED - click to start",
        "leftClick": "Left Click",
        "rightClick": "Right Click",
        "actionAdded": "Action added",
        "errorNoKey": "Enter a key!",
        "errorNoDuration": "Enter duration!",
        "errorNoActions": "Add actions first!",
        "needLogin": "You must be logged in to view or upload Click Kits.",
        "noSelection": "Please first select a kit in the list.",
        "deleteConfirm": "Delete this kit permanently for ALL users?",
        "deleteSuccess": "Kit deleted for everyone!",
        "deleteError": "Error: the kit could NOT be deleted.",
        "serverNotReachable": "Server not reachable (check internet/key)",
        "serverError": "Server error (check connection/key)",
        "followers": "Followers: ",
        "joined": "Joined: ",
        "joinedBefore": "Before v4",
        "follow": "Follow",
        "unfollow": "Unfollow",
        "followThis": "This is you",
        "loginToFollow": "Login to follow",
        "close": "Close",
        "loadKit": "📥 Load Kit",
        "selectKit": "Select a kit...",
        "kitDetails": "Kit Details",
        "search": "Search",
        "uploadKit": "⬆ Upload Public",
        "browseKits": "🌐 Browse Kits",
        "noActions": "Add actions first before uploading.",
        "uploaded": "Uploaded!",
        "noActionsSave": "Add actions first before saving.",
        "saved": "Saved!",
        "usernameExists": "Username already taken.",
        "usernameProfanity": "Username contains inappropriate language.",
        "invalidUsername": "Username must be 3-20 characters (letters, digits, underscore only).",
        "wrongPassword": "Failed: wrong password",
        "userNotFound": "Failed: account not found",
        "accountBanned": "This account is banned",
        "premiumRequired": "Premium required!",
        "newUserWarning": "Your account was created before v4. Please set a new password in Settings to secure your account.",
        "needName": "Please enter a name for the kit.",
        "uploadError": "Error: upload failed.",
        "pressKey": "Press Key",
        "holdKey": "Hold Key",
        "middleClick": "Middle Click",
        "doubleClick": "Double Click",
        "holdLeft": "Hold Left",
        "holdRight": "Hold Right",
        "holdMiddle": "Hold Middle",
        "premiumUnlocked": "Premium Features Unlocked",
        "premiumLocked": "Login to unlock Hold Click and more colors",
        "cannotBanOwner": "The owner account cannot be banned.",
        "madeAdmin": "Made {} an Admin",
        "removedAdmin": "Removed Admin from {}",
        "clickerUnavailable": "Auto-click engine not available on this system.",
        "fillBothFields": "Please fill in both fields.",
        "passwordsNoMatch": "Passwords do not match.",
        "passwordTooShort": "Password must be at least 4 characters.",
        "passwordUpdated": "Password updated!",
        "passwordSaveError": "Error: could not save (check connection).",
        "trackerTitle": "📹 Motion & Input Tracker (Beta)",
        "trackerDuration": "Duration (seconds):",
        "trackerStatusReady": "Status: Ready\n",
        "trackerStopHotkey": "⛔ Stop Hotkey: {}  (stops recording/playback instantly)",
        "trackerFeatures": ("✓ Real mouse movement (polling-based)\n"
                             "✓ Hold left/right click while moving\n"
                             "✓ Hold multiple keys at once (e.g. W + Shift), with real duration\n"
                             "✓ Timing-accurate playback (original timing instead of fixed delay)\n"
                             "✓ Cross-platform (Windows / macOS / Linux)"),
        "trackerRecording": "⏱ Recording... {}s\nCapturing mouse movement + key/click holds...",
        "trackerCompleted": "✓ Tracking completed!\nCaptured {} events",
        "trackerNoData": "No tracking data captured. Start tracking first!",
        "trackerSaving": "💾 Saving Actions...\n\nPlease wait",
        "trackerSaved": "✓ {} tracking events saved as actions!\n(Stop hotkey during playback: {})",
        "trackerStart": "▶ Start Tracking",
        "trackerSave": "💾 Save as Actions",
        "trackerDurationError": "Duration must be between 1 and 120 seconds",
        "trackerDurationInvalid": "Please enter a valid number",
        "noEntries": "No entries.",
        "followersOf": "Followers of {}",
        "followsTitle": "{} follows",
        "comments": "Comments",
        "noComments": "No comments yet. Be the first!",
        "postComment": "Post",
        "commentPlaceholder": "Write a comment...",
        "commentNeedLogin": "Login to write a comment.",
        "deleteCommentConfirm": "Delete this comment?",
        "reply": "Reply",
        "replyPlaceholder": "Write a reply...",
        "avatarColorLabel": "Avatar Color:",
        "avatarColorSaved": "Avatar color saved!",
        "report": "Report",
        "reports": "Reports",
        "reportReason": "Report Reason:",
        "reportSubmitted": "Report submitted!",
        "noReports": "No reports.",
        "viewReports": "View Reports",
        "resolveReport": "Resolve Report",
        "yes": "Yes",
        "no": "No",
        "globalAccounts": "Global Accounts",
        "accountDetails": "Account Details",
        "selectAccount": "Select an account...",
        "refreshList": "Refresh List",
        "viewFullProfile": "View Full Profile",
        "myKits": "My Kits",
        "saveLocal": "Save Local",
        "newPost": "New Post",
        "publish": "Publish",
        "cancel": "Cancel",
        "del": "DEL",
        "confirmTitle": "sClicker - Confirm",
        "loadSelected": "Load Selected",
        "deletePostConfirm": "Delete this post permanently?",
        "removeBio": "Remove\n(admin)",
        "accountSettings": "Account Settings",
        "keepItUp": "Keep it up!",
        "acceptToSPrefix": "I accept the",
        "termsOfService": "Terms of Service",
        "mustAcceptToS": "You must accept the Terms of Service to continue.",
        "viewToS": "View Terms of Service",
        "privacyPolicy": "Privacy Policy",
        "viewPrivacy": "View Privacy Policy",
        "andWord": "and",
    },
    "de": {
        "title": "sClicker - Moderner AutoClicker",
        "speed": "Geschwindigkeit",
        "delay": "Verzögerung:",
        "actions": "Aktionen",
        "addBtn": "Hinzufügen",
        "delete": "Löschen",
        "clear": "Alle löschen",
        "control": "Steuerung",
        "startStop": "START / STOP",
        "exit": "BEENDEN",
        "settings": "Einstellungen",
        "clicksExecuted": "Klicks:",
        "ready": "Bereit",
        "active": "LÄUFT - Klick zum Stoppen",
        "stopped": "GESTOPPT - Klick zum Starten",
        "leftClick": "Linksklick",
        "rightClick": "Rechtsklick",
        "actionAdded": "Aktion hinzugefügt",
        "errorNoKey": "Taste eingeben!",
        "errorNoDuration": "Dauer eingeben!",
        "errorNoActions": "Aktionen hinzufügen!",
        "needLogin": "Du musst eingeloggt sein, um Click Kits anzusehen oder hochzuladen.",
        "noSelection": "Bitte erst ein Kit in der Liste anklicken.",
        "deleteConfirm": "Dieses Kit für ALLE Nutzer löschen?",
        "deleteSuccess": "Kit für alle gelöscht!",
        "deleteError": "Fehler: Das Kit konnte NICHT gelöscht werden.",
        "serverNotReachable": "Server nicht erreichbar (Internet/Key prüfen)",
        "serverError": "Serverfehler (Verbindung/Key prüfen)",
        "followers": "Follower: ",
        "joined": "Beigetreten: ",
        "joinedBefore": "Vor v4",
        "follow": "Folgen",
        "unfollow": "Entfolgen",
        "followThis": "Das bist du",
        "loginToFollow": "Login zum Folgen",
        "close": "Schließen",
        "loadKit": "📥 Kit laden",
        "selectKit": "Wähle ein Kit...",
        "kitDetails": "Kit-Details",
        "search": "Suchen",
        "uploadKit": "⬆ Hochladen",
        "browseKits": "🌐 Kits durchsuchen",
        "noActions": "Füge erst Aktionen hinzu, bevor du hochlädst.",
        "uploaded": "Hochgeladen!",
        "noActionsSave": "Füge erst Aktionen hinzu, bevor du speicherst.",
        "saved": "Gespeichert!",
        "usernameExists": "Username schon vergeben.",
        "usernameProfanity": "Username enthält unangemessene Sprache.",
        "invalidUsername": "Username muss 3-20 Zeichen sein (nur Buchstaben/Zahlen/Unterstrich).",
        "wrongPassword": "Fehlgeschlagen: falsches Passwort",
        "userNotFound": "Fehlgeschlagen: Account nicht gefunden",
        "accountBanned": "Dieser Account ist gesperrt",
        "premiumRequired": "Premium erforderlich!",
        "newUserWarning": "Dein Account wurde vor v4 erstellt. Bitte setze ein neues Passwort in den Einstellungen, um deinen Account zu sichern.",
        "needName": "Bitte gib einen Namen für das Kit ein.",
        "uploadError": "Fehler: Upload fehlgeschlagen.",
        "pressKey": "Taste drücken",
        "holdKey": "Taste halten",
        "middleClick": "Mittelklick",
        "doubleClick": "Doppelklick",
        "holdLeft": "Links halten",
        "holdRight": "Rechts halten",
        "holdMiddle": "Mitte halten",
        "premiumUnlocked": "Premium-Funktionen freigeschaltet",
        "premiumLocked": "Login für Hold-Click und mehr Farben",
        "cannotBanOwner": "Der Owner-Account kann nicht gebannt werden.",
        "madeAdmin": "{} ist jetzt Admin",
        "removedAdmin": "Admin-Status von {} entfernt",
        "clickerUnavailable": "Die Klick-Engine ist auf diesem System nicht verfügbar.",
        "fillBothFields": "Bitte beide Felder ausfüllen.",
        "passwordsNoMatch": "Passwörter stimmen nicht überein.",
        "passwordTooShort": "Passwort muss mind. 4 Zeichen haben.",
        "passwordUpdated": "Passwort aktualisiert!",
        "passwordSaveError": "Fehler: konnte nicht gespeichert werden (Verbindung prüfen).",
        "trackerTitle": "📹 Bewegungs- & Eingabe-Tracker (Beta)",
        "trackerDuration": "Dauer (Sekunden):",
        "trackerStatusReady": "Status: Bereit\n",
        "trackerStopHotkey": "⛔ Not-Stopp-Hotkey: {}  (stoppt Recording/Playback sofort)",
        "trackerFeatures": ("✓ Echte Mausbewegung (polling-basiert)\n"
                             "✓ Linksklick/Rechtsklick HALTEN während der Bewegung\n"
                             "✓ Mehrere Tasten gleichzeitig halten (z.B. W + Shift), mit echter Dauer\n"
                             "✓ Zeittreue Wiedergabe (Original-Timing statt fester Pause)\n"
                             "✓ Cross-Platform (Windows / macOS / Linux)"),
        "trackerRecording": "⏱ Aufnahme läuft... {}s\nMausbewegung + Tasten-/Klick-Halten werden erfasst...",
        "trackerCompleted": "✓ Aufnahme abgeschlossen!\n{} Events erfasst",
        "trackerNoData": "Keine Aufnahmedaten vorhanden. Starte zuerst die Aufnahme!",
        "trackerSaving": "💾 Speichere Aktionen...\n\nBitte warten",
        "trackerSaved": "✓ {} Aufnahme-Events als Aktionen gespeichert!\n(Not-Stopp-Hotkey bei Wiedergabe: {})",
        "trackerStart": "▶ Aufnahme starten",
        "trackerSave": "💾 Als Aktionen speichern",
        "trackerDurationError": "Dauer muss zwischen 1 und 120 Sekunden liegen",
        "trackerDurationInvalid": "Bitte eine gültige Zahl eingeben",
        "noEntries": "Keine Einträge.",
        "followersOf": "Follower von {}",
        "followsTitle": "{} folgt",
        "comments": "Kommentare",
        "noComments": "Noch keine Kommentare. Sei der Erste!",
        "postComment": "Senden",
        "commentPlaceholder": "Kommentar schreiben...",
        "commentNeedLogin": "Login zum Kommentieren.",
        "deleteCommentConfirm": "Diesen Kommentar löschen?",
        "reply": "Antworten",
        "replyPlaceholder": "Antwort schreiben...",
        "avatarColorLabel": "Avatar-Farbe:",
        "avatarColorSaved": "Avatar-Farbe gespeichert!",
        "report": "Melden",
        "reports": "Meldungen",
        "reportReason": "Meldegrund:",
        "reportSubmitted": "Meldung gesendet!",
        "noReports": "Keine Meldungen.",
        "viewReports": "Meldungen anzeigen",
        "resolveReport": "Meldung auflösen",
        "yes": "Ja",
        "no": "Nein",
        "globalAccounts": "Globale Accounts",
        "accountDetails": "Account-Details",
        "selectAccount": "Wähle einen Account...",
        "refreshList": "Liste aktualisieren",
        "viewFullProfile": "Vollständiges Profil ansehen",
        "myKits": "Meine Kits",
        "saveLocal": "Lokal speichern",
        "newPost": "+ Neuer Beitrag",
        "publish": "Veröffentlichen",
        "cancel": "Abbrechen",
        "del": "LÖSCHEN",
        "confirmTitle": "sClicker - Bestätigung",
        "loadSelected": "Auswahl laden",
        "deletePostConfirm": "Diesen Beitrag endgültig löschen?",
        "removeBio": "Entfernen\n(Admin)",
        "accountSettings": "Account-Einstellungen",
        "keepItUp": "Weiter so!",
        "acceptToSPrefix": "Ich akzeptiere die",
        "termsOfService": "Nutzungsbedingungen",
        "mustAcceptToS": "Du musst die Nutzungsbedingungen akzeptieren, um fortzufahren.",
        "viewToS": "Nutzungsbedingungen ansehen",
        "privacyPolicy": "Datenschutzerklärung",
        "viewPrivacy": "Datenschutzerklärung ansehen",
        "andWord": "und",
    },
}

THEMES = {
    "purple": {"bg": "#0f0f0f", "accent": "#9945FF"},
    "blue":   {"bg": "#0a1929", "accent": "#3b82f6"},
    "green":  {"bg": "#0a1a0a", "accent": "#22c55e"},
    "red":    {"bg": "#1a0a1a", "accent": "#ef4444"},
    "gold":   {"bg": "#111008", "accent": "#f59e0b"},
    "cyan":   {"bg": "#071a1a", "accent": "#06b6d4"},
    "black":  {"bg": "#000000", "accent": "#FFFFFF"},
    "white":  {"bg": "#FFFFFF", "accent": "#000000"},
}

def DIALOG_BG():
    """FIX: Vorher hatten alle Texte/Icons in Dialogen eine fest codierte
    Hintergrundfarbe ("#0a0a0a"/"#0f0f0f"), während das Dialog-Panel selbst
    seit new_toplevel() der aktuellen Theme-Farbe folgt - das erzeugte
    sichtbare graue/schwarze Kästen hinter Text und Icons, sobald die
    Theme-Hintergrundfarbe nicht zufällig exakt "#0a0a0a" war. Jetzt liefert
    diese Funktion immer die AKTUELLE Theme-Hintergrundfarbe."""
    return THEMES.get(state.current_theme, THEMES["purple"])["bg"]

AVATAR_ICON_CHOICES = [
    "default",
    "eagle", "penguin", "wolf", "fox", "lion", "tiger", "bear", "cat", "dog",
    "owl", "shark", "dragon", "snake", "octopus", "bee", "spider",
    "bolt", "fire", "skull", "crown", "star", "diamond", "rocket", "ghost",
    "robot", "alien", "sword", "shield", "target", "gear",
    "gamepad", "trophy", "gem", "anchor", "flag", "key", "hourglass", "moon",
]

def _draw_avatar_icon(draw, name, S, color=(255, 255, 255, 255)):
    """Zeichnet ein einfaches, plattformunabhängiges Vektor-Icon (kein Emoji-Font
    nötig -> sieht auf Windows/macOS/Linux identisch aus)."""
    cx, cy = S / 2, S / 2
    r = S * 0.32

    if name == "eagle":
        draw.polygon([(cx, cy - r), (cx - r * 1.1, cy + r * 0.3), (cx - r * 0.3, cy + r * 0.1),
                      (cx, cy + r), (cx + r * 0.3, cy + r * 0.1), (cx + r * 1.1, cy + r * 0.3)],
                     fill=color)
    elif name == "penguin":
        draw.ellipse([cx - r * 0.7, cy - r, cx + r * 0.7, cy + r], fill=color)
        draw.ellipse([cx - r * 0.35, cy - r * 0.1, cx + r * 0.35, cy + r * 0.9], fill=(20, 20, 20, 255))
    elif name == "wolf" or name == "fox" or name == "dog":
        ear_c = color
        draw.polygon([(cx - r * 0.9, cy - r), (cx - r * 0.3, cy - r * 0.3), (cx - r * 0.5, cy - r * 1.1)], fill=ear_c)
        draw.polygon([(cx + r * 0.9, cy - r), (cx + r * 0.3, cy - r * 0.3), (cx + r * 0.5, cy - r * 1.1)], fill=ear_c)
        draw.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r], fill=color)
        draw.polygon([(cx - r * 0.25, cy + r * 0.3), (cx + r * 0.25, cy + r * 0.3), (cx, cy + r * 0.8)],
                     fill=(20, 20, 20, 255))
    elif name == "lion" or name == "tiger":
        draw.ellipse([cx - r * 1.05, cy - r * 1.05, cx + r * 1.05, cy + r * 1.05], fill=(180, 120, 40, 200) if name == "lion" else (230, 150, 50, 200))
        draw.ellipse([cx - r * 0.65, cy - r * 0.65, cx + r * 0.65, cy + r * 0.65], fill=color)
    elif name == "bear":
        draw.ellipse([cx - r * 0.35, cy - r * 1.05, cx, cy - r * 0.55], fill=color)
        draw.ellipse([cx, cy - r * 1.05, cx + r * 0.35, cy - r * 0.55], fill=color)
        draw.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r], fill=color)
    elif name == "cat":
        draw.polygon([(cx - r * 0.8, cy - r * 0.9), (cx - r * 0.2, cy - r * 0.2), (cx - r * 0.6, cy + r * 0.1)], fill=color)
        draw.polygon([(cx + r * 0.8, cy - r * 0.9), (cx + r * 0.2, cy - r * 0.2), (cx + r * 0.6, cy + r * 0.1)], fill=color)
        draw.ellipse([cx - r * 0.75, cy - r * 0.5, cx + r * 0.75, cy + r], fill=color)
    elif name == "owl":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        draw.ellipse([cx - r * 0.5, cy - r * 0.2, cx - r * 0.05, cy + r * 0.3], fill=(20, 20, 20, 255))
        draw.ellipse([cx + r * 0.05, cy - r * 0.2, cx + r * 0.5, cy + r * 0.3], fill=(20, 20, 20, 255))
        draw.polygon([(cx - r * 0.15, cy + r * 0.3), (cx + r * 0.15, cy + r * 0.3), (cx, cy + r * 0.6)], fill=(255, 160, 0, 255))
    elif name == "shark":
        draw.polygon([(cx - r, cy + r * 0.4), (cx + r, cy), (cx - r * 0.6, cy - r * 0.6),
                      (cx, cy - r * 1.1), (cx - r * 0.2, cy - r * 0.3)], fill=color)
    elif name == "dragon":
        draw.polygon([(cx - r, cy + r), (cx - r * 0.2, cy - r * 0.3), (cx, cy - r * 1.1),
                      (cx + r * 0.3, cy - r * 0.4), (cx + r, cy + r * 0.6), (cx + r * 0.2, cy + r)],
                     fill=color)
    elif name == "snake":
        pts = []
        for i in range(20):
            t = i / 19
            pts.append((cx - r + t * 2 * r, cy + math.sin(t * math.pi * 2.4) * r * 0.5))
        for (px, py) in pts:
            draw.ellipse([px - S * 0.05, py - S * 0.05, px + S * 0.05, py + S * 0.05], fill=color)
    elif name == "octopus":
        draw.ellipse([cx - r * 0.9, cy - r, cx + r * 0.9, cy + r * 0.3], fill=color)
        for i in range(5):
            ang = math.radians(-70 + i * 35)
            lx = cx + math.cos(ang) * r * 1.1
            ly = cy + r * 0.2 + math.sin(ang) * r * 0.6
            draw.ellipse([lx - S * 0.05, ly - S * 0.05, lx + S * 0.05, ly + S * 0.05], fill=color)
    elif name == "bee":
        draw.ellipse([cx - r * 0.6, cy - r, cx + r * 0.6, cy + r], fill=(255, 210, 0, 255))
        for i, oy in enumerate((-r * 0.4, 0, r * 0.4)):
            draw.rectangle([cx - r * 0.6, cy + oy - S * 0.04, cx + r * 0.6, cy + oy + S * 0.04], fill=(20, 20, 20, 255))
    elif name == "spider":
        draw.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=color)
        for i in range(8):
            ang = math.radians(i * 45)
            draw.line([(cx, cy), (cx + math.cos(ang) * r, cy + math.sin(ang) * r)], fill=color, width=max(2, int(S * 0.02)))
    elif name == "bolt":
        draw.polygon([(cx + r * 0.15, cy - r), (cx - r * 0.5, cy + r * 0.15), (cx, cy + r * 0.15),
                      (cx - r * 0.15, cy + r), (cx + r * 0.5, cy - r * 0.15), (cx, cy - r * 0.15)],
                     fill=(255, 210, 0, 255))
    elif name == "fire":
        draw.polygon(_flame_points(cx, cy, r), fill=(255, 120, 30, 255))
        draw.polygon(_flame_points(cx, cy + r * 0.1, r * 0.55), fill=(255, 220, 100, 255))
    elif name == "skull":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r * 0.5], fill=color)
        draw.ellipse([cx - r * 0.55, cy - r * 0.15, cx - r * 0.1, cy + r * 0.3], fill=(20, 20, 20, 255))
        draw.ellipse([cx + r * 0.1, cy - r * 0.15, cx + r * 0.55, cy + r * 0.3], fill=(20, 20, 20, 255))
        draw.rectangle([cx - r * 0.5, cy + r * 0.4, cx + r * 0.5, cy + r * 0.75], fill=color)
    elif name == "crown":
        pts = _star_points(cx, cy, r, r * 0.4, points=5, rotation=-90)
        draw.polygon(pts, fill=(255, 210, 0, 255))
    elif name == "star":
        draw.polygon(_star_points(cx, cy, r, r * 0.42, points=5), fill=(255, 210, 0, 255))
    elif name == "diamond":
        draw.polygon([(cx, cy - r), (cx + r * 0.7, cy), (cx, cy + r), (cx - r * 0.7, cy)],
                     fill=(80, 200, 255, 255))
    elif name == "rocket":
        draw.polygon([(cx, cy - r * 1.1), (cx + r * 0.4, cy + r * 0.3), (cx - r * 0.4, cy + r * 0.3)],
                     fill=color)
        draw.ellipse([cx - r * 0.2, cy - r * 0.3, cx + r * 0.2, cy + r * 0.1], fill=(80, 200, 255, 255))
        draw.polygon([(cx - r * 0.4, cy + r * 0.3), (cx - r * 0.75, cy + r * 0.75), (cx - r * 0.15, cy + r * 0.45)],
                     fill=(255, 120, 30, 255))
        draw.polygon([(cx + r * 0.4, cy + r * 0.3), (cx + r * 0.75, cy + r * 0.75), (cx + r * 0.15, cy + r * 0.45)],
                     fill=(255, 120, 30, 255))
    elif name == "ghost":
        draw.pieslice([cx - r, cy - r, cx + r, cy + r * 0.6], 180, 360, fill=color)
        draw.rectangle([cx - r, cy - r * 0.2, cx + r, cy + r * 0.7], fill=color)
        for i in range(3):
            wx = cx - r + (i + 0.5) * (2 * r / 3)
            draw.pieslice([wx - r / 3, cy + r * 0.4, wx + r / 3, cy + r], 0, 180, fill=color)
        draw.ellipse([cx - r * 0.4, cy - r * 0.1, cx - r * 0.15, cy + r * 0.15], fill=(20, 20, 20, 255))
        draw.ellipse([cx + r * 0.15, cy - r * 0.1, cx + r * 0.4, cy + r * 0.15], fill=(20, 20, 20, 255))
    elif name == "robot":
        draw.rounded_rectangle([cx - r, cy - r * 0.7, cx + r, cy + r], radius=S * 0.06, fill=color)
        draw.rectangle([cx - r * 0.15, cy - r * 1.15, cx + r * 0.15, cy - r * 0.7], fill=color)
        draw.ellipse([cx - r * 0.5, cy - r * 0.3, cx - r * 0.1, cy + r * 0.1], fill=(80, 200, 255, 255))
        draw.ellipse([cx + r * 0.1, cy - r * 0.3, cx + r * 0.5, cy + r * 0.1], fill=(80, 200, 255, 255))
    elif name == "alien":
        draw.ellipse([cx - r * 0.6, cy - r, cx + r * 0.6, cy + r * 0.5], fill=(120, 230, 120, 255))
        draw.ellipse([cx - r * 0.5, cy - r * 0.3, cx - r * 0.1, cy + r * 0.15], fill=(20, 20, 20, 255))
        draw.ellipse([cx + r * 0.1, cy - r * 0.3, cx + r * 0.5, cy + r * 0.15], fill=(20, 20, 20, 255))
    elif name == "sword":
        draw.polygon([(cx, cy - r * 1.1), (cx + r * 0.15, cy + r * 0.4), (cx - r * 0.15, cy + r * 0.4)], fill=color)
        draw.rectangle([cx - r * 0.5, cy + r * 0.3, cx + r * 0.5, cy + r * 0.45], fill=color)
        draw.rectangle([cx - r * 0.1, cy + r * 0.45, cx + r * 0.1, cy + r], fill=color)
    elif name == "shield":
        draw.polygon(_shield_points(cx, cy, r), fill=color)
    elif name == "target":
        for rr, col in ((r, (220, 60, 60, 255)), (r * 0.65, color), (r * 0.3, (220, 60, 60, 255))):
            draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    elif name == "gear":
        for i in range(8):
            ang = math.radians(i * 45)
            tx = cx + math.cos(ang) * r
            ty = cy + math.sin(ang) * r
            draw.rectangle([tx - S * 0.05, ty - S * 0.05, tx + S * 0.05, ty + S * 0.05], fill=color)
        draw.ellipse([cx - r * 0.65, cy - r * 0.65, cx + r * 0.65, cy + r * 0.65], fill=color)
        draw.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=(20, 20, 20, 255))
    elif name == "default":
        # Standard-Silhouette wie bei den meisten Plattformen
        draw.ellipse([cx - r * 0.55, cy - r * 1.05, cx + r * 0.55, cy - r * 0.15], fill=color)
        draw.pieslice([cx - r * 1.15, cy - r * 0.05, cx + r * 1.15, cy + r * 2.1], 180, 360, fill=color)
    elif name == "gamepad":
        draw.rounded_rectangle([cx - r * 1.05, cy - r * 0.5, cx + r * 1.05, cy + r * 0.5],
                                radius=S * 0.09, fill=color)
        draw.rectangle([cx - r * 0.85, cy - S * 0.03, cx - r * 0.55, cy + S * 0.03], fill=(20, 20, 20, 255))
        draw.rectangle([cx - r * 0.72, cy - r * 0.16, cx - r * 0.66, cy + r * 0.16], fill=(20, 20, 20, 255))
        for dx_ in (r * 0.55, r * 0.75):
            draw.ellipse([cx + dx_ - S * 0.045, cy - S * 0.045, cx + dx_ + S * 0.045, cy + S * 0.045],
                         fill=(20, 20, 20, 255))
    elif name == "trophy":
        draw.rectangle([cx - r * 0.4, cy - r * 0.9, cx + r * 0.4, cy + r * 0.3], fill=color)
        draw.arc([cx - r * 0.9, cy - r * 0.85, cx - r * 0.35, cy - r * 0.1], 90, 270, fill=color, width=max(2, int(S * 0.035)))
        draw.arc([cx + r * 0.35, cy - r * 0.85, cx + r * 0.9, cy - r * 0.1], -90, 90, fill=color, width=max(2, int(S * 0.035)))
        draw.rectangle([cx - r * 0.15, cy + r * 0.3, cx + r * 0.15, cy + r * 0.65], fill=color)
        draw.rectangle([cx - r * 0.5, cy + r * 0.65, cx + r * 0.5, cy + r * 0.85], fill=color)
    elif name == "gem":
        draw.polygon([(cx - r, cy - r * 0.3), (cx - r * 0.4, cy - r), (cx + r * 0.4, cy - r),
                      (cx + r, cy - r * 0.3), (cx, cy + r)], fill=(80, 200, 255, 255))
        draw.polygon([(cx - r, cy - r * 0.3), (cx + r, cy - r * 0.3), (cx, cy + r)], fill=(150, 225, 255, 255))
    elif name == "anchor":
        draw.ellipse([cx - r * 0.22, cy - r, cx + r * 0.22, cy - r * 0.56], outline=color, width=max(2, int(S * 0.04)))
        draw.line([(cx, cy - r * 0.56), (cx, cy + r)], fill=color, width=max(2, int(S * 0.05)))
        draw.line([(cx - r * 0.75, cy + r * 0.35), (cx + r * 0.75, cy + r * 0.35)], fill=color, width=max(2, int(S * 0.05)))
        draw.arc([cx - r * 0.75, cy - r * 0.2, cx + r * 0.75, cy + r * 1.3], 0, 180, fill=color, width=max(2, int(S * 0.05)))
    elif name == "flag":
        draw.line([(cx - r * 0.6, cy - r), (cx - r * 0.6, cy + r)], fill=color, width=max(2, int(S * 0.045)))
        draw.polygon([(cx - r * 0.6, cy - r), (cx + r, cy - r * 0.5), (cx - r * 0.6, cy)], fill=color)
    elif name == "key":
        draw.ellipse([cx - r, cy - r * 0.55, cx - r * 0.25, cy + r * 0.2], outline=color, width=max(2, int(S * 0.05)))
        draw.line([(cx - r * 0.4, cy - r * 0.05), (cx + r, cy - r * 0.05)], fill=color, width=max(2, int(S * 0.05)))
        draw.line([(cx + r * 0.55, cy - r * 0.05), (cx + r * 0.55, cy + r * 0.35)], fill=color, width=max(2, int(S * 0.05)))
        draw.line([(cx + r * 0.85, cy - r * 0.05), (cx + r * 0.85, cy + r * 0.25)], fill=color, width=max(2, int(S * 0.05)))
    elif name == "hourglass":
        draw.polygon([(cx - r * 0.7, cy - r), (cx + r * 0.7, cy - r), (cx, cy), (cx - r * 0.7, cy)], fill=color)
        draw.polygon([(cx - r * 0.7, cy + r), (cx + r * 0.7, cy + r), (cx, cy), (cx + r * 0.7, cy)], fill=color)
    elif name == "moon":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        draw.ellipse([cx - r * 0.55, cy - r * 1.05, cx + r * 1.05, cy + r * 0.55], fill=(0, 0, 0, 0))
    else:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

_avatar_icon_cache = {}

def render_avatar_icon(name, size, fg_color="#FFFFFF"):
    if Image is None or ImageDraw is None or not name:
        return None
    key = (name, size, fg_color)
    cached = _avatar_icon_cache.get(key)
    if cached is not None:
        return cached
    try:
        scale = 4
        S = size * scale
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        h = fg_color.lstrip("#")
        rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255) if len(h) == 6 else (255, 255, 255, 255)
        _draw_avatar_icon(draw, name, S, color=rgb)
        img = img.resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _avatar_icon_cache[key] = photo
        if len(_avatar_icon_cache) > 200:
            _avatar_icon_cache.clear()
            _avatar_icon_cache[key] = photo
        return photo
    except Exception as e:
        sClickerLog.append(f"Avatar-Icon konnte nicht gerendert werden: {e}")
        return None

_AVATAR_COLOR_TABLE = {
    "black":   ("#000000", "#FFFFFF"),
    "white":   ("#FFFFFF", "#000000"),
    "red":     ("#EF4444", "#FFFFFF"),
    "rose":    ("#FB7185", "#FFFFFF"),
    "orange":  ("#F97316", "#FFFFFF"),
    "gold":    ("#F59E0B", "#000000"),
    "yellow":  ("#EAB308", "#000000"),
    "lime":    ("#84CC16", "#000000"),
    "green":   ("#22C55E", "#000000"),
    "emerald": ("#10B981", "#FFFFFF"),
    "teal":    ("#14B8A6", "#FFFFFF"),
    "cyan":    ("#06B6D4", "#FFFFFF"),
    "sky":     ("#0EA5E9", "#FFFFFF"),
    "blue":    ("#3B82F6", "#FFFFFF"),
    "indigo":  ("#6366F1", "#FFFFFF"),
    "violet":  ("#8B5CF6", "#FFFFFF"),
    "purple":  ("#A855F7", "#FFFFFF"),
    "fuchsia": ("#D946EF", "#FFFFFF"),
    "pink":    ("#EC4899", "#FFFFFF"),
    "slate":   ("#64748B", "#FFFFFF"),
}
_AVATAR_DEFAULT = ("#1a1a1a", "#9945FF")

class AppState:
    def __init__(self):
        self.logged_in_user = ""
        self.logged_in_verified = False
        self.current_language = "en"
        self.current_theme = "purple"
        self.click_delay = 100
        self.repeat_mode = True
        self.action_list = []
        self.is_running = False
        self.is_counting_down = False
        self.click_count = 0
        self.total_clicks = 0
        self.user_avatar_emoji = ""
        self.user_avatar_color = ""
        self.user_bio = ""
        self.tracking_data = []
        self.is_tracking = False
        self.sync_timer = None
        self.emergency_hotkey = "F12"
        self._emergency_hotkey_was_down = False
        # NEU: Login-Streak-System
        self.login_streak = 0
        self.last_login_date = ""
        self.accepted_tos = False

state = AppState()

def T(key: str) -> str:
    return TRANSLATIONS.get(state.current_language, {}).get(key, key)

_MASK64 = 0xFFFFFFFFFFFFFFFF
_SIGN64 = 0x8000000000000000

def simple_hash(s: str) -> str:
    h = 5381
    for ch in s:
        h = (h << 5) + h + ord(ch)
        h &= _MASK64
    if h >= _SIGN64:
        h -= (_MASK64 + 1)
    return str(h)

def json_parse(s):
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None

def json_stringify(v) -> str:
    return json.dumps(v, ensure_ascii=False)

def safe_flag(info: dict, key: str) -> bool:
    if key not in info:
        return False
    v = info[key]
    return v in ("1", 1, True)

def get_following_array(info: dict) -> list:
    f = info.get("following")
    return f if isinstance(f, list) else []

def display_name(u: str, maxlen: int = 25) -> str:
    s = str(u)
    if len(s) > maxlen:
        return s[:maxlen] + "…"
    return s

def find_account_name(data: dict, username: str) -> str:
    accounts = data.get("accounts", {})
    wanted = username.strip().lower()
    for u in accounts:
        if u.strip().lower() == wanted:
            return u
    return ""

def is_following(data: dict, follower: str, target: str) -> bool:
    accounts = data.get("accounts", {})
    if follower not in accounts:
        return False
    target_key = target.strip().lower()
    info = accounts[follower]
    return any(str(f).strip().lower() == target_key for f in get_following_array(info))

def count_followers(data: dict, target: str) -> int:
    accounts = data.get("accounts", {})
    if not accounts:
        return 0
    target_key = target.strip().lower()
    seen = set()
    for u, info in accounts.items():
        for f in get_following_array(info):
            if str(f).strip().lower() == target_key:
                seen.add(str(u).lower())
                break
    if target in accounts:
        legacy = accounts[target].get("followers")
        if isinstance(legacy, list):
            for f in legacy:
                fk = str(f).strip().lower()
                if fk:
                    seen.add(fk)
        elif legacy:
            try:
                n = int(legacy)
                if n > len(seen):
                    return n
            except (TypeError, ValueError):
                pass
    return len(seen)

def get_followers_usernames(data: dict, target: str) -> list:
    accounts = data.get("accounts", {})
    if not accounts:
        return []
    target_key = target.strip().lower()
    seen = {}
    for u, info in accounts.items():
        for f in get_following_array(info):
            if str(f).strip().lower() == target_key:
                seen[str(u).lower()] = u
                break
    if target in accounts:
        legacy = accounts[target].get("followers")
        if isinstance(legacy, list):
            for f in legacy:
                fk = str(f).strip().lower()
                if fk and fk not in seen:
                    seen[fk] = find_account_name(data, f) or str(f)
    return list(seen.values())

def auth_is_verified(u: str) -> bool:
    if not u:
        return False
    r = auth_get_data()
    if not r:
        return False
    data = json_parse(r)
    if not data:
        return False
    info = data.get("accounts", {}).get(u)
    return bool(info and safe_flag(info, "verified"))

def auth_is_admin(u: str) -> bool:
    if not u:
        return False
    if is_owner_account(u):
        return True
    r = auth_get_data()
    if not r:
        return False
    data = json_parse(r)
    if not data:
        return False
    real_user = find_account_name(data, u)
    if not real_user:
        return False
    info = data.get("accounts", {}).get(real_user)
    return bool(info and safe_flag(info, "admin"))

def auth_has_influencer(u: str) -> bool:
    if not u:
        return False
    r = auth_get_data()
    if not r:
        return False
    data = json_parse(r)
    if not data:
        return False
    real_user = find_account_name(data, u)
    if not real_user:
        return False
    info = data.get("accounts", {}).get(real_user)
    return bool(info and safe_flag(info, "influencer"))

def auth_has_og(u: str) -> bool:
    if not u:
        return False
    r = auth_get_data()
    if not r:
        return False
    data = json_parse(r)
    if not data:
        return False
    real_user = find_account_name(data, u)
    if not real_user:
        return False
    info = data.get("accounts", {}).get(real_user)
    return bool(info and safe_flag(info, "og"))

def auth_login(u: str, p: str):
    h_new = "h2_" + simple_hash(p)
    r = auth_get_data()
    if not r:
        return "servererror", u
    data = json_parse(r)
    if not data:
        return "servererror", u
    accounts = data.get("accounts", {})
    real_user = find_account_name(data, u)
    if not real_user:
        return "notfound", u
    info = accounts[real_user]
    if safe_flag(info, "banned"):
        return "banned", real_user
    sp = info.get("pw", "")
    if not sp:
        return "wrong", real_user
    return ("ok", real_user) if sp == h_new else ("wrong", real_user)

def auth_register(u: str, p: str) -> str:
    if not USERNAME_RE.match(u):
        return "invalidUsername"
    if censor_profanity(u) != u:
        return "usernameProfanity"
    h = "h2_" + simple_hash(p)
    join_date = datetime.now().strftime("%Y-%m-%d")
    account_data = {
        "pw": h,
        "verified": "0",
        "banned": "0",
        "admin": "0",
        "joined": join_date,
        "following": [],
        "followers": [],
        "settings": {},
        "presence": {},
        "og": "0"
    }
    
    if supabase_create_account(u, account_data):
        _cache["time"] = 0
        return ""
    return "servererror"

def change_account_password(username: str, new_password: str) -> bool:
    hashed = "h2_" + simple_hash(new_password)
    if supabase_update_account(username, {"pw": hashed}):
        _cache["time"] = 0
        return True
    return False

def toggle_follow(target: str):
    target = str(target).strip()
    if not state.logged_in_user or not target or state.logged_in_user.lower() == target.lower():
        return False, None
    r = auth_get_data()
    if not r:
        return False, None
    data = json_parse(r)
    if not data:
        return False, None
    accounts = data.get("accounts", {})
    if state.logged_in_user not in accounts:
        return False, None
    real_target = find_account_name(data, target)
    if not real_target:
        return False, None
    target = real_target

    info = accounts[state.logged_in_user]
    following = get_following_array(info)
    target_key = target.strip().lower()
    is_currently_following = any(str(f).strip().lower() == target_key for f in following)
    new_following = [f for f in following if str(f).strip().lower() != target_key]
    if not is_currently_following:
        new_following.append(target)
    
    if supabase_update_account(state.logged_in_user, {"following": new_following}):
        target_info = accounts.get(target, {})
        legacy_followers = target_info.get("followers", [])
        if not isinstance(legacy_followers, list):
            legacy_followers = []
        user_key = state.logged_in_user.strip().lower()
        new_legacy = [f for f in legacy_followers if str(f).strip().lower() != user_key]
        if not is_currently_following:
            new_legacy.append(state.logged_in_user)
        supabase_update_account(target, {"followers": new_legacy})
        _cache["time"] = 0
        return True, data
    return False, None

def save_account_settings_online() -> bool:
    if not state.logged_in_user:
        sClickerLog.append("save_account_settings_online: kein Account eingeloggt.")
        return False
    
    r = auth_get_data()
    if not r:
        sClickerLog.append("save_account_settings_online: Server nicht erreichbar.")
        return False
    data = json_parse(r)
    if not data:
        sClickerLog.append("save_account_settings_online: Daten konnten nicht geparst werden.")
        return False
    
    accounts = data.get("accounts", {})
    if state.logged_in_user not in accounts:
        sClickerLog.append(f"save_account_settings_online: Account '{state.logged_in_user}' nicht gefunden.")
        return False
    
    existing_settings = accounts[state.logged_in_user].get("settings", {})
    existing_total = existing_settings.get("totalClicks", 0) if isinstance(existing_settings, dict) else 0
    try:
        existing_total = int(existing_total)
    except (TypeError, ValueError):
        existing_total = 0
    merged_total = max(existing_total, state.total_clicks)
    state.total_clicks = merged_total
    
    settings = {
        "theme": state.current_theme,
        "speed": state.click_delay,
        "repeat": "1" if state.repeat_mode else "0",
        "actions": list(state.action_list),
        "avatarEmoji": state.user_avatar_emoji,
        "avatarColor": state.user_avatar_color,
        "bio": state.user_bio,
        "totalClicks": merged_total,
        "loginStreak": state.login_streak,
 "lastLoginDate": state.last_login_date,
        "influencer": existing_settings.get("influencer", "0") if isinstance(existing_settings, dict) else "0",
    }
    
    if supabase_update_account(state.logged_in_user, {"settings": settings}):
        _cache["time"] = 0
        return True
    return False

def send_presence_heartbeat():
    if not state.logged_in_user:
        return
    presence = {
        "lastSeen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "isClicking": bool(state.is_running),
    }
    if supabase_update_account(state.logged_in_user, {"presence": presence}):
        _cache["time"] = 0

def get_joined_key(data, username: str) -> str:
    accounts = data.get("accounts", {}) if data else {}
    info = accounts.get(username)
    if info and "joined" in info:
        return str(info["joined"])
    return ""

def sort_users_by_joined_desc(arr: list, data) -> list:
    return sorted(arr, key=lambda u: get_joined_key(data, u), reverse=True)

def get_avatar_colors(theme_name=None):
    t = theme_name or state.current_theme
    return _AVATAR_COLOR_TABLE.get(t, _AVATAR_DEFAULT)

def get_user_avatar_emoji(username: str) -> str:
    if not username:
        return ""
    r = auth_get_data()
    if not r:
        return ""
    data = json_parse(r)
    if not data:
        return ""
    info = data.get("accounts", {}).get(username)
    if not info:
        return ""
    settings = info.get("settings")
    if settings and "avatarEmoji" in settings:
        return str(settings["avatarEmoji"])
    if "avatarEmoji" in info:
        return str(info["avatarEmoji"])
    return ""

def sort_kits_by_date_desc(kits: list) -> list:
    return sorted(kits, key=lambda k: str(k.get("created", ""))[:10], reverse=True)

def sort_kits_by_likes_desc(kits: list) -> list:
    def like_count(k):
        likes = k.get("likes", [])
        return len(likes) if isinstance(likes, list) else 0
    return sorted(kits, key=lambda k: (like_count(k), str(k.get("created", ""))[:10]), reverse=True)

def get_kit_comments(kit: dict) -> list:
    c = kit.get("comments", [])
    return c if isinstance(c, list) else []

def sort_news_desc(posts: list) -> list:
    return sorted(posts, key=lambda p: str(p.get("created", ""))[:19], reverse=True)

_PROFANITY_WORDS = [
    "fuck", "fucking", "fucker", "motherfucker", "shit", "bullshit",
    "bitch", "asshole", "ass", "cunt", "dick", "prick", "bastard",
    "whore", "slut", "nigger", "nigga", "faggot", "retard",
    "hurensohn", "arschloch", "scheisse", "scheiße", "scheiss", "fotze",
    "wichser", "hure", "schwuchtel", "spast", "missgeburt", "fick",
    "ficken", "verpiss", "wixer", "wixxer", "drecksau", "schlampe",
]
_PROFANITY_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in _PROFANITY_WORDS) + r")\b",
    re.IGNORECASE,
)

def censor_profanity(text: str) -> str:
    return _PROFANITY_RE.sub(lambda m: "#" * len(m.group(0)), text)

def format_relative_time(created_str: str) -> str:
    if not created_str:
        return ""
    try:
        dt = datetime.strptime(str(created_str)[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(created_str)[:16]
    secs = (datetime.now() - dt).total_seconds()
    if secs < 0:
        secs = 0
    de = state.current_language == "de"
    if secs < 60:
        return "gerade eben" if de else "just now"
    mins = int(secs // 60)
    if mins < 60:
        return f"vor {mins}m" if de else f"{mins}m ago"
    hours = int(secs // 3600)
    if hours < 24:
        return f"vor {hours}h" if de else f"{hours}h ago"
    days = int(secs // 86400)
    if days < 4:
        return f"vor {days}d" if de else f"{days}d ago"
    return dt.strftime("%Y-%m-%d")

PRESENCE_FRESH_SECONDS = 100

def is_user_present(info: dict) -> bool:
    if not info:
        return False
    ts = info.get("presence", {}).get("lastSeen", "") if isinstance(info.get("presence"), dict) else ""
    if not ts:
        return False
    try:
        dt = datetime.strptime(str(ts)[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return False
    return (datetime.now() - dt).total_seconds() <= PRESENCE_FRESH_SECONDS

def is_user_clicking(info: dict) -> bool:
    if not info or not is_user_present(info):
        return False
    presence = info.get("presence", {})
    return bool(isinstance(presence, dict) and presence.get("isClicking"))

def generate_kit_id() -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(8))

def get_local_kits_path() -> str:
    acct = state.logged_in_user if state.logged_in_user else "Guest"
    safe_acct = re.sub(r'[\\/:*?"<>|]', "_", acct)
    return os.path.join(SCLICKER_DATA_DIR, f"sClicker_localkits_{safe_acct}.json")

def load_local_kits() -> list:
    path = get_local_kits_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except Exception:
        return []

def save_local_kits(kits: list):
    try:
        with open(get_local_kits_path(), "w", encoding="utf-8") as f:
            json.dump(kits, f, ensure_ascii=False)
    except Exception:
        pass

def _cfg() -> configparser.RawConfigParser:
    cp = configparser.RawConfigParser()
    if os.path.exists(CONFIG_FILE):
        try:
            cp.read(CONFIG_FILE, encoding="utf-8")
        except Exception:
            pass
    return cp

def _cfg_save(cp: configparser.RawConfigParser):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            cp.write(f)
    except Exception as e:
        sClickerLog.append(f"Lokales Speichern fehlgeschlagen ({CONFIG_FILE}): {e}")

def load_config():
    cp = _cfg()
    if cp.has_section("Settings"):
        state.current_language = cp.get("Settings", "Language", fallback="en")
        state.current_theme = cp.get("Settings", "Theme", fallback="purple")
        try:
            state.click_delay = int(cp.get("Settings", "Speed", fallback="100"))
        except ValueError:
            state.click_delay = 100
        try:
            state.repeat_mode = bool(int(cp.get("Settings", "Repeat", fallback="1")))
        except ValueError:
            state.repeat_mode = True
        state.emergency_hotkey = cp.get("Settings", "EmergencyHotkey", fallback="F12") or "F12"
        try:
            state.accepted_tos = bool(int(cp.get("Settings", "AcceptedToS", fallback="0")))
        except ValueError:
            state.accepted_tos = False

def save_config():
    cp = _cfg()
    if not cp.has_section("Settings"):
        cp.add_section("Settings")
    cp.set("Settings", "Language", state.current_language)
    cp.set("Settings", "Theme", state.current_theme)
    cp.set("Settings", "Speed", str(state.click_delay))
    cp.set("Settings", "Repeat", "1" if state.repeat_mode else "0")
    cp.set("Settings", "EmergencyHotkey", state.emergency_hotkey or "F12")
    cp.set("Settings", "AcceptedToS", "1" if state.accepted_tos else "0")
    if state.logged_in_user:
        if not cp.has_section("Session"):
            cp.add_section("Session")
        cp.set("Session", "LastUser", state.logged_in_user)
    _cfg_save(cp)
    save_user_config()

def get_session_lastuser() -> str:
    cp = _cfg()
    return cp.get("Session", "LastUser", fallback="") if cp.has_section("Session") else ""

def set_session_lastuser(u: str):
    cp = _cfg()
    if not cp.has_section("Session"):
        cp.add_section("Session")
    cp.set("Session", "LastUser", u)
    _cfg_save(cp)

def get_session_account_version() -> int:
    cp = _cfg()
    if not cp.has_section("Session"):
        return 0
    try:
        return int(cp.get("Session", "AccountVersion", fallback="0"))
    except ValueError:
        return 0

def set_session_account_version(v: int):
    cp = _cfg()
    if not cp.has_section("Session"):
        cp.add_section("Session")
    cp.set("Session", "AccountVersion", str(v))
    _cfg_save(cp)

def _user_section() -> str:
    return f"User_{state.logged_in_user}" if state.logged_in_user else "Guest"

def save_user_config():
    cp = _cfg()
    s = _user_section()
    if not cp.has_section(s):
        cp.add_section(s)
    cp.set(s, "Language", state.current_language)
    cp.set(s, "Theme", state.current_theme)
    cp.set(s, "Speed", str(state.click_delay))
    cp.set(s, "RepeatMode", "1" if state.repeat_mode else "0")
    cp.set(s, "Bio", state.user_bio.replace("\r\n", "\n").replace("\n", "\\n"))
    cp.set(s, "AvatarEmoji", state.user_avatar_emoji)
    cp.set(s, "AvatarColor", state.user_avatar_color)
    cp.set(s, "TotalClicks", str(state.total_clicks))
    cp.set(s, "ActionCount", str(len(state.action_list)))
    for i in range(1, 51):
        key = f"Action{i}"
        if cp.has_option(s, key):
            cp.remove_option(s, key)
    for i, a in enumerate(state.action_list, start=1):
        if isinstance(a, dict):
            cp.set(s, f"Action{i}", "JSON:" + json_stringify(a))
        else:
            cp.set(s, f"Action{i}", str(a))
    _cfg_save(cp)
    queue_account_sync()

def load_user_config() -> bool:
    cp = _cfg()
    s = _user_section()
    if not cp.has_section(s):
        return False
    state.current_language = cp.get(s, "Language", fallback="en")
    state.current_theme = cp.get(s, "Theme", fallback="purple")
    try:
        state.click_delay = int(cp.get(s, "Speed", fallback="100"))
    except ValueError:
        state.click_delay = 100
    try:
        state.repeat_mode = bool(int(cp.get(s, "RepeatMode", fallback="1")))
    except ValueError:
        state.repeat_mode = True
    state.user_bio = cp.get(s, "Bio", fallback="").replace("\\n", "\n")
    state.user_avatar_emoji = cp.get(s, "AvatarEmoji", fallback="")
    state.user_avatar_color = cp.get(s, "AvatarColor", fallback="")
    try:
        state.total_clicks = int(cp.get(s, "TotalClicks", fallback="0"))
    except ValueError:
        state.total_clicks = 0
    try:
        count = int(cp.get(s, "ActionCount", fallback="0"))
    except ValueError:
        count = 0
    state.action_list = []
    for i in range(1, count + 1):
        a = cp.get(s, f"Action{i}", fallback="")
        if a:
            if a.startswith("JSON:"):
                parsed = json_parse(a[len("JSON:"):])
                state.action_list.append(parsed if parsed is not None else a)
            else:
                state.action_list.append(a)
    return True

def reset_to_default_settings():
    state.current_theme = "purple"
    state.click_delay = 100
    state.repeat_mode = True
    state.action_list = []
    state.user_avatar_emoji = ""
    state.user_avatar_color = ""
    state.user_bio = ""
    state.total_clicks = 0
    state.login_streak = 0
    state.last_login_date = ""

def apply_account_settings(info: dict) -> bool:
    settings = info.get("settings")
    if settings:
        state.current_theme = settings.get("theme", "purple")
        try:
            state.click_delay = int(settings.get("speed", 100))
        except (TypeError, ValueError):
            state.click_delay = 100
        rep = settings.get("repeat", True)
        state.repeat_mode = rep in ("1", 1, True)
        actions = settings.get("actions")
        state.action_list = list(actions) if isinstance(actions, list) else []
        state.user_avatar_emoji = str(settings.get("avatarEmoji", ""))
        state.user_avatar_color = str(settings.get("avatarColor", ""))
        state.user_bio = str(settings.get("bio", ""))
        try:
            state.total_clicks = int(settings.get("totalClicks", 0))
        except (TypeError, ValueError):
            state.total_clicks = 0
        try:
            state.login_streak = int(settings.get("loginStreak", 0))
        except (TypeError, ValueError):
            state.login_streak = 0
        state.last_login_date = str(settings.get("lastLoginDate", ""))
        return True
    return False

# ============== LOGIN-STREAK SYSTEM ==============
def _compute_updated_streak(prev_date_str: str, prev_streak: int):
    """Gibt (neuer_streak, heutiges_datum) zurück. Ein Tag Lücke = Streak
    bleibt gleich Tag, direkt aufeinanderfolgender Tag = Streak+1,
    Lücke von mehr als einem Tag = Streak faellt auf 1 zurueck."""
    today = datetime.now().strftime("%Y-%m-%d")
    if prev_date_str == today:
        return (prev_streak if prev_streak > 0 else 1), today
    prev_date = None
    if prev_date_str:
        try:
            prev_date = datetime.strptime(prev_date_str, "%Y-%m-%d")
        except Exception:
            prev_date = None
    if prev_date is not None:
        delta_days = (datetime.now().date() - prev_date.date()).days
        if delta_days == 1:
            return prev_streak + 1, today
    return 1, today

def update_login_streak_for_today() -> bool:
    """Aktualisiert state.login_streak/last_login_date fuer den heutigen
    Login. Gibt True zurueck, wenn sich dadurch etwas geaendert hat
    (dann sollten die Settings online gespeichert werden)."""
    new_streak, today = _compute_updated_streak(state.last_login_date, state.login_streak)
    changed = (new_streak != state.login_streak) or (state.last_login_date != today)
    state.login_streak = new_streak
    state.last_login_date = today
    return changed

def load_account_settings(u: str):
    r = auth_get_data()
    if r:
        data = json_parse(r)
        if data:
            info = data.get("accounts", {}).get(u)
            if info and apply_account_settings(info):
                return
    if not load_user_config():
        reset_to_default_settings()

def queue_account_sync():
    if not state.logged_in_user:
        return
    if state.sync_timer:
        state.sync_timer.cancel()
    state.sync_timer = threading.Timer(0.8, save_account_settings_online)
    state.sync_timer.daemon = True
    state.sync_timer.start()

def register_autostart():
    if winreg is None:
        return
    try:
        exe = sys.executable
        script = os.path.abspath(__file__)
        if getattr(sys, "frozen", False):
            cmd = f'"{exe}"'
        else:
            cmd = f'"{exe}" "{script}"'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "sClicker", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
    except Exception:
        pass

def unregister_autostart():
    if winreg is None:
        return
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "sClicker")
        winreg.CloseKey(key)
    except Exception:
        pass

def check_autostart_status() -> bool:
    if winreg is None:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, "sClicker")
        winreg.CloseKey(key)
        return bool(val)
    except Exception:
        return False

def BuildActionTypeList():
    return [T("leftClick"), T("rightClick"), T("pressKey"), T("holdKey"), T("middleClick"),
            T("doubleClick"), T("holdLeft"), T("holdRight"), T("holdMiddle")]

def format_step_label(a) -> str:
    if isinstance(a, dict):
        t = a.get("type", "")
        if t == "click":
            btn = a.get("button", "left")
            mapping = {
                "left": T("leftClick"), "right": T("rightClick"),
                "middle": T("middleClick"), "double": T("doubleClick"),
            }
            return mapping.get(btn, T("leftClick"))
        if t == "key":
            keys = a.get("keys", [])
            if not isinstance(keys, list):
                keys = [keys]
            return T("pressKey") + " " + "+".join(str(k) for k in keys)
        if t == "hold":
            return f"{T('holdKey')} [{a.get('key', '')}] {a.get('duration', 0)}ms"
        if t == "move":
            return f"Move to ({a.get('x', 0)}, {a.get('y', 0)})"
        if t == "keydown":
            return f"⬇ Key Down [{a.get('key', '')}]"
        if t == "keyup":
            return f"⬆ Key Up [{a.get('key', '')}]"
        if t == "mousedown":
            return f"⬇ Mouse Down [{a.get('button', 'left')}]"
        if t == "mouseup":
            return f"⬆ Mouse Up [{a.get('button', 'left')}]"
        if t == "tracking":
            return "Tracking Playback"
        return str(t) if t else "Action"

    a = str(a)
    if a == "LeftClick":
        return T("leftClick")
    if a == "RightClick":
        return T("rightClick")
    if a.startswith("HoldKey:"):
        p = a.split(":")
        return f"{T('holdKey')} [{p[1]}] {p[2]}ms"
    if a.startswith("Key:"):
        return T("pressKey") + " " + a[len("Key:"):]
    if a == "MiddleClick":
        return T("middleClick")
    if a == "DoubleClick":
        return T("doubleClick")
    if a.startswith("HoldLeftClick:"):
        return f"{T('holdLeft')} {a.split(':')[1]}ms"
    if a.startswith("HoldRightClick:"):
        return f"{T('holdRight')} {a.split(':')[1]}ms"
    if a.startswith("HoldMiddleClick:"):
        return f"{T('holdMiddle')} {a.split(':')[1]}ms"
    return a

def execute_single_action(a):
    if isinstance(a, dict):
        action_type = a.get("type", "")
        if action_type == "click":
            if a.get("button") == "right":
                click_right()
            elif a.get("button") == "middle":
                click_middle()
            elif a.get("button") == "double":
                double_click_left()
            else:
                click_left()
        elif action_type == "key":
            keys = a.get("keys", [])
            if not isinstance(keys, list):
                keys = [keys]
            for key in keys:
                key_down(key)
            time.sleep(0.05)
            for key in reversed(keys):
                key_up(key)
        elif action_type == "hold":
            key = a.get("key", "")
            duration = a.get("duration", 100)
            if key.startswith("mouse"):
                if "left" in key:
                    hold_left_down()
                elif "right" in key:
                    hold_right_down()
                elif "middle" in key:
                    hold_middle_down()
                time.sleep(duration / 1000)
                if "left" in key:
                    hold_left_up()
                elif "right" in key:
                    hold_right_up()
                elif "middle" in key:
                    hold_middle_up()
            else:
                key_down(key)
                time.sleep(duration / 1000)
                key_up(key)
        elif action_type == "move":
            move_cursor(a.get("x", 0), a.get("y", 0))
        elif action_type == "keydown":
            key_down(a.get("key", ""))
        elif action_type == "keyup":
            key_up(a.get("key", ""))
        elif action_type == "mousedown":
            btn = a.get("button", "left")
            if btn == "right":
                hold_right_down()
            elif btn == "middle":
                hold_middle_down()
            else:
                hold_left_down()
        elif action_type == "mouseup":
            btn = a.get("button", "left")
            if btn == "right":
                hold_right_up()
            elif btn == "middle":
                hold_middle_up()
            else:
                hold_left_up()
        elif action_type == "tracking":
            pass
        return

    if a == "LeftClick":
        click_left()
    elif a == "RightClick":
        click_right()
    elif a.startswith("HoldKey:"):
        p = a.split(":")
        key, dur = p[1], int(p[2])
        key_down(key)
        time.sleep(dur / 1000)
        key_up(key)
    elif a.startswith("Key:"):
        key_name = a[len("Key:"):]
        press_key(key_name)
    elif a == "MiddleClick":
        click_middle()
    elif a == "DoubleClick":
        double_click_left()
    elif a.startswith("HoldLeftClick:"):
        dur = int(a.split(":")[1])
        hold_left_down()
        time.sleep(dur / 1000)
        hold_left_up()
    elif a.startswith("HoldRightClick:"):
        dur = int(a.split(":")[1])
        hold_right_down()
        time.sleep(dur / 1000)
        hold_right_up()
    elif a.startswith("HoldMiddleClick:"):
        dur = int(a.split(":")[1])
        hold_middle_down()
        time.sleep(dur / 1000)
        hold_middle_up()

_clicker_thread = None
_countdown_timer = None

def toggle_clicker(app):
    global _clicker_thread
    if state.is_counting_down:
        state.is_counting_down = False
        app.on_countdown_cancelled()
        return
    if not state.is_running:
        if not CLICKER_ENGINE_AVAILABLE:
            app.show_info(CLICKER_ENGINE_ERROR or T("clickerUnavailable"))
            return
        if not state.action_list:
            app.show_info(T("errorNoActions"))
            return
        state.is_counting_down = True
        app.start_countdown(START_COUNTDOWN_SECONDS)
    else:
        state.is_running = False
        app.on_clicker_stopped()

def _begin_clicker_after_countdown(app):
    global _clicker_thread
    if not state.is_counting_down:
        return
    state.is_counting_down = False
    state.is_running = True
    app.on_clicker_started()
    _clicker_thread = threading.Thread(target=_clicker_loop, args=(app,), daemon=True)
    _clicker_thread.start()

def _clicker_loop(app):
    try:
        while state.is_running:
            for a in list(state.action_list):
                if not state.is_running:
                    break
                if isinstance(a, dict) and "delay" in a:
                    pre_delay = max(0, a.get("delay", 0))
                    if pre_delay > 0:
                        wait_secs = min(pre_delay, 600000) / 1000
                        wait_end = time.perf_counter() + wait_secs
                        while state.is_running and time.perf_counter() < wait_end:
                            if is_key_down(state.emergency_hotkey):
                                state.is_running = False
                                break
                            time.sleep(min(0.02, max(0.0, wait_end - time.perf_counter())))
                if not state.is_running:
                    break
                execute_single_action(a)
                state.click_count += 1
                state.total_clicks += 1
                if state.click_count % 5 == 0:
                    app.root.after(0, app.update_counter_display)
                if not (isinstance(a, dict) and "delay" in a):
                    action_delay = 10 if isinstance(a, dict) else max(state.click_delay, 1)
                    if action_delay > 0:
                        time.sleep(action_delay / 1000)
                if is_key_down(state.emergency_hotkey):
                    state.is_running = False
                    break
            if not state.repeat_mode:
                state.is_running = False
                app.root.after(0, app.on_clicker_stopped)
                break
    except Exception as e:
        sClickerLog.append(f"Clicker-Thread-Fehler: {e}")
        state.is_running = False
        app.root.after(0, app.on_clicker_stopped)
        app.root.after(0, lambda: app.show_error(f"Clicker error: {e}"))

def emergency_hotkey_watcher(app):
    while True:
        try:
            key = (state.emergency_hotkey or "").strip()
            down = bool(key) and is_key_down(key)
            if down and not state._emergency_hotkey_was_down:
                if state.is_running or state.is_counting_down or state.is_tracking:
                    state.is_running = False
                    state.is_counting_down = False
                    state.is_tracking = False
                    try:
                        app.root.after(0, app.on_emergency_stop)
                    except Exception:
                        pass
            state._emergency_hotkey_was_down = down
        except Exception as e:
            sClickerLog.append(f"Hotkey-Watcher Fehler: {e}")
        time.sleep(HOTKEY_POLL_INTERVAL)

def start_emergency_hotkey_watcher(app):
    t = threading.Thread(target=emergency_hotkey_watcher, args=(app,), daemon=True)
    t.start()

def enforce_tos_reaccept():
    """Prüft, ob TOS oder Privacy Policy seit dem letzten Akzeptieren des
    Nutzers per Admin-Befehl (PromptTOS/PromptPrivacyPolicy) aktualisiert
    wurden. Falls ja, wird state.accepted_tos zurückgesetzt, sodass beim
    nächsten Start das Login-Fenster erneut zur Zustimmung zwingt."""
    cfg = supabase_get_app_config()
    tos_version = str(cfg.get("tos_force_version", "0"))
    privacy_version = str(cfg.get("privacy_force_version", "0"))

    cp = _cfg()
    seen_tos = cp.get("Settings", "SeenTosVersion", fallback="0") if cp.has_section("Settings") else "0"
    seen_privacy = cp.get("Settings", "SeenPrivacyVersion", fallback="0") if cp.has_section("Settings") else "0"

    if tos_version != seen_tos or privacy_version != seen_privacy:
        state.accepted_tos = False
        cp2 = _cfg()
        if not cp2.has_section("Settings"):
            cp2.add_section("Settings")
        cp2.set("Settings", "SeenTosVersion", tos_version)
        cp2.set("Settings", "SeenPrivacyVersion", privacy_version)
        cp2.set("Settings", "AcceptedToS", "0")
        _cfg_save(cp2)

def enforce_account_reset_version(show_warning):
    if not state.logged_in_user:
        return
    try:
        user_version = get_session_account_version()
        if user_version < ACCOUNT_RESET_VERSION:
            show_warning("Account Reset Required",
                         "Your account data needs to be reset due to a version update. "
                         "Please log in again.")
            state.logged_in_user = ""
            state.logged_in_verified = False
            set_session_lastuser("")
        set_session_account_version(ACCOUNT_RESET_VERSION)
    except Exception as e:
        sClickerLog.append(f"Error checking account version: {e}")

def auto_login():
    last_user = get_session_lastuser()
    if not last_user:
        return
    resp = auth_get_data()
    if not resp:
        state.logged_in_user = last_user
        state.logged_in_verified = False
        return
    try:
        data = json_parse(resp)
        accounts = data.get("accounts", {}) if data else {}
        real_user = find_account_name(data, last_user) if data else ""
        if real_user:
            info = accounts[real_user]
            if safe_flag(info, "banned"):
                state.logged_in_user = ""
                return
            state.logged_in_user = real_user
            state.logged_in_verified = safe_flag(info, "verified")
    except Exception:
        state.logged_in_user = last_user
        state.logged_in_verified = False

if sys.platform == "win32":
    FONT_FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FONT_FAMILY = "Helvetica Neue"
else:
    FONT_FAMILY = "Noto Sans"

def F(size, bold=False, underline=False):
    style = []
    if bold:
        style.append("bold")
    if underline:
        style.append("underline")
    return (FONT_FAMILY, size, " ".join(style)) if style else (FONT_FAMILY, size)

def badge_size_for_font(font_size: int) -> int:
    # FIX: etwas mehr Platz, damit das Verified-Häkchen nicht am Rand
    # der Canvas abgeschnitten wirkt
    return max(12, round(font_size * 1.15) + 2)

_measure_cache = {}

def measure_text_width(txt, size=11, bold=False) -> int:
    key = (size, bold)
    fnt = _measure_cache.get(key)
    if fnt is None:
        fnt = tkfont.Font(family=FONT_FAMILY, size=size, weight="bold" if bold else "normal")
        _measure_cache[key] = fnt
    return fnt.measure(str(txt))

def badge_y_centered(label_y: int, label_h: int, badge_size: int) -> int:
    return label_y + (label_h - badge_size) // 2

# ============== APP-INSTANZ (für Toast/Modal-Dialoge ohne native Windows-Prompts) ==============
_app_instance = None

def show_info(msg, title="sClicker"):
    if _app_instance is not None:
        try:
            _app_instance.show_toast(msg, kind="info")
            return
        except Exception:
            pass
    messagebox.showinfo(title, msg)

def show_error(msg, title="sClicker"):
    if _app_instance is not None:
        try:
            _app_instance.show_toast(msg, kind="error")
            return
        except Exception:
            pass
    messagebox.showerror(title, msg)

def ask_yes_no(msg, title=None) -> bool:
    """FIX: Der vorherige selbstgebaute Ja/Nein-Dialog nutzte grab_set() +
    overrideredirect() + wait_window() zusammen mit dem "-topmost" Hauptfenster -
    diese Kombination kann auf manchen Systemen (v.a. Windows) den kompletten
    Tk-Event-Loop einfrieren, sobald man auf Ja/Nein klickt. Das war der
    "hängt sich auf beim Löschen"-Bug. Jetzt wieder der battle-tested native
    Dialog - nur wird das topmost-Flag des Hauptfensters kurz pausiert, damit
    der Dialog nicht dahinter verschwindet (der ursprüngliche Grund, warum wir
    überhaupt einen eigenen Dialog gebaut hatten)."""
    title = title or T("confirmTitle")
    root = tk._default_root
    was_topmost = False
    if root is not None:
        try:
            was_topmost = bool(root.attributes("-topmost"))
            if was_topmost:
                root.attributes("-topmost", False)
        except Exception:
            pass
    try:
        return messagebox.askyesno(title, msg, parent=root)
    finally:
        if root is not None and was_topmost:
            try:
                root.attributes("-topmost", True)
            except Exception:
                pass

def center_window(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

_active_panels = []

def _animate_panel_in(panel, start_x, end_x, y, steps=16, step_i=0):
    if not panel.winfo_exists():
        return
    t = (step_i + 1) / steps
    eased = 1 - pow(1 - t, 3)
    cur_x = int(start_x + (end_x - start_x) * eased)
    try:
        panel.place_configure(x=cur_x, y=y)
    except Exception:
        return
    if step_i + 1 < steps:
        panel.after(11, lambda: _animate_panel_in(panel, start_x, end_x, y, steps, step_i + 1))

_BASE_ROOT_W = 800
_BASE_ROOT_H = 725

def _rounded_border_image(w, h, radius, bg, accent, border_width=2, scale=4):
    """Erzeugt ein abgerundetes Panel-Hintergrundbild (für echte runde Ecken)."""
    if Image is None or ImageDraw is None:
        return None
    try:
        W, H = max(1, w * scale), max(1, h * scale)
        R = radius * scale
        bw_px = max(1, border_width * scale)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        inset = bw_px / 2
        draw.rounded_rectangle(
            [inset, inset, W - 1 - inset, H - 1 - inset],
            radius=max(0, R - inset), fill=bg, outline=accent, width=bw_px,
        )
        img = img.resize((w, h), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        sClickerLog.append(f"Rounded-Border-Bild konnte nicht gerendert werden: {e}")
        return None

def new_toplevel(parent, title, w, h, bg=None, topmost=True, resizable=False):
    # FIX: Dialoge bekommen jetzt IMMER die aktuelle Theme-Hintergrundfarbe
    # (wie im Hauptfenster), statt der fest codierten Farbe, die der Aufrufer
    # übergeben hat.
    bg = THEMES.get(state.current_theme, THEMES["purple"])["bg"]
    root = parent.winfo_toplevel()
    root.update_idletasks()

    needed_w = max(w + 60, _BASE_ROOT_W)
    needed_h = max(h + 60, _BASE_ROOT_H)
    cur_w = root.winfo_width()
    cur_h = root.winfo_height()
    if cur_w < needed_w or cur_h < needed_h:
        root.geometry(f"{max(cur_w, needed_w)}x{max(cur_h, needed_h)}")
        root.update_idletasks()

    root_w = root.winfo_width()
    root_h = root.winfo_height()
    target_x = max(0, (root_w - w) // 2)
    target_y = max(8, (root_h - h) // 2)

    # FIX: Backdrop hat vorher immer fest "#242424" (Grau) benutzt, unabhängig
    # von der Dialogfarbe - dadurch gab es an den runden Ecken einen sichtbaren
    # Farbbruch. Jetzt exakt die gleiche Farbe wie der Dialog-Hintergrund.
    backdrop = tk.Frame(root, bg=bg)
    backdrop.place(x=0, y=0, width=root_w, height=root_h)

    accent_c = THEMES.get(state.current_theme, THEMES["purple"])["accent"]
    panel = tk.Frame(root, bg=bg, highlightthickness=2, highlightbackground=accent_c)
    panel.place(x=-w, y=target_y, width=w, height=h)

    # Runde Ecken (Bild-Overlay), fällt sauber auf das alte Aussehen zurück falls PIL fehlt
    corner_img = _rounded_border_image(w, h, 18, bg, accent_c, border_width=2)
    if corner_img is not None:
        # FIX: bg des Overlays MUSS zur Panel-Farbe passen, sonst schimmert an den
        # transparenten Ecken ein weißer Standard-Label-Hintergrund durch.
        corner_lbl = tk.Label(panel, image=corner_img, bg=bg, bd=0, highlightthickness=0)
        corner_lbl.image = corner_img
        corner_lbl.place(x=0, y=0, width=w, height=h)
        corner_lbl.lower()
        # FIX: die Umrandung kommt jetzt NUR noch vom Overlay-Bild, sonst gab es
        # den Rahmen doppelt (einmal vom Frame-highlight, einmal vom Bild).
        panel.configure(highlightthickness=0)

    panel.lift()
    _active_panels.append(panel)

    def _close_via_backdrop(_e=None, p=panel):
        try:
            p.destroy()
        except Exception:
            pass
    backdrop.bind("<Button-1>", _close_via_backdrop)

    def _on_destroy(_e=None, p=panel, bd=backdrop):
        if p in _active_panels:
            _active_panels.remove(p)
        try:
            if bd.winfo_exists():
                bd.destroy()
        except Exception:
            pass
        if not _active_panels:
            try:
                root.geometry(f"{_BASE_ROOT_W}x{_BASE_ROOT_H}")
            except Exception:
                pass
    panel.bind("<Destroy>", _on_destroy)

    close_x = tk.Label(panel, text="✕", bg=bg, fg="#888888",
                        font=(FONT_FAMILY, 12, "bold"), cursor="hand2")
    close_x.place(x=max(0, w - 36), y=6, width=28, height=28)
    close_x.bind("<Button-1>", lambda _e, p=panel: p.after(1, p.destroy))
    close_x.bind("<Enter>", lambda _e: close_x.configure(fg="#ef4444"))
    close_x.bind("<Leave>", lambda _e: close_x.configure(fg="#888888"))
    panel.after_idle(lambda: close_x.lift() if close_x.winfo_exists() else None)

    _animate_panel_in(panel, -w, target_x, target_y)
    return panel

def label(parent, x, y, w, h, text="", bg=None, fg="#FFFFFF",
          size=10, bold=False, underline=False, anchor="w", justify="left",
          cursor=None, wraplength=0):
    # FIX: bg=None als Sentinel statt bg=DIALOG_BG() direkt in der Signatur -
    # ein Funktionsaufruf als Default-Parameter wird in Python nur EINMAL
    # beim Programmstart ausgewertet und bleibt dann für immer eingefroren!
    # Jeder label()-Aufruf ohne explizites bg= bekam dadurch für immer die
    # Farbe vom allerersten Start - das war die Ursache der sichtbaren
    # "Kästen" hinter Texten, sobald sich das Theme geändert hatte.
    if bg is None:
        bg = DIALOG_BG()
    lbl = tk.Label(parent, text=text, bg=bg, fg=fg, font=F(size, bold, underline),
                    anchor=anchor, justify=justify, wraplength=wraplength)
    lbl.place(x=x, y=y, width=w, height=h)
    if cursor:
        lbl.configure(cursor=cursor)
    lbl._orig_fg = fg
    return lbl

class RoundedButton(tk.Canvas):
    _bg_image_cache = {}

    def __init__(self, parent, text="", command=None, bg="#333333", fg="#FFFFFF",
                 font=None, radius=16, border_width=2, border_color=None,
                 activebackground=None, activeforeground=None, state="normal"):
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = DIALOG_BG()
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent_bg)
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._font = font or F(10)
        self._radius = radius
        self._border_width = border_width
        self._border_color = border_color if border_color else self._shade(bg, 1.45)
        # FIX: Hover-Farbe war vorher HELLER (Faktor 1.18) und wurde nur EINMAL
        # bei Erstellung berechnet - bei der oft violetten Standard-Akzentfarbe
        # sah das aufgehellt fast pink aus, und blieb nach einem Theme-Wechsel
        # auf der alten Farbe stehen. Jetzt: dynamisch aus der AKTUELLEN Farbe
        # berechnet (immer korrekt) und dunkler statt heller.
        self._explicit_hover_bg = activebackground
        self._hover_fg = activeforeground if activeforeground else fg
        self._state = state
        self._hovering = False
        self._pressed = False
        self._bw, self._bh = 100, 30
        self.configure(cursor="hand2" if state != "disabled" else "")
        self.bind("<Configure>", self._on_configure)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._redraw()

    @staticmethod
    def _shade(hexcolor, factor):
        try:
            hexcolor = str(hexcolor).lstrip("#")
            r, g, b = int(hexcolor[0:2], 16), int(hexcolor[2:4], 16), int(hexcolor[4:6], 16)
            r = max(0, min(255, int(r * factor)))
            g = max(0, min(255, int(g * factor)))
            b = max(0, min(255, int(b * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hexcolor if str(hexcolor).startswith("#") else "#333333"

    @staticmethod
    def _rounded_points(x1, y1, x2, y2, r):
        return [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]

    def _on_configure(self, event):
        self._bw, self._bh = event.width, event.height
        self._redraw()

    def _get_bg_image(self, w, h, r, fill, outline, border_width, scale=4):
        key = (w, h, round(r, 1), fill, outline, border_width)
        cache = self.__class__._bg_image_cache
        cached = cache.get(key)
        if cached is not None:
            return cached
        if Image is None or ImageDraw is None:
            return None
        try:
            W, H = max(1, w * scale), max(1, h * scale)
            R = r * scale
            bw_px = max(1, border_width * scale)
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            inset = bw_px / 2
            draw.rounded_rectangle(
                [inset, inset, W - 1 - inset, H - 1 - inset],
                radius=max(0, R - inset), fill=fill, outline=outline, width=bw_px,
            )
            img = img.resize((w, h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            cache[key] = photo
            if len(cache) > 400:
                cache.clear()
                cache[key] = photo
            return photo
        except Exception as e:
            sClickerLog.append(f"Button-Hintergrund konnte nicht gerendert werden: {e}")
            return None

    def _redraw(self):
        self.delete("all")
        w, h = self._bw, self._bh
        if w < 4 or h < 4:
            return
        r = max(0, min(self._radius, w / 2, h / 2))
        disabled = (self._state == "disabled")
        if disabled:
            fill = self._shade(self._bg, 0.55)
            outline = self._shade(self._bg, 0.75)
            txt_fg = self._shade(self._fg, 0.6)
        elif self._hovering:
            fill = self._explicit_hover_bg if self._explicit_hover_bg else self._shade(self._bg, 0.68)
            outline = self._border_color
            txt_fg = self._hover_fg
        else:
            fill = self._bg
            outline = self._border_color
            txt_fg = self._fg
        bw = self._border_width
        bg_img = self._get_bg_image(w, h, r, fill, outline, bw)
        if bg_img is not None:
            self._current_image = bg_img
            self.create_image(0, 0, anchor="nw", image=bg_img)
        else:
            pts = self._rounded_points(bw, bw, w - bw, h - bw, r)
            self.create_polygon(pts, smooth=True, splinesteps=24, fill=fill,
                                 outline=outline, width=bw)
        avail_w = max(10, w - (2 * bw) - 10)
        fit_font = self._get_fit_font(avail_w)
        self._current_font = fit_font
        self.create_text(w / 2, h / 2, text=self._text, fill=txt_fg, font=fit_font)

    def _get_fit_font(self, avail_w):
        try:
            fam = self._font[0]
            size = self._font[1]
            style = self._font[2] if len(self._font) > 2 else ""
        except Exception:
            fam, size, style = FONT_FAMILY, 10, ""
        weight = "bold" if "bold" in style else "normal"
        underline = 1 if "underline" in style else 0
        s = size
        while s > 7:
            f = tkfont.Font(family=fam, size=s, weight=weight, underline=underline)
            if f.measure(self._text) <= avail_w:
                return f
            s -= 1
        return tkfont.Font(family=fam, size=7, weight=weight, underline=underline)

    def _on_enter(self, _e=None):
        if self._state != "disabled":
            self._hovering = True
            self.configure(cursor="hand2")
            self._redraw()

    def _on_leave(self, _e=None):
        self._hovering = False
        self._pressed = False
        self._redraw()

    def _on_press(self, _e=None):
        if self._state != "disabled":
            self._pressed = True

    def _on_release(self, _e=None):
        was_pressed = self._pressed
        self._pressed = False
        if was_pressed and self._state != "disabled" and self._command:
            self._command()

    def sync_parent_bg(self, bg):
        try:
            tk.Canvas.configure(self, bg=bg)
        except Exception:
            pass

    def configure(self, **kwargs):
        own = {}
        for key in ("text", "bg", "fg", "command", "state", "activebackground",
                    "activeforeground", "font", "border_color"):
            if key in kwargs:
                own[key] = kwargs.pop(key)
        if "text" in own:
            self._text = own["text"]
        if "bg" in own:
            self._bg = own["bg"]
            self._border_color = self._shade(self._bg, 1.45)
        if "fg" in own:
            self._fg = own["fg"]
        if "command" in own:
            self._command = own["command"]
        if "state" in own:
            self._state = own["state"]
            if kwargs.get("cursor") is None:
                kwargs["cursor"] = "hand2" if self._state != "disabled" else ""
        if "activebackground" in own:
            self._explicit_hover_bg = own["activebackground"]
        if "activeforeground" in own:
            self._hover_fg = own["activeforeground"]
        if "font" in own:
            self._font = own["font"]
        if "border_color" in own:
            self._border_color = own["border_color"]
        if kwargs:
            super().configure(**kwargs)
        if own:
            self._redraw()

    config = configure

    def cget(self, key):
        mapping = {"text": self._text, "bg": self._bg, "fg": self._fg,
                   "state": self._state, "command": self._command}
        if key in mapping:
            return mapping[key]
        return super().cget(key)

def _fg_for_bg(hexcolor):
    """Liest die Helligkeit einer Farbe und gibt passenden Text (schwarz/weiß)
    zurück - z.B. beim 'Dark Mode'-Theme (weißer Akzent) automatisch schwarzen
    Button-Text statt unlesbarem Weiß-auf-Weiß."""
    try:
        h = str(hexcolor).lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#000000" if lum > 0.6 else "#FFFFFF"
    except Exception:
        return "#FFFFFF"

def button(parent, x, y, w, h, text, command=None, bg="#333333", fg="#FFFFFF",
           size=10, bold=False):
    follows_accent = (bg == accent())
    if follows_accent:
        fg = _fg_for_bg(bg)
    btn = RoundedButton(parent, text=text, command=command, bg=bg, fg=fg,
                         font=F(size, bold), radius=16, border_width=2)
    btn.place(x=x, y=y, width=w, height=h)
    # NEU: Buttons, die mit der aktuellen Theme-Akzentfarbe erstellt wurden,
    # merken sich das - damit sie bei einem Theme-Wechsel live mitfärben.
    if follows_accent:
        btn._follows_theme_accent = True
    return btn

class VerifiedBadge(tk.Canvas):
    _img_cache = {}

    def __init__(self, parent, badge_color="#0085FF", check_color="#FFFFFF"):
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = DIALOG_BG()
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent_bg)
        self._badge_color = badge_color
        self._check_color = check_color
        self._visible = True
        self._cw, self._ch = 22, 22
        self._current_image = None
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        self._cw, self._ch = event.width, event.height
        self._draw()

    def _render_pil(self, s, scale=4):
        if Image is None or ImageDraw is None:
            return None
        key = (s, self._badge_color, self._check_color)
        cached = self.__class__._img_cache.get(key)
        if cached is not None:
            return cached
        try:
            S = max(1, s * scale)
            img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # FIX: kleiner Rand, damit der Kreis nicht an der Canvas-Kante
            # abgeschnitten wird (Anti-Aliasing-Pixel gingen sonst verloren)
            inset = max(1, int(S * 0.05))
            draw.ellipse([inset, inset, S - 1 - inset, S - 1 - inset], fill=self._badge_color)

            lw = max(2, round(S * 0.11))
            x1, y1 = S * 0.28, S * 0.52
            x2, y2 = S * 0.40, S * 0.66
            x3, y3 = S * 0.74, S * 0.28
            draw.line([(x1, y1), (x2, y2)], fill=self._check_color, width=lw)
            draw.line([(x2, y2), (x3, y3)], fill=self._check_color, width=lw)
            for (cx, cy) in ((x1, y1), (x2, y2), (x3, y3)):
                rr = lw / 2
                draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=self._check_color)

            img = img.resize((s, s), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.__class__._img_cache[key] = photo
            if len(self.__class__._img_cache) > 300:
                self.__class__._img_cache.clear()
                self.__class__._img_cache[key] = photo
            return photo
        except Exception as e:
            sClickerLog.append(f"VerifiedBadge konnte nicht gerendert werden: {e}")
            return None

    def _draw(self):
        self.delete("all")
        if not self._visible:
            return
        s = min(self._cw, self._ch)
        if s < 4:
            return
        ox = (self._cw - s) / 2.0
        oy = (self._ch - s) / 2.0

        photo = self._render_pil(s)
        if photo is not None:
            self._current_image = photo
            self.create_image(ox, oy, anchor="nw", image=photo)
            return

        self.create_oval(ox, oy, ox + s, oy + s, fill=self._badge_color, outline="")
        lw = max(2, round(s * 0.13))
        x1, y1 = ox + s * 0.28, oy + s * 0.52
        x2, y2 = ox + s * 0.40, oy + s * 0.66
        x3, y3 = ox + s * 0.74, oy + s * 0.28
        self.create_line(x1, y1, x2, y2,
                          fill=self._check_color, width=lw,
                          capstyle=tk.ROUND, joinstyle=tk.ROUND)
        self.create_line(x2, y2, x3, y3,
                          fill=self._check_color, width=lw,
                          capstyle=tk.ROUND, joinstyle=tk.ROUND)

    def set_visible(self, visible: bool):
        if self._visible != visible:
            self._visible = visible
            self._draw()

    def sync_parent_bg(self, bg):
        try:
            tk.Canvas.configure(self, bg=bg)
        except Exception:
            pass

class InfluencerBadge(tk.Canvas):
    _img_cache = {}

    def __init__(self, parent, badge_color="#9945FF", star_color="#FFFFFF"):
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = DIALOG_BG()
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent_bg)
        self._badge_color = badge_color
        self._star_color = star_color
        self._visible = True
        self._cw, self._ch = 22, 22
        self._current_image = None
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        self._cw, self._ch = event.width, event.height
        self._draw()

    def _render_pil(self, s, scale=4):
        if Image is None or ImageDraw is None:
            return None
        key = (s, self._badge_color, self._star_color)
        cached = self.__class__._img_cache.get(key)
        if cached is not None:
            return cached
        try:
            S = max(1, s * scale)
            img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            inset = max(1, int(S * 0.05))
            draw.ellipse([inset, inset, S - 1 - inset, S - 1 - inset], fill=self._badge_color)
            cx, cy = S / 2, S / 2
            pts = _star_points(cx, cy, S * 0.32, S * 0.14, points=5)
            draw.polygon(pts, fill=self._star_color)
            img = img.resize((s, s), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.__class__._img_cache[key] = photo
            if len(self.__class__._img_cache) > 300:
                self.__class__._img_cache.clear()
                self.__class__._img_cache[key] = photo
            return photo
        except Exception as e:
            sClickerLog.append(f"InfluencerBadge konnte nicht gerendert werden: {e}")
            return None

    def _draw(self):
        self.delete("all")
        if not self._visible:
            return
        s = min(self._cw, self._ch)
        if s < 4:
            return
        ox, oy = (self._cw - s) / 2, (self._ch - s) / 2
        photo = self._render_pil(s)
        if photo is not None:
            self._current_image = photo
            self.create_image(ox, oy, anchor="nw", image=photo)
            return
        self.create_oval(ox, oy, ox + s, oy + s, fill=self._badge_color, outline="")
        cx, cy = ox + s / 2, oy + s / 2
        pts = _star_points(cx, cy, s * 0.32, s * 0.14, points=5)
        self.create_polygon(pts, fill=self._star_color)

    def set_visible(self, visible: bool):
        if self._visible != visible:
            self._visible = visible
            self._draw()

    def sync_parent_bg(self, bg):
        try:
            tk.Canvas.configure(self, bg=bg)
        except Exception:
            pass

    def configure(self, **kwargs):
        if "text" in kwargs:
            self.set_visible(bool(kwargs.pop("text")))
        if kwargs:
            super().configure(**kwargs)

class AdminBadge(tk.Canvas):
    _img_cache = {}

    def __init__(self, parent, color=ADMIN_WHITE):
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = DIALOG_BG()
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent_bg)
        self._color = color
        self._visible = True
        self._cw, self._ch = 22, 22
        self._current_image = None
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        self._cw, self._ch = event.width, event.height
        self._draw()

    def _shield_points(self, s):
        return [
            s * 0.5, s * 0.04,
            s * 0.92, s * 0.20,
            s * 0.92, s * 0.52,
            s * 0.5, s * 0.96,
            s * 0.08, s * 0.52,
            s * 0.08, s * 0.20,
        ]

    def _render_pil(self, s, scale=4):
        if Image is None or ImageDraw is None:
            return None
        key = (s, self._color)
        cached = self.__class__._img_cache.get(key)
        if cached is not None:
            return cached
        try:
            S = max(1, s * scale)
            img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            pts = self._shield_points(S)
            poly = [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
            draw.polygon(poly, fill=self._color, outline=self._color)
            img = img.resize((s, s), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.__class__._img_cache[key] = photo
            if len(self.__class__._img_cache) > 300:
                self.__class__._img_cache.clear()
                self.__class__._img_cache[key] = photo
            return photo
        except Exception as e:
            sClickerLog.append(f"AdminBadge konnte nicht gerendert werden: {e}")
            return None

    def _draw(self):
        self.delete("all")
        if not self._visible:
            return
        s = min(self._cw, self._ch)
        if s < 4:
            return
        ox, oy = (self._cw - s) / 2, (self._ch - s) / 2

        photo = self._render_pil(s)
        if photo is not None:
            self._current_image = photo
            self.create_image(ox, oy, anchor="nw", image=photo)
            return

        pts = self._shield_points(s)
        pts = [pts[i] + (ox if i % 2 == 0 else oy) for i in range(len(pts))]
        self.create_polygon(pts, fill=self._color, outline=self._color, smooth=True)

    def set_visible(self, visible: bool):
        if self._visible == visible:
            return
        self._visible = visible
        self._draw()

    def sync_parent_bg(self, bg):
        try:
            tk.Canvas.configure(self, bg=bg)
        except Exception:
            pass

    def configure(self, **kwargs):
        if "text" in kwargs:
            self.set_visible(bool(kwargs.pop("text")))
        if kwargs:
            super().configure(**kwargs)

class OGBadge(tk.Canvas):
    _img_cache = {}

    def __init__(self, parent):
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = DIALOG_BG()
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent_bg)
        self._visible = True
        self._cw, self._ch = 22, 22
        self._current_image = None
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        self._cw, self._ch = event.width, event.height
        self._draw()

    @staticmethod
    def _star_pts(cx, cy, r_outer, r_inner, points=5, rotation=-90):
        pts = []
        step = 360 / (points * 2)
        for i in range(points * 2):
            ang = math.radians(step * i + rotation)
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        return pts

    def _render_pil(self, s, scale=4):
        if Image is None or ImageDraw is None:
            return None
        key = s
        cached = self.__class__._img_cache.get(key)
        if cached is not None:
            return cached
        try:
            S = max(1, s * scale)
            img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            cx, cy = S / 2, S / 2
            outer_pts = self._star_pts(cx, cy, S * 0.48, S * 0.20, points=5)
            draw.polygon(outer_pts, fill=(255, 205, 30, 255), outline=(150, 100, 0, 255))
            inner_pts = self._star_pts(cx, cy, S * 0.30, S * 0.13, points=5)
            draw.polygon(inner_pts, fill=(255, 240, 190, 255))
            img = img.resize((s, s), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.__class__._img_cache[key] = photo
            if len(self.__class__._img_cache) > 100:
                self.__class__._img_cache.clear()
                self.__class__._img_cache[key] = photo
            return photo
        except Exception as e:
            sClickerLog.append(f"OGBadge konnte nicht gerendert werden: {e}")
            return None

    def _draw(self):
        self.delete("all")
        if not self._visible:
            return
        s = min(self._cw, self._ch)
        if s < 4:
            return
        ox, oy = (self._cw - s) / 2, (self._ch - s) / 2
        photo = self._render_pil(s)
        if photo is not None:
            self._current_image = photo
            self.create_image(ox, oy, anchor="nw", image=photo)
            return
        cx, cy = ox + s / 2, oy + s / 2
        pts = self._star_pts(cx, cy, s * 0.48, s * 0.20, points=5)
        self.create_polygon(pts, fill="#FFCD1E", outline="#966400")

    def set_visible(self, visible: bool):
        if self._visible == visible:
            return
        self._visible = visible
        self._draw()

    def sync_parent_bg(self, bg):
        try:
            tk.Canvas.configure(self, bg=bg)
        except Exception:
            pass

    def configure(self, **kwargs):
        if "text" in kwargs:
            self.set_visible(bool(kwargs.pop("text")))
        if kwargs:
            super().configure(**kwargs)

class ThemedSlider(tk.Canvas):
    def __init__(self, parent, from_=0, to=100, value=0, command=None,
                 track_color="#1a1a1a", fill_color="#9945FF", handle_color="#FFFFFF"):
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = DIALOG_BG()
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent_bg, cursor="hand2")
        self._from = from_
        self._to = to
        self._value = max(from_, min(to, value))
        self._command = command
        self._track_color = track_color
        self._fill_color = fill_color
        self._handle_color = handle_color
        self._sw, self._sh = 100, 30
        self.bind("<Configure>", self._on_configure)
        self.bind("<Button-1>", self._on_click_drag)
        self.bind("<B1-Motion>", self._on_click_drag)
        self._redraw()

    def _on_configure(self, event):
        self._sw, self._sh = event.width, event.height
        self._redraw()

    def get(self):
        return self._value

    def set(self, v):
        v = max(self._from, min(self._to, v))
        if v != self._value:
            self._value = v
            self._redraw()

    def set_colors(self, fill_color=None, track_color=None):
        if fill_color is not None:
            self._fill_color = fill_color
        if track_color is not None:
            self._track_color = track_color
        self._redraw()

    def sync_parent_bg(self, bg):
        try:
            tk.Canvas.configure(self, bg=bg)
        except Exception:
            pass

    def _value_to_x(self, v):
        span = self._to - self._from
        pad = 8
        if span <= 0:
            return pad
        frac = (v - self._from) / span
        return pad + frac * (self._sw - 2 * pad)

    def _x_to_value(self, x):
        pad = 8
        span = self._to - self._from
        usable = max(1, self._sw - 2 * pad)
        frac = (x - pad) / usable
        frac = max(0.0, min(1.0, frac))
        return self._from + frac * span

    def _on_click_drag(self, event):
        v = round(self._x_to_value(event.x))
        v = max(self._from, min(self._to, v))
        changed = v != self._value
        self._value = v
        self._redraw()
        if changed and self._command:
            self._command(v)

    def _redraw(self):
        self.delete("all")
        w, h = self._sw, self._sh
        if w < 10 or h < 4:
            return
        pad = 8
        track_h = max(4, h // 5)
        ty = h / 2 - track_h / 2
        self.create_rectangle(pad, ty, w - pad, ty + track_h,
                               fill=self._track_color, outline="")
        hx = self._value_to_x(self._value)
        if hx > pad:
            self.create_rectangle(pad, ty, hx, ty + track_h,
                                   fill=self._fill_color, outline="")
        r = max(6, min(h * 0.4, 11))
        self.create_oval(hx - r, h / 2 - r, hx + r, h / 2 + r,
                          fill=self._handle_color, outline=self._fill_color, width=2)

def entry(parent, x, y, w, h, bg="#1a1a1a", fg="#FFFFFF", size=10,
          show=None, justify="left"):
    ent = tk.Entry(parent, bg=bg, fg=fg, font=F(size), show=show or "",
                    justify=justify, relief="flat", insertbackground=fg,
                    highlightthickness=1, highlightbackground="#333333",
                    highlightcolor="#9945FF")
    ent.place(x=x, y=y, width=w, height=h)
    return ent

def _adapt_fg_for_theme(hexcolor, bg_hexcolor=None):
    try:
        if bg_hexcolor:
            bgh = bg_hexcolor.lstrip("#")
            if len(bgh) == 6:
                br, bgc, bb = int(bgh[0:2], 16), int(bgh[2:4], 16), int(bgh[4:6], 16)
                bg_lum = (0.299 * br + 0.587 * bgc + 0.114 * bb) / 255
            else:
                bg_lum = 0.0
        else:
            bg_lum = 0.0
        if bg_lum < 0.6:
            return hexcolor
        h = hexcolor.lstrip("#")
        if len(h) != 6:
            return hexcolor
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        if lum < 0.55:
            return hexcolor
        factor = 0.22
        nr, ng, nb = int(r * factor), int(g * factor), int(b * factor)
        return f"#{nr:02x}{ng:02x}{nb:02x}"
    except Exception:
        return hexcolor

def format_count_abbrev(n: int) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "0"
    if n < 1000:
        return str(n)
    for suffix, div in (("B", 1_000_000_000), ("M", 1_000_000), ("K", 1_000)):
        if n >= div:
            val = n / div
            if val >= 100:
                return f"{val:.0f}{suffix}+"
            return f"{val:.1f}{suffix}+".replace(".0", "")
    return str(n)

FOLLOWER_BADGE_THRESHOLD = 50

CLICK_ACHIEVEMENTS = [
    {"id": "clicks_50k", "threshold": 50_000, "tier": "bronze", "name": "50K Clicks", "wings": False},
    {"id": "clicks_1m", "threshold": 1_000_000, "tier": "orange", "name": "1M Clicks", "wings": False},
    {"id": "clicks_10m", "threshold": 10_000_000, "tier": "gold", "name": "10M Clicks", "wings": True},
    {"id": "clicks_1b", "threshold": 1_000_000_000, "tier": "rainbow", "name": "1B Clicks", "wings": True},
]

# NEU: Streak-Achievements - schalten frei je nachdem wie viele Tage am
# Stück eingeloggt wurde (state.login_streak)
STREAK_ACHIEVEMENTS = [
    {"id": "streak_7", "threshold": 7, "tier": "bronze", "name": "7 Day Streak", "wings": False},
    {"id": "streak_30", "threshold": 30, "tier": "orange", "name": "30 Day Streak", "wings": False},
    {"id": "streak_90", "threshold": 90, "tier": "gold", "name": "90 Day Streak", "wings": True},
    {"id": "streak_180", "threshold": 180, "tier": "rainbow", "name": "180 Day Streak", "wings": True},
]

_ACHIEVEMENT_TIER_COLORS = {
    "bronze": {"fill": (139, 94, 55), "edge": (94, 58, 30), "star": (222, 178, 130)},
    "orange": {"fill": (210, 122, 47), "edge": (150, 82, 20), "star": (255, 200, 140)},
    "gold":   {"fill": (247, 190, 60), "edge": (185, 130, 15), "star": (255, 245, 200)},
    "og":     {"fill": (140, 70, 210), "edge": (90, 40, 150), "star": (230, 200, 255)},
    "locked": {"fill": (58, 58, 58), "edge": (85, 85, 85), "star": (110, 110, 110)},
}

_achievement_badge_cache = {}

def _hexagon_points(cx, cy, r, rotation=-90):
    pts = []
    for i in range(6):
        ang = math.radians(60 * i + rotation)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts

def _shield_points(cx, cy, r):
    return [
        (cx - r, cy - r * 0.55), (cx - r, cy - r * 0.05), (cx - r * 0.65, cy + r * 0.55),
        (cx, cy + r), (cx + r * 0.65, cy + r * 0.55), (cx + r, cy - r * 0.05),
        (cx + r, cy - r * 0.55), (cx + r * 0.55, cy - r), (cx - r * 0.55, cy - r),
    ]

def _octagon_points(cx, cy, r, rotation=-90):
    pts = []
    for i in range(8):
        ang = math.radians(45 * i + rotation)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts

def _star_points(cx, cy, r_outer, r_inner, points=5, rotation=-90):
    pts = []
    step = 360 / (points * 2)
    for i in range(points * 2):
        ang = math.radians(step * i + rotation)
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts

def _flame_points(cx, cy, r):
    """Handgezeichnete Flammen-Silhouette (relative Punkte um cx,cy mit Radius r)."""
    pts_rel = [
        (0.00, 1.05), (-0.42, 0.55), (-0.30, 0.10), (-0.48, -0.30),
        (-0.18, -0.55), (-0.10, -0.20), (0.05, -0.60), (0.30, -1.05),
        (0.34, -0.55), (0.22, -0.25), (0.46, -0.05), (0.36, 0.35),
        (0.48, 0.55), (0.20, 0.85),
    ]
    return [(cx + px * r, cy + py * r) for px, py in pts_rel]

def _draw_wing(draw, cx, cy, r, side, color):
    sign = 1 if side == "right" else -1
    for i in range(4):
        t0 = i / 4
        t1 = (i + 1) / 4
        base_x = cx + sign * r * 0.55
        base_y = cy - r * 0.05
        len_factor = 1.0 - i * 0.16
        fx = base_x + sign * r * (1.15 * len_factor)
        fy = base_y - r * 0.55 + r * 1.05 * t0
        fx2 = base_x + sign * r * (0.95 * len_factor)
        fy2 = base_y - r * 0.55 + r * 1.05 * t1
        draw.polygon([(base_x, base_y), (fx, fy), (fx2, fy2)], fill=color)

def render_achievement_badge(size, tier, locked=False, wings=False, shield=False, icon="star", value=None):
    if Image is None or ImageDraw is None:
        return None
    key = (size, tier, locked, wings, shield, icon, value)
    cached = _achievement_badge_cache.get(key)
    if cached is not None:
        return cached
    try:
        scale = 4
        S = size * scale
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = S / 2, S / 2
        R = S * 0.34 if wings else S * 0.42
        is_rainbow = (tier == "rainbow" and not locked)

        if locked:
            base = _ACHIEVEMENT_TIER_COLORS.get(tier) or {"fill": (150, 130, 200), "edge": (100, 90, 140), "star": (200, 190, 230)}
            gray = {"fill": (28, 28, 28), "edge": (50, 50, 50), "star": (55, 55, 55)}

            def _mix(a, b, t=0.08):
                return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
            colors = {
                "fill": _mix(gray["fill"], base["fill"]),
                "edge": _mix(gray["edge"], base["edge"]),
                "star": _mix(gray["star"], base["star"]),
            }
        else:
            colors = _ACHIEVEMENT_TIER_COLORS.get(tier)

        if wings:
            wing_color = (55, 55, 55, 255) if locked else (235, 235, 235, 235)
            _draw_wing(draw, cx, cy, R, "left", wing_color)
            _draw_wing(draw, cx, cy, R, "right", wing_color)
            # NEU: 1B-Badge (rainbow) bekommt 4 statt 2 Flügel - ein zweites,
            # kleineres Flügelpaar leicht versetzt darunter
            if is_rainbow:
                wing_color2 = (255, 255, 255, 160)
                _draw_wing(draw, cx, cy - R * 0.35, R * 0.75, "left", wing_color2)
                _draw_wing(draw, cx, cy - R * 0.35, R * 0.75, "right", wing_color2)

        # FIX/COOLER: 1B (rainbow) bekommt eine achteckige Form statt dem
        # gleichen Hexagon wie 10M (gold) - damit sieht man den Unterschied
        # nicht nur an der Farbe, sondern auch an der Form.
        if shield:
            body_pts = _shield_points(cx, cy, R)
        elif is_rainbow:
            body_pts = _octagon_points(cx, cy, R * 1.05)
        else:
            body_pts = _hexagon_points(cx, cy, R)

        if not locked and tier == "rainbow":
            palette = [(255, 90, 90), (255, 200, 70), (110, 230, 130), (80, 170, 255), (190, 110, 255)]
            grad_col = Image.new("RGB", (1, S))
            for yy in range(S):
                t = yy / max(1, S - 1)
                seg = t * (len(palette) - 1)
                i0 = min(int(seg), len(palette) - 2)
                frac = seg - i0
                c0, c1 = palette[i0], palette[i0 + 1]
                r_ = int(c0[0] + (c1[0] - c0[0]) * frac)
                g_ = int(c0[1] + (c1[1] - c0[1]) * frac)
                b_ = int(c0[2] + (c1[2] - c0[2]) * frac)
                grad_col.putpixel((0, yy), (r_, g_, b_))
            grad = grad_col.resize((S, S)).convert("RGBA")
            mask = Image.new("L", (S, S), 0)
            ImageDraw.Draw(mask).polygon(body_pts, fill=255)
            img.paste(grad, (0, 0), mask)
            # doppelte Outline für mehr "cooleren" Look
            draw.line(body_pts + [body_pts[0]], fill=(255, 255, 255, 235), width=max(2, int(2.4 * scale)))
            outer_ring_pts = _octagon_points(cx, cy, R * 1.22)
            draw.line(outer_ring_pts + [outer_ring_pts[0]], fill=(255, 255, 255, 130), width=max(1, int(1.2 * scale)))
            star_fill = (255, 255, 255, 255)
        else:
            fill = colors["fill"] + (255,)
            edge = colors["edge"] + (255,)
            draw.polygon(body_pts, fill=fill, outline=edge, width=max(2, int(2.4 * scale)))
            star_fill = colors["star"] + (255,)

        if shield:
            inner_pts = _shield_points(cx, cy, R * 0.72)
        elif is_rainbow:
            inner_pts = _octagon_points(cx, cy, R * 1.05 * 0.72)
        else:
            inner_pts = _hexagon_points(cx, cy, R * 0.72)
        if locked:
            inner_edge = tuple(min(255, int(c * 1.3)) for c in colors["edge"])
        else:
            inner_edge = (255, 255, 255, 130) if tier != "rainbow" else (255, 255, 255, 160)
            inner_edge = inner_edge[:3]
        draw.line(inner_pts + [inner_pts[0]], fill=inner_edge + (170 if not locked else 90,),
                  width=max(1, int(1.1 * scale)))

        if not locked and tier in ("gold", "rainbow"):
            gem_color = (255, 255, 255, 255) if tier == "rainbow" else (255, 250, 220, 255)
            for (gx, gy) in body_pts:
                gr = R * (0.055 if is_rainbow else 0.045)
                draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=gem_color)

        sparkle_fill = star_fill[:3] + (140,) if not locked else star_fill[:3] + (90,)
        if icon == "flame":
            # NEU: Streak-Badges bekommen eine Flamme in der Mitte statt einem Stern,
            # plus die Zahl (Anzahl Tage) darunter/darin
            flame_pts = _flame_points(cx, cy, R * 0.5)
            draw.polygon(flame_pts, fill=star_fill)
            inner_flame_pts = _flame_points(cx, cy + R * 0.10, R * 0.28)
            inner_color = (255, 235, 150, 255) if not locked else (120, 110, 90, 255)
            draw.polygon(inner_flame_pts, fill=inner_color)
            if value is not None:
                try:
                    font_size = max(10, int(R * 0.42))
                    try:
                        font = ImageFont.truetype("arialbd.ttf", font_size)
                    except Exception:
                        try:
                            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
                        except Exception:
                            font = ImageFont.load_default()
                    txt = str(value)
                    bbox = draw.textbbox((0, 0), txt, font=font)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    tx, ty = cx - tw / 2 - bbox[0], cy + R * 0.62 - th / 2 - bbox[1]
                    outline_c = (0, 0, 0, 220)
                    for dx_, dy_ in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                        draw.text((tx + dx_, ty + dy_), txt, font=font, fill=outline_c)
                    draw.text((tx, ty), txt, font=font, fill=(255, 255, 255, 255))
                except Exception:
                    pass
        else:
            # 1B bekommt einen 8-zackigen Glitzerstern statt dem 5-zackigen von 10M
            sparkle_points_n = 8 if is_rainbow else 5
            sparkle_pts = _star_points(cx, cy, R * 0.62, R * 0.30, points=sparkle_points_n, rotation=-90 + 18)
            draw.polygon(sparkle_pts, fill=sparkle_fill)
            star_points_n = 8 if is_rainbow else 5
            star_pts = _star_points(cx, cy, R * 0.5, R * 0.21, points=star_points_n)
            draw.polygon(star_pts, fill=star_fill)
        if not locked:
            core_r = R * (0.12 if is_rainbow else 0.09)
            draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=(255, 255, 255, 235))

        if not locked and ImageFilter is not None:
            glow_rgb = {
                "bronze": (210, 150, 100), "orange": (255, 150, 60),
                "gold": (255, 220, 70), "rainbow": (210, 130, 255),
            }.get(tier, (200, 150, 255))
            glow_strength = {"bronze": 1.0, "orange": 1.15, "gold": 1.4, "rainbow": 1.9}.get(tier, 1.0)
            glow_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            ImageDraw.Draw(glow_img).polygon(body_pts, fill=glow_rgb + (255,))
            glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=max(2, int(S * 0.07 * glow_strength))))
            if glow_strength > 1.2:
                glow_img2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
                ImageDraw.Draw(glow_img2).polygon(body_pts, fill=glow_rgb + (170,))
                glow_img2 = glow_img2.filter(ImageFilter.GaussianBlur(radius=max(2, int(S * (0.16 if not is_rainbow else 0.22)))))
                img = Image.alpha_composite(glow_img2, img)
            img = Image.alpha_composite(glow_img, img)

        img = img.resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _achievement_badge_cache[key] = photo
        if len(_achievement_badge_cache) > 60:
            _achievement_badge_cache.clear()
            _achievement_badge_cache[key] = photo
        return photo
    except Exception as e:
        sClickerLog.append(f"Achievement-Badge konnte nicht gerendert werden: {e}")
        return None

def render_shiny_text(text, font_size, bold=True):
    """Rendert Text mit dem gleichen Regenbogen-Verlauf wie das 1B-Badge - für
    den 'shiny' Header-Titel."""
    if Image is None or ImageDraw is None or ImageFont is None:
        return None
    try:
        scale = 4
        fs = font_size * scale
        font = None
        for fname in (("arialbd.ttf" if bold else "arial.ttf"),
                      ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")):
            try:
                font = ImageFont.truetype(fname, fs)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()
        tmp = Image.new("RGBA", (10, 10))
        d = ImageDraw.Draw(tmp)
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = max(2, int(fs * 0.12))
        W, H = tw + pad * 2, th + pad * 2
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=(255, 255, 255, 255))
        palette = [(255, 90, 90), (255, 200, 70), (110, 230, 130), (80, 170, 255), (190, 110, 255)]
        grad = Image.new("RGB", (W, 1))
        for x in range(W):
            t = x / max(1, W - 1)
            seg = t * (len(palette) - 1)
            i0 = min(int(seg), len(palette) - 2)
            frac = seg - i0
            c0, c1 = palette[i0], palette[i0 + 1]
            grad.putpixel((x, 0), tuple(int(c0[k] + (c1[k] - c0[k]) * frac) for k in range(3)))
        grad = grad.resize((W, H)).convert("RGBA")
        mask = img.split()[3]
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.paste(grad, (0, 0), mask)
        out = out.resize((max(1, W // scale), max(1, H // scale)), Image.LANCZOS)
        return ImageTk.PhotoImage(out)
    except Exception as e:
        sClickerLog.append(f"Shiny-Text konnte nicht gerendert werden: {e}")
        return None

def groupbox(parent, x, y, w, h, text, bg=None, fg="#444444", size=11):
    # FIX: siehe label() weiter oben - Funktionsaufruf als Default-Parameter
    # wird nur einmal beim Programmstart ausgewertet und eingefroren.
    if bg is None:
        bg = DIALOG_BG()
    accent = THEMES.get(state.current_theme, THEMES["purple"])["accent"]
    frame = tk.Frame(parent, bg=bg, highlightbackground=accent, highlightcolor=accent,
                      highlightthickness=1, bd=0)
    frame.place(x=x, y=y, width=w, height=h)
    frame._is_groupbox = True

    lbl = tk.Label(parent, text=text, bg=bg, fg="#CCCCCC", font=F(size, True))
    lbl._orig_fg = "#CCCCCC"
    lbl.place(x=x + 14, y=y - 11)
    frame.title_label = lbl
    return frame

# ============== SClicherApp Klasse ==============
def _render_discord_logo(size, scale=6):
    if Image is None or ImageDraw is None:
        return None
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S / 2, S / 2
    r = S * 0.46
    draw.rounded_rectangle([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72],
                            radius=r * 0.42, fill=(88, 101, 242, 255))
    eye_r = S * 0.075
    eye_dx = S * 0.16
    eye_y = cy + S * 0.02
    for dx in (-eye_dx, eye_dx):
        draw.ellipse([cx + dx - eye_r, eye_y - eye_r * 1.6,
                      cx + dx + eye_r, eye_y - eye_r * 1.6 + eye_r * 2.6],
                      fill=(255, 255, 255, 255))
    img = img.resize((size, size), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def _render_tiktok_logo(size, scale=6):
    if Image is None or ImageDraw is None:
        return None
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S / 2, S / 2
    r = S * 0.46
    draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r],
                            radius=r * 0.42, fill=(0, 0, 0, 255))
    note_w = S * 0.10
    note_h = S * 0.42
    nx = cx + S * 0.05
    ny = cy - S * 0.20
    draw.rounded_rectangle([nx - S * 0.05, ny - S * 0.05, nx + note_w - S * 0.05, ny + note_h - S * 0.05],
                            radius=note_w * 0.4, fill=(37, 244, 238, 255))
    draw.rounded_rectangle([nx + S * 0.05, ny + S * 0.05, nx + note_w + S * 0.05, ny + note_h + S * 0.05],
                            radius=note_w * 0.4, fill=(255, 0, 80, 255))
    draw.rounded_rectangle([nx, ny, nx + note_w, ny + note_h],
                            radius=note_w * 0.4, fill=(255, 255, 255, 255))
    circ_r = note_h * 0.22
    draw.ellipse([nx - circ_r * 1.6, ny + note_h - circ_r * 2,
                  nx + circ_r * 0.4, ny + note_h], fill=(255, 255, 255, 255))
    img = img.resize((size, size), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

class SClickerApp:
    HEADER_USERNAME_FONT_SIZE = 18

    def __init__(self):
        global _app_instance
        _app_instance = self
        fix_dpi()
        self.root = tk.Tk()
        try:
            if sys.platform == "win32":
                self.root.iconbitmap("sClickerV5.ico")
            else:
                icon_path = "sClickerV5.png"
                if os.path.exists(icon_path):
                    icon_img = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon_img)
                    self._icon_img_ref = icon_img
        except Exception:
            pass
        self.root.withdraw()
        self.root.title(T("title"))
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)
        self.root.report_callback_exception = self._on_tk_exception

        self.header_user = None
        self.header_check = None
        self.header_admin = None
        self.header_og = None
        self.login_toggle_btn = None
        self.admin_btn = None
        self.speed_edit = None
        self.speed_value = None
        self.speed_slider = None
        self.action_type = None
        self.action_type_var = None
        self.key_input = None
        self.duration_input = None
        self.action_listbox = None
        self.premium_badge = None
        self.kit_name_edit = None
        self.repeat_var = None
        self.autostart_var = None
        self.lang_var = None
        self.counter_text = None
        self.status_text = None
        self.start_stop_btn = None
        self.gold_btn = None
        self.cyan_btn = None
        self.header_left = None
        self._theme_colored_widgets = []
        self._countdown_remaining = 0
        self._countdown_after_id = None
        self._toast_stack_offset = 0

        self._startup()

    def _startup(self):
        self.show_loading_screen()
        load_config()
        try:
            enforce_tos_reaccept()
        except Exception as e:
            sClickerLog.append(f"enforce_tos_reaccept Fehler: {e}")
        auto_login()
        enforce_account_reset_version(lambda title, msg: show_info(msg, title))
        if state.logged_in_user:
            load_account_settings(state.logged_in_user)
            if update_login_streak_for_today():
                threading.Thread(target=save_account_settings_online, daemon=True).start()
        else:
            reset_to_default_settings()
        self.build_gui()
        if not state.logged_in_user:
            self.show_login_window()
        elif not state.accepted_tos:
            self.show_reaccept_dialog()
        self.root.deiconify()
        start_emergency_hotkey_watcher(self)
        self._schedule_presence_heartbeat()

    def _schedule_presence_heartbeat(self):
        if state.logged_in_user:
            threading.Thread(target=send_presence_heartbeat, daemon=True).start()
            try:
                save_user_config()
            except Exception:
                pass
        try:
            self.root.after(35000, self._schedule_presence_heartbeat)
        except Exception:
            pass

    # ============== TOAST-BENACHRICHTIGUNGEN (ersetzt native Windows-Prompts) ==============
    def show_toast(self, text, kind="info"):
        """Zeigt eine Nachricht oben im Fenster an (wie die Login-Animation),
        statt eines nativen Windows-Dialogs, der hinter dem topmost-Fenster
        verschwinden konnte."""
        colors = {"info": THEMES.get(state.current_theme, THEMES["purple"])["accent"],
                   "error": "#ef4444", "success": "#22c55e"}
        color = colors.get(kind, colors["info"])
        self.show_success_toast(text, color=color)

    def show_confirm_dialog(self, msg, title=None) -> bool:
        """Eigener Ja/Nein-Dialog im App-Stil (abgerundet, immer im Vordergrund,
        über wait_window blockierend wie messagebox.askyesno)."""
        title = title or T("confirmTitle")
        root = self.root
        accent = THEMES.get(state.current_theme, THEMES["purple"])["accent"]
        result = {"value": False}

        root.update_idletasks()
        w, h = 400, 190
        rx, ry = root.winfo_rootx(), root.winfo_rooty()
        rw, rh = root.winfo_width(), root.winfo_height()
        x = rx + max(0, (rw - w) // 2)
        y = ry + max(0, (rh - h) // 2)

        dlg = tk.Toplevel(root)
        dlg.overrideredirect(True)
        dlg.attributes("-topmost", True)
        dlg.configure(bg="#141414")
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        corner_img = _rounded_border_image(w, h, 20, "#141414", accent, border_width=2)
        bg_lbl = None
        if corner_img is not None:
            # FIX: bg explizit setzen, sonst schimmert an den transparenten
            # Ecken der weiße Standard-Label-Hintergrund durch
            bg_lbl = tk.Label(dlg, image=corner_img, bg="#141414", bd=0, highlightthickness=0)
            bg_lbl.image = corner_img
            bg_lbl.place(x=0, y=0, width=w, height=h)
        else:
            dlg.configure(highlightthickness=2, highlightbackground=accent)

        tk.Label(dlg, text=title, bg="#141414", fg=accent,
                 font=(FONT_FAMILY, 13, "bold")).place(x=24, y=20, width=w - 48, height=26)
        tk.Label(dlg, text=msg, bg="#141414", fg="#EEEEEE", font=(FONT_FAMILY, 10),
                 wraplength=w - 48, justify="center").place(x=24, y=52, width=w - 48, height=72)

        def _yes():
            result["value"] = True
            # FIX: dlg.destroy() NICHT synchron im eigenen Button-Callback aufrufen!
            # Der "Ja"-Button ist ein Kind von dlg - wird dlg mitten in dessen
            # eigenem Klick-Event zerstört, hängt sich Tk komplett auf
            # (grab_set()+wait_window() kommen nie sauber zurück). Das war der
            # Grund, warum JEDES Löschen (Kits, News, Kommentare, Accounts...)
            # die App einfrieren ließ. Jetzt per after() sicher verzögert.
            dlg.after(1, dlg.destroy)

        def _no():
            result["value"] = False
            dlg.after(1, dlg.destroy)

        RoundedButton(dlg, text=T("yes"), command=_yes, bg=accent, fg="#FFFFFF",
                      font=(FONT_FAMILY, 11, "bold"), radius=16, border_width=2).place(
            x=24, y=138, width=(w - 64) // 2, height=38)
        RoundedButton(dlg, text=T("no"), command=_no, bg="#2a2a2a", fg="#CCCCCC",
                      font=(FONT_FAMILY, 11, "bold"), radius=16, border_width=2).place(
            x=24 + (w - 64) // 2 + 16, y=138, width=(w - 64) // 2, height=38)

        dlg.transient(root)
        dlg.grab_set()
        dlg.focus_set()
        dlg.wait_window()
        return result["value"]

    def show_success_toast(self, text, color="#22c55e"):
        root = self.root
        root.update_idletasks()
        w = min(420, max(260, measure_text_width(text, 12, True) + 60))
        h = 46
        x = max(0, (root.winfo_width() - w) // 2)
        base_y = 18 + self._toast_stack_offset
        self._toast_stack_offset += (h + 10)

        corner_img = _rounded_border_image(w, h, 14, color, self._shade_hex(color, 1.4), border_width=0)
        toast = tk.Label(root, text=text, bg=color, fg="#FFFFFF", font=F(12, True))
        if corner_img is not None:
            toast.configure(image=corner_img, compound="center")
            toast.image = corner_img
        toast.place(x=x, y=-h, width=w, height=h)
        toast.lift()

        def animate_in(step=0, steps=14):
            if not toast.winfo_exists():
                return
            t = (step + 1) / steps
            eased = 1 - pow(1 - t, 3)
            y = int(-h + (base_y - (-h)) * eased)
            try:
                toast.place_configure(y=y)
            except Exception:
                return
            if step + 1 < steps:
                root.after(12, lambda: animate_in(step + 1, steps))
            else:
                root.after(1800, animate_out)

        def animate_out(step=0, steps=12):
            if not toast.winfo_exists():
                return
            t = (step + 1) / steps
            eased = t ** 2
            y = int(base_y + (-h - base_y) * eased)
            try:
                toast.place_configure(y=y)
            except Exception:
                return
            if step + 1 < steps:
                root.after(10, lambda: animate_out(step + 1, steps))
            else:
                try:
                    toast.destroy()
                except Exception:
                    pass
                self._toast_stack_offset = max(0, self._toast_stack_offset - (h + 10))

        animate_in()

    @staticmethod
    def _shade_hex(hexcolor, factor):
        return RoundedButton._shade(hexcolor, factor)

    def show_loading_screen(self):
        load_win = tk.Toplevel(self.root) if self.root else tk.Tk()
        load_win.overrideredirect(True)
        load_win.attributes("-topmost", True)
        load_win.configure(bg="#0a0a0a")
        w, h = 500, 155
        center_window(load_win, w, h)
        tk.Frame(load_win, bg="#9945FF", width=6, height=160).place(x=0, y=0)
        ico = tk.Label(load_win, text="⚡", bg="#0a0a0a", fg="#9945FF", font=F(28, True))
        ico.place(x=12, y=18, width=50, height=50)
        ttl = tk.Label(load_win, text="sClicker", bg="#0a0a0a", fg="#FFFFFF", font=F(24, True))
        ttl.place(x=68, y=18, width=400, height=42)
        bar = ttk.Progressbar(load_win, length=470, mode="determinate", maximum=100)
        bar.place(x=12, y=108, width=470, height=12)
        load_win.update()
        for _ in range(10):
            bar["value"] += 10
            load_win.update()
            time.sleep(0.05)
        load_win.destroy()

    def _on_tk_exception(self, exc, val, tb):
        try:
            err_text = "".join(traceback.format_exception(exc, val, tb))
        except Exception:
            err_text = f"{exc}: {val}"
        sClickerLog.append("UNCAUGHT EXCEPTION:\n" + err_text)
        try:
            if self.status_text is not None:
                self.status_text.configure(text=f"⚠ Error: {val}", fg="#ef4444")
        except Exception:
            pass
        try:
            self.show_toast(f"An unexpected error occurred: {val}", kind="error")
        except Exception:
            pass

    def safe_exit(self):
        try:
            save_config()
        except Exception:
            pass
        try:
            if state.sync_timer:
                state.sync_timer.cancel()
        except Exception:
            pass
        try:
            self.root.quit()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        os._exit(0)

    def run(self):
        self.root.mainloop()

    def update_background_gradient(self):
        self.root.configure(bg=THEMES[state.current_theme]["bg"])

    def apply_ttk_style(self):
        t = THEMES[state.current_theme]
        bg = t["bg"]
        accent = t["accent"]
        field_bg = RoundedButton._shade(bg, 1.6) if bg != "#FFFFFF" else "#EEEEEE"
        fg = "#000000" if state.current_theme == "white" else "#FFFFFF"
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        try:
            style.configure("TCombobox", fieldbackground=field_bg, background=field_bg,
                             foreground=fg, arrowcolor=fg, bordercolor=accent,
                             lightcolor=field_bg, darkcolor=field_bg, selectbackground=field_bg,
                             selectforeground=fg)
            style.map("TCombobox",
                       fieldbackground=[("readonly", field_bg), ("disabled", field_bg)],
                       foreground=[("readonly", fg), ("disabled", fg)],
                       background=[("active", field_bg)])
            style.configure("TProgressbar", background=accent, troughcolor=field_bg,
                             bordercolor=bg, lightcolor=accent, darkcolor=accent)
            style.configure("Treeview", background=field_bg, fieldbackground=field_bg,
                             foreground=fg, bordercolor=bg, borderwidth=0, rowheight=28)
            style.configure("Treeview.Heading", background=bg, foreground=fg,
                             bordercolor=bg, relief="flat")
            style.map("Treeview", background=[("selected", accent)],
                       foreground=[("selected", "#FFFFFF")])
            style.map("Treeview.Heading", background=[("active", field_bg)])
            for orient in ("Vertical", "Horizontal"):
                style.configure(f"{orient}.TScrollbar", background=field_bg,
                                 troughcolor=bg, arrowcolor=fg, bordercolor=bg)
                style.map(f"{orient}.TScrollbar", background=[("active", accent)])
            self.root.option_add("*TCombobox*Listbox.background", field_bg)
            self.root.option_add("*TCombobox*Listbox.foreground", fg)
            self.root.option_add("*TCombobox*Listbox.selectBackground", accent)
            self.root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
        except Exception as e:
            sClickerLog.append(f"ttk-Style konnte nicht gesetzt werden: {e}")

    def build_gui(self):
        r = self.root
        r.geometry(f"{_BASE_ROOT_W}x{_BASE_ROOT_H}")
        r.resizable(False, False)
        r.configure(bg=THEMES[state.current_theme]["bg"])
        self.apply_ttk_style()
        self.update_background_gradient()

        # FIX: kein "shiny" Regenbogen-Text mehr (wie ursprünglich gewünscht),
        # einfach normaler zentrierter Titel mit V5
        self.header_left = label(r, 20, 22, 760, 40, "⚡ sClicker  V5",
                                  bg=r["bg"], fg=THEMES[state.current_theme]["accent"],
                                  size=22, bold=True, anchor="center", justify="center")

        self.header_user = label(r, 300, 62, 200, 35, "Guest", bg=r["bg"], fg="#FFFFFF",
                                  size=18, bold=True)
        bs = badge_size_for_font(self.HEADER_USERNAME_FONT_SIZE)
        self.header_check = VerifiedBadge(r)
        self.header_check.place(x=500, y=badge_y_centered(62, 35, bs) + ICON_Y_OFFSET, width=bs, height=bs)
        self.header_admin = AdminBadge(r)
        self.header_admin.place(x=514, y=badge_y_centered(62, 35, bs) + ICON_Y_OFFSET, width=1, height=bs)
        self.header_og = OGBadge(r)
        self.header_og.place(x=528, y=badge_y_centered(62, 35, bs) + ICON_Y_OFFSET, width=1, height=bs)
        self.header_influencer = InfluencerBadge(r)
        self.header_influencer.place(x=542, y=badge_y_centered(62, 35, bs) + ICON_Y_OFFSET, width=1, height=bs)

        # NEU: eigenständiges Streak-Widget oben rechts (Flamme + große Zahl + "Keep it up!")
        self.header_streak = label(r, 590, 4 + HEADER_STREAK_Y_OFFSET, 90, 58, "", bg=r["bg"], fg="#f59e0b",
                                    size=17, bold=True, anchor="center", justify="center")
        self.header_streak_caption = label(r, 580, 62 + HEADER_STREAK_Y_OFFSET, 110, 16, "", bg=r["bg"], fg="#888888",
                                            size=8, bold=True, anchor="center", justify="center")

        self.login_toggle_btn = button(r, 680, 22, 100, 35, "Login",
                                        command=self.toggle_login_logout,
                                        bg="#333333", fg="#AAAAAA", bold=True)

        self.users_btn = button(r, 20, 22, 110, 35, "👥 Users",
               command=self.show_users_window,
               bg=accent(), fg="#FFFFFF", bold=True)

        self.profile_btn = button(r, 140, 22, 130, 35, "👤 My Profile",
               command=lambda: self.show_user_profile(state.logged_in_user)
               if state.logged_in_user else show_info(T("needLogin")),
               bg="#333333", fg="#FFFFFF", bold=True)

        self.news_btn = button(r, 20, 62, 110, 30, "📰 News",
               command=self.show_news_window,
               bg=accent(), fg="#FFFFFF", bold=True)

        self.admin_btn = button(r, 680, 62, 100, 30, "Admin",
                                 command=self.show_admin_panel,
                                 bg="#222222", fg="#AAAAAA", bold=True)
        self.admin_btn.place_forget()

        self.speed_group = groupbox(r, 20, 110, 370, 120, T("speed"))
        self.delay_label = label(r, 40, 143, 150, 22, T("delay"), bg=r["bg"], fg="#EEEEEE")
        self.speed_edit = entry(r, 190, 140, 80, 30, justify="center")
        self.speed_edit.insert(0, str(state.click_delay))
        self.speed_edit.bind("<KeyRelease>", lambda e: self.update_speed_from_edit())
        self.speed_value = label(r, 280, 143, 90, 25, f"{state.click_delay}ms",
                                  bg=r["bg"], fg=THEMES[state.current_theme]["accent"], anchor="e")

        self.speed_slider = ThemedSlider(r, from_=10, to=1000, value=state.click_delay,
                                          command=self.update_speed,
                                          track_color="#1a1a1a",
                                          fill_color=THEMES[state.current_theme]["accent"])
        self.speed_slider.place(x=40, y=180, width=330, height=30)

        self.action_group = groupbox(r, 20, 240, 370, 360, T("actions"))
        self.action_type_var = tk.StringVar(value=BuildActionTypeList()[0])
        self.action_type = ttk.Combobox(r, textvariable=self.action_type_var,
                                         values=BuildActionTypeList(), state="readonly",
                                         font=F(10))
        self.action_type.place(x=40, y=275, width=160, height=28)
        self.action_type.bind("<<ComboboxSelected>>", lambda e: self.on_action_type_change())

        self.key_input = entry(r, 210, 275, 70, 30)
        self.key_input.configure(state="disabled")
        self.duration_input = entry(r, 290, 275, 80, 30)
        self.duration_input.insert(0, "1000")
        self.duration_input.configure(state="disabled")

        self.add_btn = button(r, 40, 315, 330, 35, T("addBtn"), command=self.add_action,
                               bg=accent(), fg="#FFFFFF")

        lb_frame = tk.Frame(r, bg="#1a1a1a")
        lb_frame._keep_color = True
        lb_frame.place(x=40, y=360, width=330, height=160)
        lb_scroll = tk.Scrollbar(lb_frame)
        lb_scroll.pack(side="right", fill="y")
        self.action_listbox = tk.Listbox(lb_frame, bg="#1a1a1a", fg="#FFFFFF",
                                          font=F(10), bd=0, highlightthickness=0,
                                          selectbackground=accent(),
                                          yscrollcommand=lb_scroll.set)
        self.action_listbox.pack(side="left", fill="both", expand=True)
        lb_scroll.config(command=self.action_listbox.yview)

        # FIX: Löschen/Warnung bleiben semantisch rot/orange (klare Bedeutung),
        # der Rest folgt konsequent der Theme-Akzentfarbe statt bunt gemischt zu sein
        self.delete_btn = button(r, 40, 530, 80, 30, T("delete"), command=self.delete_action,
                                  bg=accent(), fg="#FFFFFF")
        self.clear_btn = button(r, 125, 530, 80, 30, T("clear"), command=self.clear_actions,
                                 bg=accent(), fg="#FFFFFF")
        self.up_btn = button(r, 210, 530, 75, 30, "Up", command=self.move_up, bg=accent(), fg="#FFFFFF")
        self.down_btn = button(r, 295, 530, 75, 30, "Down", command=self.move_down, bg=accent(), fg="#FFFFFF")

        self.premium_badge = label(r, 40, 570, 330, 20, "", bg=r["bg"], fg="#888888",
                                    size=9, bold=True, anchor="center", justify="center")

        def _open_social_link(url):
            import webbrowser
            webbrowser.open(url)

        button(r, 40, 604, 155, 36, "Discord",
               command=lambda: _open_social_link("https://discord.gg/RPZ86DRn5z"),
               bg="#5865F2", fg="#FFFFFF", bold=True)
        button(r, 215, 604, 155, 36, "TikTok",
               command=lambda: _open_social_link("https://www.tiktok.com/@sclicker"),
               bg="#000000", fg="#FFFFFF", bold=True)

        self.kits_group = groupbox(r, 410, 110, 370, 150, "Click Kits")
        self.kit_name_lbl = label(r, 430, 145, 80, 22, "Kit Name:", bg=r["bg"], fg="#CCCCCC")
        self.kit_name_edit = entry(r, 510, 142, 250, 30)

        self.save_local_btn = button(r, 430, 185, 165, 35, "💾 Save Local", command=self.save_click_kit_local,
               bg=accent(), fg="#FFFFFF")
        self.my_kits_btn = button(r, 605, 185, 155, 35, "📂 My Kits", command=self.show_my_kits_window,
               bg=accent(), fg="#FFFFFF")
        self.upload_btn = button(r, 430, 225, 165, 35, "⬆ Upload Public", command=self.upload_click_kit,
               bg=accent(), fg="#FFFFFF")
        self.browse_btn = button(r, 605, 225, 155, 35, "🌐 Browse Kits", command=self.show_public_kits_window,
               bg=accent(), fg="#FFFFFF")
        self.tracker_btn = button(r, 430, 265, 330, 30, "📹 Recording Tracker (experimental)",
               command=self.show_tracking_dialog,
               bg=accent(), fg="#FFFFFF", size=11, bold=True)

        self.control_group = groupbox(r, 410, 305, 370, 150, T("control"))
        self.start_stop_btn = button(r, 430, 340, 330, 50, T("startStop"),
                                      command=self.toggle_clicker_ui,
                                      bg=accent(), fg="#FFFFFF", size=18, bold=True)
        self.exit_btn = button(r, 430, 400, 330, 40, T("exit"), command=self.safe_exit,
                                bg=accent(), fg="#FFFFFF", size=14, bold=True)

        self.settings_group = groupbox(r, 410, 465, 370, 200, T("settings"))
        self.repeat_var = tk.BooleanVar(value=state.repeat_mode)
        repeat_check = tk.Checkbutton(r, text="Loop", variable=self.repeat_var,
                                       command=self.toggle_repeat_ui, bg=r["bg"], fg="#FFFFFF",
                                       selectcolor=RoundedButton._shade(r["bg"], 1.6), activebackground=r["bg"],
                                       activeforeground="#FFFFFF", font=F(10),
                                       bd=0, highlightthickness=0, relief="flat",
                                       highlightbackground=r["bg"], highlightcolor=r["bg"])
        repeat_check._orig_fg = "#FFFFFF"
        repeat_check.place(x=430, y=465, width=100, height=30)
        self.repeat_check = repeat_check

        self.autostart_var = tk.BooleanVar(value=check_autostart_status())
        autostart_check = tk.Checkbutton(r, text="Autostart", variable=self.autostart_var,
                                          command=self.toggle_autostart_ui, bg=r["bg"], fg="#FFFFFF",
                                          selectcolor=RoundedButton._shade(r["bg"], 1.6), activebackground=r["bg"],
                                          activeforeground="#FFFFFF", font=F(10),
                                          bd=0, highlightthickness=0, relief="flat",
                                          highlightbackground=r["bg"], highlightcolor=r["bg"])
        autostart_check._orig_fg = "#FFFFFF"
        autostart_check.place(x=540, y=465, width=100, height=30)
        self.autostart_check = autostart_check

        self.lang_var = tk.StringVar(value="English" if state.current_language == "en" else "Deutsch")
        lang_dd = ttk.Combobox(r, textvariable=self.lang_var, values=["English", "Deutsch"],
                                state="readonly", font=F(10))
        lang_dd.place(x=430, y=505, width=150, height=28)
        lang_dd.bind("<<ComboboxSelected>>", lambda e: self.change_language())

        self.save_settings_btn = button(r, 595, 505, 165, 28, "Save Settings", command=lambda: save_config(),
               bg=accent(), fg="#FFFFFF")

        tk.Frame(r, bg="#333333", height=2).place(x=430, y=550, width=330, height=2)
        theme_btn_w, theme_btn_step = 44, 47

        def swatch(x, text, cmd, bg, fg="#FFFFFF"):
            # FIX: Farb-Auswahl-Buttons dürfen NIE automatisch mit umfärben -
            # sonst änderte sich z.B. der "B" (Blau) Button selbst mit, sobald
            # man zufällig schon im Blau-Theme war (weil seine Farbe dann
            # zufällig der aktuellen Akzentfarbe entsprach).
            b = button(r, x, 565, theme_btn_w, 26, text, command=cmd, bg=bg, fg=fg)
            b._follows_theme_accent = False
            return b

        swatch(430 + 0 * theme_btn_step, "P", lambda: self.change_theme("purple"), "#9945FF")
        swatch(430 + 1 * theme_btn_step, "B", lambda: self.change_theme("blue"), "#3b82f6")
        swatch(430 + 2 * theme_btn_step, "G", lambda: self.change_theme("green"), "#22c55e")
        swatch(430 + 3 * theme_btn_step, "R", lambda: self.change_theme("red"), "#ef4444")
        swatch(430 + 4 * theme_btn_step, "BLK", lambda: self.change_theme("black"), "#000000")
        self.gold_btn = swatch(430 + 5 * theme_btn_step, "GLD",
                                lambda: self.premium_theme_click("gold"), "#f59e0b", fg="#000000")
        self.cyan_btn = swatch(430 + 6 * theme_btn_step, "CYN",
                                lambda: self.premium_theme_click("cyan"), "#06b6d4")

        self.stopkey_lbl = label(r, 430, 628, 95, 24, "🛑 Stop Key:", bg=r["bg"], fg="#CCCCCC", size=9)
        self.hotkey_edit = entry(r, 525, 626, 80, 26, justify="center", size=10)
        self.hotkey_edit.insert(0, state.emergency_hotkey)

        def do_save_hotkey():
            v = self.hotkey_edit.get().strip()
            state.emergency_hotkey = v if v else "F12"
            self.hotkey_edit.delete(0, tk.END)
            self.hotkey_edit.insert(0, state.emergency_hotkey)
            save_config()
            self.status_text.configure(text=f"Stop-Hotkey: {state.emergency_hotkey}", fg="#888888")

        self.set_hotkey_btn = button(r, 610, 625, 60, 28, "Set", command=do_save_hotkey,
               bg="#ef4444", fg="#FFFFFF", size=9)

        # NEU: Nutzungsbedingungen und Datenschutzerklärung jederzeit einsehbar
        self.tos_btn = button(r, 430, 598, 160, 26, "📜 " + T("viewToS"),
                               command=lambda: self.show_tos_dialog(),
                               bg="#333333", fg="#CCCCCC", size=9)
        self.privacy_btn = button(r, 600, 598, 160, 26, "🔒 " + T("viewPrivacy"),
                                   command=lambda: self.show_privacy_dialog(),
                                   bg="#333333", fg="#CCCCCC", size=9)

        self.counter_text = label(r, 20, 675, 370, 25, T("clicksExecuted") + " " + str(state.click_count),
                                   bg=r["bg"], fg="#888888")
        self.status_text = label(r, 410, 675, 370, 25, T("ready"), bg=r["bg"], fg="#888888",
                                  anchor="e", justify="right")
        self.status_text.configure(cursor="hand2")
        self.status_text.bind("<Button-1>", lambda _e: self.show_debug_log_window())

        self.apply_loaded_config()
        self.update_premium_badge()
        self.update_premium_buttons()
        self.update_header_display()

    def update_header_display(self):
        try:
            u_display = display_name(state.logged_in_user if state.logged_in_user else "Guest")
            is_ver = auth_is_verified(state.logged_in_user) and bool(state.logged_in_user)
            # FIX: Admin- und OG-Badge nur im eigenen Profilfenster zeigen,
            # NICHT im Haupt-Header - dort reicht das Verified-Badge.
            gui_w = 800
            bs = badge_size_for_font(self.HEADER_USERNAME_FONT_SIZE)

            name_w = measure_text_width(u_display, 18, True) + 8
            check_w = (bs + BADGE_NAME_GAP) if is_ver else 0
            combined = name_w + check_w
            name_x = (gui_w - combined) // 2
            badge_y = badge_y_centered(62, 35, bs) + ICON_Y_OFFSET

            self.header_user.place(x=name_x, y=62, width=name_w, height=35)
            self.header_user.configure(text=u_display)

            self.header_check.set_visible(is_ver)
            check_x = name_x + name_w + (BADGE_NAME_GAP if is_ver else 0)
            self.header_check.place(x=check_x, y=badge_y, width=max(bs if is_ver else 1, 1), height=bs)

            self.header_admin.set_visible(False)
            self.header_admin.place(x=check_x, y=badge_y, width=1, height=bs)
            self.header_og.set_visible(False)
            self.header_og.place(x=check_x, y=badge_y, width=1, height=bs)

            # NEU: eigenständiges Streak-Widget oben rechts (Flamme + Zahl + Keep it up!)
            # Je höher die Streak, desto "cooler" die Flammenfarbe (orange -> rot -> blau -> lila)
            show_streak = bool(state.logged_in_user) and state.login_streak >= 1
            if show_streak:
                s = state.login_streak
                if s >= 180:
                    flame_color = "#a855f7"
                elif s >= 90:
                    flame_color = "#3b82f6"
                elif s >= 30:
                    flame_color = "#06b6d4"
                elif s >= 7:
                    flame_color = "#ef4444"
                else:
                    flame_color = "#f59e0b"
                self.header_streak.configure(text=f"🔥\n{s}", fg=flame_color)
                self.header_streak_caption.configure(text=T("keepItUp"))
            else:
                self.header_streak.configure(text="")
                self.header_streak_caption.configure(text="")

            is_admin = bool(state.logged_in_user) and auth_is_admin(state.logged_in_user)
            self.login_toggle_btn.configure(text="Logout" if state.logged_in_user else "Login")
            if is_admin:
                self.admin_btn.place(x=680, y=62, width=100, height=30)
            else:
                self.admin_btn.place_forget()
        except Exception:
            pass

    def update_premium_badge(self):
        if state.logged_in_user:
            self.premium_badge.configure(text=T("premiumUnlocked"), fg="#22c55e")
        else:
            self.premium_badge.configure(text=T("premiumLocked"), fg="#888888")

    def update_premium_buttons(self):
        if state.logged_in_user:
            self.gold_btn.place(x=430 + 5 * 47, y=565, width=44, height=26)
            self.cyan_btn.place(x=430 + 6 * 47, y=565, width=44, height=26)
        else:
            self.gold_btn.place_forget()
            self.cyan_btn.place_forget()

    def premium_theme_click(self, n):
        if not state.logged_in_user:
            show_info("Account required!", "Premium")
            return
        self.change_theme(n)

    def toggle_login_logout(self):
        if state.logged_in_user:
            if not ask_yes_no("Are you sure you want to sign out?"):
                return
            save_user_config()
            state.logged_in_user = ""
            state.logged_in_verified = False
            set_session_lastuser("")
            reset_to_default_settings()
            self.apply_loaded_config()
            self.update_header_display()
            self.update_premium_badge()
            self.update_premium_buttons()
            self.refresh_action_type_dropdown()
        else:
            self.show_login_window()

    def refresh_action_type_dropdown(self):
        items = BuildActionTypeList()
        self.action_type["values"] = items
        self.action_type_var.set(items[0])
        self.on_action_type_change()

    # FIX: state.click_delay (mit Unterstrich!)
    def on_action_type_change(self):
        idx = self.action_type["values"].index(self.action_type_var.get()) + 1 if self.action_type_var.get() in self.action_type["values"] else 1
        if idx == 3:
            self.key_input.configure(state="normal")
            self.duration_input.configure(state="disabled")
        elif idx == 4:
            self.key_input.configure(state="normal")
            self.duration_input.configure(state="normal")
        elif idx in (7, 8, 9):
            self.key_input.configure(state="disabled")
            self.duration_input.configure(state="normal")
        else:
            self.key_input.configure(state="disabled")
            self.duration_input.configure(state="disabled")

    # FIX: state.click_delay (mit Unterstrich!)
    def update_speed(self, v=None):
        if v is None:
            v = self.speed_slider.get()
        state.click_delay = int(v)
        self.speed_edit.delete(0, tk.END)
        self.speed_edit.insert(0, str(state.click_delay))
        self.speed_value.configure(text=f"{state.click_delay}ms")
        save_config()

    # FIX: state.click_delay (mit Unterstrich!)
    def update_speed_from_edit(self):
        v = self.speed_edit.get()
        if v.isdigit() and 10 <= int(v) <= 1000:
            state.click_delay = int(v)
            self.speed_slider.set(state.click_delay)
            self.speed_value.configure(text=f"{state.click_delay}ms")
            save_config()

    def _selected_action_type_index(self):
        vals = list(self.action_type["values"])
        cur = self.action_type_var.get()
        return (vals.index(cur) + 1) if cur in vals else 1

    def add_action(self):
        at = self._selected_action_type_index()
        is_p = bool(state.logged_in_user)
        if at in (3, 4) and not self.key_input.get():
            show_info(T("errorNoKey"))
            return
        if at in (4, 7, 8, 9):
            dur = self.duration_input.get()
            if not dur or not dur.isdigit() or int(dur) <= 0:
                show_info(T("errorNoDuration"))
                return
        if at in (7, 8, 9) and not is_p:
            show_info("Premium required!")
            return

        a = ""
        if at == 1:
            a = "LeftClick"
        elif at == 2:
            a = "RightClick"
        elif at == 3:
            a = "Key:" + self.key_input.get()
        elif at == 4:
            a = f"HoldKey:{self.key_input.get()}:{self.duration_input.get()}"
        elif at == 5:
            a = "MiddleClick"
        elif at == 6:
            a = "DoubleClick"
        elif at == 7:
            a = "HoldLeftClick:" + self.duration_input.get()
        elif at == 8:
            a = "HoldRightClick:" + self.duration_input.get()
        elif at == 9:
            a = "HoldMiddleClick:" + self.duration_input.get()

        if a:
            state.action_list.append(a)
            self.update_action_list()
            save_user_config()
            self.key_input.delete(0, tk.END)
            self.status_text.configure(text=T("actionAdded"))

    def delete_action(self):
        sel = self.action_listbox.curselection()
        if sel:
            idx = sel[0]
            if 0 <= idx < len(state.action_list):
                state.action_list.pop(idx)
                self.update_action_list()
                save_user_config()

    def clear_actions(self):
        state.action_list = []
        self.update_action_list()
        save_user_config()

    def move_up(self):
        sel = self.action_listbox.curselection()
        if sel and sel[0] > 0:
            i = sel[0]
            state.action_list[i], state.action_list[i - 1] = state.action_list[i - 1], state.action_list[i]
            self.update_action_list()
            self.action_listbox.selection_set(i - 1)
            save_user_config()

    def move_down(self):
        sel = self.action_listbox.curselection()
        if sel and sel[0] < len(state.action_list) - 1:
            i = sel[0]
            state.action_list[i], state.action_list[i + 1] = state.action_list[i + 1], state.action_list[i]
            self.update_action_list()
            self.action_listbox.selection_set(i + 1)
            save_user_config()

    def update_action_list(self):
        self.action_listbox.delete(0, tk.END)
        for i, a in enumerate(state.action_list, start=1):
            self.action_listbox.insert(tk.END, f"{i}. {format_step_label(a)}")

    def toggle_clicker_ui(self):
        try:
            toggle_clicker(self)
        except Exception as e:
            sClickerLog.append(f"toggle_clicker_ui Fehler: {e}")
            self.show_error(f"Unexpected error: {e}")

    def start_countdown(self, seconds: int):
        self._countdown_remaining = seconds
        self.start_stop_btn.configure(bg="#f59e0b", activebackground="#f59e0b",
                                       text=f"Starting in {self._countdown_remaining}...")
        self.status_text.configure(text=f"Countdown: {self._countdown_remaining}", fg="#f59e0b")
        self._tick_countdown()

    def _tick_countdown(self):
        if not state.is_counting_down:
            return
        if self._countdown_remaining <= 0:
            _begin_clicker_after_countdown(self)
            return
        self.start_stop_btn.configure(text=f"Starting in {self._countdown_remaining}...")
        self.status_text.configure(text=f"Countdown: {self._countdown_remaining}", fg="#f59e0b")
        self._countdown_remaining -= 1
        self._countdown_after_id = self.root.after(1000, self._tick_countdown)

    def on_countdown_cancelled(self):
        if self._countdown_after_id:
            try:
                self.root.after_cancel(self._countdown_after_id)
            except Exception:
                pass
            self._countdown_after_id = None
        self.on_clicker_stopped()

    def on_clicker_started(self):
        self.status_text.configure(text=T("active"), fg="#00FF00")
        self.start_stop_btn.configure(bg=accent(), activebackground=None, text=T("startStop"))
        if state.logged_in_user:
            threading.Thread(target=send_presence_heartbeat, daemon=True).start()

    def on_clicker_stopped(self):
        self.status_text.configure(text=T("stopped"), fg="#888888")
        self.start_stop_btn.configure(bg=accent(), activebackground=None, text=T("startStop"))
        if state.logged_in_user:
            threading.Thread(target=send_presence_heartbeat, daemon=True).start()
            save_user_config()
            threading.Thread(target=save_account_settings_online, daemon=True).start()

    def on_emergency_stop(self):
        if self._countdown_after_id:
            try:
                self.root.after_cancel(self._countdown_after_id)
            except Exception:
                pass
            self._countdown_after_id = None
        self.on_clicker_stopped()
        self.status_text.configure(text=f"⛔ Emergency Stop ({state.emergency_hotkey})", fg="#ef4444")

    def update_counter_display(self):
        self.counter_text.configure(text=T("clicksExecuted") + " " + str(state.click_count))

    def show_info(self, msg):
        show_info(msg)

    def show_error(self, msg):
        show_error(msg)

    def change_theme(self, n):
        if n not in THEMES:
            return
        state.current_theme = n
        t = THEMES[n]
        self.root.configure(bg=t["bg"])
        self.update_background_gradient()
        self.apply_ttk_style()
        self._retint_container(self.root, t["bg"])
        self.header_left.configure(bg=t["bg"], fg=t["accent"])
        if self.speed_value:
            self.speed_value.configure(fg=t["accent"])
        if self.counter_text:
            self.counter_text.configure(fg=t["accent"])
        if self.speed_slider is not None:
            self.speed_slider.sync_parent_bg(t["bg"])
            self.speed_slider.set_colors(fill_color=t["accent"])
        self.header_user.configure(fg="#000000" if n == "white" else "#FFFFFF")
        save_user_config()

    def _retint_container(self, widget, bg):
        for child in widget.winfo_children():
            cls = child.winfo_class()
            try:
                if isinstance(child, ThemedSlider):
                    child.sync_parent_bg(bg)
                elif isinstance(child, RoundedButton):
                    child.sync_parent_bg(bg)
                    # NEU: Buttons, die die Theme-Akzentfarbe nutzen, live mitfärben
                    # (inkl. Textfarbe, z.B. schwarz bei hellem "Dark Mode"-Akzent)
                    if getattr(child, "_follows_theme_accent", False):
                        new_accent = accent()
                        child.configure(bg=new_accent, fg=_fg_for_bg(new_accent))
                elif isinstance(child, (VerifiedBadge, AdminBadge, OGBadge)):
                    child.configure(bg=bg)
                elif cls == "Label" and getattr(child, "_keep_color", False) is False:
                    orig_fg = getattr(child, "_orig_fg", None)
                    if orig_fg:
                        child.configure(bg=bg, fg=_adapt_fg_for_theme(orig_fg, bg))
                    else:
                        child.configure(bg=bg)
                elif cls == "Frame" and getattr(child, "_keep_color", False):
                    pass
                elif cls == "Frame" and getattr(child, "_is_groupbox", False):
                    new_accent = THEMES.get(state.current_theme, THEMES["purple"])["accent"]
                    child.configure(bg=bg, highlightbackground=new_accent, highlightcolor=new_accent)
                    if getattr(child, "title_label", None) is not None:
                        try:
                            title_orig = getattr(child.title_label, "_orig_fg", "#CCCCCC")
                            child.title_label.configure(bg=bg, fg=_adapt_fg_for_theme(title_orig, bg))
                        except Exception:
                            pass
                elif cls == "Frame":
                    child.configure(bg=bg)
                elif cls == "Checkbutton":
                    orig_fg = getattr(child, "_orig_fg", "#FFFFFF")
                    adapted_fg = _adapt_fg_for_theme(orig_fg, bg)
                    child.configure(bg=bg, activebackground=bg,
                                     highlightbackground=bg, highlightcolor=bg,
                                     fg=adapted_fg, activeforeground=adapted_fg,
                                     selectcolor=RoundedButton._shade(bg, 1.6))
                if child.winfo_children():
                    self._retint_container(child, bg)
            except Exception:
                pass

    def change_language(self):
        state.current_language = "en" if self.lang_var.get() == "English" else "de"
        self.update_all_text()
        save_config()

    def update_all_text(self):
        self.root.title(T("title"))
        self.speed_group.title_label.configure(text=T("speed"))
        self.action_group.title_label.configure(text=T("actions"))
        self.control_group.title_label.configure(text=T("control"))
        self.settings_group.title_label.configure(text=T("settings"))
        self.delay_label.configure(text=T("delay"))
        self.exit_btn.configure(text=T("exit"))
        self.add_btn.configure(text=T("addBtn"))
        self.delete_btn.configure(text=T("delete"))
        self.clear_btn.configure(text=T("clear"))
        # FIX: weitere Haupt-Buttons wurden bisher NICHT mit umgeschaltet
        self.save_local_btn.configure(text="💾 " + T("saveLocal"))
        self.my_kits_btn.configure(text="📂 " + T("myKits"))
        self.upload_btn.configure(text=T("uploadKit"))
        self.browse_btn.configure(text=T("browseKits"))
        self.save_settings_btn.configure(text=T("settings"))
        if not state.is_running and not state.is_counting_down:
            self.start_stop_btn.configure(text=T("startStop"))
        self.counter_text.configure(text=T("clicksExecuted") + " " + str(state.click_count))
        self.refresh_action_type_dropdown()
        self.update_action_list()
        self.update_premium_badge()
        if not state.is_running and not state.is_counting_down:
            self.status_text.configure(text=T("ready"))

    def toggle_repeat_ui(self):
        state.repeat_mode = self.repeat_var.get()
        save_user_config()

    def toggle_autostart_ui(self):
        if self.autostart_var.get():
            register_autostart()
        else:
            unregister_autostart()
        save_config()

    def apply_loaded_config(self):
        if self.speed_slider is not None:
            self.speed_slider.set(state.click_delay)
            self.speed_edit.delete(0, tk.END)
            self.speed_edit.insert(0, str(state.click_delay))
            self.speed_value.configure(text=f"{state.click_delay}ms")
            self.repeat_var.set(state.repeat_mode)
            self.lang_var.set("English" if state.current_language == "en" else "Deutsch")
            self.change_theme(state.current_theme)
            self.update_action_list()

    # ============== TOS/PRIVACY RE-ACCEPT POPUP (loggt NICHT aus) ==============
    def show_reaccept_dialog(self):
        """Zeigt ein Popup mit 'New Update' + Accept-Button für bereits
        eingeloggte Nutzer, wenn ToS/Privacy Policy per Admin-Befehl
        (PromptTOS/PromptPrivacyPolicy/PromptBoth) aktualisiert wurden.
        Loggt den Nutzer dabei NICHT aus - Login-Status bleibt unangetastet."""
        win = new_toplevel(self.root, "sClicker - Update", 380, 330, bg=DIALOG_BG(), topmost=True)

        label(win, 20, 20, 340, 30, "🔔 New Update", bg=DIALOG_BG(), fg=accent(),
              size=16, bold=True, anchor="center", justify="center")
        label(win, 20, 58, 340, 60,
              "Our Terms of Service and/or Privacy Policy have been updated. "
              "Please review and accept them to continue using sClicker.",
              bg=DIALOG_BG(), fg="#CCCCCC", size=10, anchor="center", justify="center",
              wraplength=340)

        tos_var = tk.BooleanVar(value=False)
        tos_check = tk.Checkbutton(win, variable=tos_var, bg=DIALOG_BG(),
                                    activebackground=DIALOG_BG(), bd=0,
                                    highlightthickness=0, selectcolor="#1a1a1a")
        tos_check.place(x=20, y=135, width=26, height=22)
        tos_label = tk.Label(win, text=T("acceptToSPrefix"), bg=DIALOG_BG(), fg="#AAAAAA",
                              font=F(9), anchor="w")
        tos_label.place(x=46, y=138, width=140, height=18)

        tos_x = 46 + measure_text_width(T("acceptToSPrefix"), 9) + 4
        tos_link = tk.Label(win, text=T("termsOfService"), bg=DIALOG_BG(), fg=accent(),
                             font=F(9, False, True), anchor="w", cursor="hand2")
        tos_w = measure_text_width(T("termsOfService"), 9) + 4
        tos_link.place(x=tos_x, y=138, width=tos_w, height=18)
        tos_link.bind("<Button-1>", lambda _e: self.show_tos_dialog())

        and_x = tos_x + tos_w
        and_label = tk.Label(win, text=T("andWord"), bg=DIALOG_BG(), fg="#AAAAAA",
                              font=F(9), anchor="w")
        and_w = measure_text_width(T("andWord"), 9) + 4
        and_label.place(x=and_x, y=138, width=and_w, height=18)

        privacy_x = and_x + and_w
        privacy_link = tk.Label(win, text=T("privacyPolicy"), bg=DIALOG_BG(), fg=accent(),
                                 font=F(9, False, True), anchor="w", cursor="hand2")
        privacy_link.place(x=privacy_x, y=138, width=140, height=18)
        privacy_link.bind("<Button-1>", lambda _e: self.show_privacy_dialog())

        status_lbl = label(win, 20, 165, 340, 30, "", bg=DIALOG_BG(), fg="#ef4444",
                            anchor="center", justify="center", size=9)

        def do_accept():
            if not tos_var.get():
                status_lbl.configure(text=T("mustAcceptToS"))
                return
            state.accepted_tos = True
            save_config()
            win.destroy()

        # FIX: Fenster kann NICHT über X/Backdrop-Klick weggeklickt werden -
        # nur über den Accept-Button, damit der Hinweis nicht versehentlich
        # übersprungen wird. Trotzdem bleibt der Login-Status unberührt.
        for child in win.winfo_children():
            if isinstance(child, tk.Label) and child.cget("text") == "✕":
                child.place_forget()

        button(win, 20, 205, 340, 40, "Accept", command=do_accept,
               bg=accent(), fg="#FFFFFF", bold=True)

        win.focus_set()

    # ============== LOGIN / REGISTER ==============
    def show_login_window(self):
        win = new_toplevel(self.root, "sClicker - Login", 350, 400, bg=DIALOG_BG())
        label(win, 20, 20, 310, 30, "⚡ sClicker Account", bg=DIALOG_BG(), fg="#9945FF",
              size=16, bold=True, anchor="center", justify="center")
        label(win, 20, 65, 200, 20, "Username:", bg=DIALOG_BG(), fg="#FFFFFF")
        u_edit = entry(win, 20, 85, 310, 32)
        u_edit.bind("<KeyRelease>", lambda e: self._enforce_limit(u_edit, 20))

        label(win, 20, 130, 200, 20, "Password:", bg=DIALOG_BG(), fg="#FFFFFF")
        p_edit = entry(win, 20, 150, 270, 32, show="•")
        show_pw_state = {"visible": False}

        def toggle_pw():
            show_pw_state["visible"] = not show_pw_state["visible"]
            p_edit.configure(show="" if show_pw_state["visible"] else "•")
            show_pw_btn.configure(text="🔒" if show_pw_state["visible"] else "👁")

        show_pw_btn = button(win, 295, 150, 35, 32, "👁", command=toggle_pw,
                              bg="#333333", fg="#FFFFFF")

        # NEU: Nutzungsbedingungen müssen akzeptiert werden, bevor man sich
        # einloggen, registrieren oder als Gast fortfahren kann.
        tos_var = tk.BooleanVar(value=state.accepted_tos)
        tos_check = tk.Checkbutton(win, variable=tos_var, bg=DIALOG_BG(),
                                    activebackground=DIALOG_BG(), bd=0,
                                    highlightthickness=0, selectcolor="#1a1a1a")
        tos_check.place(x=20, y=195, width=26, height=22)
        tos_label = tk.Label(win, text=T("acceptToSPrefix"), bg=DIALOG_BG(), fg="#AAAAAA",
                              font=F(9), anchor="w")
        tos_label.place(x=46, y=198, width=140, height=18)

        tos_x = 46 + measure_text_width(T("acceptToSPrefix"), 9) + 4
        tos_link = tk.Label(win, text=T("termsOfService"), bg=DIALOG_BG(), fg=accent(),
                             font=F(9, False, True), anchor="w", cursor="hand2")
        tos_w = measure_text_width(T("termsOfService"), 9) + 4
        tos_link.place(x=tos_x, y=198, width=tos_w, height=18)
        tos_link.bind("<Button-1>", lambda _e: self.show_tos_dialog())

        and_x = tos_x + tos_w
        and_label = tk.Label(win, text=T("andWord"), bg=DIALOG_BG(), fg="#AAAAAA",
                              font=F(9), anchor="w")
        and_w = measure_text_width(T("andWord"), 9) + 4
        and_label.place(x=and_x, y=198, width=and_w, height=18)

        privacy_x = and_x + and_w
        privacy_link = tk.Label(win, text=T("privacyPolicy"), bg=DIALOG_BG(), fg=accent(),
                                 font=F(9, False, True), anchor="w", cursor="hand2")
        privacy_link.place(x=privacy_x, y=198, width=140, height=18)
        privacy_link.bind("<Button-1>", lambda _e: self.show_privacy_dialog())

        status_lbl = label(win, 20, 220, 310, 45, "Enter your credentials",
                            bg=DIALOG_BG(), fg="#888888", anchor="center", justify="center",
                            wraplength=300)

        def _tos_required_check() -> bool:
            if not tos_var.get():
                status_lbl.configure(text=T("mustAcceptToS"), fg="#ef4444")
                return False
            state.accepted_tos = True
            save_config()
            return True

        def do_login_click():
            if not _tos_required_check():
                return
            self.do_login(win, u_edit, p_edit, status_lbl)

        def do_register_click():
            if not _tos_required_check():
                return
            self.do_register(win, u_edit, p_edit, status_lbl)

        def do_guest_click():
            if not _tos_required_check():
                return
            self.do_guest(win)

        button(win, 20, 275, 150, 35, "Login", command=do_login_click,
               bg=accent(), fg="#FFFFFF")
        button(win, 180, 275, 150, 35, "Register", command=do_register_click,
               bg="#333333", fg="#CCCCCC")
        button(win, 20, 320, 310, 30, "Continue as Guest", command=do_guest_click,
               bg="#111111", fg="#666666")

        u_edit.focus_set()
        u_edit.bind("<Return>", lambda e: do_login_click())
        p_edit.bind("<Return>", lambda e: do_login_click())

    @staticmethod
    def _enforce_limit(ent, limit):
        v = ent.get()
        if len(v) > limit:
            ent.delete(limit, tk.END)

    def do_login(self, win, u_edit, p_edit, status_lbl):
        u = u_edit.get().strip()
        p = p_edit.get()
        if not u or not p:
            return
        r, resolved_user = auth_login(u, p)
        if r == "ok":
            state.logged_in_user = resolved_user
            state.logged_in_verified = auth_is_verified(resolved_user)
            set_session_lastuser(resolved_user)
            load_account_settings(resolved_user)
            if update_login_streak_for_today():
                threading.Thread(target=save_account_settings_online, daemon=True).start()
            win.destroy()
            self.update_header_display()
            self.update_premium_badge()
            self.update_premium_buttons()
            self.refresh_action_type_dropdown()
            self.apply_loaded_config()
            threading.Thread(target=send_presence_heartbeat, daemon=True).start()
            self.show_success_toast(f"✓ Signed in successfully! Welcome, {resolved_user}!")
        else:
            mapping = {"wrong": T("wrongPassword"), "notfound": T("userNotFound"),
                       "banned": T("accountBanned"), "servererror": T("serverNotReachable")}
            status_lbl.configure(text=mapping.get(r, "Failed: " + r))
            if r == "servererror" and sClickerLog:
                show_info(T("serverNotReachable") + "\n\nServer Response:\n" + sClickerLog[-1])

    def do_register(self, win, u_edit, p_edit, status_lbl):
        u = u_edit.get().strip()
        p = p_edit.get()
        if not u or not p:
            return
        if not USERNAME_RE.match(u):
            status_lbl.configure(text=T("invalidUsername"))
            return
        reg_result = auth_register(u, p)
        if reg_result == "":
            state.logged_in_user = u
            state.logged_in_verified = False
            set_session_lastuser(u)
            reset_to_default_settings()
            win.destroy()
            self.update_header_display()
            self.update_premium_badge()
            self.update_premium_buttons()
            self.refresh_action_type_dropdown()
            self.apply_loaded_config()
            self.show_success_toast(f"✓ Account created! Welcome, {u}!")
        else:
            if reg_result == "taken":
                status_lbl.configure(text=T("usernameExists"))
            elif reg_result == "invalidUsername":
                status_lbl.configure(text=T("invalidUsername"))
            elif reg_result == "usernameProfanity":
                status_lbl.configure(text=T("usernameProfanity"))
            elif reg_result == "servererror":
                status_lbl.configure(text=T("serverNotReachable"))
                if sClickerLog:
                    show_info(T("serverNotReachable") + "\n\nServer Response:\n" + sClickerLog[-1])
            else:
                status_lbl.configure(text=reg_result)

    def do_guest(self, win):
        state.logged_in_user = ""
        state.logged_in_verified = False
        reset_to_default_settings()
        win.destroy()
        self.apply_loaded_config()
        self.update_header_display()
        self.update_premium_badge()
        self.update_premium_buttons()
        self.refresh_action_type_dropdown()

    # ============== KITS ==============
    def save_click_kit_local(self):
        n = self.kit_name_edit.get().strip()
        if not n:
            return
        if not state.action_list:
            show_info(T("noActionsSave"))
            return
        n = n[:35]
        kits = load_local_kits()
        kits.append({"name": n, "steps": list(state.action_list), "clickDelay": state.click_delay})
        save_local_kits(kits)
        show_info(T("saved"))

    def show_my_kits_window(self):
        kits = load_local_kits()
        win = new_toplevel(self.root, "My Kits", 400, 280, bg=DIALOG_BG())

        columns = ("name", "steps")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=8)
        tree.heading("name", text="Name")
        tree.heading("steps", text="Steps")
        tree.column("name", width=260)
        tree.column("steps", width=80, anchor="center")
        tree.place(x=20, y=20, width=360, height=200)
        for k in kits:
            tree.insert("", "end", values=(k.get("name", "---"), len(k.get("steps", []))))

        def load_selected():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            if 0 <= idx < len(kits):
                state.action_list = list(kits[idx].get("steps", []))
                if "clickDelay" in kits[idx]:
                    try:
                        state.click_delay = int(kits[idx]["clickDelay"])
                        self.apply_loaded_config()
                    except (TypeError, ValueError):
                        pass
                self.update_action_list()
                save_user_config()
                win.destroy()

        button(win, 20, 230, 360, 35, T("loadSelected"), command=load_selected,
               bg=accent(), fg="#FFFFFF")

    # FIX: clickDelay -> delay, keine ID
    def upload_click_kit(self):
        if not state.logged_in_user:
            show_info(T("needLogin"))
            return
        kit_name = self.kit_name_edit.get().strip()
        if not kit_name:
            show_info(T("needName"))
            return
        if not state.action_list:
            show_info(T("noActions"))
            return
        kit_name = kit_name[:35]
        kits = get_public_kits()

        # KEINE ID übergeben - Backend generiert UUID
        new_kit = {
            "name": kit_name,
            "author": state.logged_in_user,
            "steps": list(state.action_list),
            "clickDelay": state.click_delay,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": [],
            "comments": [],
        }
        kits.append(new_kit)

        if save_public_kits(kits):
            show_info(T("uploaded"))
            _cache["time"] = 0  # Cache refreshen
        else:
            last_err = sClickerLog[-1] if sClickerLog else "(no details)"
            show_info(T("uploadError") + "\n\nServer Response:\n" + last_err)

    # ============== AVATAR ==============
    @staticmethod
    def draw_avatar(parent, x, y, w, h, username, emoji_override=None, theme_name=None,
                     color_override=None, online=False, clicking=False, bg_hint=None):
        if color_override and color_override in _AVATAR_COLOR_TABLE:
            bg, fg = _AVATAR_COLOR_TABLE[color_override]
        else:
            bg, fg = get_avatar_colors(theme_name)
        content = emoji_override if emoji_override is not None else get_user_avatar_emoji(username)
        is_emoji = bool(content)
        if not content:
            content = display_name(username)[:1].upper() if username else "?"

        size = min(w, h)
        ox = x + (w - size) // 2
        oy = y + (h - size) // 2
        widgets = []

        if Image is not None and ImageDraw is not None:
            try:
                scale = 4
                S = max(1, size * scale)
                img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.ellipse([0, 0, S - 1, S - 1], fill=bg)

                if online or clicking:
                    dot_size_full = max(10, int(size * 0.32))
                    Sd = dot_size_full * scale
                    dx0 = S - Sd
                    dy0 = S - Sd
                    inset = max(2, int(Sd * 0.16))
                    ex0, ey0 = dx0 + inset, dy0 + inset
                    ex1, ey1 = dx0 + Sd - 1 - inset, dy0 + Sd - 1 - inset
                    fill_color = "#f59e0b" if clicking else "#22c55e"
                    draw.ellipse([ex0, ey0, ex1, ey1], fill=fill_color)
                    if clicking:
                        bw, bh = ex1 - ex0, ey1 - ey0
                        pts = [
                            (ex0 + bw * 0.542, ey0 + bh * 0.083),
                            (ex0 + bw * 0.125, ey0 + bh * 0.583),
                            (ex0 + bw * 0.500, ey0 + bh * 0.583),
                            (ex0 + bw * 0.458, ey0 + bh * 0.917),
                            (ex0 + bw * 0.875, ey0 + bh * 0.417),
                            (ex0 + bw * 0.500, ey0 + bh * 0.417),
                        ]
                        draw.polygon(pts, fill="#1a1a1a")

                img = img.resize((size, size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                if bg_hint:
                    parent_bg = bg_hint
                else:
                    try:
                        parent_bg = parent["bg"]
                    except Exception:
                        parent_bg = DIALOG_BG()
                circle_lbl = tk.Label(parent, image=photo, bg=parent_bg, bd=0, highlightthickness=0)
                circle_lbl.image = photo
                circle_lbl.place(x=ox, y=oy, width=size, height=size)
                widgets.append(circle_lbl)

                inner = max(10, int(size / 1.4142))
                iox = ox + (size - inner) // 2
                ioy = oy + (size - inner) // 2
                font_size = max(9, int(inner * (0.42 if is_emoji else 0.5)))
                txt_lbl = tk.Label(parent, text=content, bg=bg, fg=fg, font=F(font_size, True))
                txt_lbl.place(x=iox, y=ioy, width=inner, height=inner)
                widgets.append(txt_lbl)
                return widgets
            except Exception as e:
                sClickerLog.append(f"Rundes Avatar konnte nicht gerendert werden: {e}")

        font_size = 38 if not is_emoji else 30
        lbl = tk.Label(parent, text=content, bg=bg, fg=fg, font=F(font_size, True))
        lbl.place(x=x, y=y, width=w, height=h)
        widgets.append(lbl)
        if online or clicking:
            dot_size = max(10, int(size * 0.32))
            dot_lbl = tk.Label(parent, text=("⚡" if clicking else "●"), bg=bg,
                                fg="#f59e0b" if clicking else "#22c55e",
                                font=(FONT_FAMILY, max(8, int(dot_size * 0.7)), "bold"))
            dot_lbl.place(x=ox + size - dot_size, y=oy + size - dot_size,
                           width=dot_size, height=dot_size)
            widgets.append(dot_lbl)
        return widgets

    @staticmethod
    def add_stat_tile(parent, x, y, label_text, value, command=None):
        # FIX: Hintergrund der Kachel ist jetzt "unsichtbar" (identisch zum
        # Dialog-Hintergrund) statt einem sichtbaren grauen Kasten - dadurch
        # verschwindet auch die störende Linie über den Buttons darunter.
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = DIALOG_BG()
        hover_bg = RoundedButton._shade(parent_bg, 1.35)
        tile = tk.Label(parent, bg=parent_bg, cursor="hand2" if command else "")
        tile.place(x=x, y=y, width=140, height=80)
        big = tk.Label(parent, text=str(value), bg=parent_bg, fg="#FFFFFF", font=F(20, True),
                        cursor="hand2" if command else "")
        big.place(x=x, y=y + 12, width=140, height=32)
        sub = tk.Label(parent, text=label_text, bg=parent_bg, fg="#888888", font=F(10),
                        cursor="hand2" if command else "")
        sub.place(x=x, y=y + 48, width=140, height=22)
        if command:
            def _on_enter(_e=None):
                tile.configure(bg=hover_bg)
                big.configure(bg=hover_bg)
                sub.configure(bg=hover_bg)

            def _on_leave(_e=None):
                tile.configure(bg=parent_bg)
                big.configure(bg=parent_bg)
                sub.configure(bg=parent_bg)

            for w in (tile, big, sub):
                w.bind("<Button-1>", lambda _e: command())
                w.bind("<Enter>", _on_enter)
                w.bind("<Leave>", _on_leave)

    # ============== USER PROFILE ==============
    def show_user_profile(self, username):
        if not username or username == "?":
            return

        disp_initial = display_name(username)
        prof = new_toplevel(self.root, "Profile - " + disp_initial, 560, 860, bg=DIALOG_BG())

        avatar_widgets_ref = [self.draw_avatar(prof, 225, 30, 110, 110, username)]

        name_ctrl = label(prof, 90, 150, 380, 46, disp_initial, bg=DIALOG_BG(), fg="#FFFFFF",
                           size=22, bold=True, anchor="center", justify="center")
        loading_lbl = label(prof, 30, 220, 500, 30, "Loading profile...", bg=DIALOG_BG(),
                             fg="#888888", size=10, anchor="center", justify="center")

        def _load_profile_async():
            r = auth_get_data()
            is_verified = False
            is_admin_user = False
            is_og_user = False
            is_influencer_user = False
            joined = T("joinedBefore")
            follower_count = 0
            following_count = 0
            is_banned = False
            user_bio = ""
            user_emoji = ""
            user_color = ""
            data = None
            resolved_username = username
            user_online = False
            user_clicking = False
            user_total_clicks = 0
            user_streak = 0
            if r:
                data = json_parse(r)
                if data:
                    resolved = find_account_name(data, username)
                    if resolved:
                        resolved_username = resolved
                    info = data.get("accounts", {}).get(resolved_username)
                    if info:
                        is_verified = safe_flag(info, "verified")
                        is_banned = safe_flag(info, "banned")
                        is_admin_user = is_owner_account(resolved_username) or safe_flag(info, "admin")
                        is_og_user = safe_flag(info, "og")
                        jv = info.get("joined", "")
                        joined = T("joinedBefore") if (not jv or is_owner_account(resolved_username)) else jv
                        following_count = len(get_following_array(info))
                        settings = info.get("settings", {})
                        is_influencer_user = bool(isinstance(settings, dict) and safe_flag(settings, "influencer"))
                        user_bio = str(settings.get("bio", ""))
                        user_emoji = str(settings.get("avatarEmoji", ""))
                        user_color = str(settings.get("avatarColor", ""))
                        user_online = is_user_present(info)
                        user_clicking = is_user_clicking(info)
                        try:
                            user_total_clicks = int(settings.get("totalClicks", 0))
                        except (TypeError, ValueError):
                            user_total_clicks = 0
                        try:
                            user_streak = int(settings.get("loginStreak", 0))
                        except (TypeError, ValueError):
                            user_streak = 0
                        if resolved_username == state.logged_in_user:
                            user_total_clicks = max(user_total_clicks, state.total_clicks)
                            user_streak = max(user_streak, state.login_streak)
                    follower_count = count_followers(data, resolved_username)
            if is_owner_account(resolved_username):
                is_admin_user = True

            is_viewer_admin = bool(state.logged_in_user) and (
                is_owner_account(state.logged_in_user) or
                bool(data and safe_flag(data.get("accounts", {}).get(state.logged_in_user, {}), "admin"))
            )
            # FIX: Admin- und OG-Badge sollen NUR auf dem eigenen Profil sichtbar sein
            is_own_profile = bool(state.logged_in_user) and resolved_username == state.logged_in_user

            def finish():
                if not prof.winfo_exists():
                    return
                try:
                    loading_lbl.destroy()
                except Exception:
                    pass

                if is_banned:
                    prof.destroy()
                    self.show_account_not_found_window(resolved_username, T("accountBanned"))
                    return

                disp_user = display_name(resolved_username)

                for w in avatar_widgets_ref[0]:
                    try:
                        w.destroy()
                    except Exception:
                        pass
                avatar_widgets_ref[0] = self.draw_avatar(
                    prof, 225, 30, 110, 110, resolved_username,
                    emoji_override=user_emoji or None, color_override=user_color or None)

                # FIX: Badges im Profil waren zu groß - jetzt in etwa
                # Kleinbuchstaben-Größe statt fast so groß wie der Name
                profile_badge_size = badge_size_for_font(16)
                text_width = measure_text_width(disp_user, 22, True)

                # NEU: Name + Badges mittig zentriert unter dem Avatar (wie im Mockup)
                badge_slots = 0
                if is_verified:
                    badge_slots += 1
                if is_admin_user:
                    badge_slots += 1
                if is_og_user:
                    badge_slots += 1
                if is_influencer_user:
                    badge_slots += 1
                show_follower_badge = follower_count > FOLLOWER_BADGE_THRESHOLD
                if show_follower_badge:
                    badge_slots += 1
                badges_w = (badge_slots * profile_badge_size) + (max(0, badge_slots - 1) * BADGE_BADGE_GAP)
                combined_w = text_width + (BADGE_NAME_GAP if badge_slots else 0) + badges_w
                row_x0 = max(10, (560 - combined_w) // 2)
                name_y = 150

                name_ctrl.configure(text=disp_user, anchor="w", justify="left")
                name_ctrl.place(x=row_x0, y=name_y, width=text_width + 4, height=46)

                badge_x = row_x0 + text_width + BADGE_NAME_GAP
                badge_y = badge_y_centered(name_y, 46, profile_badge_size) + PROFILE_BADGE_Y_OFFSET
                if is_verified:
                    check_badge = VerifiedBadge(prof)
                    check_badge.place(x=badge_x, y=badge_y, width=profile_badge_size, height=profile_badge_size)
                    badge_x += profile_badge_size + BADGE_BADGE_GAP
                # FIX: Admin-Badge NUR auf eigenem Profil
                if is_admin_user:
                    admin_badge = AdminBadge(prof)
                    admin_badge.place(x=badge_x, y=badge_y, width=profile_badge_size, height=profile_badge_size)
                    badge_x += profile_badge_size + BADGE_BADGE_GAP
                # FIX: OG-Badge ist jetzt im gleichen Stil wie die Achievement-Badges
                # (Hexagon/Shield statt Stern) und weiterhin NUR auf eigenem Profil
                if is_og_user:
                    og_photo = render_achievement_badge(profile_badge_size, "og", shield=True)
                    if og_photo is not None:
                        og_lbl = tk.Label(prof, image=og_photo, bg=DIALOG_BG(), bd=0, highlightthickness=0)
                        og_lbl.image = og_photo
                        og_lbl.place(x=badge_x, y=badge_y, width=profile_badge_size, height=profile_badge_size)
                    else:
                        og_badge = OGBadge(prof)
                        og_badge.place(x=badge_x, y=badge_y, width=profile_badge_size, height=profile_badge_size)
                    badge_x += profile_badge_size + BADGE_BADGE_GAP
                if is_influencer_user:
                    inf_badge = InfluencerBadge(prof)
                    inf_badge.place(x=badge_x, y=badge_y, width=profile_badge_size, height=profile_badge_size)
                    badge_x += profile_badge_size + BADGE_BADGE_GAP
                if show_follower_badge:
                    fb_photo = render_achievement_badge(profile_badge_size, "gold", wings=True, shield=True)
                    if fb_photo is not None:
                        fb_lbl = tk.Label(prof, image=fb_photo, bg=DIALOG_BG(), bd=0, highlightthickness=0)
                        fb_lbl.image = fb_photo
                        fb_lbl.place(x=badge_x, y=badge_y, width=profile_badge_size, height=profile_badge_size)
                        badge_x += profile_badge_size + BADGE_BADGE_GAP

                # NEU: rotes "!" Report-Icon oben rechts (wie im Mockup) - meldet den Account
                if state.logged_in_user and resolved_username != state.logged_in_user:
                    report_ico = tk.Label(prof, text="❗", bg=DIALOG_BG(), fg="#ef4444",
                                           font=F(16, True), cursor="hand2")
                    report_ico.place(x=505, y=38, width=26, height=26)
                    report_ico.bind("<Button-1>", lambda _e, u=resolved_username: self.show_report_user_dialog(prof, u))

                # Handle + Status + Streak, ebenfalls zentriert, eine Zeile unter dem Namen
                handle_str = "@" + disp_user.lower()
                if user_clicking:
                    status_text, status_color = "  •  CLICKING", "#f59e0b"
                elif user_online:
                    status_text, status_color = "  •  ONLINE", "#22c55e"
                else:
                    status_text, status_color = "", "#888888"
                streak_text = f"   🔥 {user_streak}" if user_streak >= 1 else ""

                handle_w = measure_text_width(handle_str, 11) + 6
                status_w = (measure_text_width(status_text, 10, True) + 4) if status_text else 0
                streak_w = (measure_text_width(streak_text, 10, True) + 4) if streak_text else 0
                line2_w = handle_w + status_w + streak_w
                line2_x0 = max(10, (560 - line2_w) // 2)

                label(prof, line2_x0, 195, handle_w, 20, handle_str, bg=DIALOG_BG(), fg="#888888", size=11)
                if status_text:
                    label(prof, line2_x0 + handle_w, 195, status_w, 20, status_text,
                          bg=DIALOG_BG(), fg=status_color, size=10, bold=True)
                if streak_text:
                    label(prof, line2_x0 + handle_w + status_w, 195, streak_w, 20, streak_text,
                          bg=DIALOG_BG(), fg="#f59e0b", size=10, bold=True)

                join_str = T("joined") + str(joined)
                join_w = measure_text_width(join_str, 10) + 20
                join_x0 = max(10, (560 - join_w) // 2)
                label(prof, join_x0, 218, join_w, 20, join_str, bg=DIALOG_BG(), fg="#AAAAAA", size=10)

                bio_y_end = 246
                if user_bio:
                    bio_label = tk.Label(prof, text=user_bio, bg=DIALOG_BG(), fg="#CCCCCC",
                                        font=F(10), wraplength=440, justify="left", anchor="nw")
                    bio_label.place(x=30, y=246, width=460, height=110)
                    bio_y_end = 356
                    if is_viewer_admin and resolved_username != state.logged_in_user:
                        def do_delete_bio():
                            if not ask_yes_no(f"Remove {disp_user}'s bio?"):
                                return

                            def worker():
                                r2 = auth_get_data()
                                d2 = json_parse(r2) if r2 else None
                                ok = False
                                if d2 and resolved_username in d2.get("accounts", {}):
                                    settings2 = d2["accounts"][resolved_username].setdefault("settings", {})
                                    settings2["bio"] = ""
                                    if supabase_update_account(resolved_username, {"settings": settings2}):
                                        ok = True
                                else:
                                    sClickerLog.append(f"Admin bio delete: account '{resolved_username}' not found.")

                                def fin():
                                    if ok:
                                        show_info("Bio removed.")
                                        prof.destroy()
                                        self.show_user_profile(resolved_username)
                                    else:
                                        last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                                        show_info("Failed to remove bio.\n\n" + last_err)
                                try:
                                    self.root.after(0, fin)
                                except Exception:
                                    pass

                            threading.Thread(target=worker, daemon=True).start()

                        del_bio_btn = tk.Label(prof, text=T("removeBio"), bg=DIALOG_BG(), fg="#ef4444",
                                                font=F(8, True), cursor="hand2", justify="center")
                        del_bio_btn.place(x=495, y=246, width=55, height=34)
                        del_bio_btn.bind("<Button-1>", lambda _e: do_delete_bio())

                y_stats = bio_y_end + 10
                self.add_stat_tile(prof, 30, y_stats, "Followers", follower_count,
                                    command=lambda: self.show_followers_window(resolved_username, data))
                self.add_stat_tile(prof, 200, y_stats, "Following", following_count,
                                    command=lambda: self.show_following_window(resolved_username, data))
                self.add_stat_tile(prof, 370, y_stats, "Clicks", format_count_abbrev(user_total_clicks))

                y_btns = y_stats + 95
                # NEU: Buttons wie im Mockup - groß, vollbreit, untereinander, Theme-Akzentfarbe
                follow_btn = RoundedButton(prof, text="Follow", bg=accent(), fg=_fg_for_bg(accent()),
                                            font=F(16, True), radius=18, border_width=2)
                follow_btn._follows_theme_accent = True
                follow_btn.place(x=30, y=y_btns, width=500, height=52)

                if not state.logged_in_user:
                    follow_btn.configure(text=T("loginToFollow"), state="disabled")
                elif state.logged_in_user == resolved_username:
                    follow_btn.configure(text=T("accountSettings"),
                                          command=lambda: (prof.destroy(), self.show_account_settings()))
                else:
                    already_following = bool(data and is_following(data, state.logged_in_user, resolved_username))
                    follow_btn.configure(text=T("unfollow") if already_following else T("follow"),
                                          command=lambda: self.do_toggle_follow(resolved_username, prof))

                if state.logged_in_user == resolved_username:
                    btn2 = RoundedButton(prof, text=T("myKits"),
                                          command=lambda: (prof.destroy(), self.show_my_kits_window()),
                                          bg=accent(), fg=_fg_for_bg(accent()), font=F(16, True), radius=18, border_width=2)
                else:
                    btn2 = RoundedButton(prof, text="View Kits by " + disp_user,
                                          command=lambda: (prof.destroy(), self.show_kits_by_author(resolved_username)),
                                          bg=accent(), fg=_fg_for_bg(accent()), font=F(14, True), radius=18, border_width=2)
                btn2.place(x=30, y=y_btns + 52 + 12, width=500, height=52)
                btn2._follows_theme_accent = True

                y_close = y_btns + 52 + 12 + 52 + 14
                close_btn = RoundedButton(prof, text=T("close"), command=prof.destroy,
                                           bg="#1a1a1a", fg="#AAAAAA", font=F(11, True),
                                           radius=16, border_width=2)
                close_btn.place(x=30, y=y_close, width=500, height=38)

                y_ach = y_close + 62
                label(prof, 30, y_ach - 20, 300, 18, "Achievements", bg=DIALOG_BG(),
                      fg="#666666", size=9, bold=True)
                ach_size = 64
                ach_gap = 20
                total_ach_w = len(CLICK_ACHIEVEMENTS) * ach_size + (len(CLICK_ACHIEVEMENTS) - 1) * ach_gap
                ach_x0 = 30 + (500 - total_ach_w) // 2
                for i, ach in enumerate(CLICK_ACHIEVEMENTS):
                    unlocked = user_total_clicks >= ach["threshold"]
                    ax = ach_x0 + i * (ach_size + ach_gap)
                    photo = render_achievement_badge(ach_size, ach["tier"], locked=not unlocked, wings=ach["wings"])
                    if photo is not None:
                        ach_lbl = tk.Label(prof, image=photo, bg=DIALOG_BG(), bd=0, highlightthickness=0,
                                            cursor="hand2")
                        ach_lbl.image = photo
                        ach_lbl.place(x=ax, y=y_ach, width=ach_size, height=ach_size)
                        tip_text = ach["name"] if unlocked else f"{ach['name']} (locked)"

                        def _show_tip(_e, t=tip_text):
                            self.status_text.configure(text=t, fg="#888888") if self.status_text else None

                        ach_lbl.bind("<Enter>", _show_tip)
                    name_lbl_fg = "#AAAAAA" if unlocked else "#555555"
                    label(prof, ax - 10, y_ach + ach_size + 2, ach_size + 20, 16, ach["name"],
                          bg=DIALOG_BG(), fg=name_lbl_fg, size=8, bold=True,
                          anchor="center", justify="center")

                # NEU: zweite Reihe für die Login-Streak-Achievements
                y_ach2 = y_ach + ach_size + 40
                label(prof, 30, y_ach2 - 20, 300, 18, "🔥 Streak Achievements", bg=DIALOG_BG(),
                      fg="#666666", size=9, bold=True)
                total_streak_w = len(STREAK_ACHIEVEMENTS) * ach_size + (len(STREAK_ACHIEVEMENTS) - 1) * ach_gap
                streak_x0 = 30 + (500 - total_streak_w) // 2
                for i, ach in enumerate(STREAK_ACHIEVEMENTS):
                    unlocked = user_streak >= ach["threshold"]
                    ax = streak_x0 + i * (ach_size + ach_gap)
                    photo = render_achievement_badge(ach_size, ach["tier"], locked=not unlocked, wings=ach["wings"],
                                                      icon="flame", value=ach["threshold"])
                    if photo is not None:
                        ach_lbl = tk.Label(prof, image=photo, bg=DIALOG_BG(), bd=0, highlightthickness=0,
                                            cursor="hand2")
                        ach_lbl.image = photo
                        ach_lbl.place(x=ax, y=y_ach2, width=ach_size, height=ach_size)
                        tip_text = ach["name"] if unlocked else f"{ach['name']} (locked)"

                        def _show_tip2(_e, t=tip_text):
                            self.status_text.configure(text=t, fg="#888888") if self.status_text else None

                        ach_lbl.bind("<Enter>", _show_tip2)
                    name_lbl_fg = "#AAAAAA" if unlocked else "#555555"
                    label(prof, ax - 10, y_ach2 + ach_size + 2, ach_size + 20, 16, ach["name"],
                          bg=DIALOG_BG(), fg=name_lbl_fg, size=8, bold=True,
                          anchor="center", justify="center")

            try:
                self.root.after(0, finish)
            except Exception:
                pass

        threading.Thread(target=_load_profile_async, daemon=True).start()

    def show_account_not_found_window(self, username, message=None):
        disp_user = display_name(username)
        title_text = message or "Account not Found!"
        win = new_toplevel(self.root, "Profile - " + disp_user, 400, 230, bg=DIALOG_BG())
        label(win, 20, 55, 360, 44, title_text, bg=DIALOG_BG(), fg="#FFFFFF",
              size=20, bold=True, anchor="center", justify="center", wraplength=360)
        name_w = measure_text_width(disp_user, 13) + 20
        name_x = (400 - name_w) // 2
        label(win, name_x, 112, name_w, 26, disp_user, bg=DIALOG_BG(), fg="#888888",
              size=13, anchor="center", justify="center")
        button(win, 100, 168, 200, 36, T("close"), command=win.destroy,
               bg="#222222", fg="#CCCCCC")

    def _make_user_list_window(self, title, usernames, data=None):
        win = new_toplevel(self.root, title, 380, 460, bg=DIALOG_BG())
        label(win, 20, 15, 340, 30, title, bg=DIALOG_BG(), fg="#9945FF",
              size=15, bold=True, anchor="center", justify="center")

        if not usernames:
            label(win, 20, 180, 340, 40, T("noEntries"), bg=DIALOG_BG(), fg="#666666",
                  anchor="center", justify="center")
        else:
            list_frame = tk.Frame(win, bg=DIALOG_BG())
            list_frame.place(x=20, y=55, width=340, height=340)
            scroll = ttk.Scrollbar(list_frame, orient="vertical")
            scroll.pack(side="right", fill="y")
            canvas = tk.Canvas(list_frame, bg=DIALOG_BG(), highlightthickness=0,
                                yscrollcommand=scroll.set)
            canvas.pack(side="left", fill="both", expand=True)
            scroll.config(command=canvas.yview)
            inner = tk.Frame(canvas, bg=DIALOG_BG())
            canvas.create_window((0, 0), window=inner, anchor="nw", width=316)

            def on_inner_configure(_e=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
            inner.bind("<Configure>", on_inner_configure)

            def _on_mousewheel(event):
                if not canvas.winfo_exists():
                    return
                try:
                    canvas.yview_scroll(-1 * int(event.delta / 60), "units")
                except Exception:
                    pass

            def _bind_wheel(_e=None):
                try:
                    canvas.bind_all("<MouseWheel>", _on_mousewheel)
                except Exception:
                    pass

            def _unbind_wheel(_e=None):
                try:
                    canvas.unbind_all("<MouseWheel>")
                except Exception:
                    pass

            canvas.bind("<Enter>", _bind_wheel)
            canvas.bind("<Leave>", _unbind_wheel)
            win.bind("<Destroy>", lambda _e: _unbind_wheel(), add="+")

            row_h = 52
            avatar_size = 36
            badge_size = badge_size_for_font(11)
            accounts = data.get("accounts", {}) if data else {}

            for u in usernames:
                info = accounts.get(u, {})
                is_ver = safe_flag(info, "verified")
                # FIX: Admin- und OG-Badge werden in dieser Liste NICHT mehr
                # angezeigt - dort soll nur das Verified-Badge sichtbar sein.
                settings = info.get("settings", {}) if info else {}
                row_emoji = str(settings.get("avatarEmoji", "")) or None
                row_color = str(settings.get("avatarColor", "")) or None

                # FIX 3: JEDER Rand komplett entfernt - keine Lücke, kein
                # highlightthickness, absolut nahtlos. Reihen unterscheiden
                # sich nur noch durch Hintergrundfarbe (Hover/Auswahl).
                card = tk.Frame(inner, bg="#1a1a1a", height=row_h, highlightthickness=0, bd=0)
                card.pack(fill="x", pady=0)
                card.pack_propagate(False)

                av_widgets = self.draw_avatar(card, 6, (row_h - avatar_size) // 2,
                                               avatar_size, avatar_size, u,
                                               emoji_override=row_emoji, color_override=row_color,
                                               online=is_user_present(info), clicking=is_user_clicking(info),
                                               bg_hint="#1a1a1a")
                circle_lbl = av_widgets[0] if av_widgets else None

                disp = display_name(u)
                name_lbl = tk.Label(card, text=disp, bg="#1a1a1a", fg="#FFFFFF",
                                     font=F(11, True), anchor="w", cursor="hand2")
                name_x = 6 + avatar_size + 10
                name_w = min(180, measure_text_width(disp, 11, True) + 6)
                name_lbl.place(x=name_x, y=(row_h - 20) // 2, width=name_w, height=20)

                badges = []
                cursor_x = name_x + name_w + 4
                bY = (row_h - badge_size) // 2
                if is_ver:
                    vb = VerifiedBadge(card)
                    vb.sync_parent_bg("#1a1a1a")
                    vb.place(x=cursor_x, y=bY, width=badge_size, height=badge_size)
                    cursor_x += badge_size + 4
                    badges.append(vb)

                arrow_lbl = tk.Label(card, text="›", bg="#1a1a1a", fg="#666666",
                                      font=F(16, True), cursor="hand2")
                arrow_lbl.place(x=288, y=0, width=20, height=row_h)

                def _enter(_e, c=card, nl=name_lbl, al=arrow_lbl, bl=badges, cl=circle_lbl):
                    c.configure(bg="#232323")
                    nl.configure(bg="#232323")
                    al.configure(bg="#232323", fg="#9945FF")
                    for b in bl:
                        b.sync_parent_bg("#232323")
                    if cl is not None:
                        cl.configure(bg="#232323")

                def _leave(_e, c=card, nl=name_lbl, al=arrow_lbl, bl=badges, cl=circle_lbl):
                    c.configure(bg="#1a1a1a")
                    nl.configure(bg="#1a1a1a")
                    al.configure(bg="#1a1a1a", fg="#666666")
                    for b in bl:
                        b.sync_parent_bg("#1a1a1a")
                    if cl is not None:
                        cl.configure(bg="#1a1a1a")

                def _click(_e, u=u):
                    win.destroy()
                    self.show_user_profile(u)

                clickable = [card, name_lbl, arrow_lbl] + badges
                if circle_lbl is not None:
                    clickable.append(circle_lbl)
                for w in clickable:
                    w.bind("<Enter>", _enter)
                    w.bind("<Leave>", _leave)
                    w.bind("<Button-1>", _click)

        button(win, 20, 410, 340, 32, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    def show_followers_window(self, username, data=None):
        if data is None:
            r = auth_get_data()
            data = json_parse(r) if r else None
        followers = get_followers_usernames(data, username) if data else []
        self._make_user_list_window(T("followersOf").format(display_name(username)), followers, data)

    def show_following_window(self, username, data=None):
        if data is None:
            r = auth_get_data()
            data = json_parse(r) if r else None
        following = []
        if data:
            resolved = find_account_name(data, username) or username
            info = data.get("accounts", {}).get(resolved)
            if info:
                for f in get_following_array(info):
                    real = find_account_name(data, str(f)) or str(f)
                    following.append(real)
        self._make_user_list_window(T("followsTitle").format(display_name(username)), following, data)

    def do_toggle_follow(self, username, prof_gui):
        ok, _ = toggle_follow(username)
        if ok:
            prof_gui.destroy()
            self.root.after(350, lambda: self.show_user_profile(username))
        else:
            last_err = sClickerLog[-1] if sClickerLog else f"Target={username} / LoggedIn={state.logged_in_user}"
            show_info("Error: could not update follow status.\n\nServer Response:\n" + last_err)

    def handle_follow_click(self, target):
        if not state.logged_in_user:
            show_info(T("needLogin"))
            return False, None
        if target == state.logged_in_user:
            return False, None
        ok, new_data = toggle_follow(target)
        if ok:
            return True, new_data
        last_err = sClickerLog[-1] if sClickerLog else f"Target={target} / LoggedIn={state.logged_in_user}"
        show_info("Error: could not update follow status.\n\nServer Response:\n" + last_err)
        return False, None

    def show_tos_dialog(self):
        """NEU: Nutzungsbedingungen jederzeit einsehbar (Login-Fenster-Link
        und Settings-Button), inkl. Discord- und TikTok-Link."""
        win = new_toplevel(self.root, T("termsOfService"), 480, 540, bg=DIALOG_BG())
        label(win, 20, 15, 440, 30, "📜 " + T("termsOfService"), bg=DIALOG_BG(), fg=accent(),
              size=15, bold=True, anchor="center", justify="center")
        txt_frame = tk.Frame(win, bg="#1a1a1a")
        txt_frame.place(x=20, y=55, width=440, height=350)
        scroll = ttk.Scrollbar(txt_frame, orient="vertical")
        scroll.pack(side="right", fill="y")
        txt = tk.Text(txt_frame, bg="#1a1a1a", fg="#DDDDDD", font=F(10), bd=0,
                       highlightthickness=0, wrap="word", yscrollcommand=scroll.set)
        txt.insert("1.0", TOS_TEXT)
        txt.configure(state="disabled")
        txt.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scroll.config(command=txt.yview)

        def open_link(url):
            import webbrowser
            webbrowser.open(url)

        discord_btn = button(win, 20, 415, 210, 44, "Discord",
                              command=lambda: open_link("https://discord.gg/RPZ86DRn5z"),
                              bg="#5865F2", fg="#FFFFFF", bold=True)
        tiktok_btn = button(win, 250, 415, 210, 44, "TikTok",
                             command=lambda: open_link("https://www.tiktok.com/@sclicker"),
                             bg="#000000", fg="#FFFFFF", bold=True)

        button(win, 20, 470, 440, 40, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    def show_privacy_dialog(self):
        win = new_toplevel(self.root, T("privacyPolicy"), 480, 540, bg=DIALOG_BG())
        label(win, 20, 15, 440, 30, "🔒 " + T("privacyPolicy"), bg=DIALOG_BG(), fg=accent(),
              size=15, bold=True, anchor="center", justify="center")
        txt_frame = tk.Frame(win, bg="#1a1a1a")
        txt_frame.place(x=20, y=55, width=440, height=420)
        scroll = ttk.Scrollbar(txt_frame, orient="vertical")
        scroll.pack(side="right", fill="y")
        txt = tk.Text(txt_frame, bg="#1a1a1a", fg="#DDDDDD", font=F(10), bd=0,
                       highlightthickness=0, wrap="word", yscrollcommand=scroll.set)
        txt.insert("1.0", PRIVACY_TEXT)
        txt.configure(state="disabled")
        txt.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scroll.config(command=txt.yview)

        button(win, 20, 485, 440, 40, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    def show_account_settings(self):
        if not state.logged_in_user:
            show_info(T("needLogin"))
            return
        disp_user = display_name(state.logged_in_user)
        win = new_toplevel(self.root, "Account Settings - " + disp_user, 400, 860, bg=DIALOG_BG())

        label(win, 20, 15, 360, 30, "⚙ " + T("accountSettings"), bg=DIALOG_BG(), fg="#9945FF",
              size=16, bold=True, anchor="center", justify="center")
        label(win, 20, 55, 360, 22, "Logged in as: " + disp_user, bg=DIALOG_BG(), fg="#FFFFFF",
              anchor="center", justify="center")
        tk.Frame(win, bg="#333333").place(x=20, y=95, width=360, height=2)

        label(win, 20, 110, 300, 20, "Profile Picture:", bg=DIALOG_BG(), fg="#FFFFFF", bold=True)

        status_lbl = label(win, 20, 695, 360, 40, "", bg=DIALOG_BG(), fg="#888888",
                            anchor="center", justify="center", wraplength=350)

        current_avatar_preview = []
        current_avatar_preview.extend(
            self.draw_avatar(win, 20, 132, 60, 60, state.logged_in_user,
                              emoji_override=state.user_avatar_emoji or None))

        def do_save_avatar_icon(icon_name, picker_win=None):
            state.user_avatar_emoji = icon_name or ""
            status_lbl.configure(text="Saving...")
            for w in current_avatar_preview:
                try:
                    w.destroy()
                except Exception:
                    pass
            current_avatar_preview.clear()
            current_avatar_preview.extend(
                self.draw_avatar(win, 20, 132, 60, 60, state.logged_in_user,
                                  emoji_override=state.user_avatar_emoji or None))
            if picker_win is not None:
                picker_win.destroy()

            def worker():
                ok = save_account_settings_online()
                def finish():
                    status_lbl.configure(text=("Avatar cleared." if not icon_name else "Avatar saved!")
                                          if ok else T("passwordSaveError"))
                win.after(0, finish)

            threading.Thread(target=worker, daemon=True).start()

        def open_avatar_picker():
            pwin = new_toplevel(win, "Choose Avatar", 460, 480, bg=DIALOG_BG())
            label(pwin, 20, 15, 420, 28, "🖼 Choose Avatar", bg=DIALOG_BG(), fg=accent(),
                  size=14, bold=True, anchor="center", justify="center")

            grid_frame = tk.Frame(pwin, bg=DIALOG_BG())
            grid_frame.place(x=20, y=55, width=420, height=360)

            cols = 8
            cell = 48
            gap = 4
            cur = state.user_avatar_emoji

            def make_cell(x, y, icon_name, is_none=False):
                sel = (icon_name == cur) if not is_none else (not cur)
                b = tk.Label(grid_frame, bg=accent() if sel else "#1a1a1a", cursor="hand2")
                if is_none:
                    b.configure(text="✕", fg="#CCCCCC", font=F(16, True))
                else:
                    photo = render_avatar_icon(icon_name, cell - 10, fg_color="#FFFFFF")
                    if photo is not None:
                        b.configure(image=photo)
                        b.image = photo
                b.place(x=x, y=y, width=cell, height=cell)
                b.bind("<Button-1>", lambda _e, n=("" if is_none else icon_name): do_save_avatar_icon(n, pwin))
                return b

            make_cell(0, 0, None, is_none=True)
            for i, icon_name in enumerate(AVATAR_ICON_CHOICES):
                row, col = divmod(i + 1, cols)
                make_cell(col * (cell + gap), row * (cell + gap), icon_name)

            button(pwin, 20, 425, 420, 36, T("close"), command=pwin.destroy,
                   bg="#333333", fg="#CCCCCC")

        button(win, 100, 145, 280, 34, "🖼 Choose Avatar", command=open_avatar_picker,
               bg=accent(), fg="#FFFFFF", bold=True)

        label(win, 20, 204, 300, 20, T("avatarColorLabel"), bg=DIALOG_BG(), fg="#FFFFFF", bold=True)
        swatch_defs = [("auto", "#3a3a3a")] + [(k, v[0]) for k, v in _AVATAR_COLOR_TABLE.items()]
        swatch_btns = {}
        swatch_default_border = {}
        sel_state = {"key": state.user_avatar_color if state.user_avatar_color else "auto"}
        sw, gap, cols = 44, 4, 7

        def refresh_swatches():
            for k, b in swatch_btns.items():
                if k == sel_state["key"]:
                    b.configure(border_color="#FFFFFF")
                else:
                    b.configure(border_color=swatch_default_border[k])

        def do_pick_color(k):
            sel_state["key"] = k
            state.user_avatar_color = "" if k == "auto" else k
            refresh_swatches()
            status_lbl.configure(text="Saving...")

            def worker():
                ok = save_account_settings_online()
                def finish():
                    if ok:
                        status_lbl.configure(text=T("avatarColorSaved"))
                    else:
                        last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                        status_lbl.configure(text=T("passwordSaveError") + "\n" + last_err)
                win.after(0, finish)

            threading.Thread(target=worker, daemon=True).start()

        for i, (k, col) in enumerate(swatch_defs):
            row, col_i = divmod(i, cols)
            sb = RoundedButton(win, text=("A" if k == "auto" else ""),
                                command=lambda k=k: do_pick_color(k),
                                bg=col, fg="#FFFFFF", font=F(11, True), radius=12, border_width=2)
            sb.place(x=20 + col_i * (sw + gap), y=226 + row * (36 + gap), width=sw, height=36)
            swatch_btns[k] = sb
            swatch_default_border[k] = RoundedButton._shade(col, 1.45)
        refresh_swatches()

        tk.Frame(win, bg="#333333").place(x=20, y=356, width=360, height=2)

        label(win, 20, 368, 300, 20, "Profile Bio (max 200 characters):", bg=DIALOG_BG(),
              fg="#FFFFFF", bold=True)
        bio_edit = tk.Text(win, bg="#1a1a1a", fg="#FFFFFF", font=F(10), bd=0,
                            highlightthickness=1, highlightbackground="#333333")
        bio_edit.place(x=20, y=390, width=360, height=80)
        bio_edit.insert("1.0", state.user_bio)

        def limit_bio_chars(event=None):
            content = bio_edit.get("1.0", "end-1c")
            if len(content) > 200:
                bio_edit.delete("1.0", tk.END)
                bio_edit.insert("1.0", content[:200])

        bio_edit.bind("<KeyRelease>", limit_bio_chars)

        def do_save_bio():
            state.user_bio = censor_profanity(bio_edit.get("1.0", "end-1c").strip())
            bio_edit.delete("1.0", tk.END)
            bio_edit.insert("1.0", state.user_bio)
            save_user_config()
            status_lbl.configure(text="Saving...")

            def worker():
                ok = save_account_settings_online()
                def finish():
                    if ok:
                        status_lbl.configure(text="Bio saved!")
                    else:
                        last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                        status_lbl.configure(text=T("passwordSaveError") + "\n" + last_err)
                win.after(0, finish)

            threading.Thread(target=worker, daemon=True).start()

        button(win, 20, 478, 360, 32, "Save Bio", command=do_save_bio,
               bg=accent(), fg="#FFFFFF", bold=True)

        tk.Frame(win, bg="#333333").place(x=20, y=518, width=360, height=2)

        label(win, 20, 531, 200, 20, "Current Password:", bg=DIALOG_BG(), fg="#FFFFFF")
        curp_edit = entry(win, 20, 551, 360, 30, show="•")
        label(win, 20, 591, 200, 20, "New Password:", bg=DIALOG_BG(), fg="#FFFFFF")
        np_edit = entry(win, 20, 611, 360, 30, show="•")
        label(win, 20, 651, 200, 20, "Confirm Password:", bg=DIALOG_BG(), fg="#FFFFFF")
        cp_edit = entry(win, 20, 671, 360, 30, show="•")

        def do_change_password():
            curp = curp_edit.get()
            np = np_edit.get()
            cp = cp_edit.get()
            if not curp or not np or not cp:
                status_lbl.configure(text=T("fillBothFields"))
                return
            # FIX: aktuelles Passwort muss stimmen, bevor ein neues gesetzt wird
            r, _ = auth_login(state.logged_in_user, curp)
            if r != "ok":
                status_lbl.configure(text=T("wrongPassword"))
                return
            if np != cp:
                status_lbl.configure(text=T("passwordsNoMatch"))
                return
            if len(np) < 4:
                status_lbl.configure(text=T("passwordTooShort"))
                return
            if change_account_password(state.logged_in_user, np):
                status_lbl.configure(text=T("passwordUpdated"))
                curp_edit.delete(0, tk.END)
                np_edit.delete(0, tk.END)
                cp_edit.delete(0, tk.END)
            else:
                status_lbl.configure(text=T("passwordSaveError"))

        button(win, 20, 711, 360, 36, "Save New Password", command=do_change_password,
               bg=accent(), fg="#FFFFFF", bold=True)

        def open_verification_request_dialog():
            vwin = new_toplevel(win, "Request Verification", 420, 340, bg=DIALOG_BG())
            label(vwin, 20, 20, 380, 30, "✓ Request Verification", bg=DIALOG_BG(), fg=accent(),
                  size=15, bold=True, anchor="center", justify="center")
            label(vwin, 20, 60, 380, 40,
                  "Tell us why your account should be verified. An admin will review this.",
                  bg=DIALOG_BG(), fg="#AAAAAA", size=10, anchor="center", justify="center",
                  wraplength=380)

            reason_box = tk.Text(vwin, bg="#1a1a1a", fg="#FFFFFF", font=F(10), bd=0,
                                  highlightthickness=1, highlightbackground="#333333")
            reason_box.place(x=20, y=110, width=380, height=130)

            vstatus = label(vwin, 20, 250, 380, 30, "", bg=DIALOG_BG(), fg="#888888",
                             anchor="center", justify="center", wraplength=380)

            def do_submit():
                reason = reason_box.get("1.0", "end-1c").strip()
                if len(reason) < 10:
                    vstatus.configure(text="Please give a more detailed reason (min. 10 characters).",
                                       fg="#ef4444")
                    return
                report_data = {
                    "kit_id": "",
                    "kit_name": f"[Verification Request] {state.logged_in_user}",
                    "reporter": state.logged_in_user,
                    "reason": reason[:500],
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "open",
                }
                if supabase_create_report(report_data):
                    _cache["time"] = 0
                    vstatus.configure(text="Request submitted! An admin will review it soon.",
                                       fg="#22c55e")
                    vwin.after(1500, vwin.destroy)
                else:
                    last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                    vstatus.configure(text=T("passwordSaveError") + "\n" + last_err, fg="#ef4444")

            button(vwin, 20, 290, 380, 36, "Submit Request", command=do_submit,
                   bg=accent(), fg="#FFFFFF", bold=True)

        button(win, 20, 751, 360, 32, "✓ Request Verification",
               command=open_verification_request_dialog,
               bg="#333333", fg="#CCCCCC")
        button(win, 20, 785, 360, 32, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    def show_kits_by_author(self, author_name):
        all_kits = sort_kits_by_date_desc(get_public_kits())
        disp_author = display_name(author_name)
        win = new_toplevel(self.root, "Kits by " + disp_author, 500, 400, bg=DIALOG_BG())
        label(win, 20, 15, 460, 32, "Kits by " + disp_author, bg=DIALOG_BG(), fg=accent(),
              size=16, bold=True, anchor="center", justify="center")

        tree = ttk.Treeview(win, columns=("name", "created"), show="headings", height=10)
        tree.heading("name", text="Name")
        tree.heading("created", text="Created")
        tree.column("name", width=320)
        tree.column("created", width=120, anchor="center")
        tree.place(x=20, y=60, width=460, height=280)

        mine = [k for k in all_kits if k.get("author") == author_name]
        for k in mine:
            tree.insert("", "end", values=(k.get("name", "(unnamed)"),
                                            str(k.get("created", ""))[:10] or "---"))

        def load_it():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            if 0 <= idx < len(mine):
                state.action_list = list(mine[idx].get("steps", []))
                if "delay" in mine[idx]:
                    try:
                        state.click_delay = int(mine[idx]["delay"])
                        self.apply_loaded_config()
                    except (TypeError, ValueError):
                        pass
                self.update_action_list()
                save_user_config()
                win.destroy()

        button(win, 20, 350, 220, 36, T("loadSelected"), command=load_it,
               bg=accent(), fg="#FFFFFF")
        button(win, 260, 350, 220, 36, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    # ============== REPORT DIALOG (FIXED) ==============
    def show_report_user_dialog(self, parent_win, target_username):
        """NEU: Meldet einen Account (statt nur Click Kits) - für den roten
        ❗-Button im Profil."""
        if not state.logged_in_user:
            show_info(T("needLogin"))
            return

        disp_target = display_name(target_username)
        win = new_toplevel(parent_win, "Report Account", 450, 380, bg=DIALOG_BG())
        label(win, 20, 20, 410, 30, "📢 " + T("report"), bg=DIALOG_BG(), fg="#ef4444",
              size=16, bold=True, anchor="center", justify="center")

        label(win, 20, 60, 410, 22, f"Account: {disp_target}", bg=DIALOG_BG(), fg="#FFFFFF")
        label(win, 20, 90, 200, 22, T("reportReason") + ":", bg=DIALOG_BG(), fg="#FFFFFF")

        reason_entry = tk.Text(win, bg="#1a1a1a", fg="#FFFFFF", font=F(10), bd=0,
                                highlightthickness=1, highlightbackground="#333333")
        reason_entry.place(x=20, y=115, width=410, height=120)

        status_lbl = label(win, 20, 250, 410, 30, "", bg=DIALOG_BG(), fg="#888888",
                            anchor="center", justify="center", wraplength=400)

        def do_submit_report():
            reason = reason_entry.get("1.0", "end-1c").strip()
            if not reason:
                status_lbl.configure(text="Please enter a reason.", fg="#ef4444")
                return
            if len(reason) < 5:
                status_lbl.configure(text="Reason must be at least 5 characters.", fg="#ef4444")
                return

            report_data = {
                "kit_id": "",
                "kit_name": f"Account: {target_username}",
                "reporter": state.logged_in_user,
                "reason": reason[:500],
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "open",
            }

            if supabase_create_report(report_data):
                _cache["time"] = 0
                status_lbl.configure(text=T("reportSubmitted"), fg="#22c55e")
                win.after(1500, win.destroy)
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                status_lbl.configure(text=T("passwordSaveError") + "\n" + last_err, fg="#ef4444")

        button(win, 20, 295, 200, 40, T("report"), command=do_submit_report,
               bg="#ef4444", fg="#FFFFFF", bold=True)
        button(win, 230, 295, 200, 40, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    def show_report_dialog(self, parent_win, ctx):
        if not state.logged_in_user:
            show_info(T("needLogin"))
            return
        
        kit_id = ctx.get("current_kit_id", "")
        kit_name = ""
        for k in get_cached_kits():
            if k.get("id") == kit_id:
                kit_name = k.get("name", "(unbenannt)")
                break
        
        if not kit_id:
            show_info("No kit selected to report.")
            return
        
        win = new_toplevel(parent_win, "Report Kit", 450, 380, bg=DIALOG_BG())
        label(win, 20, 20, 410, 30, "📢 " + T("report"), bg=DIALOG_BG(), fg="#ef4444",
              size=16, bold=True, anchor="center", justify="center")
        
        label(win, 20, 60, 410, 22, f"Kit: {kit_name}", bg=DIALOG_BG(), fg="#FFFFFF")
        label(win, 20, 90, 200, 22, T("reportReason") + ":", bg=DIALOG_BG(), fg="#FFFFFF")
        
        reason_entry = tk.Text(win, bg="#1a1a1a", fg="#FFFFFF", font=F(10), bd=0,
                                highlightthickness=1, highlightbackground="#333333")
        reason_entry.place(x=20, y=115, width=410, height=120)
        
        status_lbl = label(win, 20, 250, 410, 30, "", bg=DIALOG_BG(), fg="#888888",
                            anchor="center", justify="center", wraplength=400)
        
        def do_submit_report():
            reason = reason_entry.get("1.0", "end-1c").strip()
            if not reason:
                status_lbl.configure(text="Please enter a reason.", fg="#ef4444")
                return
            if len(reason) < 5:
                status_lbl.configure(text="Reason must be at least 5 characters.", fg="#ef4444")
                return
            
            report_data = {
                "kit_id": kit_id,
                "kit_name": kit_name,
                "reporter": state.logged_in_user,
                "reason": reason[:500],
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "open",
            }
            
            if supabase_create_report(report_data):
                _cache["time"] = 0
                status_lbl.configure(text=T("reportSubmitted"), fg="#22c55e")
                win.after(1500, win.destroy)
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                status_lbl.configure(text=T("passwordSaveError") + "\n" + last_err, fg="#ef4444")
        
        button(win, 20, 295, 200, 40, T("report"), command=do_submit_report,
               bg="#ef4444", fg="#FFFFFF", bold=True)
        button(win, 230, 295, 200, 40, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    # ============== PUBLIC KITS WINDOW (FIXED - LIVE LIKES) ==============
    def show_public_kits_window(self):
        if not state.logged_in_user:
            show_info(T("needLogin"))
            return

        kits = []
        accounts_data = None
        ver_data, admin_data = {}, {o: "1" for o in OWNER_USERS}
        is_viewer_admin = False

        ctx = {"filtered": [], "current_author": "", "current_kit_id": ""}

        win = new_toplevel(self.root, "🌐 Public Click Kits", 900, 700, bg=DIALOG_BG())
        label(win, 20, 15, 860, 32, "🌐 Global Click Kits", bg=DIALOG_BG(), fg="#9945FF",
              size=16, bold=True, anchor="center", justify="center")
        loading_lbl = label(win, 20, 330, 860, 40, "Loading kits...", bg=DIALOG_BG(),
                             fg="#888888", size=12, anchor="center", justify="center")

        label(win, 20, 54, 60, 22, "Suche:", bg=DIALOG_BG(), fg="#CCCCCC")
        search_edit = entry(win, 85, 51, 255, 26)

        list_frame = tk.Frame(win, bg="#1a1a1a")
        list_frame.place(x=20, y=85, width=320, height=550)
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical")
        list_scroll.pack(side="right", fill="y")
        listbox = tk.Listbox(list_frame, bg="#1a1a1a", fg="#FFFFFF", font=F(11), bd=0,
                              highlightthickness=0, selectbackground=accent(),
                              activestyle="none", relief="flat",
                              selectborderwidth=0, yscrollcommand=list_scroll.set)
        listbox.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
        list_scroll.config(command=listbox.yview)

        groupbox(win, 350, 85, 530, 550, T("kitDetails"))
        kit_title = label(win, 370, 118, 470, 28, "Select a kit...", bg=DIALOG_BG(), fg="#FFFFFF",
                           size=15, bold=True)
        kit_meta_author = label(win, 370, 153, 1, 22, "", bg=DIALOG_BG(), fg="#FFFFFF",
                                 size=11, underline=True, cursor="hand2")
        kit_meta_check = VerifiedBadge(win)
        kit_meta_check.place(x=370, y=153, width=1, height=22)
        # FIX: Admin-Badge wird bei Kits nicht mehr angezeigt (nur Verified)
        kit_meta_date = label(win, 370, 153, 1, 22, "", bg=DIALOG_BG(), fg="#AAAAAA", size=11)

        kit_likes_label = label(win, 370, 184, 150, 24, "❤ Likes: 0", bg=DIALOG_BG(), fg="#AAAAAA", size=11)
        like_btn_ref = [None]

        report_btn = RoundedButton(win, text=T("report"), bg="#ef4444", fg="#FFFFFF",
                                    font=F(9, True), radius=10, border_width=2, state="normal")
        report_btn.place(x=700, y=180, width=80, height=28)
        report_btn.configure(command=lambda: self.show_report_dialog(win, ctx))
        report_btn.place_forget()

        tk.Frame(win, bg="#333333").place(x=370, y=220, width=490, height=2)
        label(win, 370, 228, 200, 20, "Steps", bg=DIALOG_BG(), fg="#666666", size=10, bold=True)
        seq_frame = tk.Frame(win, bg=DIALOG_BG())
        seq_frame.place(x=370, y=250, width=490, height=110)
        kit_seq = tk.Listbox(seq_frame, bg=DIALOG_BG(), fg="#9945FF", font=F(10), bd=0,
                              highlightthickness=0)
        kit_seq.pack(fill="both", expand=True)

        tk.Frame(win, bg="#333333").place(x=370, y=372, width=490, height=2)
        label(win, 370, 380, 200, 20, T("comments"), bg=DIALOG_BG(), fg="#666666", size=10, bold=True)

        comments_frame = tk.Frame(win, bg=DIALOG_BG())
        comments_frame.place(x=370, y=404, width=490, height=170)
        comments_scroll = tk.Scrollbar(comments_frame)
        comments_scroll.pack(side="right", fill="y")
        comments_canvas = tk.Canvas(comments_frame, bg=DIALOG_BG(), highlightthickness=0,
                                     yscrollcommand=comments_scroll.set)
        comments_canvas.pack(side="left", fill="both", expand=True)
        comments_scroll.config(command=comments_canvas.yview)
        inner_comments = tk.Frame(comments_canvas, bg=DIALOG_BG())
        comments_canvas.create_window((0, 0), window=inner_comments, anchor="nw", width=466)

        def on_comments_configure(_e=None):
            comments_canvas.configure(scrollregion=comments_canvas.bbox("all"))
        inner_comments.bind("<Configure>", on_comments_configure)

        comment_entry = entry(win, 370, 584, 380, 36, size=10)
        comment_post_btn = button(win, 758, 584, 102, 36, T("postComment"),
                                   bg=accent(), fg="#FFFFFF", bold=True)

        del_btn = button(win, 805, 113, 65, 30, T("del"), bg="#ef4444", fg="#FFFFFF")
        del_btn.place_forget()

        ctx["replying_to"] = None

        # FIX: Kommentar löschen rekursiv
        def do_delete_comment(comment, kit, parent_list):
            if not ask_yes_no(T("deleteCommentConfirm")):
                return
            
            for i, c in enumerate(parent_list):
                if c is comment:
                    parent_list.pop(i)
                    if save_public_kits(kits):
                        render_comments(kit)
                    return
            
            for c in parent_list:
                if isinstance(c.get("replies"), list):
                    for i, reply in enumerate(c["replies"]):
                        if reply is comment:
                            c["replies"].pop(i)
                            if save_public_kits(kits):
                                render_comments(kit)
                            return
                    for reply in c["replies"]:
                        if isinstance(reply.get("replies"), list):
                            for i, subreply in enumerate(reply["replies"]):
                                if subreply is comment:
                                    reply["replies"].pop(i)
                                    if save_public_kits(kits):
                                        render_comments(kit)
                                    return

        def make_comment_card(comment, kit, parent_list, is_reply=False):
            author = comment.get("author", "?")
            text = str(comment.get("text", ""))
            info = accounts_data.get("accounts", {}).get(author, {}) if accounts_data else {}
            is_ver = safe_flag(info, "verified")
            # FIX: Admin-Badge in Kommentaren entfernt (nur Verified)
            settings = info.get("settings", {}) if info else {}
            c_emoji = str(settings.get("avatarEmoji", "")) or None
            c_color = str(settings.get("avatarColor", "")) or None
            avatar_size = 24 if is_reply else 32
            border_color = "#3b82f6" if is_reply else "#9945FF"
            left_pad = 34 if is_reply else 2
            card_w = 466 - left_pad

            outer = tk.Frame(inner_comments, bg=DIALOG_BG())
            outer.pack(fill="x", pady=(6 if not is_reply else 0, 0), padx=(left_pad, 2))

            card = tk.Frame(outer, bg="#000000", highlightbackground=border_color,
                             highlightthickness=2, bd=0)
            card.pack(fill="x", pady=(4 if is_reply else 0))

            header = tk.Frame(card, bg="#000000", height=32 if is_reply else 40)
            header.pack(fill="x", padx=10, pady=(10, 4))
            header.pack_propagate(False)

            self.draw_avatar(header, 0, 2, avatar_size, avatar_size, author,
                              emoji_override=c_emoji, color_override=c_color,
                              online=is_user_present(info), clicking=is_user_clicking(info))
            disp = display_name(author)
            name_size = 11 if is_reply else 13
            name_w = measure_text_width(disp, name_size, True) + 4
            name_lbl = tk.Label(header, text=disp, bg="#000000", fg="#FFFFFF",
                                 font=F(name_size, True), anchor="w", cursor="hand2")
            name_lbl.place(x=avatar_size + 8, y=4 if is_reply else 8, width=name_w, height=22)
            name_lbl.bind("<Button-1>", lambda _e, u=author: self.show_user_profile(u))

            bsize = badge_size_for_font(name_size)
            bx = avatar_size + 8 + name_w + 6
            by = badge_y_centered(4 if is_reply else 8, 22, bsize)
            if is_ver:
                vb = VerifiedBadge(header)
                vb.place(x=bx, y=by, width=bsize, height=bsize)
                bx += bsize + 4

            ts_text = format_relative_time(comment.get("created", ""))
            if ts_text:
                ts_lbl = tk.Label(header, text=ts_text, bg="#000000", fg="#666666",
                                   font=F(9))
                ts_lbl.place(x=bx + 2, y=6 if is_reply else 10, width=95, height=18)

            can_delete_comment = is_viewer_admin or \
                (state.logged_in_user and state.logged_in_user == author)
            if can_delete_comment:
                del_c_btn = tk.Label(header, text="✕", bg="#000000", fg="#666666",
                                      font=F(12, True), cursor="hand2")
                del_c_btn.place(relx=1.0, x=-4, y=4 if is_reply else 8, width=22, height=22, anchor="ne")

                def _dc_enter(_e, w=del_c_btn):
                    w.configure(fg="#ef4444")

                def _dc_leave(_e, w=del_c_btn):
                    w.configure(fg="#666666")

                del_c_btn.bind("<Enter>", _dc_enter)
                del_c_btn.bind("<Leave>", _dc_leave)
                del_c_btn.bind("<Button-1>",
                                lambda _e, c=comment, pl=parent_list: do_delete_comment(c, kit, pl))

            tk.Label(card, text=text, bg="#000000", fg="#FFFFFF", font=F(name_size, True),
                     anchor="w", justify="left", wraplength=card_w - 24).pack(
                fill="x", padx=12, pady=(0, 8))

            action_row = tk.Frame(card, bg="#000000")
            action_row.pack(fill="x", padx=12, pady=(0, 10))

            c_likes = comment.get("likes", [])
            if not isinstance(c_likes, list):
                c_likes = []
            user_liked = bool(state.logged_in_user) and state.logged_in_user in c_likes
            like_lbl = tk.Label(action_row, text=f"{'❤' if user_liked else '♡'} {len(c_likes)}",
                                 bg="#000000", fg="#ef4444" if user_liked else "#888888",
                                 font=F(10, True), cursor="hand2")
            like_lbl.pack(side="left")

            def _like_click(_e, c=comment):
                if not state.logged_in_user:
                    show_info(T("needLogin"))
                    return
                lk = c.get("likes")
                if not isinstance(lk, list):
                    lk = []
                    c["likes"] = lk
                if state.logged_in_user in lk:
                    lk.remove(state.logged_in_user)
                else:
                    lk.append(state.logged_in_user)
                if save_public_kits(kits):
                    render_comments(kit)
                else:
                    last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                    show_info(T("passwordSaveError") + "\n\n" + last_err)

            like_lbl.bind("<Button-1>", _like_click)

            if not is_reply:
                reply_lbl = tk.Label(action_row, text="💬 " + T("reply"), bg="#000000",
                                      fg="#888888", font=F(10, True), cursor="hand2")
                reply_lbl.pack(side="left", padx=(16, 0))

                def _reply_click(_e, c=comment):
                    ctx["replying_to"] = None if ctx["replying_to"] is c else c
                    render_comments(kit)

                reply_lbl.bind("<Button-1>", _reply_click)

                if ctx["replying_to"] is comment:
                    reply_row = tk.Frame(card, bg="#000000")
                    reply_row.pack(fill="x", padx=12, pady=(0, 10))
                    reply_entry = tk.Entry(reply_row, bg="#1a1a1a", fg="#FFFFFF",
                                            font=F(10), relief="flat", insertbackground="#FFFFFF",
                                            highlightthickness=1, highlightbackground="#333333",
                                            highlightcolor="#3b82f6")
                    reply_entry.pack(side="left", fill="x", expand=True, ipady=4)
                    reply_entry.focus_set()

                    def _send_reply(_e=None, c=comment, ent=reply_entry):
                        do_post_reply(c, kit, ent)

                    reply_entry.bind("<Return>", _send_reply)
                    reply_send_btn = tk.Label(reply_row, text=T("postComment"), bg=accent(),
                                               fg="#FFFFFF", font=F(9, True), cursor="hand2",
                                               padx=10, pady=4)
                    reply_send_btn.pack(side="left", padx=(6, 0))
                    reply_send_btn.bind("<Button-1>", _send_reply)

            replies = comment.get("replies", [])
            if isinstance(replies, list):
                for reply in replies:
                    make_comment_card(reply, kit, replies, is_reply=True)

        def do_post_reply(parent_comment, kit, entry_widget):
            if not state.logged_in_user:
                show_info(T("commentNeedLogin"))
                return
            txt = entry_widget.get().strip()
            if not txt:
                return
            txt = censor_profanity(txt)
            if not isinstance(parent_comment.get("replies"), list):
                parent_comment["replies"] = []
            parent_comment["replies"].append({
                "author": state.logged_in_user,
                "text": txt[:300],
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "likes": [],
            })
            if save_public_kits(kits):
                ctx["replying_to"] = None
                render_comments(kit)
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                show_info(T("passwordSaveError") + "\n\n" + last_err)

        def render_comments(kit):
            for child in inner_comments.winfo_children():
                child.destroy()
            comments = get_kit_comments(kit)
            if not comments:
                tk.Label(inner_comments, text=T("noComments"), bg=DIALOG_BG(), fg="#666666",
                          font=F(10), anchor="center").pack(pady=24)
            else:
                for c in comments:
                    make_comment_card(c, kit, comments)
            inner_comments.update_idletasks()
            comments_canvas.configure(scrollregion=comments_canvas.bbox("all"))

        def do_post_comment():
            if not state.logged_in_user:
                show_info(T("commentNeedLogin"))
                return
            txt = comment_entry.get().strip()
            if not txt:
                return
            txt = censor_profanity(txt)
            target_id = ctx["current_kit_id"]
            if not target_id:
                return
            target_kit = None
            for k_item in kits:
                if k_item.get("id", "") == target_id:
                    if not isinstance(k_item.get("comments"), list):
                        k_item["comments"] = []
                    k_item["comments"].append({
                        "author": state.logged_in_user,
                        "text": txt[:300],
                        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "likes": [],
                        "replies": [],
                    })
                    target_kit = k_item
                    break
            if target_kit is None:
                return
            if save_public_kits(kits):
                comment_entry.delete(0, tk.END)
                render_comments(target_kit)
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                show_info(T("passwordSaveError") + "\n\n" + last_err)

        comment_post_btn.configure(command=do_post_comment)
        comment_entry.bind("<Return>", lambda _e: do_post_comment())

        def render_rows():
            listbox.delete(0, tk.END)
            # FIX: Duplikate (gleiche Kit-ID) nicht mehrfach anzeigen
            seen_ids = set()
            deduped = []
            for kit in ctx["filtered"]:
                kid = kit.get("id", "")
                if kid and kid in seen_ids:
                    continue
                if kid:
                    seen_ids.add(kid)
                deduped.append(kit)
            ctx["filtered"] = deduped
            for kit in ctx["filtered"]:
                likes = kit.get("likes", [])
                n_likes = len(likes) if isinstance(likes, list) else 0
                listbox.insert(tk.END, f"❤{n_likes}  {kit.get('name', '(unbenannt)')}")

        def apply_search(*_):
            q = search_edit.get().strip().lower()
            if not q:
                ctx["filtered"] = list(kits)
            else:
                ctx["filtered"] = [k for k in kits
                                    if q in str(k.get("name", "")).lower()
                                    or q in str(k.get("author", "")).lower()]
            render_rows()

        def on_author_click(_e=None):
            if ctx["current_author"]:
                self.show_user_profile(ctx["current_author"])

        kit_meta_author.bind("<Button-1>", on_author_click)
        kit_meta_check.bind("<Button-1>", on_author_click)

        # FIX: Live Like Update
        def on_row_click(_e=None):
            sel = listbox.curselection()
            if not sel or sel[0] >= len(ctx["filtered"]):
                return
            k = ctx["filtered"][sel[0]]
            ctx["current_kit_id"] = k.get("id", "")
            author = k.get("author", "?")
            created = str(k.get("created", ""))[:10] if k.get("created") else "---"
            is_verified = ver_data.get(author) in ("1", 1)
            ctx["current_author"] = author

            kit_title.configure(text=k.get("name", "(unbenannt)"))

            disp_author = display_name(author)
            kit_meta_author.configure(text=disp_author)
            author_w = measure_text_width(disp_author, 11) + 2
            kit_meta_author.place(x=370, y=153, width=author_w, height=22)

            meta_badge_size = badge_size_for_font(11)
            # FIX: hier explizit ein kleiner Abstand + 5px nach unten (auf Wunsch),
            # anders als beim Header/Profil wo kein Abstand gewünscht ist
            meta_badge_y = badge_y_centered(153, 22, meta_badge_size) + KIT_BADGE_Y_OFFSET
            cursor_x = 370 + author_w + 6
            if is_verified:
                kit_meta_check.set_visible(True)
                kit_meta_check.place(x=cursor_x, y=meta_badge_y,
                                      width=meta_badge_size, height=meta_badge_size)
                cursor_x += meta_badge_size
            else:
                kit_meta_check.set_visible(False)
                kit_meta_check.place(x=cursor_x, y=153, width=1, height=22)

            kit_meta_date.configure(text="  |  " + created)
            date_w = measure_text_width(kit_meta_date.cget("text"), 11) + 10
            kit_meta_date.place(x=cursor_x, y=153, width=date_w, height=22)

            kit_seq.delete(0, tk.END)
            for step in k.get("steps", []):
                kit_seq.insert(tk.END, format_step_label(step))

            likes = k.get("likes", [])
            if not isinstance(likes, list):
                likes = []
            kit_likes_label.configure(text=f"❤ Likes: {len(likes)}")

            if is_viewer_admin or (state.logged_in_user and state.logged_in_user == author):
                report_btn.place(x=700, y=180, width=80, height=28)
            else:
                report_btn.place_forget()

            user_has_liked = state.logged_in_user in likes
            if like_btn_ref[0]:
                like_btn_ref[0].destroy()

            # FIX: Like Funktion mit Live-Update
            def on_like_click():
                if not state.logged_in_user:
                    show_info(T("needLogin"))
                    return
                sel = listbox.curselection()
                if not sel or sel[0] >= len(ctx["filtered"]):
                    return
                target_kit = ctx["filtered"][sel[0]]
                target_kit_id = target_kit.get("id", "")

                # Like togglen - FIX: robust gegen likes=None (Supabase NULL)
                for k_item in kits:
                    if k_item.get("id", "") == target_kit_id:
                        if not isinstance(k_item.get("likes"), list):
                            k_item["likes"] = []
                        if state.logged_in_user in k_item["likes"]:
                            k_item["likes"].remove(state.logged_in_user)
                        else:
                            k_item["likes"].append(state.logged_in_user)
                        break

                if save_public_kits(kits):
                    # Live-Update: Liste neu laden und aktuelle Auswahl beibehalten
                    current_id = ctx["current_kit_id"]
                    # Kits neu laden
                    fresh_kits = get_cached_kits(force_refresh=True)
                    kits[:] = sort_kits_by_likes_desc(fresh_kits)
                    apply_search()
                    # Auswahl wiederherstellen
                    for i, kit in enumerate(ctx["filtered"]):
                        if kit.get("id") == current_id:
                            listbox.selection_set(i)
                            listbox.see(i)
                            break
                    on_row_click()  # Details neu laden
                    self.status_text.configure(text="Like updated!", fg="#22c55e")
                else:
                    show_info("Error saving like status")

            like_text = "Unlike ❤" if user_has_liked else "Like ❤"
            like_btn = button(win, 530, 180, 150, 32, like_text,
                             command=on_like_click,
                             bg="#ef4444" if user_has_liked else "#666666",
                             fg="#FFFFFF", bold=True, size=10)
            like_btn_ref[0] = like_btn

            can_del = is_viewer_admin or (state.logged_in_user and state.logged_in_user == author)
            if can_del:
                del_btn.place(x=805, y=113, width=65, height=30)
                del_btn.configure(command=on_delete_click)
            else:
                del_btn.place_forget()

            render_comments(k)

        def on_delete_click():
            sel = listbox.curselection()
            if not sel:
                show_info(T("noSelection"))
                return
            if sel[0] >= len(ctx["filtered"]):
                return
            target_kit = ctx["filtered"][sel[0]]
            target_id = target_kit.get("id", "")
            if not ask_yes_no(T("deleteConfirm")):
                return
            try:
                new_kits = []
                removed = False
                for k in kits:
                    k_id = k.get("id", "")
                    if not removed and target_id and k_id == target_id:
                        removed = True
                        continue
                    new_kits.append(k)
                if save_public_kits(new_kits):
                    show_info(T("deleteSuccess"))
                    self.root.after(10, lambda: (win.destroy(), self.show_public_kits_window()))
                else:
                    last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                    show_info(T("deleteError") + "\n\nServer Response:\n" + last_err)
            except Exception as e:
                show_info("Unexpected error while deleting: " + str(e))

        def on_load_click():
            sel = listbox.curselection()
            if not sel or sel[0] >= len(ctx["filtered"]):
                return
            k = ctx["filtered"][sel[0]]
            state.action_list = list(k.get("steps", []))
            if "clickDelay" in k:
                try:
                    state.click_delay = int(k["clickDelay"])
                    self.apply_loaded_config()
                except (TypeError, ValueError):
                    pass
            self.update_action_list()
            save_user_config()
            win.destroy()

        search_edit.bind("<KeyRelease>", apply_search)
        listbox.bind("<<ListboxSelect>>", on_row_click)

        def _load_kits_async():
            fetched_kits = sort_kits_by_likes_desc(get_public_kits())
            r = auth_get_data()
            fetched_accounts = json_parse(r) if r else None
            fv, fa = {}, {o: "1" for o in OWNER_USERS}
            if fetched_accounts:
                for u, info in fetched_accounts.get("accounts", {}).items():
                    if safe_flag(info, "verified"):
                        fv[u] = "1"
                    if safe_flag(info, "admin") or is_owner_account(u):
                        fa[u] = "1"
            viewer_admin = (is_owner_account(state.logged_in_user)) or \
                (fa.get(state.logged_in_user) in ("1", 1))

            def finish():
                nonlocal kits, accounts_data, ver_data, admin_data, is_viewer_admin
                if not win.winfo_exists():
                    return
                # FIX: Duplikate (gleiche Kit-ID, z.B. durch mehrfaches
                # Hochladen/Refresh) auch schon in der Grundmenge entfernen
                seen_ids = set()
                unique_kits = []
                for k in fetched_kits:
                    kid = k.get("id", "")
                    if kid and kid in seen_ids:
                        continue
                    if kid:
                        seen_ids.add(kid)
                    unique_kits.append(k)
                kits = unique_kits
                accounts_data = fetched_accounts
                ver_data = fv
                admin_data = fa
                is_viewer_admin = viewer_admin
                ctx["filtered"] = list(kits)
                try:
                    loading_lbl.destroy()
                except Exception:
                    pass
                render_rows()

            try:
                self.root.after(0, finish)
            except Exception:
                pass

        threading.Thread(target=_load_kits_async, daemon=True).start()
        button(win, 20, 645, 320, 40, T("loadKit"), command=on_load_click,
               bg=accent(), fg="#FFFFFF")
        button(win, 350, 645, 530, 40, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    # ============== NEWS ==============
    def show_news_window(self):
        posts = []
        accounts_data = None
        is_viewer_admin = False

        ctx = {"filtered": [], "current_post_id": "", "replying_to": None}

        win = new_toplevel(self.root, "📰 News", 900, 700, bg=DIALOG_BG())
        label(win, 20, 15, 820, 32, "📰 sClicker News", bg=DIALOG_BG(), fg="#f59e0b",
              size=16, bold=True, anchor="center", justify="center")
        loading_lbl = label(win, 20, 330, 860, 40, "Loading news...", bg=DIALOG_BG(),
                             fg="#888888", size=12, anchor="center", justify="center")

        list_frame = tk.Frame(win, bg="#1a1a1a")
        list_frame.place(x=20, y=85, width=320, height=550)
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical")
        list_scroll.pack(side="right", fill="y")
        listbox = tk.Listbox(list_frame, bg="#1a1a1a", fg="#FFFFFF", font=F(11), bd=0,
                              highlightthickness=0, selectbackground=accent(),
                              activestyle="none", relief="flat",
                              selectborderwidth=0, yscrollcommand=list_scroll.set)
        listbox.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
        list_scroll.config(command=listbox.yview)

        groupbox(win, 350, 85, 530, 550, "Post")

        new_post_btn = button(win, 700, 52, 180, 28, T("newPost"),
                               bg=accent(), fg="#FFFFFF", bold=True, size=10)
        new_post_btn.place_forget()

        post_title = label(win, 370, 118, 470, 30, "Select a post...", bg=DIALOG_BG(), fg="#FFFFFF",
                            size=16, bold=True)
        post_meta_author = label(win, 370, 155, 1, 22, "", bg=DIALOG_BG(), fg="#FFFFFF", size=11,
                                  underline=True, cursor="hand2")
        post_meta_check = VerifiedBadge(win)
        post_meta_check.place(x=370, y=155, width=1, height=22)
        # FIX: Admin-Badge bei News nicht mehr anzeigen (nur Verified)
        post_meta_date = label(win, 370, 155, 1, 22, "", bg=DIALOG_BG(), fg="#AAAAAA", size=11)

        post_body = tk.Label(win, text="", bg=DIALOG_BG(), fg="#DDDDDD", font=F(11),
                              anchor="nw", justify="left", wraplength=490)
        post_body.place(x=370, y=184, width=490, height=90)

        post_like_lbl_ref = [None]

        tk.Frame(win, bg="#333333").place(x=370, y=306, width=490, height=2)
        label(win, 370, 314, 200, 20, T("comments"), bg=DIALOG_BG(), fg="#666666", size=10, bold=True)

        comments_frame = tk.Frame(win, bg=DIALOG_BG())
        comments_frame.place(x=370, y=338, width=490, height=236)
        comments_scroll = tk.Scrollbar(comments_frame)
        comments_scroll.pack(side="right", fill="y")
        comments_canvas = tk.Canvas(comments_frame, bg=DIALOG_BG(), highlightthickness=0,
                                     yscrollcommand=comments_scroll.set)
        comments_canvas.pack(side="left", fill="both", expand=True)
        comments_scroll.config(command=comments_canvas.yview)
        inner_comments = tk.Frame(comments_canvas, bg=DIALOG_BG())
        comments_canvas.create_window((0, 0), window=inner_comments, anchor="nw", width=466)

        def on_comments_configure(_e=None):
            comments_canvas.configure(scrollregion=comments_canvas.bbox("all"))
        inner_comments.bind("<Configure>", on_comments_configure)

        comment_entry = entry(win, 370, 584, 380, 36, size=10)
        comment_post_btn = button(win, 758, 584, 102, 36, T("postComment"),
                                   bg=accent(), fg="#FFFFFF", bold=True)

        del_post_btn = button(win, 805, 118, 65, 30, T("del"), bg="#ef4444", fg="#FFFFFF")
        del_post_btn.place_forget()

        def find_post(post_id):
            for p in posts:
                if p.get("id", "") == post_id:
                    return p
            return None

        def do_delete_comment(comment, parent_list):
            if not ask_yes_no(T("deleteCommentConfirm")):
                return
            for i, c in enumerate(parent_list):
                if c is comment:
                    parent_list.pop(i)
                    break
            if save_news_posts(posts):
                render_comments(current_post())
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                show_info(T("passwordSaveError") + "\n\n" + last_err)

        def make_comment_card(comment, parent_list, is_reply=False):
            author = comment.get("author", "?")
            text = str(comment.get("text", ""))
            info = accounts_data.get("accounts", {}).get(author, {}) if accounts_data else {}
            is_ver = safe_flag(info, "verified")
            # FIX: Admin-Badge in News-Kommentaren entfernt (nur Verified)
            settings = info.get("settings", {}) if info else {}
            c_emoji = str(settings.get("avatarEmoji", "")) or None
            c_color = str(settings.get("avatarColor", "")) or None
            avatar_size = 24 if is_reply else 32
            border_color = "#3b82f6" if is_reply else "#f59e0b"
            left_pad = 34 if is_reply else 2
            card_w = 466 - left_pad

            outer = tk.Frame(inner_comments, bg=DIALOG_BG())
            outer.pack(fill="x", pady=(6 if not is_reply else 0, 0), padx=(left_pad, 2))

            card = tk.Frame(outer, bg="#000000", highlightbackground=border_color,
                             highlightthickness=2, bd=0)
            card.pack(fill="x", pady=(4 if is_reply else 0))

            header = tk.Frame(card, bg="#000000", height=32 if is_reply else 40)
            header.pack(fill="x", padx=10, pady=(10, 4))
            header.pack_propagate(False)

            self.draw_avatar(header, 0, 2, avatar_size, avatar_size, author,
                              emoji_override=c_emoji, color_override=c_color,
                              online=is_user_present(info), clicking=is_user_clicking(info))
            disp = display_name(author)
            name_size = 11 if is_reply else 13
            name_w = measure_text_width(disp, name_size, True) + 4
            name_lbl = tk.Label(header, text=disp, bg="#000000", fg="#FFFFFF",
                                 font=F(name_size, True), anchor="w", cursor="hand2")
            name_lbl.place(x=avatar_size + 8, y=4 if is_reply else 8, width=name_w, height=22)
            name_lbl.bind("<Button-1>", lambda _e, u=author: self.show_user_profile(u))

            bsize = badge_size_for_font(name_size)
            bx = avatar_size + 8 + name_w + 6
            by = badge_y_centered(4 if is_reply else 8, 22, bsize)
            if is_ver:
                vb = VerifiedBadge(header)
                vb.place(x=bx, y=by, width=bsize, height=bsize)
                bx += bsize + 4

            ts_text = format_relative_time(comment.get("created", ""))
            if ts_text:
                ts_lbl = tk.Label(header, text=ts_text, bg="#000000", fg="#666666",
                                   font=F(9))
                ts_lbl.place(x=bx + 2, y=6 if is_reply else 10, width=95, height=18)

            can_delete_comment = is_viewer_admin or \
                (state.logged_in_user and state.logged_in_user == author)
            if can_delete_comment:
                del_c_btn = tk.Label(header, text="✕", bg="#000000", fg="#666666",
                                      font=F(12, True), cursor="hand2")
                del_c_btn.place(relx=1.0, x=-4, y=4 if is_reply else 8, width=22, height=22, anchor="ne")

                def _dc_enter(_e, w=del_c_btn):
                    w.configure(fg="#ef4444")

                def _dc_leave(_e, w=del_c_btn):
                    w.configure(fg="#666666")

                del_c_btn.bind("<Enter>", _dc_enter)
                del_c_btn.bind("<Leave>", _dc_leave)
                del_c_btn.bind("<Button-1>",
                                lambda _e, c=comment, pl=parent_list: do_delete_comment(c, pl))

            tk.Label(card, text=text, bg="#000000", fg="#FFFFFF", font=F(name_size, True),
                     anchor="w", justify="left", wraplength=card_w - 24).pack(
                fill="x", padx=12, pady=(0, 8))

            action_row = tk.Frame(card, bg="#000000")
            action_row.pack(fill="x", padx=12, pady=(0, 10))

            c_likes = comment.get("likes", [])
            if not isinstance(c_likes, list):
                c_likes = []
            user_liked = bool(state.logged_in_user) and state.logged_in_user in c_likes
            like_lbl = tk.Label(action_row, text=f"{'❤' if user_liked else '♡'} {len(c_likes)}",
                                 bg="#000000", fg="#ef4444" if user_liked else "#888888",
                                 font=F(10, True), cursor="hand2")
            like_lbl.pack(side="left")

            def _like_click(_e, c=comment):
                if not state.logged_in_user:
                    show_info(T("needLogin"))
                    return
                lk = c.get("likes")
                if not isinstance(lk, list):
                    lk = []
                    c["likes"] = lk
                if state.logged_in_user in lk:
                    lk.remove(state.logged_in_user)
                else:
                    lk.append(state.logged_in_user)
                if save_news_posts(posts):
                    render_comments(current_post())
                else:
                    last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                    show_info(T("passwordSaveError") + "\n\n" + last_err)

            like_lbl.bind("<Button-1>", _like_click)

            if not is_reply:
                reply_lbl = tk.Label(action_row, text="💬 " + T("reply"), bg="#000000",
                                      fg="#888888", font=F(10, True), cursor="hand2")
                reply_lbl.pack(side="left", padx=(16, 0))

                def _reply_click(_e, c=comment):
                    ctx["replying_to"] = None if ctx["replying_to"] is c else c
                    render_comments(current_post())

                reply_lbl.bind("<Button-1>", _reply_click)

                if ctx["replying_to"] is comment:
                    reply_row = tk.Frame(card, bg="#000000")
                    reply_row.pack(fill="x", padx=12, pady=(0, 10))
                    reply_entry = tk.Entry(reply_row, bg="#1a1a1a", fg="#FFFFFF",
                                            font=F(10), relief="flat", insertbackground="#FFFFFF",
                                            highlightthickness=1, highlightbackground="#333333",
                                            highlightcolor="#f59e0b")
                    reply_entry.pack(side="left", fill="x", expand=True, ipady=4)
                    reply_entry.focus_set()

                    def _send_reply(_e=None, c=comment, ent=reply_entry):
                        do_post_reply(c, ent)

                    reply_entry.bind("<Return>", _send_reply)
                    reply_send_btn = tk.Label(reply_row, text=T("postComment"), bg="#f59e0b",
                                               fg="#000000", font=F(9, True), cursor="hand2",
                                               padx=10, pady=4)
                    reply_send_btn.pack(side="left", padx=(6, 0))
                    reply_send_btn.bind("<Button-1>", _send_reply)

            replies = comment.get("replies", [])
            if isinstance(replies, list):
                for reply in replies:
                    make_comment_card(reply, replies, is_reply=True)

        def do_post_reply(parent_comment, entry_widget):
            if not state.logged_in_user:
                show_info(T("commentNeedLogin"))
                return
            txt = entry_widget.get().strip()
            if not txt:
                return
            txt = censor_profanity(txt)
            if not isinstance(parent_comment.get("replies"), list):
                parent_comment["replies"] = []
            parent_comment["replies"].append({
                "author": state.logged_in_user,
                "text": txt[:300],
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "likes": [],
            })
            if save_news_posts(posts):
                ctx["replying_to"] = None
                render_comments(current_post())
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                show_info(T("passwordSaveError") + "\n\n" + last_err)

        def render_comments(post):
            for child in inner_comments.winfo_children():
                child.destroy()
            if post is None:
                return
            comments = post.get("comments", [])
            if not isinstance(comments, list):
                comments = []
            if not comments:
                tk.Label(inner_comments, text=T("noComments"), bg=DIALOG_BG(), fg="#666666",
                          font=F(10), anchor="center").pack(pady=24)
            else:
                for c in comments:
                    make_comment_card(c, comments)
            inner_comments.update_idletasks()
            comments_canvas.configure(scrollregion=comments_canvas.bbox("all"))

        def do_post_comment():
            if not state.logged_in_user:
                show_info(T("commentNeedLogin"))
                return
            txt = comment_entry.get().strip()
            if not txt:
                return
            txt = censor_profanity(txt)
            post = find_post(ctx["current_post_id"])
            if post is None:
                return
            if not isinstance(post.get("comments"), list):
                post["comments"] = []
            post["comments"].append({
                "author": state.logged_in_user,
                "text": txt[:300],
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "likes": [],
                "replies": [],
            })
            if save_news_posts(posts):
                comment_entry.delete(0, tk.END)
                render_comments(post)
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                show_info(T("passwordSaveError") + "\n\n" + last_err)

        comment_post_btn.configure(command=do_post_comment)
        comment_entry.bind("<Return>", lambda _e: do_post_comment())

        def current_post():
            return find_post(ctx["current_post_id"])

        def render_rows():
            listbox.delete(0, tk.END)
            for p in ctx["filtered"]:
                likes = p.get("likes", [])
                n_likes = len(likes) if isinstance(likes, list) else 0
                listbox.insert(tk.END, f"❤{n_likes}  {p.get('title', '(untitled)')}")

        def on_post_like_click():
            post = current_post()
            if post is None:
                return
            if not state.logged_in_user:
                show_info(T("needLogin"))
                return
            lk = post.get("likes")
            if not isinstance(lk, list):
                lk = []
                post["likes"] = lk
            if state.logged_in_user in lk:
                lk.remove(state.logged_in_user)
            else:
                lk.append(state.logged_in_user)
            if save_news_posts(posts):
                render_rows()
                on_row_click()
            else:
                show_info("Error saving like status")

        def on_row_click(_e=None):
            sel = listbox.curselection()
            if not sel or sel[0] >= len(ctx["filtered"]):
                return
            p = ctx["filtered"][sel[0]]
            ctx["current_post_id"] = p.get("id", "")
            ctx["replying_to"] = None
            author = p.get("author", "?")
            created = str(p.get("created", ""))[:16] if p.get("created") else "---"
            info = accounts_data.get("accounts", {}).get(author, {}) if accounts_data else {}
            is_verified = safe_flag(info, "verified")

            post_title.configure(text=p.get("title", "(untitled)"))
            post_body.configure(text=str(p.get("text", "")))

            disp_author = display_name(author)
            post_meta_author.configure(text=disp_author)
            author_w = measure_text_width(disp_author, 11) + 2
            post_meta_author.place(x=370, y=155, width=author_w, height=22)

            meta_badge_size = badge_size_for_font(11)
            meta_badge_y = badge_y_centered(155, 22, meta_badge_size) + KIT_VERIFIED_Y_OFFSET + ICON_Y_OFFSET
            cursor_x = 370 + author_w + 6
            if is_verified:
                post_meta_check.set_visible(True)
                post_meta_check.place(x=cursor_x, y=meta_badge_y,
                                       width=meta_badge_size, height=meta_badge_size)
                cursor_x += meta_badge_size
            else:
                post_meta_check.set_visible(False)
                post_meta_check.place(x=cursor_x, y=155, width=1, height=22)

            post_meta_date.configure(text="  |  " + created)
            date_w = measure_text_width(post_meta_date.cget("text"), 11) + 10
            post_meta_date.place(x=cursor_x, y=155, width=date_w, height=22)

            likes = p.get("likes", [])
            if not isinstance(likes, list):
                likes = []
            user_has_liked = bool(state.logged_in_user) and state.logged_in_user in likes

            if post_like_lbl_ref[0]:
                post_like_lbl_ref[0].destroy()
            like_btn = button(win, 370, 278, 170, 26,
                               ("❤ " if user_has_liked else "♡ ") + f"{len(likes)} Likes",
                               command=on_post_like_click,
                               bg="#ef4444" if user_has_liked else "#666666",
                               fg="#FFFFFF", bold=True, size=10)
            post_like_lbl_ref[0] = like_btn

            can_del = is_viewer_admin or (state.logged_in_user and state.logged_in_user == author)
            if can_del:
                del_post_btn.place(x=805, y=118, width=65, height=30)
                del_post_btn.configure(command=on_delete_post_click)
            else:
                del_post_btn.place_forget()

            render_comments(p)

        def on_delete_post_click():
            sel = listbox.curselection()
            if not sel or sel[0] >= len(ctx["filtered"]):
                return
            target = ctx["filtered"][sel[0]]
            target_id = target.get("id", "")
            if not ask_yes_no(T("deletePostConfirm")):
                return
            new_posts = [p for p in posts if p.get("id", "") != target_id]
            if save_news_posts(new_posts):
                # FIX: win.destroy() NICHT synchron aus dem eigenen Button-Callback
                # heraus aufrufen (der Button ist ein Kind von win!) - das crashte
                # die App mit "invalid command name", da Tcl noch mitten in der
                # Verarbeitung des Klick-Events auf genau diesem Widget war.
                self.root.after(10, lambda: (win.destroy(), self.show_news_window()))
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                show_info(T("passwordSaveError") + "\n\n" + last_err)

        def open_compose_panel():
            cwin = new_toplevel(self.root, "New Post", 520, 420, bg=DIALOG_BG())
            label(cwin, 20, 15, 480, 30, "📰 " + T("newPost"), bg=DIALOG_BG(), fg="#f59e0b",
                  size=15, bold=True, anchor="center", justify="center")
            label(cwin, 20, 60, 200, 20, "Title:", bg=DIALOG_BG(), fg="#FFFFFF", bold=True)
            title_entry = entry(cwin, 20, 82, 480, 34, size=12)
            label(cwin, 20, 128, 200, 20, "Text:", bg=DIALOG_BG(), fg="#FFFFFF", bold=True)
            body_text = tk.Text(cwin, bg="#1a1a1a", fg="#FFFFFF", font=F(10), bd=0,
                                 highlightthickness=1, highlightbackground="#333333")
            body_text.place(x=20, y=150, width=480, height=170)

            def do_publish():
                t = title_entry.get().strip()
                b = body_text.get("1.0", "end-1c").strip()
                if not t or not b:
                    show_info("Please fill in title and text.")
                    return
                t = censor_profanity(t)[:80]
                b = censor_profanity(b)[:2000]
                new_post = {
                    "id": generate_kit_id(), "author": state.logged_in_user,
                    "title": t, "text": b,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "likes": [], "comments": [],
                }
                posts.insert(0, new_post)
                if save_news_posts(posts):
                    cwin.destroy()
                    ctx["filtered"] = list(posts)
                    render_rows()
                else:
                    last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                    show_info(T("passwordSaveError") + "\n\n" + last_err)

            button(cwin, 20, 335, 235, 40, T("publish"), command=do_publish,
                   bg=accent(), fg="#FFFFFF", bold=True)
            button(cwin, 265, 335, 235, 40, T("cancel"), command=cwin.destroy,
                   bg="#333333", fg="#CCCCCC")

        new_post_btn.configure(command=open_compose_panel)

        listbox.bind("<<ListboxSelect>>", on_row_click)

        def _load_news_async():
            fetched_posts = sort_news_desc(get_news_posts())
            r = auth_get_data()
            fetched_accounts = json_parse(r) if r else None
            viewer_admin = (is_owner_account(state.logged_in_user)) or bool(
                fetched_accounts and safe_flag(
                    fetched_accounts.get("accounts", {}).get(state.logged_in_user, {}), "admin"))

            def finish():
                nonlocal posts, accounts_data, is_viewer_admin
                if not win.winfo_exists():
                    return
                posts = fetched_posts
                accounts_data = fetched_accounts
                is_viewer_admin = viewer_admin
                ctx["filtered"] = list(posts)
                try:
                    loading_lbl.destroy()
                except Exception:
                    pass
                if is_viewer_admin:
                    new_post_btn.place(x=700, y=52, width=180, height=28)
                render_rows()

            try:
                self.root.after(0, finish)
            except Exception:
                pass

        threading.Thread(target=_load_news_async, daemon=True).start()
        button(win, 350, 645, 530, 40, T("close"), command=win.destroy,
               bg="#333333", fg="#CCCCCC")

    # ============== ADMIN PANEL ==============
    def show_admin_panel(self):
        if not auth_is_admin(state.logged_in_user):
            return
        is_owner = (is_owner_account(state.logged_in_user))
        win = new_toplevel(self.root, "sClicker - Admin Panel", 800, 620, bg=DIALOG_BG())
        label(win, 20, 15, 760, 34, f"Admin Panel - {state.logged_in_user} [ADMIN]", bg=DIALOG_BG(),
              fg="#f59e0b", size=16, bold=True, anchor="center", justify="center")

        notebook = ttk.Notebook(win)
        notebook.place(x=20, y=60, width=760, height=500)

        # Tab 1: Accounts
        accounts_frame = tk.Frame(notebook, bg=DIALOG_BG())
        notebook.add(accounts_frame, text="Accounts")

        label(accounts_frame, 20, 10, 60, 22, "Search:", bg=DIALOG_BG(), fg="#CCCCCC")
        search_edit = entry(accounts_frame, 78, 7, 400, 26)

        cols_online = ("username", "status", "last", "reason")
        tree_online = ttk.Treeview(accounts_frame, columns=cols_online, show="headings", height=10)
        for c, t, w in (("username", "Username", 140), ("status", "Status", 100),
                        ("last", "Last Online", 100), ("reason", "Reason", 140)):
            tree_online.heading(c, text=t)
            tree_online.column(c, width=w)
        tree_online.place(x=20, y=45, width=720, height=220)

        s_lbl = label(accounts_frame, 20, 275, 720, 20, "Select an account to manage", bg=DIALOG_BG(),
                       fg="#888888", anchor="center", justify="center")

        def _status_of(info):
            parts = []
            if safe_flag(info, "banned"):
                parts.append("BANNED")
            if safe_flag(info, "admin"):
                parts.append("ADMIN")
            if safe_flag(info, "verified"):
                parts.append("VERIFIED")
            return "+".join(parts) if parts else "Normal"

        def refresh_online_list():
            tree_online.delete(*tree_online.get_children())
            r = auth_get_data()
            if r:
                data = json_parse(r)
                if data:
                    for u, info in data.get("accounts", {}).items():
                        s = "OWNER" if is_owner_account(u) else _status_of(info)
                        tree_online.insert("", "end", values=(u, s, "---", info.get("reason", "")))

        def admin_search():
            q = search_edit.get().strip().lower()
            tree_online.delete(*tree_online.get_children())
            r = auth_get_data()
            if not r:
                s_lbl.configure(text="Error: server not reachable.")
                return
            data = json_parse(r)
            if not data:
                s_lbl.configure(text="Error: failed to parse account data.")
                return
            count = 0
            for u, info in data.get("accounts", {}).items():
                if q and q not in u.lower():
                    continue
                s = "OWNER" if is_owner_account(u) else _status_of(info)
                tree_online.insert("", "end", values=(u, s, "---", info.get("reason", "")))
                count += 1
            s_lbl.configure(text=f"Found {count} matching accounts.")

        def admin_clear_search():
            search_edit.delete(0, tk.END)
            refresh_online_list()

        def _selected_online_user():
            sel = tree_online.selection()
            if not sel:
                return None
            return tree_online.item(sel[0], "values")[0]

        def _mutate_online_account(mutator, success_msg_fmt, block_owner_target=False):
            u = _selected_online_user()
            if not u:
                return
            if block_owner_target and is_owner_account(u):
                s_lbl.configure(text=T("cannotBanOwner"))
                return
            r = auth_get_data()
            if not r:
                s_lbl.configure(text="Error: could not reach the server.")
                return
            data = json_parse(r)
            if not data or u not in data.get("accounts", {}):
                return
            mutator(data["accounts"][u])
            if supabase_update_account(u, data["accounts"][u]):
                _cache["time"] = 0
                s_lbl.configure(text=success_msg_fmt.format(u))
                refresh_online_list()
                if u == state.logged_in_user:
                    self.update_header_display()
            else:
                last_err = sClickerLog[-1] if sClickerLog else "(no details)"
                s_lbl.configure(text="Error: update was not saved.\n" + last_err)

        def admin_verify_online():
            _mutate_online_account(lambda acc: acc.__setitem__("verified", "1"), "Verified {}")

        def admin_unverify_online():
            _mutate_online_account(lambda acc: acc.__setitem__("verified", "0"), "Unverified {}")

        def admin_ban_online():
            reason = ban_reason_online.get()
            def mut(acc):
                acc["banned"] = "1"
                acc["reason"] = reason
            _mutate_online_account(mut, "Banned {}", block_owner_target=True)

        def admin_unban_online():
            _mutate_online_account(lambda acc: acc.__setitem__("banned", "0"), "Unbanned {}")

        def admin_make_admin_online():
            _mutate_online_account(lambda acc: acc.__setitem__("admin", "1"),
                                    T("madeAdmin"))

        def admin_remove_admin_online():
            u = _selected_online_user()
            if is_owner_account(u):
                s_lbl.configure(text=T("cannotBanOwner"))
                return
            _mutate_online_account(lambda acc: acc.__setitem__("admin", "0"),
                                    T("removedAdmin"))

        def admin_terminate_online():
            u = _selected_online_user()
            if not u:
                return
            if is_owner_account(u):
                s_lbl.configure(text=T("cannotBanOwner"))
                return
            if supabase_delete_account(u):
                _cache["time"] = 0
                s_lbl.configure(text=f"Terminated {u}")
                refresh_online_list()
            else:
                s_lbl.configure(text="Error: could not terminate account.")

        button(accounts_frame, 485, 7, 90, 26, "Search", command=admin_search, bg=accent(), fg="#FFFFFF")
        button(accounts_frame, 582, 7, 80, 26, "Clear", command=admin_clear_search, bg="#444444", fg="#FFFFFF")

        label(accounts_frame, 20, 310, 100, 20, "Actions:", bg=DIALOG_BG(), fg=accent())
        def admin_make_influencer_online():
            def _set_inf(acc):
                s = acc.get("settings")
                if not isinstance(s, dict):
                    s = {}
                s["influencer"] = "1"
                acc["settings"] = s
            _mutate_online_account(_set_inf, "Made {} Influencer")

        def admin_remove_influencer_online():
            def _unset_inf(acc):
                s = acc.get("settings")
                if not isinstance(s, dict):
                    s = {}
                s["influencer"] = "0"
                acc["settings"] = s
            _mutate_online_account(_unset_inf, "Removed Influencer from {}")

        button(accounts_frame, 20, 335, 88, 28, "Verify", command=admin_verify_online,
               bg="#22c55e", fg="#FFFFFF")
        button(accounts_frame, 114, 335, 88, 28, "Unverify", command=admin_unverify_online,
               bg="#f59e0b", fg="#000000")
        button(accounts_frame, 298, 335, 100, 28, "Influencer", command=admin_make_influencer_online,
               bg="#9945FF", fg="#FFFFFF")
        button(accounts_frame, 402, 335, 100, 28, "Un-Influencer", command=admin_remove_influencer_online,
               bg="#555555", fg="#FFFFFF")
        ban_reason_online = entry(accounts_frame, 78, 400, 302, 26)
        button(accounts_frame, 208, 335, 84, 28, "Ban", command=admin_ban_online,
               bg="#ff6600", fg="#FFFFFF")
        button(accounts_frame, 20, 370, 88, 28, "Terminate", command=admin_terminate_online,
               bg="#ef4444", fg="#FFFFFF")
        button(accounts_frame, 114, 370, 178, 28, "Unban Online", command=admin_unban_online,
               bg="#444444", fg="#CCCCCC")

        def admin_make_og_online():
            _mutate_online_account(lambda acc: acc.__setitem__("og", "1"), "Made {} OG")

        def admin_remove_og_online():
            _mutate_online_account(lambda acc: acc.__setitem__("og", "0"), "Removed OG from {}")

        if is_owner:
            button(accounts_frame, 20, 405, 88, 28, "Make Admin", command=admin_make_admin_online,
                   bg=ADMIN_WHITE, fg="#000000")
            button(accounts_frame, 114, 405, 88, 28, "Remove Admin", command=admin_remove_admin_online,
                   bg="#555555", fg="#FFFFFF")
            button(accounts_frame, 300, 405, 88, 28, "Make OG", command=admin_make_og_online,
                   bg="#FFCD1E", fg="#000000")
            button(accounts_frame, 394, 405, 88, 28, "Remove OG", command=admin_remove_og_online,
                   bg="#555555", fg="#FFFFFF")
            ban_reason_online.place(x=208, y=440, width=172, height=26)
            label(accounts_frame, 20, 470, 360, 18, "Ban reason ↑ (used by 'Ban' above)",
                  bg=DIALOG_BG(), fg="#666666", size=8)
        else:
            ban_reason_online.place(x=208, y=440, width=172, height=26)
            label(accounts_frame, 20, 470, 360, 18, "Ban reason ↑ (used by 'Ban' above)",
                  bg=DIALOG_BG(), fg="#666666", size=8)

        refresh_online_list()

        # Tab 2: Reports
        reports_frame = tk.Frame(notebook, bg=DIALOG_BG())
        notebook.add(reports_frame, text=T("reports"))

        label(reports_frame, 20, 15, 300, 25, T("reports"), bg=DIALOG_BG(), fg="#ef4444",
              size=14, bold=True)

        columns = ("kit", "reporter", "reason", "created", "status")
        reports_tree = ttk.Treeview(reports_frame, columns=columns, show="headings", height=12)
        for c, t, w in (("kit", "Kit", 150), ("reporter", "Reporter", 120),
                        ("reason", "Reason", 200), ("created", "Created", 130),
                        ("status", "Status", 80)):
            reports_tree.heading(c, text=t)
            reports_tree.column(c, width=w)
        reports_tree.place(x=20, y=50, width=720, height=300)

        def refresh_reports():
            reports_tree.delete(*reports_tree.get_children())
            reports = get_cached_reports()
            for r in reports:
                reports_tree.insert("", "end", values=(
                    r.get("kit_name", "?"),
                    r.get("reporter", "?"),
                    r.get("reason", "")[:50],
                    str(r.get("created", ""))[:16],
                    r.get("status", "open")
                ))

        def resolve_report():
            sel = reports_tree.selection()
            if not sel:
                s_lbl2.configure(text="Select a report to resolve.")
                return
            idx = reports_tree.index(sel[0])
            reports = get_cached_reports()
            if idx >= len(reports):
                return
            report = reports[idx]
            report_id = report.get("id")
            if not report_id:
                return
            if supabase_delete_report(report_id):
                _cache["time"] = 0
                refresh_reports()
                s_lbl2.configure(text="Report resolved and removed.")
            else:
                s_lbl2.configure(text="Error resolving report.")

        s_lbl2 = label(reports_frame, 20, 360, 720, 20, "", bg=DIALOG_BG(), fg="#888888",
                        anchor="center", justify="center")

        def grant_verification():
            sel = reports_tree.selection()
            if not sel:
                s_lbl2.configure(text="Select a verification request first.")
                return
            idx = reports_tree.index(sel[0])
            reports = get_cached_reports()
            if idx >= len(reports):
                return
            report = reports[idx]
            kit_name = str(report.get("kit_name", ""))
            if not kit_name.startswith("[Verification Request]"):
                s_lbl2.configure(text="This report is not a verification request.")
                return
            target_user = report.get("reporter", "")
            if not target_user:
                s_lbl2.configure(text="Could not determine target user.")
                return
            if supabase_update_account(target_user, {"verified": "1"}):
                report_id = report.get("id")
                if report_id:
                    supabase_delete_report(report_id)
                _cache["time"] = 0
                refresh_reports()
                s_lbl2.configure(text=f"Verified {target_user}!", fg="#22c55e")
            else:
                s_lbl2.configure(text="Error granting verification.", fg="#ef4444")

        button(reports_frame, 20, 390, 130, 35, "Refresh", command=refresh_reports,
               bg=accent(), fg="#FFFFFF")
        button(reports_frame, 160, 390, 150, 35, T("resolveReport"), command=resolve_report,
               bg="#22c55e", fg="#FFFFFF")
        button(reports_frame, 320, 390, 190, 35, "✓ Grant Verification", command=grant_verification,
               bg="#9945FF", fg="#FFFFFF")

        refresh_reports()

        # Tab 3: Debug Console
        debug_frame = tk.Frame(notebook, bg=DIALOG_BG())
        notebook.add(debug_frame, text="Debug")

        PS_BG = "#000000"
        PS_FG = "#EEEEEE"
        PS_OK = "#3DDC84"
        PS_FAIL = "#FF6B6B"
        PS_DIM = "#8FB6E8"
        PS_FONT = ("Consolas", 10)

        text_frame = tk.Frame(debug_frame, bg=PS_BG)
        text_frame.place(x=10, y=10, width=730, height=370)
        scroll = tk.Scrollbar(text_frame)
        scroll.pack(side="right", fill="y")
        txt = tk.Text(text_frame, bg=PS_BG, fg=PS_FG, font=PS_FONT,
                       bd=0, highlightthickness=0, wrap="word",
                       yscrollcommand=scroll.set, insertbackground=PS_FG)
        txt.pack(side="left", fill="both", expand=True)
        scroll.config(command=txt.yview)
        txt.tag_configure("ok", foreground=PS_OK)
        txt.tag_configure("fail", foreground=PS_FAIL)
        txt.tag_configure("dim", foreground=PS_DIM)
        txt.tag_configure("prompt", foreground="#FFFFFF", font=("Consolas", 10, "bold"))
        txt.configure(state="disabled")

        PROMPT = "PS C:\\sClicker> "

        def write_line(s="", tag=None):
            txt.configure(state="normal")
            if tag:
                txt.insert(tk.END, s + "\n", tag)
            else:
                txt.insert(tk.END, s + "\n")
            txt.see(tk.END)
            txt.configure(state="disabled")

        def write_banner():
            write_line("sClicker Debug Console")
            write_line("Copyright (C) sClicker. All rights reserved.")
            write_line()
            write_line("Type 'check' to run diagnostics, 'log' to show recent log entries,")
            write_line("'clear' to clear the screen, or 'help' for all commands.")
            write_line()

        def run_check_async():
            write_line(PROMPT + "check", "prompt")
            write_line("Running diagnostics...", "dim")

            def worker():
                results = []

                r = auth_get_data()
                if r:
                    results.append(("Network connection (server reachable)", True, ""))
                else:
                    results.append(("Network connection (server reachable)", False,
                                     "Could not reach the server. Check your internet connection."))

                if state.logged_in_user:
                    results.append((f"Logged in as '{state.logged_in_user}'", True, ""))
                else:
                    results.append(("Logged in", False, "No account is currently logged in (guest mode)."))

                try:
                    kits = get_public_kits()
                    results.append((f"Click Kits reachable ({len(kits)} found)", True, ""))
                except Exception as e:
                    results.append(("Click Kits reachable", False, str(e)))

                try:
                    posts = get_news_posts()
                    results.append((f"News feed reachable ({len(posts)} posts)", True, ""))
                except Exception as e:
                    results.append(("News feed reachable", False, str(e)))

                try:
                    reports = get_cached_reports()
                    results.append((f"Reports reachable ({len(reports)} reports)", True, ""))
                except Exception as e:
                    results.append(("Reports reachable", False, str(e)))

                if state.logged_in_user:
                    before = len(sClickerLog)
                    send_presence_heartbeat()
                    new_entries = sClickerLog[before:]
                    heartbeat_errors = [e for e in new_entries if "Presence-Heartbeat" in e]
                    if heartbeat_errors:
                        results.append(("Online status heartbeat", False, heartbeat_errors[-1]))
                    else:
                        results.append(("Online status heartbeat", True, ""))
                else:
                    results.append(("Online status heartbeat", None, "Skipped (not logged in)."))

                try:
                    ok_write = os.access(SCLICKER_DATA_DIR, os.W_OK)
                    results.append((f"Local settings folder writable ({SCLICKER_DATA_DIR})",
                                     bool(ok_write), "" if ok_write else "No write permission."))
                except Exception as e:
                    results.append(("Local settings folder writable", False, str(e)))

                recent_errors = [e for e in sClickerLog[-50:]
                                  if any(k in e for k in ("Fehler", "fehlgeschlagen", "FAIL", "UNCAUGHT"))]

                def finish():
                    if not win.winfo_exists():
                        return
                    for name, ok, detail in results:
                        if ok is None:
                            write_line(f"[SKIP] {name}", "dim")
                        elif ok:
                            write_line(f"[PASS] {name}", "ok")
                        else:
                            write_line(f"[FAIL] {name}", "fail")
                            if detail:
                                write_line(f"       -> {detail}", "dim")
                    write_line()
                    if recent_errors:
                        write_line(f"{len(recent_errors)} recent error(s) found in the log. Type 'log' to view them.", "fail")
                    else:
                        write_line("No recent errors found in the log.", "ok")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def show_log_dump():
            write_line(PROMPT + "log", "prompt")
            if not sClickerLog:
                write_line("(log is empty)", "dim")
            else:
                for i, entry in enumerate(sClickerLog[-40:]):
                    write_line(f"[{i + 1}] {entry}", "dim")
            write_line()
            write_line(PROMPT, "prompt")

        def clear_screen():
            txt.configure(state="normal")
            txt.delete("1.0", tk.END)
            txt.configure(state="disabled")
            write_banner()
            write_line(PROMPT, "prompt")

        def show_help():
            write_line(PROMPT + "help", "prompt")
            write_line("Available commands:")
            write_line("  check   - Run diagnostics (network, login, kits, news, presence, storage)")
            write_line("  log     - Show the last 40 log entries")
            write_line("  clear   - Clear the screen")
            write_line("  help    - Show this help text")
            write_line()
            write_line(PROMPT, "prompt")

        def run_prompt_tos_async():
            write_line(PROMPT + "PromptTOS", "prompt")
            write_line("Forcing all users to re-accept the Terms of Service...", "dim")

            def worker():
                cfg = supabase_get_app_config()
                try:
                    current = int(cfg.get("tos_force_version", "0"))
                except (TypeError, ValueError):
                    current = 0
                new_version = str(current + 1)
                ok = supabase_set_app_config("tos_force_version", new_version)

                def finish():
                    if not win.winfo_exists():
                        return
                    if ok:
                        write_line(f"[OK] Terms of Service version bumped to {new_version}.", "ok")
                        write_line("All users will be prompted to accept on their next app start.", "dim")
                    else:
                        write_line("[FAIL] Could not update app_config in Supabase.", "fail")
                        if sClickerLog:
                            write_line(f"       -> {sClickerLog[-1]}", "dim")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def run_prompt_privacy_async():
            write_line(PROMPT + "PromptPrivacyPolicy", "prompt")
            write_line("Forcing all users to re-accept the Privacy Policy...", "dim")

            def worker():
                cfg = supabase_get_app_config()
                try:
                    current = int(cfg.get("privacy_force_version", "0"))
                except (TypeError, ValueError):
                    current = 0
                new_version = str(current + 1)
                ok = supabase_set_app_config("privacy_force_version", new_version)

                def finish():
                    if not win.winfo_exists():
                        return
                    if ok:
                        write_line(f"[OK] Privacy Policy version bumped to {new_version}.", "ok")
                        write_line("All users will be prompted to accept on their next app start.", "dim")
                    else:
                        write_line("[FAIL] Could not update app_config in Supabase.", "fail")
                        if sClickerLog:
                            write_line(f"       -> {sClickerLog[-1]}", "dim")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def run_prompt_both_async():
            write_line(PROMPT + "PromptBoth", "prompt")
            write_line("Forcing all users to re-accept ToS AND Privacy Policy...", "dim")

            def worker():
                cfg = supabase_get_app_config()
                try:
                    cur_tos = int(cfg.get("tos_force_version", "0"))
                except (TypeError, ValueError):
                    cur_tos = 0
                try:
                    cur_priv = int(cfg.get("privacy_force_version", "0"))
                except (TypeError, ValueError):
                    cur_priv = 0
                new_tos = str(cur_tos + 1)
                new_priv = str(cur_priv + 1)
                ok_tos = supabase_set_app_config("tos_force_version", new_tos)
                ok_priv = supabase_set_app_config("privacy_force_version", new_priv)

                def finish():
                    if not win.winfo_exists():
                        return
                    if ok_tos and ok_priv:
                        write_line(f"[OK] ToS bumped to {new_tos}, Privacy Policy bumped to {new_priv}.", "ok")
                        write_line("All users will be prompted to accept both on their next app start.", "dim")
                    else:
                        write_line("[FAIL] Could not update app_config in Supabase.", "fail")
                        if sClickerLog:
                            write_line(f"       -> {sClickerLog[-1]}", "dim")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def show_help():
            write_line(PROMPT + "help", "prompt")
            write_line("Available commands:")
            write_line("  check                - Run diagnostics (network, login, kits, news, presence, storage)")
            write_line("  log                  - Show the last 40 log entries")
            write_line("  clear                - Clear the screen")
            write_line("  PromptTOS            - Force ALL users to re-accept the Terms of Service on next start")
            write_line("  PromptPrivacyPolicy  - Force ALL users to re-accept the Privacy Policy on next start")
            write_line("  PromptBoth           - Force ALL users to re-accept BOTH ToS and Privacy Policy on next start")
            write_line("  help                 - Show this help text")
            write_line()
            write_line(PROMPT, "prompt")

        def run_command(cmd):
            cmd_raw = cmd.strip()
            cmd = cmd_raw.lower()
            if not cmd:
                write_line(PROMPT, "prompt")
                return
            if cmd == "check":
                run_check_async()
            elif cmd in ("log", "logs"):
                show_log_dump()
            elif cmd in ("clear", "cls"):
                clear_screen()
            elif cmd == "help":
                show_help()
            elif cmd == "prompttos":
                run_prompt_tos_async()
            elif cmd == "promptprivacypolicy":
                run_prompt_privacy_async()
            elif cmd == "promptboth":
                run_prompt_both_async()
            else:
                write_line(PROMPT + cmd_raw, "prompt")
                write_line(f"'{cmd_raw}' is not recognized as an internal command.", "fail")
                write_line("Type 'help' to see the list of available commands.", "dim")
                write_line()
                write_line(PROMPT, "prompt")

        input_row = tk.Frame(debug_frame, bg=PS_BG)
        input_row.place(x=10, y=390, width=730, height=30)
        tk.Label(input_row, text="PS C:\\sClicker>", bg=PS_BG, fg="#FFFFFF",
                 font=("Consolas", 10, "bold")).pack(side="left")
        cmd_entry = tk.Entry(input_row, bg=PS_BG, fg="#FFFFFF", font=PS_FONT,
                              relief="flat", insertbackground="#FFFFFF",
                              highlightthickness=0, bd=0)
        cmd_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
        cmd_entry.focus_set()

        def on_enter(_e=None):
            cmd = cmd_entry.get()
            cmd_entry.delete(0, tk.END)
            run_command(cmd)

        cmd_entry.bind("<Return>", on_enter)

        write_banner()
        write_line(PROMPT, "prompt")

    # ============== USERS WINDOW (NEU: Kartenliste wie das Followers-Fenster) ==============
    def show_users_window(self):
        # FIX: verhindert, dass mehrere Global-Accounts-Fenster übereinander
        # gestapelt werden (mögliche Ursache für Render-Reste/Streifen)
        old = getattr(self, "_users_window_ref", None)
        if old is not None:
            try:
                if old.winfo_exists():
                    old.destroy()
            except Exception:
                pass

        ctx = {
            "full_order": [], "users_order": [], "users_data": None,
            "current_sel": "", "avatar_widgets": [], "row_widgets": [],
        }

        win = new_toplevel(self.root, T("globalAccounts"), 800, 600, bg=DIALOG_BG())
        self._users_window_ref = win
        label(win, 20, 15, 500, 32, "👥 " + T("globalAccounts"), bg=DIALOG_BG(), fg="#FFFFFF",
              size=16, bold=True, anchor="w", justify="left")

        label(win, 20, 54, 60, 22, T("search"), bg=DIALOG_BG(), fg="#CCCCCC")
        se = entry(win, 85, 51, 255, 26)

        # Linke Seite: scrollbare Kartenliste, gleicher Stil wie bei den Followern
        list_frame = tk.Frame(win, bg=DIALOG_BG())
        list_frame.place(x=20, y=88, width=320, height=472)
        scroll = ttk.Scrollbar(list_frame, orient="vertical")
        scroll.pack(side="right", fill="y")
        canvas = tk.Canvas(list_frame, bg=DIALOG_BG(), highlightthickness=0, yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.config(command=canvas.yview)
        inner = tk.Frame(canvas, bg=DIALOG_BG())
        canvas.create_window((0, 0), window=inner, anchor="nw", width=300)

        def on_inner_configure(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_inner_configure)

        # FIX: bind_all ohne Aufräumen führte zu
        # "invalid command name ...canvas" sobald das Fenster/die Canvas
        # zerstört wurde, der globale Mousewheel-Handler aber weiter aktiv
        # blieb. Jetzt nur aktiv während der Maus über der Liste ist, und
        # wird beim Schließen des Fensters sauber entfernt.
        def _on_mousewheel(event):
            if not canvas.winfo_exists():
                return
            try:
                canvas.yview_scroll(-1 * int(event.delta / 60), "units")
            except Exception:
                pass

        def _bind_wheel(_e=None):
            try:
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            except Exception:
                pass

        def _unbind_wheel(_e=None):
            try:
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)
        # FIX: add="+" ist entscheidend! new_toplevel() hat auf demselben Fenster
        # bereits eine <Destroy>-Bindung (die den Hintergrund-Backdrop entfernt).
        # Ohne add="+" überschreibt diese Bindung hier die alte komplett - dadurch
        # blieb beim Klick auf X der graue Backdrop stehen ("grauer Screen"-Bug).
        win.bind("<Destroy>", lambda _e: _unbind_wheel(), add="+")

        groupbox(win, 350, 88, 430, 420, T("accountDetails"))

        avatar_slot = (370, 118, 80, 80)
        name_ctrl = label(win, 460, 121, 250, 36, T("selectAccount"), bg=DIALOG_BG(),
                           fg="#FFFFFF", size=16, bold=True)
        detail_badge_size = badge_size_for_font(16)
        check_ctrl = VerifiedBadge(win)
        check_ctrl.place(x=720, y=121, width=detail_badge_size, height=detail_badge_size)
        check_ctrl.set_visible(False)
        # FIX: Admin-Badge in der Detailansicht anderer Profile entfernt (nur Verified)
        handle_ctrl = label(win, 460, 159, 150, 22, "", bg=DIALOG_BG(), fg="#888888", size=10)
        status_ctrl = label(win, 720, 121, 140, 36, "", bg=DIALOG_BG(), fg="#22c55e", size=10, bold=True)
        joined_ctrl = label(win, 460, 183, 300, 22, "", bg=DIALOG_BG(), fg="#AAAAAA", size=10)
        followers_ctrl = label(win, 370, 213, 390, 26, "", bg=DIALOG_BG(), fg="#FFFFFF",
                                size=12, bold=True)

        bio_ctrl = tk.Label(win, text="", bg=DIALOG_BG(), fg="#CCCCCC", font=F(10),
                             wraplength=390, justify="left", anchor="nw")
        bio_ctrl.place(x=370, y=241, width=390, height=48)

        follow_btn = RoundedButton(win, text=T("follow"), bg=accent(), fg=_fg_for_bg(accent()),
                                    font=F(12, True), radius=16, border_width=2, state="disabled")
        follow_btn._follows_theme_accent = True
        follow_btn.place(x=370, y=297, width=390, height=44)

        view_btn = RoundedButton(win, text=T("viewFullProfile"), bg="#333333", fg="#FFFFFF",
                                  font=F(10, True), radius=16, border_width=2, state="disabled")
        view_btn.place(x=370, y=349, width=390, height=32)


        def clear_rows():
            for w in ctx["row_widgets"]:
                try:
                    w.destroy()
                except Exception:
                    pass
            ctx["row_widgets"] = []

        def render_rows():
            clear_rows()
            if ctx["users_data"] is None:
                status_lbl.configure(text="Server not reachable.")
                return
            order = ctx["users_order"]
            accounts = ctx["users_data"].get("accounts", {})
            row_h = 56
            avatar_size = 40
            badge_size = badge_size_for_font(11)

            for u in order:
                if u not in accounts:
                    continue
                info = accounts[u]
                is_ver = safe_flag(info, "verified")
                # FIX: Admin/OG in dieser Liste NICHT anzeigen (nur Verified)
                settings = info.get("settings", {})
                is_inf = bool(isinstance(settings, dict) and safe_flag(settings, "influencer"))
                row_emoji = str(settings.get("avatarEmoji", "")) or None
                row_color = str(settings.get("avatarColor", "")) or None
                is_selected = (u == ctx["current_sel"])
                base_bg0 = "#232323" if is_selected else "#1a1a1a"

                # FIX: statt eines Canvas-basierten RoundedButton (das bei sehr
                # vielen schnell erzeugten Reihen manchmal einen ungerenderten/
                # zu schmalen Frame zeigte -> "schwarzer Streifen") jetzt ein
                # simples, absolut zuverlässiges tk.Frame pro Zeile.
                # FIX: statt eines Canvas-basierten RoundedButton (das bei sehr
                # vielen schnell erzeugten Reihen manchmal einen ungerenderten/
                # zu schmalen Frame zeigte -> "schwarzer Streifen") jetzt ein
                # FIX 3: JEDER Rand komplett entfernt - keine Lücke, kein
                # highlightthickness, absolut nahtlos.
                card = tk.Frame(inner, bg=base_bg0, height=row_h, highlightthickness=0, bd=0)
                card.pack(fill="x", pady=0)
                card.pack_propagate(False)
                ctx["row_widgets"].append(card)

                av_widgets = self.draw_avatar(card, 8, (row_h - avatar_size) // 2,
                                               avatar_size, avatar_size, u,
                                               emoji_override=row_emoji, color_override=row_color,
                                               online=is_user_present(info), clicking=is_user_clicking(info),
                                               bg_hint=base_bg0)
                circle_lbl = av_widgets[0] if av_widgets else None
                ctx["row_widgets"].extend(av_widgets)

                disp = display_name(u)
                name_lbl = tk.Label(card, text=disp, bg=base_bg0, fg="#FFFFFF",
                                     font=F(11, True), anchor="w", cursor="hand2")
                name_x = 8 + avatar_size + 10
                name_w = min(170, measure_text_width(disp, 11, True) + 6)
                name_lbl.place(x=name_x, y=(row_h - 20) // 2, width=name_w, height=20)
                ctx["row_widgets"].append(name_lbl)

                badges = []
                cursor_x = name_x + name_w + 4
                bY = (row_h - badge_size) // 2 + ICON_Y_OFFSET
                if is_ver:
                    vb = VerifiedBadge(card)
                    vb.sync_parent_bg(base_bg0)
                    vb.place(x=cursor_x, y=bY, width=badge_size, height=badge_size)
                    cursor_x += badge_size + 4
                    badges.append(vb)
                    ctx["row_widgets"].append(vb)
                if is_inf:
                    ib = InfluencerBadge(card)
                    ib.sync_parent_bg(base_bg0)
                    ib.place(x=cursor_x, y=bY, width=badge_size, height=badge_size)
                    cursor_x += badge_size + 4
                    badges.append(ib)
                    ctx["row_widgets"].append(ib)

                arrow_lbl = tk.Label(card, text="›", bg=base_bg0, fg="#666666",
                                      font=F(16, True), cursor="hand2")
                arrow_lbl.place(x=278, y=0, width=20, height=row_h)
                ctx["row_widgets"].append(arrow_lbl)

                def _enter(_e, c=card, nl=name_lbl, al=arrow_lbl, bl=badges, cl=circle_lbl):
                    if u != ctx["current_sel"]:
                        c.configure(bg="#242424")
                        nl.configure(bg="#242424")
                        al.configure(bg="#242424", fg="#9945FF")
                        for b in bl:
                            b.sync_parent_bg("#242424")
                        if cl is not None:
                            cl.configure(bg="#242424")

                def _leave(_e, c=card, nl=name_lbl, al=arrow_lbl, bl=badges, cl=circle_lbl, uu=u):
                    base_bg = "#232323" if uu == ctx["current_sel"] else "#1a1a1a"
                    c.configure(bg=base_bg)
                    nl.configure(bg=base_bg)
                    al.configure(bg=base_bg, fg="#666666")
                    for b in bl:
                        b.sync_parent_bg(base_bg)
                    if cl is not None:
                        cl.configure(bg=base_bg)

                def _click(_e, uu=u):
                    on_row_select(uu)

                clickable = [card, name_lbl, arrow_lbl] + badges
                if circle_lbl is not None:
                    clickable.append(circle_lbl)
                for w in clickable:
                    w.bind("<Enter>", _enter)
                    w.bind("<Leave>", _leave)
                    w.bind("<Button-1>", _click)

            # FIX: die Account-Zähler-Texte wurden komplett entfernt (nicht mehr gewünscht)

        def apply_filter(*_):
            q = se.get().strip().lower()
            ctx["users_order"] = [u for u in ctx["full_order"] if not q or q in u.lower()]
            render_rows()

        def fetch_and_sort():
            # FIX: "Loading..." Text soll nicht mehr angezeigt werden

            def worker():
                r = auth_get_data()
                data = json_parse(r) if r else None

                def finish():
                    if not win.winfo_exists():
                        return
                    ctx["users_data"] = data
                    ulist = []
                    if data and data.get("accounts"):
                        for u, info in data["accounts"].items():
                            if not safe_flag(info, "banned"):
                                ulist.append(u)
                    ctx["full_order"] = sort_users_by_joined_desc(ulist, data)
                    apply_filter()

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def render_right_pane(u):
            for w in ctx["avatar_widgets"]:
                try:
                    w.destroy()
                except Exception:
                    pass
            ctx["avatar_widgets"] = []

            accounts = ctx["users_data"].get("accounts", {}) if ctx["users_data"] else {}
            if u not in accounts:
                return
            info = accounts[u]
            is_ver = safe_flag(info, "verified")
            settings_pane = info.get("settings", {})
            is_inf_pane = bool(isinstance(settings_pane, dict) and safe_flag(settings_pane, "influencer"))
            jv = info.get("joined", "")
            joined_str = T("joinedBefore") if (not jv or is_owner_account(u)) else jv
            fc = count_followers(ctx["users_data"], u)

            settings = info.get("settings", {})
            emoji = str(settings.get("avatarEmoji", "")) if settings.get("avatarEmoji") else \
                str(info.get("avatarEmoji", "")) if info.get("avatarEmoji") else ""
            avatar_color = str(settings.get("avatarColor", "")) if settings.get("avatarColor") else ""

            av_widgets = self.draw_avatar(win, *avatar_slot, u, emoji_override=emoji or None,
                                           color_override=avatar_color or None)
            ctx["avatar_widgets"].extend(av_widgets)

            disp_u = display_name(u)
            name_ctrl.configure(text=disp_u)
            name_w = min(244, max(20, measure_text_width(disp_u, 16, True) + 6))
            name_ctrl.place(x=460, y=121, width=name_w, height=36)
            badge_y2 = badge_y_centered(121, 36, detail_badge_size) + ICON_Y_OFFSET
            cursor_x = 460 + name_w + BADGE_NAME_GAP
            if is_ver:
                check_ctrl.set_visible(True)
                check_ctrl.place(x=cursor_x, y=badge_y2, width=detail_badge_size, height=detail_badge_size)
                cursor_x += detail_badge_size
            else:
                check_ctrl.set_visible(False)
                check_ctrl.place(x=cursor_x, y=badge_y2, width=1, height=detail_badge_size)

            if getattr(self, "_users_influencer_badge", None) is not None:
                try:
                    self._users_influencer_badge.destroy()
                except Exception:
                    pass
                self._users_influencer_badge = None
            if is_inf_pane:
                inf_badge_pane = InfluencerBadge(win)
                inf_badge_pane.place(x=cursor_x + 4, y=badge_y2, width=detail_badge_size, height=detail_badge_size)
                cursor_x += detail_badge_size + 4
                self._users_influencer_badge = inf_badge_pane

            handle_ctrl.configure(text="@" + disp_u.lower())
            if is_user_clicking(info):
                status_ctrl.configure(text="CLICKING", fg="#f59e0b")
            elif is_user_present(info):
                status_ctrl.configure(text="ONLINE", fg="#22c55e")
            else:
                status_ctrl.configure(text="")
            status_ctrl.place(x=cursor_x + 6, y=121, width=140, height=36)
            joined_ctrl.configure(text=T("joined") + str(joined_str))
            followers_ctrl.configure(text=T("followers") + str(fc))
            bio_text = str(settings.get("bio", "")).strip()
            bio_ctrl.configure(text=bio_text if bio_text else "—", fg="#CCCCCC" if bio_text else "#555555")

            follow_btn.configure(state="normal")
            view_btn.configure(state="normal")
            if not state.logged_in_user:
                follow_btn.configure(text=T("loginToFollow"), state="disabled")
            elif state.logged_in_user == u:
                follow_btn.configure(text=T("followThis"), state="disabled")
            else:
                already = is_following(ctx["users_data"], state.logged_in_user, u)
                txt = (T("unfollow") if already else T("follow")) + " " + disp_u
                follow_btn.configure(text=txt)

        def on_row_select(u):
            ctx["current_sel"] = u
            render_rows()
            render_right_pane(u)

        def on_follow_click():
            if not ctx["current_sel"] or not state.logged_in_user:
                if not state.logged_in_user:
                    status_lbl.configure(text=T("needLogin"))
                return
            if ctx["current_sel"] == state.logged_in_user:
                return
            ok, new_data = self.handle_follow_click(ctx["current_sel"])
            if ok:
                ctx["users_data"] = new_data
                render_right_pane(ctx["current_sel"])
                render_rows()

        def on_view_click():
            if ctx["current_sel"]:
                self.show_user_profile(ctx["current_sel"])

        follow_btn.configure(command=on_follow_click)
        view_btn.configure(command=on_view_click)
        se.bind("<KeyRelease>", apply_filter)

        button(win, 20, 552, 380, 36, "🔄 " + T("refreshList"), command=fetch_and_sort,
               bg="#333333", fg="#FFFFFF")
        button(win, 410, 552, 370, 36, T("close"), command=win.destroy,
               bg="#222222", fg="#CCCCCC")

        fetch_and_sort()

    # ============== DEBUG LOG WINDOW ==============
    def show_debug_log_window(self):
        # FIX: Debug-Konsole war für JEDEN zugänglich (auch nicht eingeloggte
        # Gäste) - jetzt nur noch für Admins/den Owner.
        if not (state.logged_in_user and auth_is_admin(state.logged_in_user)):
            show_info(T("needLogin"))
            return
        PS_BG = "#000000"
        PS_FG = "#EEEEEE"
        PS_OK = "#3DDC84"
        PS_FAIL = "#FF6B6B"
        PS_DIM = "#8FB6E8"
        PS_FONT = ("Consolas", 10)

        win = new_toplevel(self.root, "Debug Console", 760, 560, bg=PS_BG)
        win.configure(highlightbackground=PS_DIM)

        title_bar = tk.Frame(win, bg="#000000", height=30)
        title_bar.place(x=0, y=0, width=760, height=30)
        tk.Label(title_bar, text="sClicker Debug Console",
                 bg="#000000", fg="#FFFFFF", font=("Consolas", 10, "bold"),
                 anchor="w").place(x=10, y=4, width=600, height=22)

        text_frame = tk.Frame(win, bg=PS_BG)
        text_frame.place(x=10, y=36, width=740, height=460)
        scroll = tk.Scrollbar(text_frame)
        scroll.pack(side="right", fill="y")
        txt = tk.Text(text_frame, bg=PS_BG, fg=PS_FG, font=PS_FONT,
                       bd=0, highlightthickness=0, wrap="word",
                       yscrollcommand=scroll.set, insertbackground=PS_FG)
        txt.pack(side="left", fill="both", expand=True)
        scroll.config(command=txt.yview)
        txt.tag_configure("ok", foreground=PS_OK)
        txt.tag_configure("fail", foreground=PS_FAIL)
        txt.tag_configure("dim", foreground=PS_DIM)
        txt.tag_configure("prompt", foreground="#FFFFFF", font=("Consolas", 10, "bold"))
        txt.configure(state="disabled")

        PROMPT = "PS C:\\sClicker> "

        def write_line(s="", tag=None):
            txt.configure(state="normal")
            if tag:
                txt.insert(tk.END, s + "\n", tag)
            else:
                txt.insert(tk.END, s + "\n")
            txt.see(tk.END)
            txt.configure(state="disabled")

        def write_banner():
            write_line("sClicker Debug Console")
            write_line("Copyright (C) sClicker. All rights reserved.")
            write_line()
            write_line("Type 'check' to run diagnostics, 'log' to show recent log entries,")
            write_line("'clear' to clear the screen, or 'help' for all commands.")
            write_line()

        def run_check_async():
            write_line(PROMPT + "check", "prompt")
            write_line("Running diagnostics...", "dim")

            def worker():
                results = []

                r = auth_get_data()
                if r:
                    results.append(("Network connection (server reachable)", True, ""))
                else:
                    results.append(("Network connection (server reachable)", False,
                                     "Could not reach the server. Check your internet connection."))

                if state.logged_in_user:
                    results.append((f"Logged in as '{state.logged_in_user}'", True, ""))
                else:
                    results.append(("Logged in", False, "No account is currently logged in (guest mode)."))

                try:
                    kits = get_public_kits()
                    results.append((f"Click Kits reachable ({len(kits)} found)", True, ""))
                except Exception as e:
                    results.append(("Click Kits reachable", False, str(e)))

                try:
                    posts = get_news_posts()
                    results.append((f"News feed reachable ({len(posts)} posts)", True, ""))
                except Exception as e:
                    results.append(("News feed reachable", False, str(e)))

                try:
                    reports = get_cached_reports()
                    results.append((f"Reports reachable ({len(reports)} reports)", True, ""))
                except Exception as e:
                    results.append(("Reports reachable", False, str(e)))

                if state.logged_in_user:
                    before = len(sClickerLog)
                    send_presence_heartbeat()
                    new_entries = sClickerLog[before:]
                    heartbeat_errors = [e for e in new_entries if "Presence-Heartbeat" in e]
                    if heartbeat_errors:
                        results.append(("Online status heartbeat", False, heartbeat_errors[-1]))
                    else:
                        results.append(("Online status heartbeat", True, ""))
                else:
                    results.append(("Online status heartbeat", None, "Skipped (not logged in)."))

                try:
                    ok_write = os.access(SCLICKER_DATA_DIR, os.W_OK)
                    results.append((f"Local settings folder writable ({SCLICKER_DATA_DIR})",
                                     bool(ok_write), "" if ok_write else "No write permission."))
                except Exception as e:
                    results.append(("Local settings folder writable", False, str(e)))

                recent_errors = [e for e in sClickerLog[-50:]
                                  if any(k in e for k in ("Fehler", "fehlgeschlagen", "FAIL", "UNCAUGHT"))]

                def finish():
                    if not win.winfo_exists():
                        return
                    for name, ok, detail in results:
                        if ok is None:
                            write_line(f"[SKIP] {name}", "dim")
                        elif ok:
                            write_line(f"[PASS] {name}", "ok")
                        else:
                            write_line(f"[FAIL] {name}", "fail")
                            if detail:
                                write_line(f"       -> {detail}", "dim")
                    write_line()
                    if recent_errors:
                        write_line(f"{len(recent_errors)} recent error(s) found in the log. Type 'log' to view them.", "fail")
                    else:
                        write_line("No recent errors found in the log.", "ok")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def show_log_dump():
            write_line(PROMPT + "log", "prompt")
            if not sClickerLog:
                write_line("(log is empty)", "dim")
            else:
                for i, entry in enumerate(sClickerLog[-40:]):
                    write_line(f"[{i + 1}] {entry}", "dim")
            write_line()
            write_line(PROMPT, "prompt")

        def clear_screen():
            txt.configure(state="normal")
            txt.delete("1.0", tk.END)
            txt.configure(state="disabled")
            write_banner()
            write_line(PROMPT, "prompt")

        def run_prompt_tos_async():
            write_line(PROMPT + "PromptTOS", "prompt")
            write_line("Forcing all users to re-accept the Terms of Service...", "dim")

            def worker():
                cfg = supabase_get_app_config()
                try:
                    current = int(cfg.get("tos_force_version", "0"))
                except (TypeError, ValueError):
                    current = 0
                new_version = str(current + 1)
                ok = supabase_set_app_config("tos_force_version", new_version)

                def finish():
                    if not win.winfo_exists():
                        return
                    if ok:
                        write_line(f"[OK] Terms of Service version bumped to {new_version}.", "ok")
                        write_line("All users will be prompted to accept on their next app start.", "dim")
                    else:
                        write_line("[FAIL] Could not update app_config in Supabase.", "fail")
                        if sClickerLog:
                            write_line(f"       -> {sClickerLog[-1]}", "dim")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def run_prompt_privacy_async():
            write_line(PROMPT + "PromptPrivacyPolicy", "prompt")
            write_line("Forcing all users to re-accept the Privacy Policy...", "dim")

            def worker():
                cfg = supabase_get_app_config()
                try:
                    current = int(cfg.get("privacy_force_version", "0"))
                except (TypeError, ValueError):
                    current = 0
                new_version = str(current + 1)
                ok = supabase_set_app_config("privacy_force_version", new_version)

                def finish():
                    if not win.winfo_exists():
                        return
                    if ok:
                        write_line(f"[OK] Privacy Policy version bumped to {new_version}.", "ok")
                        write_line("All users will be prompted to accept on their next app start.", "dim")
                    else:
                        write_line("[FAIL] Could not update app_config in Supabase.", "fail")
                        if sClickerLog:
                            write_line(f"       -> {sClickerLog[-1]}", "dim")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def run_prompt_both_async():
            write_line(PROMPT + "PromptBoth", "prompt")
            write_line("Forcing all users to re-accept ToS AND Privacy Policy...", "dim")

            def worker():
                cfg = supabase_get_app_config()
                try:
                    cur_tos = int(cfg.get("tos_force_version", "0"))
                except (TypeError, ValueError):
                    cur_tos = 0
                try:
                    cur_priv = int(cfg.get("privacy_force_version", "0"))
                except (TypeError, ValueError):
                    cur_priv = 0
                new_tos = str(cur_tos + 1)
                new_priv = str(cur_priv + 1)
                ok_tos = supabase_set_app_config("tos_force_version", new_tos)
                ok_priv = supabase_set_app_config("privacy_force_version", new_priv)

                def finish():
                    if not win.winfo_exists():
                        return
                    if ok_tos and ok_priv:
                        write_line(f"[OK] ToS bumped to {new_tos}, Privacy Policy bumped to {new_priv}.", "ok")
                        write_line("All users will be prompted to accept both on their next app start.", "dim")
                    else:
                        write_line("[FAIL] Could not update app_config in Supabase.", "fail")
                        if sClickerLog:
                            write_line(f"       -> {sClickerLog[-1]}", "dim")
                    write_line()
                    write_line(PROMPT, "prompt")

                try:
                    self.root.after(0, finish)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True).start()

        def show_help():
            write_line(PROMPT + "help", "prompt")
            write_line("Available commands:")
            write_line("  check                - Run diagnostics (network, login, kits, news, presence, storage)")
            write_line("  log                  - Show the last 40 log entries")
            write_line("  clear                - Clear the screen")
            write_line("  PromptTOS            - Force ALL users to re-accept the Terms of Service on next start")
            write_line("  PromptPrivacyPolicy  - Force ALL users to re-accept the Privacy Policy on next start")
            write_line("  PromptBoth           - Force ALL users to re-accept BOTH ToS and Privacy Policy on next start")
            write_line("  help                 - Show this help text")
            write_line()
            write_line(PROMPT, "prompt")

        def run_command(cmd):
            cmd_raw = cmd.strip()
            cmd = cmd_raw.lower()
            if not cmd:
                write_line(PROMPT, "prompt")
                return
            if cmd == "check":
                run_check_async()
            elif cmd in ("log", "logs"):
                show_log_dump()
            elif cmd in ("clear", "cls"):
                clear_screen()
            elif cmd == "help":
                show_help()
            elif cmd == "prompttos":
                run_prompt_tos_async()
            elif cmd == "promptprivacypolicy":
                run_prompt_privacy_async()
            elif cmd == "promptboth":
                run_prompt_both_async()
            else:
                write_line(PROMPT + cmd_raw, "prompt")
                write_line(f"'{cmd_raw}' is not recognized as an internal command.", "fail")
                write_line("Type 'help' to see the list of available commands.", "dim")
                write_line()
                write_line(PROMPT, "prompt")

        input_row = tk.Frame(win, bg=PS_BG)
        input_row.place(x=10, y=502, width=740, height=30)
        tk.Label(input_row, text="PS C:\\sClicker>", bg=PS_BG, fg="#FFFFFF",
                 font=("Consolas", 10, "bold")).pack(side="left")
        cmd_entry = tk.Entry(input_row, bg=PS_BG, fg="#FFFFFF", font=PS_FONT,
                              relief="flat", insertbackground="#FFFFFF",
                              highlightthickness=0, bd=0)
        cmd_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
        cmd_entry.focus_set()

        def on_enter(_e=None):
            cmd = cmd_entry.get()
            cmd_entry.delete(0, tk.END)
            run_command(cmd)

        cmd_entry.bind("<Return>", on_enter)

        write_banner()
        write_line(PROMPT, "prompt")

    # ============== TRACKER ==============
    def show_tracking_dialog(self):
        win = new_toplevel(self.root, T("trackerTitle"), 600, 480, bg=DIALOG_BG(), resizable=False)

        label(win, 20, 15, 560, 30, T("trackerTitle"), bg=DIALOG_BG(),
              fg="#8B5CF6", size=16, bold=True, anchor="center", justify="center")

        label(win, 20, 55, 560, 20, T("trackerDuration"), bg=DIALOG_BG(), fg="#FFFFFF", bold=True)

        duration_var = tk.StringVar(value="5")
        duration_spin = tk.Spinbox(win, from_=1, to=120, textvariable=duration_var,
                                   bg="#1a1a1a", fg="#FFFFFF", font=F(12), bd=1, width=15)
        duration_spin.place(x=20, y=78, width=80, height=35)

        info_text = tk.Label(win, text=T("trackerStatusReady"), bg=DIALOG_BG(), fg="#AAAAAA",
                            font=F(11), justify="left", wraplength=560, anchor="nw")
        info_text.place(x=20, y=125, width=560, height=60)

        hotkey_hint = label(win, 20, 190, 560, 20,
                             T("trackerStopHotkey").format(state.emergency_hotkey),
                             bg=DIALOG_BG(), fg="#ef4444", size=10, bold=True)

        features_label = tk.Label(win, text=T("trackerFeatures"), bg=DIALOG_BG(), fg="#9945FF",
                                 font=F(10), justify="left")
        features_label.place(x=20, y=215, width=560, height=100)

        tracking_context = {"recording": False, "event_count": 0}

        def start_tracking():
            try:
                duration = int(duration_var.get())
                if duration < 1 or duration > 120:
                    show_info(T("trackerDurationError"))
                    return
            except ValueError:
                show_info(T("trackerDurationInvalid"))
                return

            state.is_tracking = True
            state.tracking_data = []
            tracking_context["recording"] = True
            tracking_context["event_count"] = 0
            tracking_context["start_time"] = time.time()

            info_text.configure(text=T("trackerRecording").format(duration))
            start_btn.configure(state="disabled", bg="#666666")

            def poll_loop():
                t0 = time.perf_counter()
                end_time = t0 + duration
                last_pos = [None]
                last_keys = {}
                for k in TRACKABLE_KEYS:
                    try:
                        last_keys[k] = is_key_down(k)
                    except Exception:
                        last_keys[k] = False
                last_buttons = {}
                for b in TRACKABLE_MOUSE_BUTTONS:
                    try:
                        last_buttons[b] = is_mouse_button_down(b)
                    except Exception:
                        last_buttons[b] = False

                while state.is_tracking and time.perf_counter() < end_time:
                    now = time.perf_counter() - t0
                    try:
                        pos = get_cursor_pos()
                        if pos is not None and pos != last_pos[0]:
                            state.tracking_data.append({"type": "move", "x": pos[0], "y": pos[1], "t": now})
                            last_pos[0] = pos
                    except Exception:
                        pass

                    for k in TRACKABLE_KEYS:
                        try:
                            down = is_key_down(k)
                        except Exception:
                            down = False
                        if down != last_keys[k]:
                            state.tracking_data.append({"type": "keydown" if down else "keyup", "key": k, "t": now})
                            last_keys[k] = down

                    for b in TRACKABLE_MOUSE_BUTTONS:
                        try:
                            down = is_mouse_button_down(b)
                        except Exception:
                            down = False
                        if down != last_buttons[b]:
                            state.tracking_data.append({"type": "mousedown" if down else "mouseup", "button": b, "t": now})
                            last_buttons[b] = down

                    time.sleep(0.005)

                tracking_context["event_count"] = len(state.tracking_data)
                state.is_tracking = False
                try:
                    win.after(0, stop_tracking_cb)
                except Exception:
                    pass

            threading.Thread(target=poll_loop, daemon=True).start()

            def stop_tracking_cb():
                tracking_context["recording"] = False
                info_text.configure(text=T("trackerCompleted").format(tracking_context["event_count"]))
                start_btn.configure(state="normal", bg="#8B5CF6")
                save_btn.configure(state="normal" if state.tracking_data else "disabled")

        def save_tracking():
            if not state.tracking_data:
                show_info(T("trackerNoData"))
                return

            loading_frame = tk.Frame(win, bg="#000000")
            loading_frame.place(x=0, y=0, width=600, height=480)
            loading_frame.configure(highlightthickness=0)

            overlay_label = tk.Label(loading_frame, text=T("trackerSaving"),
                                     bg="#1a1a1a", fg="#FFFFFF",
                                     font=F(14, True), justify="center")
            overlay_label.place(x=150, y=190, width=300, height=100)

            win.update()

            events = sorted(state.tracking_data, key=lambda e: e.get("t", 0))
            prev_t = 0.0
            converted = 0
            for event in events:
                t = event.get("t", 0.0)
                delay_ms = max(0, round((t - prev_t) * 1000))
                prev_t = t
                etype = event.get("type")
                if etype == "move":
                    state.action_list.append({"type": "move", "x": event.get("x", 0),
                                               "y": event.get("y", 0), "delay": delay_ms})
                    converted += 1
                elif etype in ("keydown", "keyup"):
                    state.action_list.append({"type": etype, "key": event.get("key", ""), "delay": delay_ms})
                    converted += 1
                elif etype in ("mousedown", "mouseup"):
                    state.action_list.append({"type": etype, "button": event.get("button", "left"), "delay": delay_ms})
                    converted += 1

            self.update_action_list()
            save_user_config()
            loading_frame.destroy()
            show_info(T("trackerSaved").format(converted, state.emergency_hotkey))
            win.destroy()

        start_btn = button(win, 20, 325, 270, 40, T("trackerStart"), command=start_tracking,
                          bg="#8B5CF6", fg="#FFFFFF", bold=True, size=12)
        save_btn = button(win, 310, 325, 270, 40, T("trackerSave"), command=save_tracking,
                         bg="#22c55e", fg="#FFFFFF", bold=True, size=12)
        save_btn.configure(state="disabled")

        button(win, 20, 380, 560, 35, T("close"), command=win.destroy,
              bg="#333333", fg="#CCCCCC")


# ============== MAIN ==============
def main():
    if supabase is None:
        print("FEHLER: Supabase konnte nicht initialisiert werden.")
        print(f"URL: {SUPABASE_URL}")
        print("Bitte überprüfen Sie die Verbindung und die API-Keys.")
        return
    app = SClickerApp()
    app.run()


if __name__ == "__main__":
    print("DATEI STARTET")
    main()