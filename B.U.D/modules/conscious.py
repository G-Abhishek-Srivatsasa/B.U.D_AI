import time
import threading
try:
    import keyboard
except ImportError:
    keyboard = None
    
try:
    import pygetwindow as gw
except ImportError:
    gw = None

# --- CONSTANTS (Configurable) ---
TYPING_THRESHOLD = 2.0  # Keystrokes per second to be considered "Typing Fast"
FOCUS_TIMEOUT = 5.0     # Function stays "Focused" for this many seconds after typing stops
INTERRUPT_CHECK_INTERVAL = 0.5 

# Priorities
PRIORITY_LOW = 1    # Spontaneous chatter
PRIORITY_NORMAL = 5 # Normal command responses
PRIORITY_HIGH = 10  # Critical warnings / Direct Execution

class FocusDetector:
    def __init__(self):
        self.keystrokes = 0
        self.last_keystroke_time = 0
        self.is_monitoring = False
        self.typing_speed = 0.0 # keys/sec
        
        # Start background monitor if keyboard is available
        if keyboard:
            self.start_monitoring()
            
    def _on_key_event(self, e):
        """Called on every key press."""
        self.keystrokes += 1
        self.last_keystroke_time = time.time()
        
    def start_monitoring(self):
        if self.is_monitoring: return
        
        self.is_monitoring = True
        
        # 1. Hook Keyboard (Safe wrapper)
        try:
            keyboard.on_press(self._on_key_event)
        except Exception as e:
            print(f"Warning: Could not hook keyboard (Focus detection limited): {e}")

        # 2. Start Analyzer Thread
        t = threading.Thread(target=self._analyze_loop, daemon=True)
        t.start()
        
    def _analyze_loop(self):
        """Calculates typing speed every second."""
        while True:
            time.sleep(1)
            # Calculate speed based on last second
            current_strokes = self.keystrokes
            self.keystrokes = 0 # Reset counter
            
            # Simple moving average for smoothness
            self.typing_speed = (self.typing_speed * 0.7) + (current_strokes * 0.3)
            
            # Debugging (Uncomment to see speed)
            # if self.typing_speed > 0: print(f"Speed: {self.typing_speed:.1f}")

    def is_typing_active(self):
        """Returns True if user is typing fast or recently typed."""
        # Check immediate speed
        if self.typing_speed > TYPING_THRESHOLD:
            return True
            
        # Check recent activity (decay)
        if (time.time() - self.last_keystroke_time) < FOCUS_TIMEOUT:
            return True
            
        return False
        
    def is_fullscreen(self):
        """Checks if the active window is fullscreen (Movie/Game)."""
        if not gw: return False
        
        try:
            window = gw.getActiveWindow()
            if not window: return False
            
            # Check logic: If window matches screen resolution (approx)
            # This is a heuristic. 
            # Better checking strategy can be added here if needed.
            # For now, simplistic check:
            if window.isMaximized:
                # Maximized is NOT fullscreen (taskbar still visible).
                # But we treat it as 'Safe' usually. 
                return False
                
            # True fullscreen usually covers entire screen including taskbar
            # We can't easily get screen resolution in pure python without other libs
            # But let's assume if it looks "big" and titled.
            
            return False 
        except:
            return False

# --- GLOBAL INSTANCE ---
detector = FocusDetector()

def should_interrupt(priority=PRIORITY_LOW):
    """
    The Decision Maker.
    Returns:
        True: Yes, speak now.
        False: No, stay silent (User is busy).
    """
    
    # 1. HIGH Priority always overrides
    if priority >= PRIORITY_HIGH:
        return True
        
    # 2. Check Focus (Typing)
    if detector.is_typing_active():
        # User is typing. Block LOW priority (Spontaneous)
        if priority == PRIORITY_LOW:
            # print("   [CONSCIOUS] Suppressing thought (User is typing)")
            return False
            
    # 3. Check Fullscreen (Movies/Games)
    # (Leaving placeholder for now as logic is complex without screen dims)
    # if detector.is_fullscreen():
    #     if priority < PRIORITY_HIGH: return False
        
    return True
