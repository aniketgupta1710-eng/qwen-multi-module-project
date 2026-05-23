import sys

def main():
    """Entry point for the application."""
    # Check if we should launch GUI or headless tests (future)
    # For now, just launch GUI

    # We defer GUI imports so we don't crash if PySide6 isn't installed
    # (e.g. running in simple environments)
    try:
        from app.gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Failed to start GUI. Is PySide6 installed? Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure sys.path is correct if running as script
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    main()
