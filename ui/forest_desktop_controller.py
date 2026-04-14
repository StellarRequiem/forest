#!/usr/bin/env python3
"""
Forest Desktop Controller — Stable working version with diagnostics
"""

import sys
import subprocess
import threading
import traceback
import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox,
    QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / '.forest_state' / 'app.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

FOREST_PATH = Path.home() / "Forest"

logger.info("=" * 80)
logger.info("Forest Desktop Controller Starting")
logger.info("=" * 80)


class ProcessMonitor(QThread):
    """Monitor system metrics"""
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        logger.info("ProcessMonitor initialized")
        
    def run(self):
        logger.info("ProcessMonitor thread started")
        try:
            while self.running:
                try:
                    metrics = {
                        'cpu_percent': psutil.cpu_percent(interval=1),
                        'memory_percent': psutil.virtual_memory().percent,
                    }
                    self.metrics_updated.emit(metrics)
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
                self.msleep(2000)
        except Exception as e:
            logger.error(f"ProcessMonitor crashed: {e}")
            traceback.print_exc()
    
    def stop(self):
        self.running = False
        logger.info("ProcessMonitor stopping")


class TerminalWidget(QTextEdit):
    """Terminal output"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #22c55e;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid #333;
                padding: 5px;
            }
        """)
        logger.debug("TerminalWidget created")
    
    def append_output(self, text: str):
        """Append text"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.append(f"[{timestamp}] {text}")
        except Exception as e:
            logger.error(f"Error appending output: {e}")


class ModulePanel(QWidget):
    """Generic module panel"""
    
    def __init__(self, title: str, module_id: str):
        super().__init__()
        self.title_text = title
        self.module_id = module_id
        self.process = None
        logger.info(f"Creating panel for {module_id}: {title}")
        try:
            self.init_ui()
        except Exception as e:
            logger.error(f"Error initializing panel {module_id}: {e}")
            traceback.print_exc()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(self.title_text)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #22c55e;")
        layout.addWidget(title)
        
        # For P1, add task input
        if self.module_id == "p1":
            task_group = QGroupBox("Task Configuration")
            task_layout = QGridLayout()
            task_layout.addWidget(QLabel("Task:"), 0, 0)
            self.task_input = QLineEdit()
            self.task_input.setText("monitor")
            task_layout.addWidget(self.task_input, 0, 1)
            task_group.setLayout(task_layout)
            layout.addWidget(task_group)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setStyleSheet("background-color: #22c55e; color: black; font-weight: bold; padding: 8px;")
        self.start_btn.clicked.connect(self.safe_execute)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold; padding: 8px;")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.safe_stop)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Terminal
        self.terminal = TerminalWidget()
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.terminal)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def safe_execute(self):
        """Safe wrapper for execute"""
        try:
            self.execute()
        except Exception as e:
            logger.error(f"Error in execute: {e}")
            traceback.print_exc()
            self.terminal.append_output(f"ERROR: {str(e)}")
    
    def safe_stop(self):
        """Safe wrapper for stop"""
        try:
            self.stop_execution()
        except Exception as e:
            logger.error(f"Error in stop_execution: {e}")
            traceback.print_exc()
    
    def execute(self):
        """Execute module command"""
        logger.info(f"Executing module: {self.module_id}")
        
        # Define commands for each module
        commands = {
            'p1': ['python3', 'cus_core.py', '--task', self.task_input.text()],
            'p2': ['python3', 'forest_cli.py', 'agents'],
            'p3': ['python3', 'forest_cli.py', 'network'],
            'p4': ['python3', 'forest_cli.py', 'audit'],
            'p5': ['python3', 'forest_auto_runner.py'],
            'p6': ['python3', 'forest_auto_runner.py'],
            'p8': ['python3', '-m', 'pytest', 'tests/', '-v'],
        }
        
        if self.module_id not in commands:
            error_msg = f"ERROR: Unknown module {self.module_id}"
            logger.error(error_msg)
            self.terminal.append_output(error_msg)
            return
        
        cmd = commands[self.module_id]
        logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            self.terminal.append_output(f"Executing: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                cwd=str(FOREST_PATH),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            
            logger.info(f"Process started with PID: {self.process.pid}")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Read output in background
            thread = threading.Thread(target=self._read_output, daemon=True)
            thread.start()
        
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            logger.error(error_msg)
            self.terminal.append_output(error_msg)
            traceback.print_exc()
    
    def _read_output(self):
        """Read process output"""
        try:
            logger.info("Output reader thread started")
            line_count = 0
            for line in self.process.stdout:
                line = line.rstrip()
                if line:
                    self.terminal.append_output(line)
                    line_count += 1
            
            return_code = self.process.wait()
            logger.info(f"Process exited with code {return_code} after {line_count} lines")
            self.terminal.append_output(f"\nProcess exited with code {return_code}")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        except Exception as e:
            error_msg = f"ERROR reading output: {str(e)}"
            logger.error(error_msg)
            self.terminal.append_output(error_msg)
            traceback.print_exc()
    
    def stop_execution(self):
        """Stop process"""
        logger.info(f"Stopping process for {self.module_id}")
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
                self.terminal.append_output("Process terminated")
                logger.info("Process terminated successfully")
            except subprocess.TimeoutExpired:
                logger.warning("Process didn't terminate, killing...")
                self.process.kill()
                self.terminal.append_output("Process killed")
            except Exception as e:
                error_msg = f"Error stopping: {str(e)}"
                logger.error(error_msg)
                self.terminal.append_output(error_msg)
            
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)


class DashboardPanel(QWidget):
    """P7 Dashboard panel"""
    
    def __init__(self):
        super().__init__()
        logger.info("Creating Dashboard panel")
        try:
            self.init_ui()
        except Exception as e:
            logger.error(f"Error initializing dashboard: {e}")
            traceback.print_exc()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("P7: Dashboards — Web UI")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #22c55e;")
        layout.addWidget(title)
        
        btn = QPushButton("📊 Open Streamlit Dashboard")
        btn.setStyleSheet("background-color: #3b82f6; color: white; padding: 10px; font-weight: bold;")
        btn.clicked.connect(self.safe_open)
        layout.addWidget(btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def safe_open(self):
        """Safe wrapper"""
        try:
            self.open_dashboard()
        except Exception as e:
            logger.error(f"Error opening dashboard: {e}")
    
    def open_dashboard(self):
        import webbrowser
        logger.info("Opening Streamlit dashboard")
        webbrowser.open('http://localhost:8501')


class ForestDesktopController(QMainWindow):
    """Main application"""
    
    def __init__(self):
        super().__init__()
        logger.info("Initializing ForestDesktopController")
        self.forest_path = FOREST_PATH
        
        try:
            # Process monitor
            self.process_monitor = ProcessMonitor()
            self.process_monitor.metrics_updated.connect(self.safe_update_metrics)
            self.process_monitor.start()
            
            self.init_ui()
            logger.info("UI initialized")
            
            self.setWindowTitle("🌲 Forest Desktop Controller (Live)")
            self.setGeometry(100, 100, 1400, 900)
            self.apply_theme()
            
            logger.info("Applying theme")
        except Exception as e:
            logger.error(f"Error in __init__: {e}")
            traceback.print_exc()
    
    def init_ui(self):
        """Initialize UI"""
        logger.info("Starting UI initialization")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🌲 FOREST — 8-Module Desktop Controller")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #22c55e;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet("color: #aaa;")
        header_layout.addWidget(self.cpu_label)
        
        self.mem_label = QLabel("MEM: 0%")
        self.mem_label.setStyleSheet("color: #aaa;")
        header_layout.addWidget(self.mem_label)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        logger.info("Creating tabs")
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; }
            QTabBar::tab { background-color: #1f1f1f; color: #aaa; padding: 8px 15px; border: 1px solid #333; }
            QTabBar::tab:selected { background-color: #2a2a2a; color: #22c55e; }
        """)
        
        tabs.addTab(ModulePanel("P1: CUS Core — Orchestration", "p1"), "P1: CUS Core")
        tabs.addTab(ModulePanel("P2: Agents — AI Workers", "p2"), "P2: Agents")
        tabs.addTab(ModulePanel("P3: Network Monitor — Blue Team", "p3"), "P3: Network")
        tabs.addTab(ModulePanel("P4: Audit — Cryptex Logging", "p4"), "P4: Audit")
        tabs.addTab(ModulePanel("P5: Training Pipeline — Self-Improve", "p5"), "P5: Training")
        tabs.addTab(ModulePanel("P6: Auto-Runner — 24/7 Daemon", "p6"), "P6: Auto-Runner")
        tabs.addTab(DashboardPanel(), "P7: Dashboards")
        tabs.addTab(ModulePanel("P8: Testing — QA Suite", "p8"), "P8: Testing")
        
        main_layout.addWidget(tabs)
        
        self.statusBar().showMessage("✅ Ready - Click any tab to execute Forest commands")
        
        central_widget.setLayout(main_layout)
        logger.info("UI initialization complete")
    
    def apply_theme(self):
        """Apply theme"""
        self.setStyleSheet("""
            QMainWindow { background-color: #0a0a0a; color: #e0e0e0; }
            QWidget { background-color: #0a0a0a; color: #e0e0e0; }
            QPushButton { background-color: #1f1f1f; color: #e0e0e0; border: 1px solid #333; padding: 5px; border-radius: 3px; }
            QPushButton:hover { background-color: #2a2a2a; }
            QPushButton:pressed { background-color: #333; }
            QLineEdit { background-color: #1f1f1f; color: #e0e0e0; border: 1px solid #333; padding: 5px; }
            QGroupBox { color: #22c55e; border: 1px solid #333; padding: 5px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QLabel { color: #e0e0e0; }
            QStatusBar { background-color: #1f1f1f; color: #aaa; }
        """)
    
    def safe_update_metrics(self, metrics: dict):
        """Safe wrapper for update metrics"""
        try:
            self.update_metrics(metrics)
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def update_metrics(self, metrics: dict):
        """Update metrics"""
        self.cpu_label.setText(f"CPU: {metrics['cpu_percent']:.1f}%")
        self.mem_label.setText(f"MEM: {metrics['memory_percent']:.1f}%")
    
    def closeEvent(self, event):
        """Clean up"""
        logger.info("Closing application")
        try:
            self.process_monitor.stop()
            self.process_monitor.wait()
            logger.info("ProcessMonitor stopped")
        except Exception as e:
            logger.error(f"Error stopping process monitor: {e}")
        
        logger.info("=" * 80)
        logger.info("Forest Desktop Controller Closed")
        logger.info("=" * 80)
        event.accept()


def main():
    logger.info("Main function starting")
    try:
        app = QApplication(sys.argv)
        logger.info("QApplication created")
        
        window = ForestDesktopController()
        logger.info("ForestDesktopController window created")
        
        window.show()
        logger.info("Window shown, entering event loop")
        
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
