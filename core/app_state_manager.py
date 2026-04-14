#!/usr/bin/env python3
"""
Forest Application State Manager
Manages persistent state, task queues, and module lifecycle
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModuleStatus(Enum):
    """Module execution status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class Task:
    """Represents a task in the system"""
    id: str
    module: str
    name: str
    command: List[str]
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = None
    started_at: str = None
    completed_at: str = None
    output: List[str] = None
    error: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.output is None:
            self.output = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'module': self.module,
            'name': self.name,
            'command': self.command,
            'status': self.status.value,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'output': self.output,
            'error': self.error,
        }


@dataclass
class ModuleState:
    """Represents module state"""
    name: str
    status: ModuleStatus = ModuleStatus.STOPPED
    pid: Optional[int] = None
    current_task: Optional[str] = None
    task_count: int = 0
    last_output: str = None
    uptime: float = 0.0
    start_time: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'status': self.status.value,
            'pid': self.pid,
            'current_task': self.current_task,
            'task_count': self.task_count,
            'last_output': self.last_output,
            'uptime': self.uptime,
            'start_time': self.start_time,
        }


class AppStateManager:
    """Manages application state persistence"""
    
    def __init__(self, forest_path: Path):
        self.forest_path = forest_path
        self.state_dir = forest_path / ".forest_state"
        self.state_dir.mkdir(exist_ok=True)
        
        self.tasks_file = self.state_dir / "tasks.json"
        self.modules_file = self.state_dir / "modules.json"
        self.config_file = self.state_dir / "config.json"
        
        self.tasks: Dict[str, Task] = {}
        self.modules: Dict[str, ModuleState] = {}
        self.config: Dict[str, Any] = {}
        
        self.load_state()
    
    def load_state(self):
        """Load persisted state from disk"""
        # Load tasks
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file) as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        task = Task(
                            id=task_data['id'],
                            module=task_data['module'],
                            name=task_data['name'],
                            command=task_data['command'],
                            status=TaskStatus(task_data['status']),
                            created_at=task_data.get('created_at'),
                            started_at=task_data.get('started_at'),
                            completed_at=task_data.get('completed_at'),
                            output=task_data.get('output', []),
                            error=task_data.get('error'),
                        )
                        self.tasks[task.id] = task
            except Exception as e:
                print(f"Error loading tasks: {e}")
        
        # Load modules
        if self.modules_file.exists():
            try:
                with open(self.modules_file) as f:
                    modules_data = json.load(f)
                    for module_data in modules_data:
                        module = ModuleState(
                            name=module_data['name'],
                            status=ModuleStatus(module_data.get('status', 'stopped')),
                            pid=module_data.get('pid'),
                            current_task=module_data.get('current_task'),
                            task_count=module_data.get('task_count', 0),
                            last_output=module_data.get('last_output'),
                            uptime=module_data.get('uptime', 0.0),
                            start_time=module_data.get('start_time'),
                        )
                        self.modules[module.name] = module
            except Exception as e:
                print(f"Error loading modules: {e}")
        
        # Load config
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_state(self):
        """Persist state to disk"""
        # Save tasks
        try:
            with open(self.tasks_file, 'w') as f:
                tasks_data = [task.to_dict() for task in self.tasks.values()]
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
        
        # Save modules
        try:
            with open(self.modules_file, 'w') as f:
                modules_data = [module.to_dict() for module in self.modules.values()]
                json.dump(modules_data, f, indent=2)
        except Exception as e:
            print(f"Error saving modules: {e}")
        
        # Save config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def add_task(self, module: str, name: str, command: List[str]) -> Task:
        """Create a new task"""
        task_id = hashlib.md5(f"{module}{name}{time.time()}".encode()).hexdigest()[:12]
        task = Task(
            id=task_id,
            module=module,
            name=name,
            command=command,
        )
        self.tasks[task_id] = task
        self.save_state()
        return task
    
    def update_task(self, task_id: str, status: TaskStatus = None, output: str = None, error: str = None):
        """Update task status"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if status:
                task.status = status
                if status == TaskStatus.RUNNING and not task.started_at:
                    task.started_at = datetime.now().isoformat()
                elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    task.completed_at = datetime.now().isoformat()
            
            if output:
                task.output.append(output)
            
            if error:
                task.error = error
            
            self.save_state()
    
    def update_module(self, module_name: str, status: ModuleStatus = None, pid: int = None, 
                     current_task: str = None, last_output: str = None):
        """Update module state"""
        if module_name not in self.modules:
            self.modules[module_name] = ModuleState(name=module_name)
        
        module = self.modules[module_name]
        
        if status:
            module.status = status
            if status == ModuleStatus.RUNNING and not module.start_time:
                module.start_time = datetime.now().isoformat()
            elif status == ModuleStatus.STOPPED:
                module.start_time = None
                module.uptime = 0.0
        
        if pid is not None:
            module.pid = pid
        
        if current_task is not None:
            module.current_task = current_task
        
        if last_output:
            module.last_output = last_output
        
        self.save_state()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_module(self, module: str) -> List[Task]:
        """Get all tasks for a module"""
        return [task for task in self.tasks.values() if task.module == module]
    
    def get_recent_tasks(self, limit: int = 10) -> List[Task]:
        """Get most recent tasks"""
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )
        return sorted_tasks[:limit]
