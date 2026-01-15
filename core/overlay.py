"""
Modernized Holographic Overlay for ALFRED - WayneTech Edition.
Features: Tactical radar, sharp industrial borders, WayneTech amber/steel color scheme.
"""

import sys
import math
import random
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QRadialGradient, QPolygonF, 
                         QFont, QFontMetrics, QLinearGradient, QConicalGradient)

# Import sounds module (optional - graceful fallback if not available)
try:
    from core import sounds
    SOUNDS_AVAILABLE = True
except ImportError:
    try:
        import sounds
        SOUNDS_AVAILABLE = True
    except ImportError:
        SOUNDS_AVAILABLE = False

# Import config for animation settings (performance tuning)
try:
    import config
    ANIM_INTERVAL = getattr(config, 'OVERLAY_ANIMATION_INTERVAL', 60)
    WAVEFORM_INTERVAL = getattr(config, 'WAVEFORM_ANIMATION_INTERVAL', 100)
    DIAGNOSTICS_INTERVAL = getattr(config, 'DIAGNOSTICS_UPDATE_INTERVAL', 5000)
except ImportError:
    ANIM_INTERVAL = 60
    WAVEFORM_INTERVAL = 100
    DIAGNOSTICS_INTERVAL = 5000

# --- WAYNETECH COLOR PALETTE ---
# Dark, tactical, industrial
COLOR_BG_DARK = QColor(10, 12, 15, 230)      # Carbon Black / Dark Matte
COLOR_BG_LIGHT = QColor(25, 30, 35, 200)     # Gunmetal Grey
COLOR_BORDER = QColor(100, 149, 237, 180)    # Steel Blue (Default System)
COLOR_ACCENT = QColor(255, 165, 0)           # WayneTech Amber (Attention)

COLOR_TEXT = QColor(220, 230, 240)           # Off-white/Silver
COLOR_TEXT_DIM = QColor(112, 128, 144)       # Slate Grey

# State Colors
COLOR_SYSTEM_OK = QColor(100, 149, 237)      # Steel Blue
COLOR_ACTIVE_SCAN = QColor(255, 200, 50)     # Bright Amber (Scanning/Listening)
COLOR_WARNING = QColor(255, 140, 0)          # Deep Orange
COLOR_CRITICAL = QColor(220, 20, 60)         # Crimson Red
COLOR_SUCCESS = QColor(50, 205, 50)          # Tactical Green


class BootSequence(QWidget):
    """
    Cinematic boot sequence animation.
    Shows hex codes, initialization messages, and radar warm-up.
    """
    boot_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 200)
        
        # Boot phases
        self.phase = 0  # 0=hex, 1=messages, 2=complete
        self.phase_progress = 0.0
        self.opacity = 1.0
        
        # Hex code animation
        self.hex_lines = []
        self.current_hex_chars = 0
        self.max_hex_chars = 200
        
        # Status messages
        self.messages = [
            "WAYNE ENTERPRISES SECURE BOOT v3.2.1",
            "INITIALIZING NEURAL INTERFACE...",
            "LOADING TACTICAL SYSTEMS...",
            "CALIBRATING AUDIO SENSORS...",
            "ESTABLISHING SECURE UPLINK...",
            "SYSTEM READY"
        ]
        self.visible_messages = []
        self.message_index = 0
        
        # Fonts
        self.hex_font = QFont("Consolas", 8)
        self.msg_font = QFont("Consolas", 10)
        self.msg_font.setBold(True)
        self.title_font = QFont("Consolas", 12)
        self.title_font.setBold(True)
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        
        # Generate hex data
        self._generate_hex()
        
    def _generate_hex(self):
        """Generate random hex strings for background."""
        for _ in range(8):
            line = ''.join(random.choice('0123456789ABCDEF') for _ in range(60))
            self.hex_lines.append(line)
    
    def start(self):
        """Begin the boot sequence."""
        self.phase = 0
        self.phase_progress = 0.0
        self.current_hex_chars = 0
        self.visible_messages = []
        self.message_index = 0
        self.opacity = 1.0
        self.show()
        self.timer.start(30)
    
    def animate(self):
        if self.phase == 0:  # Hex reveal phase
            self.current_hex_chars = min(self.current_hex_chars + 8, self.max_hex_chars)
            self.phase_progress = self.current_hex_chars / self.max_hex_chars
            
            if self.phase_progress >= 1.0:
                self.phase = 1
                self.phase_progress = 0.0
                
        elif self.phase == 1:  # Message reveal phase
            self.phase_progress += 0.03
            
            # Add messages progressively
            messages_to_show = int(self.phase_progress * len(self.messages))
            while len(self.visible_messages) < messages_to_show and len(self.visible_messages) < len(self.messages):
                self.visible_messages.append(self.messages[len(self.visible_messages)])
            
            if len(self.visible_messages) >= len(self.messages) and self.phase_progress > 1.2:
                self.phase = 2
                self.phase_progress = 0.0
                
        elif self.phase == 2:  # Fade out phase
            self.opacity -= 0.05
            if self.opacity <= 0:
                self.timer.stop()
                self.hide()
                self.boot_complete.emit()
                return
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.opacity)
        
        w, h = self.width(), self.height()
        
        # Background
        bg_grad = QLinearGradient(0, 0, 0, h)
        bg_grad.setColorAt(0, QColor(5, 8, 12, 245))
        bg_grad.setColorAt(1, QColor(15, 20, 25, 245))
        painter.setBrush(QBrush(bg_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 4, 4)
        
        # Border
        border_pen = QPen(COLOR_ACCENT)
        border_pen.setWidth(2)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(1, 1, w-2, h-2, 4, 4)
        
        # Corner accents
        corner_len = 20
        thick_pen = QPen(COLOR_ACCENT)
        thick_pen.setWidth(3)
        painter.setPen(thick_pen)
        
        # Top Left
        painter.drawLine(0, 0, corner_len, 0)
        painter.drawLine(0, 0, 0, corner_len)
        # Top Right
        painter.drawLine(w, 0, w-corner_len, 0)
        painter.drawLine(w, 0, w, corner_len)
        # Bottom Left
        painter.drawLine(0, h, corner_len, h)
        painter.drawLine(0, h, 0, h-corner_len)
        # Bottom Right
        painter.drawLine(w, h, w-corner_len, h)
        painter.drawLine(w, h, w, h-corner_len)
        
        # Hex code background (dim)
        painter.setFont(self.hex_font)
        hex_color = QColor(COLOR_ACCENT)
        hex_color.setAlpha(40)
        painter.setPen(hex_color)
        
        chars_drawn = 0
        for i, line in enumerate(self.hex_lines):
            y = 20 + i * 12
            chars_to_draw = min(len(line), self.current_hex_chars - chars_drawn)
            if chars_to_draw > 0:
                painter.drawText(15, y, line[:chars_to_draw])
                chars_drawn += chars_to_draw
            if chars_drawn >= self.current_hex_chars:
                break
        
        # Status messages
        painter.setFont(self.msg_font)
        for i, msg in enumerate(self.visible_messages):
            y = 40 + i * 22
            
            # Highlight "SYSTEM READY"
            if msg == "SYSTEM READY":
                painter.setPen(COLOR_SUCCESS)
            else:
                painter.setPen(COLOR_TEXT)
            
            # Add blinking cursor effect for latest message
            display_msg = msg
            if i == len(self.visible_messages) - 1 and self.phase == 1:
                if int(self.phase_progress * 10) % 2 == 0:
                    display_msg += "_"
            
            painter.drawText(20, y, "> " + display_msg)
        
        # Title bar
        painter.setFont(self.title_font)
        painter.setPen(COLOR_ACCENT)
        title_rect = QRectF(0, h - 30, w, 25)
        painter.drawText(title_rect, int(Qt.AlignmentFlag.AlignCenter), "[ WAYNE ENTERPRISES ]")


class SystemDiagnosticsPanel(QWidget):
    """
    Compact system diagnostics panel showing CPU, RAM, and Battery.
    Updates every 2 seconds with color-coded status.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 80)
        
        # System stats
        self.cpu_percent = 0.0
        self.ram_percent = 0.0
        self.battery_percent = 100.0
        self.battery_charging = False
        self.has_battery = True
        
        # Fonts
        self.label_font = QFont("Consolas", 8)
        self.value_font = QFont("Consolas", 9)
        self.value_font.setBold(True)
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_stats)
        self.update_timer.start(DIAGNOSTICS_INTERVAL)  # Use config interval for CPU savings
        
        # Initial update
        self._update_stats()
    
    def _update_stats(self):
        """Fetch current system stats."""
        try:
            import psutil
            self.cpu_percent = psutil.cpu_percent(interval=None)
            self.ram_percent = psutil.virtual_memory().percent
            
            battery = psutil.sensors_battery()
            if battery:
                self.battery_percent = battery.percent
                self.battery_charging = battery.power_plugged
                self.has_battery = True
            else:
                self.has_battery = False
        except Exception:
            pass
        
        self.update()
    
    def _get_color_for_percent(self, percent):
        """Return color based on percentage (green->amber->red)."""
        if percent < 60:
            return COLOR_SUCCESS
        elif percent < 80:
            return COLOR_WARNING
        else:
            return COLOR_CRITICAL
    
    def _get_battery_color(self, percent, charging):
        """Return color for battery (inverted - low is bad)."""
        if charging:
            return COLOR_ACTIVE_SCAN
        if percent > 40:
            return COLOR_SUCCESS
        elif percent > 15:
            return COLOR_WARNING
        else:
            return COLOR_CRITICAL
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # Background (semi-transparent)
        bg_color = QColor(10, 12, 15, 180)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 4, 4)
        
        # Border
        border_pen = QPen(COLOR_BORDER)
        border_pen.setWidth(1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(0, 0, w-1, h-1, 4, 4)
        
        # Draw stats
        y_offset = 12
        bar_width = 80
        bar_height = 8
        bar_x = 45
        
        # CPU
        self._draw_stat_row(painter, "CPU", self.cpu_percent, 
                           bar_x, y_offset, bar_width, bar_height,
                           self._get_color_for_percent(self.cpu_percent))
        
        # RAM
        self._draw_stat_row(painter, "RAM", self.ram_percent,
                           bar_x, y_offset + 22, bar_width, bar_height,
                           self._get_color_for_percent(self.ram_percent))
        
        # Battery
        if self.has_battery:
            label = "BAT" + ("+" if self.battery_charging else "")
            self._draw_stat_row(painter, label, self.battery_percent,
                               bar_x, y_offset + 44, bar_width, bar_height,
                               self._get_battery_color(self.battery_percent, self.battery_charging))
        else:
            # Show "AC" for desktop
            painter.setFont(self.label_font)
            painter.setPen(COLOR_TEXT_DIM)
            painter.drawText(10, y_offset + 52, "PWR")
            painter.setPen(COLOR_SUCCESS)
            painter.setFont(self.value_font)
            painter.drawText(bar_x, y_offset + 52, "AC POWER")
    
    def _draw_stat_row(self, painter, label, percent, bar_x, y, bar_w, bar_h, color):
        """Draw a single stat row with label, bar, and percentage."""
        # Label
        painter.setFont(self.label_font)
        painter.setPen(COLOR_TEXT_DIM)
        painter.drawText(8, y + bar_h, label)
        
        # Bar background
        bg_rect = QRectF(bar_x, y, bar_w, bar_h)
        painter.setBrush(QBrush(QColor(30, 35, 40)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bg_rect, 2, 2)
        
        # Bar fill
        fill_width = (percent / 100.0) * bar_w
        fill_rect = QRectF(bar_x, y, fill_width, bar_h)
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(fill_rect, 2, 2)
        
        # Percentage text
        painter.setFont(self.value_font)
        painter.setPen(COLOR_TEXT)
        text_x = bar_x + bar_w + 5
        painter.drawText(int(text_x), y + bar_h, f"{int(percent)}%")


class StatusIndicators(QWidget):
    """
    Small status icons showing system states.
    Displays: Microphone, Speaker, Connection status.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 25)
        
        # Status states
        self.mic_active = False
        self.speaker_active = False
        self.connected = True
        
        # Icons (using unicode symbols)
        self.MIC_ON = "🎤"
        self.MIC_OFF = "🔇"
        self.SPEAKER_ON = "🔊"
        self.SPEAKER_OFF = "🔈"
        self.CONNECTED = "●"
        self.DISCONNECTED = "○"
        
        # Font for icons
        self.icon_font = QFont("Segoe UI Emoji", 10)
        self.dot_font = QFont("Consolas", 12)
        self.dot_font.setBold(True)
        
    def set_mic_active(self, active):
        self.mic_active = active
        self.update()
        
    def set_speaker_active(self, active):
        self.speaker_active = active
        self.update()
        
    def set_connected(self, connected):
        self.connected = connected
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        y_center = h // 2 + 4
        
        # Spacing for icons
        spacing = 30
        x = 10
        
        # Microphone status
        mic_color = COLOR_SUCCESS if self.mic_active else COLOR_TEXT_DIM
        painter.setPen(mic_color)
        painter.setFont(self.icon_font)
        painter.drawText(x, y_center, self.MIC_ON if self.mic_active else self.MIC_OFF)
        
        # Speaker status
        x += spacing
        speaker_color = COLOR_SUCCESS if self.speaker_active else COLOR_TEXT_DIM
        painter.setPen(speaker_color)
        painter.drawText(x, y_center, self.SPEAKER_ON if self.speaker_active else self.SPEAKER_OFF)
        
        # Connection status (simple dot)
        x += spacing
        painter.setFont(self.dot_font)
        conn_color = COLOR_SUCCESS if self.connected else COLOR_CRITICAL
        painter.setPen(conn_color)
        painter.drawText(x, y_center, self.CONNECTED if self.connected else self.DISCONNECTED)


class WaveformVisualizer(QWidget):
    """
    Animated audio waveform bars for speech visualization.
    Shows dynamic bars when ALFRED is speaking.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 30)
        
        # Bar configuration
        self.num_bars = 20
        self.bar_width = 6
        self.bar_spacing = 3
        self.max_height = 25
        self.min_height = 3
        
        # Current and target heights for smooth animation
        self.current_heights = [self.min_height] * self.num_bars
        self.target_heights = [self.min_height] * self.num_bars
        
        # State
        self.is_speaking = False
        self.color = COLOR_SYSTEM_OK
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(WAVEFORM_INTERVAL)  # Use config interval for CPU savings
    
    def set_speaking(self, speaking):
        """Enable/disable waveform animation."""
        self.is_speaking = speaking
        if not speaking:
            # Fade out to minimum
            self.target_heights = [self.min_height] * self.num_bars
    
    def set_color(self, color):
        """Set the waveform color."""
        self.color = color
    
    def _animate(self):
        """Update bar heights with smooth interpolation."""
        if self.is_speaking:
            # Generate random target heights with wave-like pattern
            for i in range(self.num_bars):
                # Create a wave pattern with randomness
                wave = math.sin(i * 0.5 + random.random() * 2) * 0.5 + 0.5
                randomness = random.random() * 0.6
                combined = wave * 0.4 + randomness * 0.6
                self.target_heights[i] = self.min_height + (self.max_height - self.min_height) * combined
        
        # Smooth interpolation towards targets
        for i in range(self.num_bars):
            diff = self.target_heights[i] - self.current_heights[i]
            self.current_heights[i] += diff * 0.3
        
        self.update()
    
    def paintEvent(self, event):
        if not any(h > self.min_height + 1 for h in self.current_heights):
            return  # Don't paint if all bars are at minimum
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        center_y = h // 2
        
        # Calculate starting x to center the bars
        total_width = self.num_bars * self.bar_width + (self.num_bars - 1) * self.bar_spacing
        start_x = (w - total_width) // 2
        
        for i, bar_height in enumerate(self.current_heights):
            x = start_x + i * (self.bar_width + self.bar_spacing)
            half_height = bar_height / 2
            
            # Draw bar (centered vertically)
            bar_color = QColor(self.color)
            bar_color.setAlpha(int(180 + 75 * (bar_height / self.max_height)))
            
            # Gradient effect
            gradient = QLinearGradient(x, center_y - half_height, x, center_y + half_height)
            gradient.setColorAt(0, bar_color)
            c2 = QColor(self.color)
            c2.setAlpha(100)
            gradient.setColorAt(1, c2)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                QRectF(x, center_y - half_height, self.bar_width, bar_height),
                2, 2
            )


class TechBubble(QWidget):
    """
    Tactical Info Bubble.
    Sharp edges, specific techno-industrial framing.
    """
    def __init__(self, text=""):
        super().__init__()
        self.full_text = text
        self.displayed_text = ""
        self.opacity = 0.0
        self.target_opacity = 0.0
        
        # Sizing Config
        self.MAX_WIDTH = 420
        self.MAX_HEIGHT = 320
        self.MIN_HEIGHT = 90
        self.PADDING = 20
        self.BORDER_RADIUS = 2  # Sharp, nearly square corners
        
        # Typography - Header font for ALFRED prefix
        self.header_font = QFont("Consolas", 11)
        self.header_font.setBold(True)
        self.header_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        
        # Tactical Font for body text
        self.font = QFont("Consolas", 10)
        if not self.font.exactMatch():
            self.font = QFont("Courier New", 10)
        self.font.setBold(True)
        self.font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.5)
        
        # Prefix configuration
        self.show_prefix = True
        self.prefix_text = "ALFRED:"
        self.prefix_height = 18  # Height reserved for prefix line
        
        # Initial geometry
        self.setFixedWidth(self.MAX_WIDTH)
        self.setFixedHeight(self.MIN_HEIGHT)
        
        # Animation phase
        self.scan_line_y = 0.0

        # Typewriter Timer
        self.typewriter_timer = QTimer()
        self.typewriter_timer.timeout.connect(self.update_typewriter)
        self.char_index = 0
        
        # Animation Timer
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(ANIM_INTERVAL)  # Use config interval for CPU savings
        
        # Scroll State
        self.scroll_y = 0
        self.max_scroll = 0
        
        self.border_color = COLOR_BORDER
        self.target_border_color = COLOR_BORDER
        
        # Waveform visualizer (positioned at bottom of bubble)
        self.waveform = WaveformVisualizer(self)
        self.waveform.move(10, self.height() - 35)
        self.waveform.hide()
        
        # Particle system for floating data effect
        self.particles = []
        self.max_particles = 10  # Reduced from 25 for CPU savings
        self._init_particles()
        
    def set_border_color(self, color):
        self.target_border_color = color
        self.waveform.set_color(color)
    
    def set_speaking(self, speaking):
        """Enable/disable waveform animation for speech visualization."""
        self.waveform.set_speaking(speaking)
        if speaking:
            self.waveform.show()
        else:
            # Hide after animation fades out
            QTimer.singleShot(500, lambda: self.waveform.hide() if not self.waveform.is_speaking else None)
    
    def _init_particles(self):
        """Initialize floating particles."""
        for _ in range(self.max_particles):
            self.particles.append({
                'x': random.randint(10, self.MAX_WIDTH - 10),
                'y': random.randint(10, self.MAX_HEIGHT),
                'speed': random.uniform(0.3, 1.0),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(0.1, 0.4),
                'drift': random.uniform(-0.2, 0.2)
            })
    
    def _update_particles(self):
        """Update particle positions."""
        for p in self.particles:
            # Move upward
            p['y'] -= p['speed']
            # Slight horizontal drift
            p['x'] += p['drift']
            
            # Reset particle when it goes off screen
            if p['y'] < 0:
                p['y'] = self.height()
                p['x'] = random.randint(10, self.width() - 10)
                p['alpha'] = random.uniform(0.1, 0.4)
    
    def animate(self):
        self.scan_line_y = (self.scan_line_y + 2) % self.height()
        
        # Smooth opacity
        self.opacity += (self.target_opacity - self.opacity) * 0.2
        
        # Smooth color
        if self.border_color != self.target_border_color:
            self.border_color = self._lerp_color(self.border_color, self.target_border_color, 0.15)
        
        # Update particles
        self._update_particles()
        
        self.update()
    
    def _lerp_color(self, c1, c2, t):
        return QColor(
            int(c1.red() + (c2.red() - c1.red()) * t),
            int(c1.green() + (c2.green() - c1.green()) * t),
            int(c1.blue() + (c2.blue() - c1.blue()) * t),
            int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
        )

    def set_text(self, text):
        if not text:
            self.target_opacity = 0.0
            self.typewriter_timer.stop()
        else:
            self.full_text = text
            self.displayed_text = ""
            self.char_index = 0
            self.target_opacity = 1.0
            self.scroll_y = 0
            
            # Sizing logic
            metrics = QFontMetrics(self.font)
            text_width = self.MAX_WIDTH - (self.PADDING * 2)
            rect = metrics.boundingRect(0, 0, text_width, 0, Qt.TextFlag.TextWordWrap, text)
            required_height = rect.height() + (self.PADDING * 2) + 10
            new_height = max(self.MIN_HEIGHT, min(required_height, self.MAX_HEIGHT))
            self.setFixedHeight(new_height)
            
            speed = max(5, min(30, 1000 // max(len(text), 1)))
            self.typewriter_timer.start(speed)
            
        self.update()

    def update_typewriter(self):
        if self.char_index < len(self.full_text):
            self.displayed_text += self.full_text[self.char_index]
            self.char_index += 1
            
            # Auto-scroll
            metrics = QFontMetrics(self.font)
            text_width = self.width() - (self.PADDING * 2)
            current_rect = metrics.boundingRect(0, 0, text_width, 0, Qt.TextFlag.TextWordWrap, self.displayed_text)
            
            if current_rect.height() > (self.height() - self.PADDING * 2):
                self.scroll_y = current_rect.height() - (self.height() - self.PADDING * 2)
                
            self.update()
        else:
            self.typewriter_timer.stop()
            
    def paintEvent(self, event):
        if self.target_opacity == 0 and self.opacity < 0.05:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.opacity)
        
        w, h = self.width(), self.height()
        
        # --- BACKGROUND (Carbon Fiber / Matte Mesh feel) ---
        bg_brush = QBrush(COLOR_BG_DARK)
        painter.setBrush(bg_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, self.BORDER_RADIUS, self.BORDER_RADIUS)
        
        # --- GRID OVERLAY (SUBTLE) ---
        grid_pen = QPen(QColor(255, 255, 255, 10))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        for i in range(0, w, 20):
            painter.drawLine(i, 0, i, h)
        
        # --- FLOATING PARTICLES ---
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            particle_color = QColor(self.border_color)
            particle_color.setAlphaF(p['alpha'] * 0.5)
            painter.setBrush(QBrush(particle_color))
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])
        
        # --- BORDER & CORNER ACCENTS ---
        border_pen = QPen(self.border_color)
        border_pen.setWidth(1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(1, 1, w-2, h-2, self.BORDER_RADIUS, self.BORDER_RADIUS)
        
        # Thick corners (Tactical brackets)
        corner_len = 15
        thick_pen = QPen(self.border_color)
        thick_pen.setWidth(3)
        painter.setPen(thick_pen)
        
        # Top Left
        painter.drawLine(0, 0, corner_len, 0)
        painter.drawLine(0, 0, 0, corner_len)
        # Top Right
        painter.drawLine(w, 0, w-corner_len, 0)
        painter.drawLine(w, 0, w, corner_len)
        # Bottom Left
        painter.drawLine(0, h, corner_len, h)
        painter.drawLine(0, h, 0, h-corner_len)
        # Bottom Right
        painter.drawLine(w, h, w-corner_len, h)
        painter.drawLine(w, h, w, h-corner_len)

        # --- TEXT ---
        text_y_offset = self.PADDING
        
        # Draw ALFRED prefix if enabled and we have text
        if self.show_prefix and self.displayed_text:
            painter.setClipRect(self.PADDING, self.PADDING, w - 2*self.PADDING, h - 2*self.PADDING)
            painter.setFont(self.header_font)
            painter.setPen(COLOR_ACCENT)  # Amber color for prefix
            painter.drawText(self.PADDING, self.PADDING + 12, self.prefix_text)
            text_y_offset = self.PADDING + self.prefix_height
        
        # Draw main text
        painter.setClipRect(self.PADDING, text_y_offset, w - 2*self.PADDING, h - self.PADDING - text_y_offset)
        painter.setPen(COLOR_TEXT)
        painter.setFont(self.font)
        
        text_rect = QRectF(self.PADDING, text_y_offset - self.scroll_y, w - 2*self.PADDING, 10000)
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap), self.displayed_text)
        
        # --- SCAN LINE (Subtle vertical scan) ---
        painter.setClipping(False)
        scan_pen = QPen(QColor(255, 255, 255, 15))
        scan_pen.setWidth(2)
        painter.setPen(scan_pen)
        painter.drawLine(0, int(self.scan_line_y), w, int(self.scan_line_y))



class WayneSystemStatus(QWidget):
    """
    Tactical Radar / System Status Indicator.
    Replaces the 'Jarvis Arc Reactor'.
    """
    clicked = pyqtSignal()  # Signal emitted when clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Show hand cursor
        
        self.sweep_angle = 0.0
        self.active = False
        self.pulse_radius = 0.0
        
        self.current_color = COLOR_SYSTEM_OK
        self.target_color = COLOR_SYSTEM_OK
        
        # Breathing animation
        self.breathing_phase = 0.0
        self.breathing_intensity = 0.0  # Current intensity (for smooth transitions)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(ANIM_INTERVAL)  # Use config interval for CPU savings
        
        self.blips = [] # Random radar blips
        
    def set_color(self, color):
        self.target_color = color
        
    def set_active(self, active):
        self.active = active

    def mousePressEvent(self, event):
        """Handle click to wake."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            # Play click sound
            if SOUNDS_AVAILABLE:
                sounds.play_click()
            # Visual feedback
            self.pulse_radius = 0
            self.set_color(COLOR_ACTIVE_SCAN)
            QTimer.singleShot(200, lambda: self.set_color(COLOR_SYSTEM_OK))
        
    def animate(self):
        # Rotation speed
        speed = 4.0 if self.active else 1.5
        self.sweep_angle = (self.sweep_angle + speed) % 360
        
        # Pulse
        self.pulse_radius += 1.0
        if self.pulse_radius > 60:
            self.pulse_radius = 0
        
        # Breathing animation (only when not active)
        self.breathing_phase += 0.03
        if self.breathing_phase > 2 * math.pi:
            self.breathing_phase -= 2 * math.pi
        
        # Smooth breathing intensity transition
        target_intensity = 0.0 if self.active else 1.0
        self.breathing_intensity += (target_intensity - self.breathing_intensity) * 0.1
            
        # Color Interp
        if self.current_color != self.target_color:
            self.current_color = self._lerp_color(self.current_color, self.target_color, 0.1)

        # Random blips management
        if random.random() < 0.05 and self.active:
            self.blips.append({'r': random.randint(10, 50), 'a': random.randint(0, 360), 'life': 1.0})
        
        for blip in self.blips:
            blip['life'] -= 0.02
        self.blips = [b for b in self.blips if b['life'] > 0]
            
        self.update()

    def _lerp_color(self, c1, c2, t):
        return QColor(
            int(c1.red() + (c2.red() - c1.red()) * t),
            int(c1.green() + (c2.green() - c1.green()) * t),
            int(c1.blue() + (c2.blue() - c1.blue()) * t)
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = 75, 75
        
        # --- BASE RADAR GRID ---
        grid_color = QColor(self.current_color)
        grid_color.setAlpha(80)
        grid_pen = QPen(grid_color)
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Concentric circles
        painter.drawEllipse(QPointF(cx, cy), 20, 20)
        painter.drawEllipse(QPointF(cx, cy), 40, 40)
        painter.drawEllipse(QPointF(cx, cy), 60, 60)
        
        # Crosshairs
        painter.drawLine(cx - 65, cy, cx + 65, cy)
        painter.drawLine(cx, cy - 65, cx, cy + 65)
        
        # --- RADAR SWEEP ---
        scan_grad = QConicalGradient(cx, cy, -self.sweep_angle)
        c = self.current_color
        scan_grad.setColorAt(0, QColor(0, 0, 0, 0))
        scan_grad.setColorAt(0.75, QColor(0, 0, 0, 0))
        scan_grad.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 180))
        
        painter.setBrush(QBrush(scan_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 62, 62)
        
        # --- BLIPS ---
        for blip in self.blips:
            # Draw blip if sweep just passed it? 
            # Simplified: just draw fading blips
            bx = cx + blip['r'] * math.cos(math.radians(blip['a']))
            by = cy + blip['r'] * math.sin(math.radians(blip['a']))
            
            blip_color = QColor(self.current_color)
            blip_color.setAlphaF(blip['life'])
            
            painter.setBrush(QBrush(blip_color))
            painter.drawEllipse(QPointF(bx, by), 3, 3)

        # --- OUTER RING (Rotates slowly opposite) ---
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.sweep_angle * 0.3)
        
        outer_pen = QPen(self.current_color)
        outer_pen.setWidth(2)
        painter.setPen(outer_pen)
        
        # Draw segmented ring
        for i in range(0, 360, 45):
            painter.drawArc(QRectF(-68, -68, 136, 136), i * 16, 30 * 16)
            
        painter.restore()
        
        # --- BREATHING GLOW (when idle) ---
        if self.breathing_intensity > 0.05:
            # Calculate breathing glow intensity using sine wave
            glow_strength = (math.sin(self.breathing_phase) * 0.5 + 0.5) * self.breathing_intensity
            
            # Draw multiple expanding glow rings
            for ring in range(3):
                glow_alpha = int(40 * glow_strength * (1 - ring * 0.3))
                if glow_alpha > 0:
                    glow_color = QColor(self.current_color)
                    glow_color.setAlpha(glow_alpha)
                    glow_pen = QPen(glow_color)
                    glow_pen.setWidth(2 + ring)
                    painter.setPen(glow_pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    radius = 65 + ring * 4 + glow_strength * 3
                    painter.drawEllipse(QPointF(cx, cy), radius, radius)


class OverlayWindow(QWidget):
    """
    Main Overlay Container.
    Transparent, click-through, always-on-top.
    Draggable via mouse.
    """
    wake_request = pyqtSignal() # Propagate up
    boot_complete = pyqtSignal()  # Emitted when boot animation finishes

    def __init__(self):
        super().__init__()
        
        # Window Flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True) 
        # Removed ShowWithoutActivating to allow mouse interaction
        
        self.setFixedSize(650, 280)  # Increased height for diagnostics
        
        # Main horizontal layout
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)
        
        # Text bubble (left side)
        self.bubble = TechBubble()
        self.layout.addWidget(self.bubble)
        
        # Right side container (radar + diagnostics + status stacked vertically)
        from PyQt6.QtWidgets import QVBoxLayout, QWidget as QW
        right_container = QW()
        right_container.setFixedWidth(160)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Radar widget
        self.radar = WayneSystemStatus()
        self.radar.clicked.connect(self.wake_request.emit)
        right_layout.addWidget(self.radar, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # System diagnostics panel
        self.diagnostics = SystemDiagnosticsPanel()
        right_layout.addWidget(self.diagnostics, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Status indicators
        self.status_indicators = StatusIndicators()
        right_layout.addWidget(self.status_indicators, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.layout.addWidget(right_container)
        self.right_container = right_container  # Keep reference
        
        # Boot sequence (positioned over the overlay)
        self.boot_sequence = BootSequence(self)
        self.boot_sequence.boot_complete.connect(self._on_boot_complete)
        self.boot_sequence.hide()
        self._boot_completed = False
        
        # Minimize state
        self._minimized = False
        self._expanded_size = (650, 280)
        self._minimized_size = (180, 280)
        
        # Drag mechanics
        self.old_pos = None
        self._click_time = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            # Track click time for double-click detection
            import time
            current_time = time.time()
            if current_time - self._click_time < 0.3:  # Double click
                self.toggle_minimize()
            self._click_time = current_time

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
    
    def toggle_minimize(self):
        """Toggle between minimized (radar only) and expanded (full) mode."""
        self._minimized = not self._minimized
        
        if self._minimized:
            # Hide bubble, show only radar + diagnostics
            self.bubble.hide()
            self.setFixedSize(*self._minimized_size)
        else:
            # Show everything
            self.bubble.show()
            self.setFixedSize(*self._expanded_size)
    
    def contextMenuEvent(self, event):
        """Show right-click context menu with position presets."""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0a0c0f;
                color: #dce6f0;
                border: 1px solid #6495ed;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #1a1f25;
            }
        """)
        
        # Position options
        top_left = QAction("↖ Top Left", self)
        top_left.triggered.connect(lambda: self._move_to_position("top_left"))
        menu.addAction(top_left)
        
        top_right = QAction("↗ Top Right", self)
        top_right.triggered.connect(lambda: self._move_to_position("top_right"))
        menu.addAction(top_right)
        
        bottom_left = QAction("↙ Bottom Left", self)
        bottom_left.triggered.connect(lambda: self._move_to_position("bottom_left"))
        menu.addAction(bottom_left)
        
        bottom_right = QAction("↘ Bottom Right", self)
        bottom_right.triggered.connect(lambda: self._move_to_position("bottom_right"))
        menu.addAction(bottom_right)
        
        menu.addSeparator()
        
        center = QAction("◎ Center", self)
        center.triggered.connect(lambda: self._move_to_position("center"))
        menu.addAction(center)
        
        menu.addSeparator()
        
        # Minimize toggle
        min_action = QAction("⊟ Minimize" if not self._minimized else "⊞ Expand", self)
        min_action.triggered.connect(self.toggle_minimize)
        menu.addAction(min_action)
        
        menu.exec(event.globalPos())
    
    def _move_to_position(self, position):
        """Move window to a preset position."""
        screen = QApplication.primaryScreen()
        if not screen:
            return
            
        available = screen.availableGeometry()
        margin = 30
        
        if position == "top_left":
            x = available.x() + margin
            y = available.y() + margin
        elif position == "top_right":
            x = available.x() + available.width() - self.width() - margin
            y = available.y() + margin
        elif position == "bottom_left":
            x = available.x() + margin
            y = available.y() + available.height() - self.height() - margin
        elif position == "bottom_right":
            x = available.x() + available.width() - self.width() - margin
            y = available.y() + available.height() - self.height() - margin
        elif position == "center":
            x = available.x() + (available.width() - self.width()) // 2
            y = available.y() + (available.height() - self.height()) // 2
        else:
            return
        
        self.move(x, y)
        
    def showEvent(self, event):
        # Initial position bottom right
        # We only do this ONCE or if it's way off screen
        # For now, let's stick to the corner but allow movement
        if self.pos().x() == 0 and self.pos().y() == 0:
            self._position_bottom_right()
        
        # Start boot sequence on first show
        if not self._boot_completed:
            self.start_boot_sequence()
            
        super().showEvent(event)
        
    def _position_bottom_right(self):
        screen = QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            margin = 30
            window_x = available.x() + available.width() - self.width() - margin
            window_y = available.y() + available.height() - self.height() - margin
            self.move(window_x, window_y)
    
    def start_boot_sequence(self):
        """Start the cinematic boot animation."""
        # Center boot sequence in window
        self.boot_sequence.move(
            (self.width() - self.boot_sequence.width()) // 2,
            (self.height() - self.boot_sequence.height()) // 2
        )
        # Hide main components during boot
        self.bubble.hide()
        self.boot_sequence.start()
        # Play boot beep
        if SOUNDS_AVAILABLE:
            sounds.play_boot_beep()
    
    def _on_boot_complete(self):
        """Called when boot animation finishes."""
        self._boot_completed = True
        self.bubble.show()
        # Play success sound
        if SOUNDS_AVAILABLE:
            sounds.play_success()
        self.boot_complete.emit()
            
    def set_text(self, text):
        # Don't show text during boot sequence
        if not self._boot_completed:
            return
            
        if text:
            self.radar.set_active(True)
            self.bubble.set_text(text)
            self.bubble.show()
        else:
            self.radar.set_active(False)
            self.bubble.set_text("")
            
    def set_sentiment_color(self, color):
        self.radar.set_color(color)
        self.bubble.set_border_color(color)
    
    def set_speaking(self, speaking):
        """Enable/disable waveform animation for speech visualization."""
        self.bubble.set_speaking(speaking)
        # Also update speaker status indicator
        self.status_indicators.set_speaker_active(speaking)
    
    def set_mic_active(self, active):
        """Update microphone status indicator."""
        self.status_indicators.set_mic_active(active)
    
    def set_connected(self, connected):
        """Update connection status indicator."""
        self.status_indicators.set_connected(connected)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OverlayWindow()
    win.set_sentiment_color(COLOR_SYSTEM_OK)
    win.show()
    
    # Test Loop - waits for boot to complete
    def cycle_modes():
        import itertools
        colors = itertools.cycle([COLOR_ACTIVE_SCAN, COLOR_WARNING, COLOR_CRITICAL, COLOR_SYSTEM_OK])
        texts = itertools.cycle([
            "SCANNING PERIMETER...",
            "WARNING: INTRUSION DETECTED IN SECTOR 7",
            "CRITICAL FAILURE: BATMOBILE REMOTE LINK LOST",
            "SYSTEM NOMINAL"
        ])
        
        def update():
            c = next(colors)
            t = next(texts)
            win.set_sentiment_color(c)
            win.set_text(t)
            # Simulate speaking for 2 seconds
            win.set_speaking(True)
            QTimer.singleShot(2000, lambda: win.set_speaking(False))
            QTimer.singleShot(4000, update)
        
        # Start first update after boot completes
        def on_boot_done():
            win.set_text("WAYNE ENTERPRISES SERVER ONLINE\nAUTHENTICATION VERIFIED.")
            win.set_speaking(True)
            QTimer.singleShot(2000, lambda: win.set_speaking(False))
            QTimer.singleShot(3000, update)
        
        win.boot_complete.connect(on_boot_done)
        
    cycle_modes()
    sys.exit(app.exec())
