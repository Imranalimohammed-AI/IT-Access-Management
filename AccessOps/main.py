#!/usr/bin/env python3
"""
IT Access Management — AccessOps
Cotiviti IT Engineering

Flask backend that serves the AccessOps dashboard and provides REST API
endpoints for Okta, Active Directory, access requests, audit log, and
bulk offboarding workflows.

Run:
    python main.py

Then open: http://localhost:5050
"""

import csv
import io
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("accessops")

# ── Config ────────────────────────────────────────────────────────────────────
OKTA_DOMAIN    = os.environ.get("OKTA_DOMAIN", "")
OKTA_API_TOKEN = os.environ.get("OKTA_API_TOKEN", "")
AD_SERVER      = os.environ.get("AD_SERVER", "")
AD_DOMAIN      = os.environ.get("AD_DOMAIN", "cotiviti.com")
AD_BIND_USER   = os.environ.get("AD_BIND_USER", "")
AD_BIND_PASS   = os.environ.get("AD_BIND_PASSWORD", "")
PORT           = int(os.environ.get("FLASK_PORT", 5050))
DEBUG          = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
AUDIT_FILE  = DATA_DIR / "audit_log.jsonl"
REQ_FILE    = DATA_DIR / "access_requests.jsonl"
OFFBOARD_FILE = DATA_DIR / "offboarded_users.jsonl"
DATA_DIR.mkdir(exist_ok=True)

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app)

# ── Input sanitization ────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

def _safe_email(email: str) -> str:
    email = email.strip()[:200]
    if not _EMAIL_RE.match(email):
        raise ValueError(f"Invalid email format: {email!r}")
    return email

def _safe_str(s: str, max_len: int = 500) -> str:
    return str(s).strip()[:max_len]

# ── Audit log ─────────────────────────────────────────────────────────────────
def _audit(action: str, target: str, performed_by: str = "system", detail: str = "") -> None:
    record = {
        "id":           str(uuid.uuid4()),
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "action":       _safe_str(action),
        "target":       _safe_str(target),
        "performed_by": _safe_str(performed_by),
        "detail":       _safe_str(detail),
    }
    with open(AUDIT_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")

# ── Okta helpers ──────────────────────────────────────────────────────────────
def _okta_headers() -> dict:
    if not OKTA_API_TOKEN:
        raise RuntimeError("OKTA_API_TOKEN not set in environment.")
    return {
        "Authorization": f"SSWS {OKTA_API_TOKEN}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
    }

def _okta_get(path: str, params: dict | None = None) -> dict | list:
    if not OKTA_DOMAIN:
        raise RuntimeError("OKTA_DOMAIN not set in environment.")
    url = f"https://{OKTA_DOMAIN}/api/v1/{path}"
    resp = requests.get(url, headers=_okta_headers(), params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def _okta_post(path: str, payload: dict) -> dict:
    url = f"https://{OKTA_DOMAIN}/api/v1/{path}"
    resp = requests.post(url, headers=_okta_headers(), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

# ── AD/LDAP helpers ───────────────────────────────────────────────────────────
def _ad_connect():
    try:
        from ldap3 import Server, Connection, ALL, NTLM
    except ImportError:
        raise RuntimeError("Run: pip install ldap3")
    server = Server(AD_SERVER, get_info=ALL)
    conn   = Connection(server, user=AD_BIND_USER, password=AD_BIND_PASS, authentication=NTLM, auto_bind=True)
    return conn

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), "it-access-dashboard.html")

# ── Okta: User lookup ─────────────────────────────────────────────────────────

@app.route("/api/okta/user", methods=["GET"])
def okta_get_user():
    """
    GET /api/okta/user?email=user@cotiviti.com
    Returns Okta user profile, status, groups, and app assignments.
    """
    try:
        email = _safe_email(request.args.get("email", ""))
        users = _okta_get("users", params={"filter": f'profile.email eq "{email}"'})
        if not users:
            return jsonify({"error": "User not found in Okta"}), 404
        user = users[0]
        uid  = user["id"]

        groups = _okta_get(f"users/{uid}/groups")
        apps   = _okta_get(f"users/{uid}/appLinks")

        _audit("OKTA_LOOKUP", email)
        return jsonify({"user": user, "groups": groups, "apps": apps})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except requests.HTTPError as exc:
        return jsonify({"error": f"Okta API error: {exc.response.status_code}"}), exc.response.status_code

# ── Okta: Suspend / Activate / Reset MFA ──────────────────────────────────────

@app.route("/api/okta/user/<user_id>/suspend", methods=["POST"])
def okta_suspend(user_id: str):
    try:
        user_id = _safe_str(user_id, 64)
        requests.post(
            f"https://{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/suspend",
            headers=_okta_headers(), timeout=10
        ).raise_for_status()
        _audit("OKTA_SUSPEND", user_id, detail="User suspended via AccessOps")
        return jsonify({"status": "suspended"})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except requests.HTTPError as exc:
        return jsonify({"error": f"Okta error: {exc.response.status_code}"}), exc.response.status_code

@app.route("/api/okta/user/<user_id>/activate", methods=["POST"])
def okta_activate(user_id: str):
    try:
        user_id = _safe_str(user_id, 64)
        requests.post(
            f"https://{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/activate",
            headers=_okta_headers(), params={"sendEmail": "false"}, timeout=10
        ).raise_for_status()
        _audit("OKTA_ACTIVATE", user_id, detail="User activated via AccessOps")
        return jsonify({"status": "active"})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except requests.HTTPError as exc:
        return jsonify({"error": f"Okta error: {exc.response.status_code}"}), exc.response.status_code

@app.route("/api/okta/user/<user_id>/reset-mfa", methods=["POST"])
def okta_reset_mfa(user_id: str):
    try:
        user_id = _safe_str(user_id, 64)
        requests.post(
            f"https://{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/reset_factors",
            headers=_okta_headers(), timeout=10
        ).raise_for_status()
        _audit("OKTA_RESET_MFA", user_id, detail="MFA factors reset via AccessOps")
        return jsonify({"status": "mfa_reset"})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except requests.HTTPError as exc:
        return jsonify({"error": f"Okta error: {exc.response.status_code}"}), exc.response.status_code

@app.route("/api/okta/user/<user_id>/reset-password", methods=["POST"])
def okta_reset_password(user_id: str):
    try:
        user_id = _safe_str(user_id, 64)
        resp = requests.post(
            f"https://{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/reset_password",
            headers=_okta_headers(), params={"sendEmail": "true"}, timeout=10
        )
        resp.raise_for_status()
        _audit("OKTA_RESET_PASSWORD", user_id, detail="Password reset email sent via AccessOps")
        return jsonify({"status": "reset_email_sent"})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except requests.HTTPError as exc:
        return jsonify({"error": f"Okta error: {exc.response.status_code}"}), exc.response.status_code

@app.route("/api/okta/user/<user_id>/remove-app", methods=["POST"])
def okta_remove_app(user_id: str):
    """POST body: { "app_instance_id": "..." }"""
    try:
        user_id = _safe_str(user_id, 64)
        body    = request.get_json(force=True) or {}
        app_id  = _safe_str(body.get("app_instance_id", ""), 64)
        if not app_id:
            return jsonify({"error": "app_instance_id required"}), 400
        requests.delete(
            f"https://{OKTA_DOMAIN}/api/v1/apps/{app_id}/users/{user_id}",
            headers=_okta_headers(), timeout=10
        ).raise_for_status()
        _audit("OKTA_REMOVE_APP", user_id, detail=f"Removed from app {app_id}")
        return jsonify({"status": "removed"})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except requests.HTTPError as exc:
        return jsonify({"error": f"Okta error: {exc.response.status_code}"}), exc.response.status_code

# ── Active Directory ──────────────────────────────────────────────────────────

@app.route("/api/ad/user", methods=["GET"])
def ad_get_user():
    """GET /api/ad/user?email=user@cotiviti.com"""
    try:
        email = _safe_email(request.args.get("email", ""))
        conn  = _ad_connect()
        base  = ",".join(f"DC={part}" for part in AD_DOMAIN.split("."))
        conn.search(
            search_base=base,
            search_filter=f"(mail={email})",
            attributes=["cn", "sAMAccountName", "mail", "department", "title",
                        "memberOf", "accountExpires", "userAccountControl",
                        "lastLogonTimestamp", "whenCreated"],
        )
        if not conn.entries:
            return jsonify({"error": "User not found in Active Directory"}), 404
        entry  = conn.entries[0]
        groups = [str(g).split(",")[0].replace("CN=", "") for g in (entry.memberOf.values or [])]
        _audit("AD_LOOKUP", email)
        return jsonify({
            "display_name":    str(entry.cn),
            "sam_account":     str(entry.sAMAccountName),
            "email":           str(entry.mail),
            "department":      str(entry.department),
            "title":           str(entry.title),
            "groups":          groups,
            "account_expires": str(entry.accountExpires),
            "created":         str(entry.whenCreated),
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

@app.route("/api/ad/user/disable", methods=["POST"])
def ad_disable_user():
    """POST body: { "sam_account": "jdoe" }"""
    try:
        body    = request.get_json(force=True) or {}
        sam     = _safe_str(body.get("sam_account", ""), 64)
        if not sam:
            return jsonify({"error": "sam_account required"}), 400
        conn    = _ad_connect()
        base    = ",".join(f"DC={part}" for part in AD_DOMAIN.split("."))
        conn.search(base, f"(sAMAccountName={sam})", attributes=["userAccountControl"])
        if not conn.entries:
            return jsonify({"error": "User not found"}), 404
        dn  = conn.entries[0].entry_dn
        uac = int(conn.entries[0].userAccountControl.value)
        conn.modify(dn, {"userAccountControl": [("MODIFY_REPLACE", [uac | 0x2])]})
        _audit("AD_DISABLE", sam, detail="Account disabled via AccessOps")
        return jsonify({"status": "disabled"})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

@app.route("/api/ad/user/remove-group", methods=["POST"])
def ad_remove_group():
    """POST body: { "sam_account": "jdoe", "group_dn": "CN=..." }"""
    try:
        body      = request.get_json(force=True) or {}
        sam       = _safe_str(body.get("sam_account", ""), 64)
        group_dn  = _safe_str(body.get("group_dn", ""), 500)
        if not sam or not group_dn:
            return jsonify({"error": "sam_account and group_dn required"}), 400
        conn    = _ad_connect()
        base    = ",".join(f"DC={part}" for part in AD_DOMAIN.split("."))
        conn.search(base, f"(sAMAccountName={sam})", attributes=["dn"])
        if not conn.entries:
            return jsonify({"error": "User not found"}), 404
        user_dn = conn.entries[0].entry_dn
        conn.modify(group_dn, {"member": [("MODIFY_DELETE", [user_dn])]})
        _audit("AD_REMOVE_GROUP", sam, detail=f"Removed from group {group_dn}")
        return jsonify({"status": "removed"})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

# ── Access Requests ───────────────────────────────────────────────────────────

@app.route("/api/requests", methods=["GET"])
def get_requests():
    if not REQ_FILE.exists():
        return jsonify([])
    records = []
    for line in REQ_FILE.read_text(encoding="utf-8").strip().splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return jsonify(records)

@app.route("/api/requests", methods=["POST"])
def create_request():
    """POST body: { "requester": "email", "target_user": "email", "resource": "app/group name", "reason": "..." }"""
    body = request.get_json(force=True) or {}
    try:
        record = {
            "id":          str(uuid.uuid4()),
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "status":      "pending",
            "requester":   _safe_email(body.get("requester", "")),
            "target_user": _safe_email(body.get("target_user", "")),
            "resource":    _safe_str(body.get("resource", ""), 200),
            "reason":      _safe_str(body.get("reason", ""), 500),
        }
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    with open(REQ_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    _audit("REQUEST_CREATED", record["target_user"], detail=record["resource"])
    return jsonify(record), 201

@app.route("/api/requests/<req_id>/approve", methods=["POST"])
def approve_request(req_id: str):
    return _update_request_status(req_id, "approved")

@app.route("/api/requests/<req_id>/deny", methods=["POST"])
def deny_request(req_id: str):
    return _update_request_status(req_id, "denied")

def _update_request_status(req_id: str, new_status: str):
    req_id = _safe_str(req_id, 64)
    if not REQ_FILE.exists():
        return jsonify({"error": "Not found"}), 404
    lines   = REQ_FILE.read_text(encoding="utf-8").strip().splitlines()
    updated = []
    found   = False
    for line in lines:
        try:
            r = json.loads(line)
            if r["id"] == req_id:
                r["status"]     = new_status
                r["resolved_at"] = datetime.now(timezone.utc).isoformat()
                found = True
            updated.append(json.dumps(r))
        except json.JSONDecodeError:
            updated.append(line)
    if not found:
        return jsonify({"error": "Request not found"}), 404
    REQ_FILE.write_text("\n".join(updated) + "\n", encoding="utf-8")
    _audit(f"REQUEST_{new_status.upper()}", req_id)
    return jsonify({"status": new_status})

# ── Audit Log ─────────────────────────────────────────────────────────────────

@app.route("/api/audit", methods=["GET"])
def get_audit():
    if not AUDIT_FILE.exists():
        return jsonify([])
    records = []
    for line in AUDIT_FILE.read_text(encoding="utf-8").strip().splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return jsonify(list(reversed(records[-200:])))

# ── Bulk Offboarding ──────────────────────────────────────────────────────────

@app.route("/api/offboard/preview", methods=["POST"])
def offboard_preview():
    """
    POST multipart/form-data with CSV file.
    Returns parsed rows for review before execution.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f    = request.files["file"]
    text = f.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if "email" not in (reader.fieldnames or []):
        return jsonify({"error": "CSV must have an 'email' column"}), 400
    rows = []
    for i, row in enumerate(reader):
        if i >= 500:
            break
        try:
            email = _safe_email(row.get("email", ""))
            rows.append({
                "email":       email,
                "employee_id": _safe_str(row.get("employee_id", ""), 50),
                "reason":      _safe_str(row.get("reason", "Offboarding"), 200),
                "notes":       _safe_str(row.get("notes", ""), 300),
            })
        except ValueError:
            pass
    return jsonify({"count": len(rows), "rows": rows})

@app.route("/api/offboard/execute", methods=["POST"])
def offboard_execute():
    """
    POST body: { "users": [...rows from preview...], "actions": ["okta_suspend", "ad_disable", "remove_apps"] }
    Executes offboarding for each user and returns per-user results.
    """
    body    = request.get_json(force=True) or {}
    users   = body.get("users", [])
    actions = set(body.get("actions", ["okta_suspend", "ad_disable"]))
    results = []

    for u in users[:500]:
        email  = u.get("email", "")
        result = {"email": email, "steps": [], "status": "success"}
        try:
            email = _safe_email(email)
        except ValueError:
            result["status"] = "error"
            result["steps"].append({"action": "validate", "status": "error", "detail": "Invalid email"})
            results.append(result)
            continue

        # Okta suspend
        if "okta_suspend" in actions and OKTA_DOMAIN and OKTA_API_TOKEN:
            try:
                okta_users = _okta_get("users", params={"filter": f'profile.email eq "{email}"'})
                if okta_users:
                    uid = okta_users[0]["id"]
                    requests.post(
                        f"https://{OKTA_DOMAIN}/api/v1/users/{uid}/lifecycle/suspend",
                        headers=_okta_headers(), timeout=10
                    ).raise_for_status()
                    result["steps"].append({"action": "okta_suspend", "status": "ok"})
                else:
                    result["steps"].append({"action": "okta_suspend", "status": "not_found"})
            except Exception as exc:
                result["steps"].append({"action": "okta_suspend", "status": "error", "detail": str(exc)[:100]})
                result["status"] = "partial"

        # AD disable
        if "ad_disable" in actions and AD_SERVER:
            try:
                conn = _ad_connect()
                base = ",".join(f"DC={p}" for p in AD_DOMAIN.split("."))
                conn.search(base, f"(mail={email})", attributes=["userAccountControl"])
                if conn.entries:
                    dn  = conn.entries[0].entry_dn
                    uac = int(conn.entries[0].userAccountControl.value)
                    conn.modify(dn, {"userAccountControl": [("MODIFY_REPLACE", [uac | 0x2])]})
                    result["steps"].append({"action": "ad_disable", "status": "ok"})
                else:
                    result["steps"].append({"action": "ad_disable", "status": "not_found"})
            except Exception as exc:
                result["steps"].append({"action": "ad_disable", "status": "error", "detail": str(exc)[:100]})
                result["status"] = "partial"

        # Audit
        _audit("OFFBOARD", email, detail=f"Actions: {', '.join(actions)} | Reason: {u.get('reason', '')[:100]}")

        # Persist offboarded record
        record = {
            "email":          email,
            "offboarded_at":  datetime.now(timezone.utc).isoformat(),
            "reason":         _safe_str(u.get("reason", ""), 200),
            "steps":          result["steps"],
        }
        with open(OFFBOARD_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

        results.append(result)

    success = sum(1 for r in results if r["status"] == "success")
    return jsonify({
        "total":   len(results),
        "success": success,
        "partial": sum(1 for r in results if r["status"] == "partial"),
        "error":   sum(1 for r in results if r["status"] == "error"),
        "results": results,
    })

@app.route("/api/offboard/history", methods=["GET"])
def offboard_history():
    if not OFFBOARD_FILE.exists():
        return jsonify([])
    records = []
    for line in OFFBOARD_FILE.read_text(encoding="utf-8").strip().splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return jsonify(list(reversed(records[-100:])))

# ── Health check ──────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status":       "ok",
        "okta":         bool(OKTA_DOMAIN and OKTA_API_TOKEN),
        "ad":           bool(AD_SERVER),
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    })

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("AccessOps starting on http://localhost:%d", PORT)
    log.info("Okta configured: %s", bool(OKTA_DOMAIN and OKTA_API_TOKEN))
    log.info("AD configured  : %s", bool(AD_SERVER))
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
