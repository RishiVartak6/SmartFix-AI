"""
SmartFix AI — Proper Windows Application (PyQt6)
Main Window: Dashboard + System Tray + Live Monitor + Alert Popups
"""
import sys
import os
import threading
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List


ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QDialog, QProgressBar,
    QSystemTrayIcon, QMenu, QListWidget, QListWidgetItem, QStackedWidget,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QSize, QPoint
)
from PyQt6.QtGui import (
    QColor, QFont, QIcon, QPainter, QPen, QBrush,
    QPixmap, QLinearGradient, QPalette, QAction, QFontDatabase
)


from monitor.error_catalog import ERROR_CATALOG, CATALOG_LIST
from monitor.monitor import BackgroundMonitor
from monitor.repair_engine import execute_repair

from monitor.history import get_history, get_stats, clear_history, log_repair, log_ignore, log_detection, get_stats, clear_history
from monitor.network_diag import run_full_diagnostics
from monitor.system_report import save_report, generate_html_report
import webbrowser

from monitor.ai_dialog import AIAssistantDialog
from monitor.demo_mode import DemoController, DEMO_SCENARIOS, DEMO_LIST

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("smartfix.app")


BG_MAIN    = "#0E0F14"
BG_SIDEBAR = "#09090D"
BG_CARD    = "#13141A"
BG_CARD2   = "#1A1B23"
BORDER     = "#1E2030"
BORDER2    = "#2A2D40"
ACCENT     = "#5B6EF5"
GREEN      = "#34D399"
RED        = "#F87171"
ORANGE     = "#FB923C"
YELLOW     = "#FBBF24"
TEXT1      = "#E8EAF0"
TEXT2      = "#8B8FA8"
TEXT3      = "#4A4D62"

SEV_COLORS = {"CRITICAL": RED, "HIGH": ORANGE, "MEDIUM": YELLOW, "LOW": ACCENT}
SEV_ICONS  = {"CRITICAL": "C", "HIGH": "H", "MEDIUM": "M", "LOW": "L"}

STYLESHEET = f"""
QWidget {{
    background-color: {BG_MAIN};
    color: {TEXT1};
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER2};
    border-radius: 2px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}
QTableWidget {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    gridline-color: {BORDER};
    outline: 0;
}}
QTableWidget::item {{ padding: 8px 16px; border-bottom: 1px solid {BORDER}; }}
QTableWidget::item:selected {{ background: {ACCENT}15; color: {TEXT1}; }}
QHeaderView::section {{
    background: {BG_CARD};
    color: {TEXT3};
    padding: 8px 16px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 600;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}
QTextEdit {{
    background: {BG_SIDEBAR};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 10px 12px;
    color: {TEXT2};
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 11px;
    line-height: 1.5;
}}
"""



class RepairWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, repair_id: str):
        super().__init__()
        self.repair_id = repair_id

    def run(self):
        result = execute_repair(self.repair_id)
        self.finished.emit(result)



class AlertBridge(QThread):
    """Bridges monitor alerts from background threads to Qt signals."""
    alert_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._queue = []
        self._lock = threading.Lock()
        self._monitor = None

    def set_monitor(self, monitor):
        self._monitor = monitor

    def on_alert(self, error_info: dict):
        self.alert_received.emit(error_info)



class StatCard(QFrame):
    def __init__(self, title: str, value: str, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"""
            color: {TEXT1};
            font-size: 28px;
            font-weight: 700;
            background: transparent;
            border: none;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(self.value_lbl)

        row = QHBoxLayout()
        row.setSpacing(6)

        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(f"background: {color}; border-radius: 3px; border: none;")
        row.addWidget(dot)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 11px; font-weight: 500; background: transparent; border: none;")
        row.addWidget(title_lbl)
        row.addStretch()
        layout.addLayout(row)

    def set_value(self, v: str):
        self.value_lbl.setText(v)



class AlertItem(QFrame):
    def __init__(self, error_info: dict, on_fix, on_ignore, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        sev   = error_info.get("severity", "HIGH")
        color = SEV_COLORS.get(sev, ORANGE)

        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 2px solid {color};
                border-radius: 4px;
            }}
            QFrame:hover {{ border-color: {BORDER2}; border-left: 2px solid {color}; }}
        """)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 12, 12, 12)
        outer.setSpacing(14)

        # Severity indicator dot
        dot_col = QVBoxLayout()
        dot_col.setAlignment(Qt.AlignmentFlag.AlignTop)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {color}; border-radius: 4px; border: none; margin-top: 4px;")
        dot_col.addWidget(dot)
        outer.addLayout(dot_col)

        # Content
        mid = QVBoxLayout()
        mid.setSpacing(3)

        name_lbl = QLabel(error_info.get("name", "Unknown Error"))
        name_lbl.setStyleSheet(f"color: {TEXT1}; font-weight: 600; font-size: 13px; background: transparent; border: none;")
        mid.addWidget(name_lbl)

        desc_text = error_info.get("description", "")
        if len(desc_text) > 90:
            desc_text = desc_text[:90] + "..."
        desc = QLabel(desc_text)
        desc.setStyleSheet(f"color: {TEXT2}; font-size: 11px; background: transparent; border: none;")
        desc.setWordWrap(True)
        mid.addWidget(desc)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)

        sev_lbl = QLabel(sev)
        sev_lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 600; background: transparent; border: none;")
        meta_row.addWidget(sev_lbl)

        sep = QLabel("|")
        sep.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent; border: none;")
        meta_row.addWidget(sep)

        cat_lbl = QLabel(error_info.get("category", "System"))
        cat_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent; border: none;")
        meta_row.addWidget(cat_lbl)

        ts = error_info.get("detected_at", "")[:16].replace("T", " ")
        if ts:
            sep2 = QLabel("|")
            sep2.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent; border: none;")
            meta_row.addWidget(sep2)
            time_lbl = QLabel(ts)
            time_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent; border: none;")
            meta_row.addWidget(time_lbl)

        meta_row.addStretch()
        mid.addLayout(meta_row)
        outer.addLayout(mid, 1)

        # Action buttons
        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        btn_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        fix_btn = QPushButton("Fix")
        fix_btn.setFixedSize(64, 28)
        fix_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: #6D7EF7; }}
            QPushButton:pressed {{ background: #4A5BE0; }}
        """)
        fix_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fix_btn.clicked.connect(lambda: on_fix(error_info, self))
        btn_col.addWidget(fix_btn)

        ign_btn = QPushButton("Ignore")
        ign_btn.setFixedSize(64, 28)
        ign_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT3};
                border: 1px solid {BORDER};
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover {{ color: {TEXT2}; border-color: {BORDER2}; }}
        """)
        ign_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ign_btn.clicked.connect(lambda: on_ignore(self))
        btn_col.addWidget(ign_btn)

        outer.addLayout(btn_col)



class RepairDialog(QDialog):
    def __init__(self, error_info: dict, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        self.repair_id  = error_info.get("repair_id", "")
        self.worker     = None

        self.setWindowTitle("SmartFix — Repairing")
        self.setFixedSize(480, 320)
        self.setStyleSheet(f"""
            QDialog {{ background: {BG_CARD}; }}
            QLabel  {{ background: transparent; border: none; }}
        """)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self._build_ui()
        self._start_repair()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        top = QFrame()
        top.setFixedHeight(52)
        top.setStyleSheet(f"background: {BG_SIDEBAR}; border-bottom: 1px solid {BORDER};")
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(20, 0, 20, 0)

        brand = QLabel("SmartFix")
        brand.setStyleSheet(f"color: {TEXT3}; font-size: 11px; font-weight: 600; letter-spacing: 0.06em;")
        top_l.addWidget(brand)
        top_l.addStretch()

        self.title_lbl = QLabel("Repairing...")
        self.title_lbl.setStyleSheet(f"color: {TEXT2}; font-size: 11px;")
        top_l.addWidget(self.title_lbl)
        layout.addWidget(top)

        # Progress bar (below top bar)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(2)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: {BORDER}; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT}; }}
        """)
        layout.addWidget(self.progress)

        # Body
        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(24, 20, 24, 20)
        body_l.setSpacing(12)

        err_name = QLabel(self.error_info.get("name", ""))
        err_name.setStyleSheet(f"color: {TEXT1}; font-size: 15px; font-weight: 600;")
        body_l.addWidget(err_name)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Running repair...")
        body_l.addWidget(self.log_box)

        self.result_lbl = QLabel()
        self.result_lbl.setWordWrap(True)
        self.result_lbl.setVisible(False)
        body_l.addWidget(self.result_lbl)

        self.close_btn = QPushButton("Done")
        self.close_btn.setVisible(False)
        self.close_btn.setFixedHeight(36)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: white; border: none;
                border-radius: 4px; font-weight: 600; font-size: 12px;
            }}
            QPushButton:hover {{ background: #6D7EF7; }}
        """)
        self.close_btn.clicked.connect(self.accept)
        body_l.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(body)

    def _start_repair(self):
        self.log_box.append(f"Starting: {self.repair_id}")
        self.worker = RepairWorker(self.repair_id)
        self.worker.finished.connect(self._on_repair_done)
        self.worker.start()

    def _on_repair_done(self, result: dict):
        success = result.get("success", False)
        output  = result.get("output", "")[:600]
        elapsed = result.get("elapsed_seconds", 0)

        self.log_box.append(f"\n{output}\n\nCompleted in {elapsed}s")
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: {BORDER}; border: none; }}
            QProgressBar::chunk {{ background: {'#34D399' if success else RED}; }}
        """)

        log_repair(self.error_info, result)

        if success:
            self.title_lbl.setText("Repair complete")
            self.result_lbl.setText("The issue has been resolved.")
            self.result_lbl.setStyleSheet(f"color: {GREEN}; font-size: 12px; font-weight: 600;")
        else:
            self.title_lbl.setText("Repair encountered issues")
            self.result_lbl.setText("Some steps may need Administrator rights.")
            self.result_lbl.setStyleSheet(f"color: {ORANGE}; font-size: 12px; font-weight: 600;")

        self.result_lbl.setVisible(True)
        self.close_btn.setVisible(True)



class AlertPopup(QDialog):
    """Minimal notification toast — bottom right. CRITICAL only. One at a time."""

    def __init__(self, error_info: dict, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        self._countdown = 25

        self.setFixedWidth(340)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui()
        self._position()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)

        card = QFrame()
        card.setObjectName("toast")
        card.setStyleSheet(f"""
            QFrame#toast {{
                background: {BG_CARD};
                border: 1px solid {BORDER2};
                border-radius: 8px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 140))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        # Top strip
        strip = QFrame()
        strip.setFixedHeight(3)
        strip.setStyleSheet(f"background: {RED}; border-radius: 8px 8px 0 0; border: none;")
        cl.addWidget(strip)

        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(16, 12, 16, 12)
        body_l.setSpacing(8)

        # Header
        hdr = QHBoxLayout()
        app_lbl = QLabel("SMARTFIX")
        app_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 9px; font-weight: 700; letter-spacing: 0.12em; background: transparent;")
        hdr.addWidget(app_lbl)
        hdr.addStretch()
        time_lbl = QLabel(datetime.now().strftime("%H:%M"))
        time_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent;")
        hdr.addWidget(time_lbl)
        x_btn = QPushButton("x")
        x_btn.setFixedSize(16, 16)
        x_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        x_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; color: {TEXT3}; font-size: 10px; margin-left:6px; }} QPushButton:hover {{ color: {TEXT1}; }}")
        x_btn.clicked.connect(self._ignore)
        hdr.addWidget(x_btn)
        body_l.addLayout(hdr)

        # Error name
        name_lbl = QLabel(self.error_info.get("name", "Critical Error"))
        name_lbl.setStyleSheet(f"color: {TEXT1}; font-size: 13px; font-weight: 600; background: transparent;")
        name_lbl.setWordWrap(True)
        body_l.addWidget(name_lbl)

        cat_lbl = QLabel(f"Critical  ·  {self.error_info.get('category', 'System')}")
        cat_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent;")
        body_l.addWidget(cat_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        fix_btn = QPushButton("Fix Now")
        fix_btn.setFixedHeight(30)
        fix_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: white; border: none;
                border-radius: 4px; padding: 0 16px;
                font-weight: 600; font-size: 11px;
            }}
            QPushButton:hover {{ background: #6D7EF7; }}
        """)
        fix_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fix_btn.clicked.connect(self._fix)
        btn_row.addWidget(fix_btn)

        ign_btn = QPushButton("Dismiss")
        ign_btn.setFixedHeight(30)
        ign_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT3};
                border: 1px solid {BORDER}; border-radius: 4px;
                padding: 0 12px; font-size: 11px;
            }}
            QPushButton:hover {{ color: {TEXT2}; }}
        """)
        ign_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ign_btn.clicked.connect(self._ignore)
        btn_row.addWidget(ign_btn)
        btn_row.addStretch()
        body_l.addLayout(btn_row)
        cl.addWidget(body)

        # Countdown bar
        self.countdown_bar = QProgressBar()
        self.countdown_bar.setRange(0, 25)
        self.countdown_bar.setValue(25)
        self.countdown_bar.setFixedHeight(2)
        self.countdown_bar.setTextVisible(False)
        self.countdown_bar.setStyleSheet(f"""
            QProgressBar {{ background: transparent; border: none; }}
            QProgressBar::chunk {{ background: {BORDER2}; }}
        """)
        cl.addWidget(self.countdown_bar)

    def _position(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        tx = screen.right() - self.width() - 16
        ty = screen.bottom() - self.height() - 16
        self.move(screen.right() + 40, ty)
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(280)
        self.animation.setStartValue(QPoint(screen.right() + 40, ty))
        self.animation.setEndValue(QPoint(tx, ty))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def _tick(self):
        self._countdown -= 1
        self.countdown_bar.setValue(self._countdown)
        if self._countdown <= 0:
            self._ignore()

    def _fix(self):
        self._timer.stop()
        self.hide()
        if self.error_info.get("repair_id") == "unknown_error":
            dlg = AIAssistantDialog(self.error_info)
        else:
            dlg = RepairDialog(self.error_info)
        dlg.exec()
        self.close()

    def _ignore(self):
        self._timer.stop()
        self.close()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        
        hdr = QHBoxLayout()
        brand = QLabel("🛡 SmartFix AI")
        brand.setStyleSheet(f"color: {ACCENT}; font-weight: bold; font-size: 15px;")
        hdr.addWidget(brand)
        hdr.addStretch()
        layout.addLayout(hdr)

        
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {BORDER};")
        layout.addWidget(div)

        
        title_row = QHBoxLayout()
        self.status_icon = QLabel("⚙️")
        self.status_icon.setStyleSheet("font-size: 28px;")
        title_row.addWidget(self.status_icon)

        title_col = QVBoxLayout()
        self.title_lbl = QLabel("Repair in Progress…")
        self.title_lbl.setStyleSheet(f"color: {TEXT1}; font-size: 16px; font-weight: bold;")
        title_col.addWidget(self.title_lbl)

        error_lbl = QLabel(self.error_info.get("name", ""))
        error_lbl.setStyleSheet(f"color: {TEXT2}; font-size: 12px;")
        title_col.addWidget(error_lbl)
        title_row.addLayout(title_col)
        layout.addLayout(title_row)

        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background: {BORDER};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {ACCENT};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress)

        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(100)
        self.log_box.setPlaceholderText("Running repair scripts…")
        layout.addWidget(self.log_box)

        
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet(f"background: {BG_CARD2}; border-radius: 8px; border: 1px solid {BORDER};")
        self.result_frame.setVisible(False)
        res_layout = QHBoxLayout(self.result_frame)
        self.result_icon = QLabel("✅")
        self.result_icon.setStyleSheet("font-size: 22px;")
        res_layout.addWidget(self.result_icon)
        self.result_lbl = QLabel("Repair successful!")
        self.result_lbl.setStyleSheet(f"color: {GREEN}; font-weight: bold; font-size: 13px;")
        res_layout.addWidget(self.result_lbl)
        layout.addWidget(self.result_frame)

        
        self.close_btn = QPushButton("Close")
        self.close_btn.setVisible(False)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: #3D7ADB; }}
        """)
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _start_repair(self):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting repair: {self.repair_id}")
        self.worker = RepairWorker(self.repair_id)
        self.worker.finished.connect(self._on_repair_done)
        self.worker.start()

    def _on_repair_done(self, result: dict):
        success = result.get("success", False)
        output = result.get("output", "")[:800]
        elapsed = result.get("elapsed_seconds", 0)

        self.log_box.append(f"\n[Output]\n{output}")
        self.log_box.append(f"\n[Elapsed: {elapsed}s]")

        
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        log_repair(self.error_info, result)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background: {BORDER};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {'#00D26A' if success else RED};
                border-radius: 3px;
            }}
        """)

        
        self.result_frame.setVisible(True)
        if success:
            self.status_icon.setText("✅")
            self.title_lbl.setText("Repair Successful!")
            self.title_lbl.setStyleSheet(f"color: {GREEN}; font-size: 16px; font-weight: bold;")
            self.result_icon.setText("✅")
            self.result_lbl.setText("The issue has been resolved successfully.")
            self.result_lbl.setStyleSheet(f"color: {GREEN}; font-weight: bold; font-size: 13px;")
        else:
            self.status_icon.setText("❌")
            self.title_lbl.setText("Repair Encountered Issues")
            self.title_lbl.setStyleSheet(f"color: {RED}; font-size: 16px; font-weight: bold;")
            self.result_icon.setText("⚠️")
            self.result_lbl.setText("Some steps may require Administrator rights.")
            self.result_lbl.setStyleSheet(f"color: {ORANGE}; font-weight: bold; font-size: 13px;")

        self.close_btn.setVisible(True)



class AlertPopup(QDialog):
    """Clean Windows-11 style toast notification — bottom right corner. CRITICAL only."""

    def __init__(self, error_info: dict, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        self._countdown = 30
        self._color = RED

        self.setFixedWidth(380)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self._position()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        card = QFrame()
        card.setObjectName("toast")
        card.setStyleSheet(f"""
            QFrame#toast {{
                background: {BG_CARD};
                border-radius: 14px;
                border: 1px solid {BORDER};
                border-top: 2px solid {RED};
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        outer.addWidget(card)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(10)

        # Header row
        hdr = QHBoxLayout()
        app_lbl = QLabel("SmartFix AI")
        app_lbl.setStyleSheet(f"color: {ACCENT}; font-size: 10px; font-weight: 700; letter-spacing: 0.06em; background: transparent;")
        hdr.addWidget(app_lbl)
        hdr.addStretch()

        time_lbl = QLabel(datetime.now().strftime("%H:%M"))
        time_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent;")
        hdr.addWidget(time_lbl)

        x_btn = QPushButton("✕")
        x_btn.setFixedSize(18, 18)
        x_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        x_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; color: {TEXT3}; font-size: 11px; margin-left: 8px; }} QPushButton:hover {{ color: {RED}; }}")
        x_btn.clicked.connect(self._ignore)
        hdr.addWidget(x_btn)
        cl.addLayout(hdr)

        # Thin separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        cl.addWidget(sep)

        # Error row — icon + title stacked
        err_row = QHBoxLayout()
        err_row.setSpacing(12)

        # Red exclamation circle
        icon_lbl = QLabel("⚠")
        icon_lbl.setFixedWidth(36)
        icon_lbl.setFixedHeight(36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 18px; color: {RED}; background: {RED}18; border-radius: 18px;")
        err_row.addWidget(icon_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        name = self.error_info.get("name", "Unknown Error")
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {TEXT1}; font-size: 13px; font-weight: 600; background: transparent;")
        name_lbl.setWordWrap(True)
        title_col.addWidget(name_lbl)

        cat = self.error_info.get("category", "System")
        cat_lbl = QLabel(f"Critical  ·  {cat}")
        cat_lbl.setStyleSheet(f"color: {RED}; font-size: 10px; font-weight: 600; background: transparent;")
        title_col.addWidget(cat_lbl)
        err_row.addLayout(title_col)
        cl.addLayout(err_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        fix_btn = QPushButton("Fix Now")
        fix_btn.setFixedHeight(34)
        fix_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: #818CF8; }}
            QPushButton:pressed {{ background: #4F46E5; }}
        """)
        fix_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fix_btn.clicked.connect(self._fix)
        btn_row.addWidget(fix_btn)

        ign_btn = QPushButton("Dismiss")
        ign_btn.setFixedHeight(34)
        ign_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT2};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: {BG_CARD2}; color: {TEXT1}; }}
        """)
        ign_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ign_btn.clicked.connect(self._ignore)
        btn_row.addWidget(ign_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

        # Progress bar countdown
        self.countdown_bar = QProgressBar()
        self.countdown_bar.setRange(0, 30)
        self.countdown_bar.setValue(30)
        self.countdown_bar.setFixedHeight(2)
        self.countdown_bar.setTextVisible(False)
        self.countdown_bar.setStyleSheet(f"""
            QProgressBar {{ background: {BORDER}20; border-radius: 1px; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT}; border-radius: 1px; }}
        """)
        cl.addWidget(self.countdown_bar)

    def _position(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        target_x = screen.right() - self.width() - 20
        target_y = screen.bottom() - self.height() - 20
        self.move(screen.right() + 50, target_y)

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(350)
        self.animation.setStartValue(QPoint(screen.right() + 50, target_y))
        self.animation.setEndValue(QPoint(target_x, target_y))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def _tick(self):
        self._countdown -= 1
        self.countdown_bar.setValue(self._countdown)
        if self._countdown <= 0:
            self._ignore()

    def _fix(self):
        self._timer.stop()
        self.hide()
        if self.error_info.get("repair_id") == "unknown_error":
            dlg = AIAssistantDialog(self.error_info)
        else:
            dlg = RepairDialog(self.error_info)
        dlg.exec()
        self.close()

    def _ignore(self):
        self._timer.stop()
        self.close()



class MainWindow(QMainWindow):
    _alert_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartFix AI — Windows Error Monitor")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(STYLESHEET)

        self._alerts: List[dict] = []
        self._alert_count = 0
        self._fixed_count = 0
        self._ignored_count = 0
        self._monitor = None
        self._demo = None
        self._active_popups: List[AlertPopup] = []
        # Track IDs of alerts currently showing in the alerts list (prevents duplicate entries)
        self._active_alert_ids: set = set()
        # Prevent popup spam — only 1 popup at a time
        self._popup_visible: bool = False

        
        self._alert_signal.connect(self._show_alert)

        self._build_ui()
        self._setup_tray()
        self._start_monitor()
        self._start_metric_timer()

    

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        
        sidebar = self._make_sidebar()
        root.addWidget(sidebar)

        
        self.stack = QStackedWidget()
        self.stack.addWidget(self._make_dashboard())   
        self.stack.addWidget(self._make_alerts_page()) 
        self.stack.addWidget(self._make_catalog_page()) 
        self.stack.addWidget(self._make_demo_page())   
        self.stack.addWidget(self._make_history_page()) 
        self.stack.addWidget(self._make_network_page()) 
        self.stack.addWidget(self._make_report_page()) 
        root.addWidget(self.stack, 1)

    def _make_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {BG_SIDEBAR};
                border-right: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Brand area
        logo_frame = QFrame()
        logo_frame.setFixedHeight(60)
        logo_frame.setStyleSheet(f"background: {BG_SIDEBAR}; border-bottom: 1px solid {BORDER};")
        logo_l = QHBoxLayout(logo_frame)
        logo_l.setContentsMargins(16, 0, 16, 0)

        icon_box = QLabel("SF")
        icon_box.setFixedSize(28, 28)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setStyleSheet(f"""
            background: {ACCENT};
            color: white;
            border-radius: 6px;
            border: none;
            font-size: 11px;
            font-weight: 700;
        """)
        logo_l.addWidget(icon_box)

        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand_lbl = QLabel("SmartFix")
        brand_lbl.setStyleSheet(f"color: {TEXT1}; font-size: 13px; font-weight: 600; background: transparent; border: none;")
        brand_col.addWidget(brand_lbl)
        sub_lbl = QLabel("Error Monitor")
        sub_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent; border: none;")
        brand_col.addWidget(sub_lbl)
        logo_l.addLayout(brand_col)
        logo_l.addStretch()
        layout.addWidget(logo_frame)

        # Status pill
        self.status_frame = QFrame()
        self.status_frame.setFixedHeight(36)
        self.status_frame.setStyleSheet(f"background: {BG_SIDEBAR}; border-bottom: 1px solid {BORDER};")
        status_l = QHBoxLayout(self.status_frame)
        status_l.setContentsMargins(16, 0, 16, 0)
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(6, 6)
        self.status_dot.setStyleSheet(f"background: {GREEN}; border-radius: 3px; border: none;")
        status_l.addWidget(self.status_dot)
        self.status_lbl = QLabel("Monitoring")
        self.status_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 10px; background: transparent; border: none; margin-left: 6px;")
        status_l.addWidget(self.status_lbl)
        status_l.addStretch()
        layout.addWidget(self.status_frame)

        # Nav section label
        nav_section = QLabel("NAVIGATION")
        nav_section.setStyleSheet(f"color: {TEXT3}; font-size: 9px; font-weight: 700; letter-spacing: 0.1em; background: transparent; border: none; padding: 14px 16px 6px 16px;")
        layout.addWidget(nav_section)

        nav_items = [
            ("Dashboard",     0),
            ("Active Alerts", 1),
            ("Error Catalog", 2),
            ("Demo Mode",     3),
            ("History",       4),
            ("Network",       5),
            ("System Report", 6),
        ]

        nav_wrap = QWidget()
        nav_wrap.setStyleSheet("background: transparent;")
        nav_l = QVBoxLayout(nav_wrap)
        nav_l.setContentsMargins(8, 0, 8, 0)
        nav_l.setSpacing(1)

        self._nav_btns = []
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setFixedHeight(34)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT2};
                    border: none;
                    text-align: left;
                    padding-left: 12px;
                    font-size: 12px;
                    border-radius: 4px;
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background: {BG_CARD};
                    color: {TEXT1};
                }}
                QPushButton:checked {{
                    background: {BG_CARD};
                    color: {TEXT1};
                    font-weight: 500;
                }}
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx, b=btn: self._nav(i, b))
            self._nav_btns.append(btn)
            nav_l.addWidget(btn)

        layout.addWidget(nav_wrap)
        self._nav_btns[0].setChecked(True)
        layout.addStretch()

        ver_lbl = QLabel("v1.0")
        ver_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 9px; background: transparent; border: none; padding: 10px 16px;")
        layout.addWidget(ver_lbl)

        return sidebar

    def _nav(self, idx: int, btn: QPushButton):
        for b in self._nav_btns:
            b.setChecked(False)
        btn.setChecked(True)
        self.stack.setCurrentIndex(idx)

    def _make_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        
        title_row = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet(f"color: {TEXT1}; font-size: 26px; font-weight: 700; letter-spacing: -0.5px;")
        title_row.addWidget(title)
        title_row.addStretch()

        self.last_scan_lbl = QLabel("Scanning…")
        self.last_scan_lbl.setStyleSheet(f"color: {TEXT3}; font-size: 11px; background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 12px;")
        title_row.addWidget(self.last_scan_lbl)
        layout.addLayout(title_row)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        self.card_alerts    = StatCard("Active Alerts",     "0",                     RED)
        self.card_fixed     = StatCard("Issues Fixed",      "0",                     GREEN)
        self.card_monitored = StatCard("Errors Monitored",  str(len(CATALOG_LIST)),  ACCENT)
        self.card_uptime    = StatCard("Uptime",            "0m",                    TEXT3)

        for card in [self.card_alerts, self.card_fixed, self.card_monitored, self.card_uptime]:
            card.setFixedHeight(100)
            cards_row.addWidget(card)
        layout.addLayout(cards_row)

        health_row = QHBoxLayout()
        health_title = QLabel("System Health")
        health_title.setStyleSheet(f"color: {TEXT2}; font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;")
        health_row.addWidget(health_title)
        health_row.addStretch()
        layout.addLayout(health_row)

        health_grid = QGridLayout()
        health_grid.setSpacing(8)

        self.health_widgets = {}
        health_items = [
            ("CPU Usage",         "cpu",    "--"),
            ("Memory Usage",      "ram",    "--"),
            ("Disk (C:)",         "disk",   "--"),
            ("Network",           "net",    "--"),
            ("Critical Services", "svc",    "--"),
            ("Recent Alerts",     "errors", "--"),
        ]
        for i, (label, key, val) in enumerate(health_items):
            card = QFrame()
            card.setStyleSheet(f"background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 4px;")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(14, 11, 14, 11)

            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT3}; font-size: 11px; font-weight: 500; background: transparent; border: none;")
            card_layout.addWidget(lbl)
            card_layout.addStretch()

            val_lbl = QLabel(val)
            val_lbl.setStyleSheet(f"color: {TEXT1}; font-size: 13px; font-weight: 600; background: transparent; border: none;")
            card_layout.addWidget(val_lbl)

            self.health_widgets[key] = val_lbl
            health_grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(health_grid)
        layout.addStretch()

        return page

    def _make_alerts_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        
        hdr = QHBoxLayout()
        title = QLabel("Active Alerts")
        title.setStyleSheet(f"color: {TEXT1}; font-size: 20px; font-weight: 700; letter-spacing: -0.3px;")
        hdr.addWidget(title)
        hdr.addStretch()

        clear_btn = QPushButton("Clear all")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT3};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 5px 14px;
                font-size: 11px;
            }}
            QPushButton:hover {{ color: {RED}; border-color: {RED}40; }}
        """)
        clear_btn.clicked.connect(self._clear_all_alerts)
        hdr.addWidget(clear_btn)
        layout.addLayout(hdr)

        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }}")

        self.alerts_container = QWidget()
        self.alerts_layout = QVBoxLayout(self.alerts_container)
        self.alerts_layout.setSpacing(10)
        self.alerts_layout.addStretch()

        self.no_alerts_lbl = QLabel("✅  No active alerts. System is healthy.")
        self.no_alerts_lbl.setStyleSheet(f"color: {GREEN}; font-size: 14px;")
        self.no_alerts_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alerts_layout.insertWidget(0, self.no_alerts_lbl)

        scroll.setWidget(self.alerts_container)
        layout.addWidget(scroll)
        return page

    def _make_catalog_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel(f"Error Catalog  ({len(CATALOG_LIST)} errors monitored)")
        title.setStyleSheet(f"color: {TEXT1}; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["#", "Error Name", "Category", "Severity", "Detection"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 40)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setRowCount(len(CATALOG_LIST))

        for row, err in enumerate(CATALOG_LIST):
            sev = err.get("severity", "HIGH")
            color = SEV_COLORS.get(sev, ORANGE)
            icon = SEV_ICONS.get(sev, "⚠️")
            det = err.get("detection", {})
            det_str = det.get("type", "") + (f": {det.get('service_name','')}" if det.get('service_name') else
                                              f" ID {det.get('event_ids','')}" if det.get('event_ids') else "")

            items = [
                QTableWidgetItem(str(row + 1)),
                QTableWidgetItem(err.get("name", "")),
                QTableWidgetItem(err.get("category", "")),
                QTableWidgetItem(f"{icon} {sev}"),
                QTableWidgetItem(det_str),
            ]
            items[3].setForeground(QColor(color))
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                table.setItem(row, col, item)

        layout.addWidget(table)
        return page

    def _make_demo_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        title = QLabel("Demo Mode")
        title.setStyleSheet(f"color: {TEXT1}; font-size: 26px; font-weight: 700; letter-spacing: -0.5px;")
        outer.addWidget(title)

        subtitle = QLabel(
            "Select a scenario to simulate a real Windows error. "
            "SmartFix detects it in seconds and shows the alert. "
            "Click \u2018Fix Now\u2019 to apply the real repair."
        )
        subtitle.setStyleSheet(f"color: {TEXT2}; font-size: 12px;")
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        warn = QFrame()
        warn.setStyleSheet(f"background: {ORANGE}18; border: 1px solid {ORANGE}60; border-radius: 8px;")
        warn_layout = QHBoxLayout(warn)
        warn_layout.setContentsMargins(16, 10, 16, 10)
        warn_icon = QLabel("\u26a0")
        warn_icon.setStyleSheet(f"color: {ORANGE}; font-size: 16px; background: transparent; border: none;")
        warn_layout.addWidget(warn_icon)
        warn_lbl = QLabel("Demo scenarios temporarily stop real Windows services. They are fully reversed by the repair. Requires Administrator.")
        warn_lbl.setStyleSheet(f"color: {ORANGE}; font-size: 11px; background: transparent; border: none;")
        warn_lbl.setWordWrap(True)
        warn_layout.addWidget(warn_lbl, 1)
        outer.addWidget(warn)

        # Scrollable card list — fully responsive at any window size
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        cards_widget = QWidget()
        cards_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(cards_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        for sc in DEMO_LIST:
            self._make_demo_card(layout, sc)

        layout.addStretch()
        scroll.setWidget(cards_widget)
        outer.addWidget(scroll)
        return page

    def _make_demo_card(self, parent_layout, sc):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-color: {ACCENT};
            }}
        """)
        row = QHBoxLayout(card)
        row.setContentsMargins(20, 14, 16, 14)

        
        col = QVBoxLayout()
        col.setSpacing(3)
        name_lbl = QLabel(sc.name)
        name_lbl.setStyleSheet(f"color: {TEXT1}; font-weight: bold; font-size: 13px; background: transparent; border: none;")
        col.addWidget(name_lbl)
        desc_lbl = QLabel(sc.description)
        desc_lbl.setStyleSheet(f"color: {TEXT2}; font-size: 11px; background: transparent; border: none;")
        col.addWidget(desc_lbl)

        err = ERROR_CATALOG.get(sc.error_id, {})
        sev = err.get("severity", "HIGH")
        color = SEV_COLORS.get(sev, ORANGE)
        badge = QLabel(f" {sev} ")
        badge.setStyleSheet(f"background: {color}; color: white; border-radius: 4px; font-size: 9px; font-weight: bold; padding: 2px 6px; border: none;")
        badge_row = QHBoxLayout()
        badge_row.addWidget(badge)
        badge_row.addStretch()
        col.addLayout(badge_row)
        row.addLayout(col, 1)

        
        trigger_btn = QPushButton("▶  Trigger Demo")
        trigger_btn.setFixedWidth(150)
        trigger_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: #3D7ADB; }}
            QPushButton:pressed {{ background: #2A5FBD; }}
        """)
        trigger_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        trigger_btn.clicked.connect(lambda checked, sid=sc.error_id, btn=trigger_btn: self._run_demo(sid, btn))
        row.addWidget(trigger_btn)

        parent_layout.addWidget(card)

    

    
    def _make_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        
        title_row = QHBoxLayout()
        title = QLabel("Repair History")
        title.setStyleSheet(f"color: {TEXT1}; font-size: 22px; font-weight: bold;")
        title_row.addWidget(title)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(f"background: {BG_CARD2}; color: {TEXT1}; padding: 6px 16px; border-radius: 6px; border: 1px solid {BORDER};")
        refresh_btn.clicked.connect(lambda: self._populate_history())
        title_row.addWidget(refresh_btn)
        title_row.addStretch()
        layout.addLayout(title_row)
        
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["Time", "Error Name", "Category", "Action", "Success"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setColumnWidth(0, 140)
        self.history_table.setColumnWidth(1, 280)
        self.history_table.setColumnWidth(2, 120)
        self.history_table.setColumnWidth(3, 100)
        layout.addWidget(self.history_table)
        
        self._populate_history()
        return page

    def _populate_history(self):
        if not hasattr(self, 'history_table'): return
        try:
            records = get_history(50)
            self.history_table.setRowCount(len(records))
            for i, r in enumerate(records):
                ts = str(r.get('timestamp', ''))[:19].replace('T', ' ')
                self.history_table.setItem(i, 0, QTableWidgetItem(ts))
                self.history_table.setItem(i, 1, QTableWidgetItem(r.get('error_name', '')))
                self.history_table.setItem(i, 2, QTableWidgetItem(r.get('category', '')))
                
                action = r.get('action', '')
                act_item = QTableWidgetItem(action)
                if action == 'REPAIRED': act_item.setForeground(QColor(GREEN))
                elif action == 'DETECTED': act_item.setForeground(QColor(ORANGE))
                self.history_table.setItem(i, 3, act_item)
                
                succ = r.get('success', '')
                succ_str = ""
                if action == 'REPAIRED':
                    succ_str = "Yes" if succ else "No"
                succ_item = QTableWidgetItem(succ_str)
                if succ == 1: succ_item.setForeground(QColor(GREEN))
                elif succ == 0 and action == 'REPAIRED': succ_item.setForeground(QColor(RED))
                self.history_table.setItem(i, 4, succ_item)
        except Exception as e:
            logger.error(f"History load failed: {e}")

    def _make_network_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        
        title = QLabel("Network Diagnostics")
        title.setStyleSheet(f"color: {TEXT1}; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)
        
        desc = QLabel("Run a full network stack diagnosis including DNS, Gateway, Ports, and Internet connectivity.")
        desc.setStyleSheet(f"color: {TEXT2}; font-size: 13px;")
        layout.addWidget(desc)
        
        self.net_btn = QPushButton("Run Network Diagnostics")
        self.net_btn.setStyleSheet(f"background: {ACCENT}; color: white; padding: 12px 24px; font-weight: bold; font-size: 14px; border-radius: 8px; border: none; margin-top: 10px; width: 250px;")
        self.net_btn.setFixedWidth(250)
        self.net_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.net_btn.clicked.connect(self._run_network_diag)
        layout.addWidget(self.net_btn)
        
        self.net_log = QTextEdit()
        self.net_log.setReadOnly(True)
        self.net_log.setPlaceholderText("Click 'Run Network Diagnostics' to start...")
        layout.addWidget(self.net_log)
        
        return page

    def _run_network_diag(self):
        self.net_btn.setEnabled(False)
        self.net_btn.setText("Running...")
        self.net_log.clear()
        self.net_log.append("Running diagnostics... This may take up to 30 seconds.")
        
        
        def runner():
            try:
                res = run_full_diagnostics()
                self._alert_signal.emit({"type": "net_done", "res": res})
            except Exception as e:
                self._alert_signal.emit({"type": "net_err", "err": str(e)})
        threading.Thread(target=runner, daemon=True).start()

    def _make_report_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        
        title = QLabel("System Health Report")
        title.setStyleSheet(f"color: {TEXT1}; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)
        
        desc = QLabel("Generate a comprehensive HTML report covering Hardware, Software, Security, and Repair History.")
        desc.setStyleSheet(f"color: {TEXT2}; font-size: 13px;")
        layout.addWidget(desc)
        
        self.rep_btn = QPushButton("Generate HTML Report")
        self.rep_btn.setStyleSheet(f"background: {ACCENT}; color: white; padding: 12px 24px; font-weight: bold; font-size: 14px; border-radius: 8px; border: none; margin-top: 10px; width: 250px;")
        self.rep_btn.setFixedWidth(250)
        self.rep_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rep_btn.clicked.connect(self._run_report)
        layout.addWidget(self.rep_btn)
        
        self.rep_log = QTextEdit()
        self.rep_log.setReadOnly(True)
        self.rep_log.setPlaceholderText("Click 'Generate HTML Report' to create and open the report in your browser...")
        layout.addWidget(self.rep_log)
        
        return page

    def _run_report(self):
        self.rep_btn.setEnabled(False)
        self.rep_btn.setText("Generating...")
        self.rep_log.clear()
        self.rep_log.append("Gathering system telemetry...")
        
        def runner():
            try:
                records = get_history(50)
                path = save_report(history_records=records)
                self._alert_signal.emit({"type": "rep_done", "path": path})
            except Exception as e:
                self._alert_signal.emit({"type": "rep_err", "err": str(e)})
        threading.Thread(target=runner, daemon=True).start()


    def _setup_tray(self):
        try:
            
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(QColor(0, 210, 106)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, 28, 28)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "SF")
            painter.end()

            self.tray = QSystemTrayIcon(QIcon(pixmap), self)
            self.tray.setToolTip("SmartFix AI — Monitoring Active ✓")

            tray_menu = QMenu()
            tray_menu.setStyleSheet(f"""
                QMenu {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    color: {TEXT1};
                    font-size: 12px;
                    border-radius: 8px;
                }}
                QMenu::item:selected {{ background: {BG_CARD2}; }}
                QMenu::separator {{ background: {BORDER}; height: 1px; margin: 4px 0; }}
            """)

            show_action = QAction("📊 Open Dashboard", self)
            show_action.triggered.connect(self.show_and_raise)
            tray_menu.addAction(show_action)

            demo_action = QAction("🎭 Demo Mode", self)
            demo_action.triggered.connect(lambda: self._nav(3, self._nav_btns[3]))
            tray_menu.addAction(demo_action)

            tray_menu.addSeparator()

            exit_action = QAction("❌ Exit SmartFix", self)
            exit_action.triggered.connect(QApplication.quit)
            tray_menu.addAction(exit_action)

            self.tray.setContextMenu(tray_menu)
            self.tray.activated.connect(self._tray_activated)
            self.tray.show()
        except Exception as e:
            logger.error(f"Tray setup failed: {e}")

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_and_raise()

    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    

    def _start_monitor(self):
        self._monitor = BackgroundMonitor(
            on_alert=lambda info: self._alert_signal.emit(info),
            check_interval=30,
        )
        self._monitor.start()
        self._demo = DemoController(
            on_inject_error=self._monitor.inject_demo_error
        )
        self._start_time = time.time()

    def _start_metric_timer(self):
        # Prime psutil cpu_percent so first real reading is accurate
        try:
            import psutil as _ps
            _ps.cpu_percent(interval=None)
        except Exception:
            pass

        self._metric_timer = QTimer(self)
        self._metric_timer.timeout.connect(self._update_metrics)
        self._metric_timer.start(4000)   # update every 4 seconds
        QTimer.singleShot(1200, self._update_metrics)  # first reading after 1.2s warmup

    def _update_metrics(self):
        """Run metric collection on a background thread, post results back to UI."""
        def _collect():
            try:
                import psutil
                cpu  = psutil.cpu_percent(interval=1)   # blocking 1s sample — accurate
                mem  = psutil.virtual_memory()
                disk = psutil.disk_usage('C:\\')
                net_ok = True
                try:
                    import socket
                    socket.setdefaulttimeout(1)
                    socket.gethostbyname("8.8.8.8")
                except Exception:
                    net_ok = False
                uptime_m = int((time.time() - self._start_time) / 60)
                self._alert_signal.emit({
                    "__type__": "metric_update",
                    "cpu":  cpu,
                    "ram":  mem.percent,
                    "disk": disk.percent,
                    "net_ok": net_ok,
                    "uptime_m": uptime_m,
                })
            except Exception as e:
                logger.error(f"Metric collect failed: {e}")

        t = threading.Thread(target=_collect, daemon=True)
        t.start()

    

    def _show_alert(self, error_info: dict):
        """Called on main thread via signal."""

        # ── Metric update from background thread ───────────────────
        if error_info.get("__type__") == "metric_update":
            def color_val(val, warn=70, crit=90):
                if val >= crit: return RED
                if val >= warn: return ORANGE
                return GREEN

            cpu  = error_info.get("cpu",  0)
            ram  = error_info.get("ram",  0)
            disk = error_info.get("disk", 0)
            net_ok    = error_info.get("net_ok", True)
            uptime_m  = error_info.get("uptime_m", 0)

            self.health_widgets["cpu"].setText(f"{cpu:.1f}%")
            self.health_widgets["cpu"].setStyleSheet(
                f"color: {color_val(cpu)}; font-size: 13px; font-weight: 600; background: transparent; border: none;")

            self.health_widgets["ram"].setText(f"{ram:.1f}%")
            self.health_widgets["ram"].setStyleSheet(
                f"color: {color_val(ram)}; font-size: 13px; font-weight: 600; background: transparent; border: none;")

            self.health_widgets["disk"].setText(f"{disk:.1f}%")
            self.health_widgets["disk"].setStyleSheet(
                f"color: {color_val(disk)}; font-size: 13px; font-weight: 600; background: transparent; border: none;")

            net_txt = "Connected" if net_ok else "No Internet"
            net_col = GREEN if net_ok else RED
            self.health_widgets["net"].setText(net_txt)
            self.health_widgets["net"].setStyleSheet(
                f"color: {net_col}; font-size: 13px; font-weight: 600; background: transparent; border: none;")

            hrs = uptime_m // 60
            mins = uptime_m % 60
            uptime_str = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"
            self.card_uptime.set_value(uptime_str)
            self.card_monitored.set_value(str(len(CATALOG_LIST)))
            self.last_scan_lbl.setText(f"Updated {datetime.now().strftime('%H:%M:%S')}")
            return

        sig_type = error_info.get("type")

        if sig_type == "net_done":

            res = error_info.get("res", {})
            self.net_btn.setText("Run Network Diagnostics")
            self.net_btn.setEnabled(True)
            self.net_log.clear()
            self.net_log.append(f"Network Diagnostics Complete:\n")
            import json
            self.net_log.append(json.dumps(res, indent=2))
            return
            
        if sig_type == "net_err":
            self.net_btn.setText("Run Network Diagnostics")
            self.net_btn.setEnabled(True)
            self.net_log.append(f"\nError: {error_info.get('err')}")
            return
            
        if sig_type == "rep_done":
            path = error_info.get("path")
            self.rep_btn.setText("Generate HTML Report")
            self.rep_btn.setEnabled(True)
            self.rep_log.append(f"\nReport saved to: {path}")
            self.rep_log.append("Opening report in browser...")
            import webbrowser
            webbrowser.open(path)
            return
            
        if sig_type == "rep_err":
            self.rep_btn.setText("Generate HTML Report")
            self.rep_btn.setEnabled(True)
            self.rep_log.append(f"\nError generating report: {error_info.get('err')}")
            return

        self._alert_count += 1
        self._alerts.append(error_info)
        self.card_alerts.set_value(str(self._alert_count))
        self.health_widgets["errors"].setText(f"{self._alert_count} alert(s)")
        self.health_widgets["errors"].setStyleSheet(f"color: {RED}; font-size: 13px; font-weight: 600; background: transparent; border: none;")
        log_detection(error_info)

        eid = error_info.get("id", "")

        # Skip if this error is already showing in the Active Alerts list
        if eid in self._active_alert_ids:
            self._alert_count = max(0, self._alert_count - 1)
            self.card_alerts.set_value(str(self._alert_count))
            return
        if eid:
            self._active_alert_ids.add(eid)

        self.no_alerts_lbl.setVisible(False)
        alert_item = AlertItem(error_info, self._fix_from_list, self._ignore_from_list)
        self.alerts_layout.insertWidget(0, alert_item)

        # Only show 1 popup at a time, CRITICAL only
        if error_info.get("severity") == "CRITICAL" and not self._popup_visible:
            self._popup_visible = True
            popup = AlertPopup(error_info, self)
            popup.destroyed.connect(lambda: setattr(self, '_popup_visible', False))
            popup.show()
            self._active_popups.append(popup)

    def _fix_from_list(self, error_info: dict, item_widget: QFrame):
        eid = error_info.get("id", "")
        item_widget.setParent(None)
        self._alert_count = max(0, self._alert_count - 1)
        self.card_alerts.set_value(str(self._alert_count))
        # Allow this error to appear again only after a long cooldown
        if eid:
            self._active_alert_ids.discard(eid)
            # Tell the monitor this error is resolved — suppress re-alerting for 60 min
            if self._monitor:
                self._monitor.mark_resolved(eid, cooldown_seconds=3600)
        if error_info.get("repair_id") == "unknown_error":
            dlg = AIAssistantDialog(error_info, self)
            dlg.exec()
        else:
            dlg = RepairDialog(error_info, self)
            if dlg.exec():
                self._fixed_count += 1
                self.card_fixed.set_value(str(self._fixed_count))
        if self._alert_count == 0:
            self.no_alerts_lbl.setVisible(True)
            self.health_widgets["errors"].setText("None")
            self.health_widgets["errors"].setStyleSheet(f"color: {GREEN}; font-size: 13px; font-weight: 600; background: transparent; border: none;")

    def _ignore_from_list(self, item_widget: QFrame):
        eid = item_widget.error_info.get("id", "")
        log_ignore(item_widget.error_info)
        item_widget.setParent(None)
        self._alert_count = max(0, self._alert_count - 1)
        self.card_alerts.set_value(str(self._alert_count))
        self._ignored_count += 1
        if eid:
            self._active_alert_ids.discard(eid)
            # Re-enable alerting after standard cooldown
            if self._monitor:
                self._monitor.mark_resolved(eid, cooldown_seconds=600)
        if self._alert_count == 0:
            self.no_alerts_lbl.setVisible(True)
            self.health_widgets["errors"].setText("None")
            self.health_widgets["errors"].setStyleSheet(f"color: {GREEN}; font-size: 13px; font-weight: 600; background: transparent; border: none;")

    def _clear_all_alerts(self):
        for i in reversed(range(self.alerts_layout.count())):
            w = self.alerts_layout.itemAt(i).widget()
            if w and w is not self.no_alerts_lbl:
                w.setParent(None)
        self._alert_count = 0
        self.card_alerts.set_value("0")
        self.no_alerts_lbl.setVisible(True)

    

    def _run_demo(self, scenario_id: str, btn: QPushButton):
        original_text = btn.text()
        btn.setText("⏳ Running…")
        btn.setEnabled(False)

        def restore():
            btn.setText(original_text)
            btn.setEnabled(True)

        if self._demo:
            self._demo.run_demo(scenario_id, delay_seconds=2.0)

        QTimer.singleShot(5000, restore)

    def closeEvent(self, event):
        """Minimize to tray instead of closing."""
        event.ignore()
        self.hide()
        if hasattr(self, 'tray'):
            self.tray.showMessage(
                "SmartFix AI",
                "Still running in the system tray. Right-click the tray icon to open or exit.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )



def _is_admin() -> bool:
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def _relaunch_as_admin():
    import ctypes
    script = os.path.abspath(sys.argv[0])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
    sys.exit(0)



def main():
    if not _is_admin():
        _relaunch_as_admin()
        return

    app = QApplication(sys.argv)
    app.setApplicationName("SmartFix AI")
    app.setOrganizationName("SmartFix")
    app.setQuitOnLastWindowClosed(False)  

    
    QFontDatabase.addApplicationFont("C:\\Windows\\Fonts\\segoeui.ttf")
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
