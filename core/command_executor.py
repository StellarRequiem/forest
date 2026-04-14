#!/usr/bin/env python3
"""
Forest Command Executor
Executes Forest module commands with proper integration
"""

import subprocess
import threading
from pathlib import Path
from typing import List, Callable, Optional
import os
import signal


class CommandExecutor:
    """Executes commands with real-time output streaming"""
    
    def __init__(self, forest_path: Path):
        self.forest_path = forest_path
        self.processes = {}
        self.threads = {}
    
    def execute_command(
        self,
        command_id: str,
        cmd: List[str],
        on_output: Callable[[str], None] = None,
        on_error: Callable[[str], None] = None,
        on_complete: Callable[[int], None] = None,
        env: dict = None,
    ) -> bool:
        """Execute a command with callbacks"""
        
        try:
            # Set up environment
            cmd_env = os.environ.copy()
            cmd_env['PYTHONUNBUFFERED'] = '1'
            if env:
                cmd_env.update(env)
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=str(self.forest_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=cmd_env,
                preexec_fn=None if sys.platform == 'win32' else None,
            )
            
            self.processes[command_id] = process
            
            # Start reader thread
            thread = threading.Thread(
                target=self._read_output,
                args=(command_id, process, on_output, on_error, on_complete),
                daemon=True,
            )
            self.threads[command_id] = thread
            thread.start()
            
            return True
        
        except Exception as e:
            if on_error:
                on_error(f"Failed to execute: {str(e)}")
            return False
    
    def _read_output(
        self,
        command_id: str,
        process: subprocess.Popen,
        on_output: Callable,
        on_error: Callable,
        on_complete: Callable,
    ):
        """Read process output in background thread"""
        try:
            for line in process.stdout:
                line = line.rstrip()
                if line and on_output:
                    on_output(line)
            
            return_code = process.wait()
            
            if on_complete:
                on_complete(return_code)
            
            # Cleanup
            if command_id in self.processes:
                del self.processes[command_id]
            if command_id in self.threads:
                del self.threads[command_id]
        
        except Exception as e:
            if on_error:
                on_error(f"Error reading output: {str(e)}")
    
    def stop_command(self, command_id: str) -> bool:
        """Stop a running command"""
        if command_id in self.processes:
            process = self.processes[command_id]
            try:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                return True
            except Exception:
                return False
        return False
    
    def is_running(self, command_id: str) -> bool:
        """Check if command is running"""
        if command_id in self.processes:
            return self.processes[command_id].poll() is None
        return False


class ForestCommandBuilder:
    """Builds Forest module commands"""
    
    # Module entry points
    COMMANDS = {
        'p1_cus_core': {
            'cmd': ['python3', 'cus_core.py'],
            'args': ['--task'],
            'description': 'CUS Core Orchestration',
        },
        'p2_agents': {
            'cmd': ['python3', 'forest_cli.py', 'agents'],
            'description': 'List agents',
        },
        'p3_network': {
            'cmd': ['python3', 'forest_cli.py', 'network'],
            'description': 'Network monitoring',
        },
        'p4_audit': {
            'cmd': ['python3', 'forest_cli.py', 'audit'],
            'description': 'Audit logs',
        },
        'p5_training': {
            'cmd': ['python3', 'forest_auto_runner.py'],
            'description': 'Training pipeline',
        },
        'p6_autorunner': {
            'cmd': ['python3', 'forest_auto_runner.py'],
            'description': 'Auto-runner daemon',
        },
        'p7_dashboard': {
            'cmd': ['streamlit', 'run', 'ui/dashboards/forest_dashboard.py'],
            'description': 'Dashboard',
        },
        'p8_testing': {
            'cmd': ['python3', '-m', 'pytest', 'tests/', '-v'],
            'description': 'Testing suite',
        },
    }
    
    @staticmethod
    def build_command(module: str, args: dict = None) -> List[str]:
        """Build command for module"""
        if module not in ForestCommandBuilder.COMMANDS:
            raise ValueError(f"Unknown module: {module}")
        
        cmd_spec = ForestCommandBuilder.COMMANDS[module]
        cmd = cmd_spec['cmd'].copy()
        
        if args and 'args' in cmd_spec:
            for arg_name in cmd_spec['args']:
                if arg_name in args:
                    cmd.extend([f'--{arg_name}', str(args[arg_name])])
        
        return cmd
