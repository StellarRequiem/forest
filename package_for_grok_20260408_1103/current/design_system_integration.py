# design_system_integration.py
# v4.1 - Simple bridge that connects DesignSystemManager to CUS
# Created step-by-step for Alex with zero tech background

from design_system_manager import DesignSystemManager

# Global manager so the whole system can use it
design_manager = DesignSystemManager()

def load_design_system_for_cus(brand: str):
    """Called by the Supervisor or Worker when a design system is approved"""
    print(f"[DESIGN] Attempting to load design system: {brand}")
    success = design_manager.fetch(brand)
    if success:
        injection = design_manager.get_injection_prompt(brand)
        print(f"[DESIGN] ✅ SUCCESS: {brand} design system loaded and ready")
        print(f"[DESIGN] Active system is now: {design_manager.active_system}")
        return injection
    else:
        print(f"[DESIGN] ❌ Failed to load {brand}")
        return None

def get_current_design_status():
    """Show what design system is currently active"""
    return design_manager.get_status()

# Simple test function you can run
if __name__ == "__main__":
    print("=== Design System Integration Test ===")
    print("Try loading 'ollama' as an example...")
    load_design_system_for_cus("ollama")
    print(get_current_design_status())
