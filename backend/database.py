"""
Database setup and configuration for SQLite.
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = "redteam.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize the database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Scans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                timestamp TEXT NOT NULL,
                results TEXT,
                progress INTEGER DEFAULT 0,
                error TEXT
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                exploit TEXT,
                payload TEXT,
                uid TEXT,
                pid INTEGER,
                opened TEXT NOT NULL,
                closed TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL,
                report_type TEXT DEFAULT 'general'
            )
        """)
        
        # Vulnerabilities table (cached CVE data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT UNIQUE NOT NULL,
                description TEXT,
                severity TEXT,
                cvss_score REAL,
                published_date TEXT,
                affected_products TEXT,
                exploit_available INTEGER DEFAULT 0
            )
        """)
        
        # Exploit modules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exploit_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                module_type TEXT NOT NULL,
                rank TEXT,
                disclosure_date TEXT,
                platform TEXT,
                arch TEXT,
                author TEXT,
                description TEXT
            )
        """)
        
        # Payload modules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payload_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                module_type TEXT NOT NULL,
                platform TEXT,
                arch TEXT,
                description TEXT
            )
        """)
        
        conn.commit()


# Scan operations
def create_scan(target: str, scan_type: str) -> int:
    """Create a new scan record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO scans (target, scan_type, status, timestamp) VALUES (?, ?, ?, ?)",
            (target, scan_type, "pending", timestamp)
        )
        conn.commit()
        return cursor.lastrowid


def update_scan_status(scan_id: int, status: str, progress: int = 0, results: Optional[str] = None, error: Optional[str] = None):
    """Update scan status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if results:
            cursor.execute(
                "UPDATE scans SET status = ?, progress = ?, results = ?, error = ? WHERE id = ?",
                (status, progress, results, error, scan_id)
            )
        else:
            cursor.execute(
                "UPDATE scans SET status = ?, progress = ?, error = ? WHERE id = ?",
                (status, progress, error, scan_id)
            )
        conn.commit()


def get_scan(scan_id: int) -> Optional[Dict[str, Any]]:
    """Get scan by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_scans() -> List[Dict[str, Any]]:
    """Get all scans."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]


# Session operations
def create_session(target: str, exploit: str = None, payload: str = None, uid: str = None, pid: int = None) -> int:
    """Create a new session record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        opened = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO sessions (target, exploit, payload, uid, pid, opened, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (target, exploit, payload, uid, pid, opened, "active")
        )
        conn.commit()
        return cursor.lastrowid


def update_session(session_id: int, uid: str = None, pid: int = None, status: str = None):
    """Update session details."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if uid and pid:
            cursor.execute(
                "UPDATE sessions SET uid = ?, pid = ?, status = ? WHERE id = ?",
                (uid, pid, status, session_id)
            )
        elif status:
            cursor.execute(
                "UPDATE sessions SET status = ? WHERE id = ?",
                (status, session_id)
            )
        conn.commit()


def get_session(session_id: int) -> Optional[Dict[str, Any]]:
    """Get session by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all sessions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY opened DESC")
        return [dict(row) for row in cursor.fetchall()]


def close_session(session_id: int):
    """Close a session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        closed = datetime.utcnow().isoformat()
        cursor.execute(
            "UPDATE sessions SET status = ?, closed = ? WHERE id = ?",
            ("closed", closed, session_id)
        )
        conn.commit()


# Report operations
def create_report(title: str, data: str, report_type: str = "general") -> int:
    """Create a new report."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO reports (title, timestamp, data, report_type) VALUES (?, ?, ?, ?)",
            (title, timestamp, data, report_type)
        )
        conn.commit()
        return cursor.lastrowid


def get_report(report_id: int) -> Optional[Dict[str, Any]]:
    """Get report by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_reports() -> List[Dict[str, Any]]:
    """Get all reports."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]


# Vulnerability operations
def add_vulnerability(cve_id: str, description: str, severity: str, cvss_score: float, 
                      published_date: str, affected_products: str, exploit_available: bool = False) -> int:
    """Add a vulnerability to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO vulnerabilities 
            (cve_id, description, severity, cvss_score, published_date, affected_products, exploit_available) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cve_id, description, severity, cvss_score, published_date, affected_products, 1 if exploit_available else 0))
        conn.commit()
        return cursor.lastrowid


def get_vulnerabilities(severity: str = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Get vulnerabilities with optional severity filter."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if severity:
            cursor.execute(
                "SELECT * FROM vulnerabilities WHERE severity = ? ORDER BY cvss_score DESC LIMIT ?",
                (severity, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM vulnerabilities ORDER BY cvss_score DESC LIMIT ?",
                (limit,)
            )
        return [dict(row) for row in cursor.fetchall()]


def get_vulnerability(cve_id: str) -> Optional[Dict[str, Any]]:
    """Get vulnerability by CVE ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vulnerabilities WHERE cve_id = ?", (cve_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


# Exploit module operations
def add_exploit_module(name: str, full_name: str, module_type: str, rank: str = None,
                       disclosure_date: str = None, platform: str = None, arch: str = None,
                       author: str = None, description: str = None) -> int:
    """Add an exploit module to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO exploit_modules 
            (name, full_name, module_type, rank, disclosure_date, platform, arch, author, description) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, full_name, module_type, rank, disclosure_date, platform, arch, author, description))
        conn.commit()
        return cursor.lastrowid


def get_exploit_modules(platform: str = None, module_type: str = None) -> List[Dict[str, Any]]:
    """Get exploit modules with optional filters."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM exploit_modules WHERE 1=1"
        params = []
        if platform:
            query += " AND platform LIKE ?"
            params.append(f"%{platform}%")
        if module_type:
            query += " AND module_type = ?"
            params.append(module_type)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


# Payload module operations
def add_payload_module(name: str, full_name: str, module_type: str, platform: str = None,
                       arch: str = None, description: str = None) -> int:
    """Add a payload module to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO payload_modules 
            (name, full_name, module_type, platform, arch, description) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, full_name, module_type, platform, arch, description))
        conn.commit()
        return cursor.lastrowid


def get_payload_modules(platform: str = None, module_type: str = None) -> List[Dict[str, Any]]:
    """Get payload modules with optional filters."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM payload_modules WHERE 1=1"
        params = []
        if platform:
            query += " AND platform LIKE ?"
            params.append(f"%{platform}%")
        if module_type:
            query += " AND module_type = ?"
            params.append(module_type)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


# Dashboard statistics
def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total scans
        cursor.execute("SELECT COUNT(*) as count FROM scans")
        total_scans = cursor.fetchone()["count"]
        
        # Completed scans
        cursor.execute("SELECT COUNT(*) as count FROM scans WHERE status = 'completed'")
        completed_scans = cursor.fetchone()["count"]
        
        # Active sessions
        cursor.execute("SELECT COUNT(*) as count FROM sessions WHERE status = 'active'")
        active_sessions = cursor.fetchone()["count"]
        
        # Total reports
        cursor.execute("SELECT COUNT(*) as count FROM reports")
        total_reports = cursor.fetchone()["count"]
        
        # Vulnerabilities count
        cursor.execute("SELECT COUNT(*) as count FROM vulnerabilities")
        total_vulnerabilities = cursor.fetchone()["count"]
        
        # High severity vulnerabilities
        cursor.execute("SELECT COUNT(*) as count FROM vulnerabilities WHERE severity = 'HIGH'")
        high_severity = cursor.fetchone()["count"]
        
        # Recent scans
        cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC LIMIT 5")
        recent_scans = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_scans": total_scans,
            "completed_scans": completed_scans,
            "active_sessions": active_sessions,
            "total_reports": total_reports,
            "total_vulnerabilities": total_vulnerabilities,
            "high_severity_vulnerabilities": high_severity,
            "recent_scans": recent_scans
        }


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
