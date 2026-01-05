import sys
import math
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPolygonF, QFont, QConicalGradient, QFontMetrics, QRegion

# --- CONFIG ---
COLOR_CYAN = QColor(0, 255, 255)
COLOR_DEEP_BLUE = QColor(0, 40, 60, 200)
COLOR_WHITE = QColor(255, 255, 255)
COLOR_ACTIVE = QColor(0, 255, 180) # Slight greenish-cyan for listening

# --- SENTIMENT COLORS ---
COLOR_HAPPY = QColor(0, 255, 100)      # Green - Success/Positive
COLOR_ALERT = QColor(255, 165, 0)      # Orange - Warning/Alert
COLOR_ERROR = QColor(255, 50, 50)      # Red - Error/Danger
COLOR_NEUTRAL = QColor(0, 255, 255)    # Cyan - Default state

class TechBubble(QWidget):
    """
    Advanced TechBubble with Dynamic Sizing and Auto-Scrolling.
    """
    def __init__(self, text=""):
        super().__init__()
        self.full_text = text
        self.displayed_text = ""
        self.opacity = 0.0
        self.target_opacity = 0.0
        
        # Sizing Config
        self.MAX_WIDTH = 400   # Maximum width (less wide than before)
        self.MAX_HEIGHT = 300  # Maximum height before scrolling
        self.MIN_HEIGHT = 80   # Minimum height for short texts
        self.PADDING = 20
        
        # Setup Font
        self.font = QFont("Consolas", 11) 
        self.font.setBold(False)
        
        # Initial geometry
        self.setFixedWidth(self.MAX_WIDTH)
        self.setFixedHeight(self.MIN_HEIGHT)

        # Typewriter Timer
        self.typewriter_timer = QTimer()
        self.typewriter_timer.timeout.connect(self.update_typewriter)
        self.char_index = 0
        
        # Scroll State
        self.scroll_y = 0
        self.max_scroll = 0  # Maximum scrollable distance
        
        # Enable mouse tracking for scroll events
        self.setMouseTracking(True)

    def set_text(self, text):
        if not text:
            self.target_opacity = 0.0
            self.typewriter_timer.stop()
        else:
            self.full_text = text
            self.displayed_text = ""
            self.char_index = 0
            self.target_opacity = 1.0
            self.scroll_y = 0 # Reset scroll
            
            # 1. CALCULATE REQUIRED SIZE
            # We measure how tall the full text WILL be
            metrics = QFontMetrics(self.font)
            # Width available for text
            text_width = self.MAX_WIDTH - (self.PADDING * 2)
            
            # Calculate bounding rect for the full text
            rect = metrics.boundingRect(
                0, 0, text_width, 0, 
                Qt.TextFlag.TextWordWrap, 
                text
            )
            
            required_height = rect.height() + (self.PADDING * 2) + 10
            
            # 2. APPLY DYNAMIC SIZING
            # Clamp between MIN and MAX
            new_height = max(self.MIN_HEIGHT, min(required_height, self.MAX_HEIGHT))
            self.setFixedHeight(new_height)
            
            # Start Typewriter
            speed = max(10, min(50, 1500 // len(text)))
            self.typewriter_timer.start(speed)
            
        self.update()

    def update_typewriter(self):
        if self.char_index < len(self.full_text):
            self.displayed_text += self.full_text[self.char_index]
            self.char_index += 1
            
            # 3. AUTO-SCROLL LOGIC
            # Measure height of currently visible text
            metrics = QFontMetrics(self.font)
            text_width = self.width() - (self.PADDING * 2)
            
            current_rect = metrics.boundingRect(
                0, 0, text_width, 0, 
                Qt.TextFlag.TextWordWrap, 
                self.displayed_text
            )
            
            text_height = current_rect.height()
            visible_height = self.height() - (self.PADDING * 2)
            
            # Calculate max scroll distance
            self.max_scroll = max(0, text_height - visible_height)
            
            # If text is taller than window, scroll up (auto-scroll to bottom)
            if text_height > visible_height:
                self.scroll_y = self.max_scroll
            
            self.update()
        else:
            self.typewriter_timer.stop()
    
    def wheelEvent(self, event):
        """Handle mouse wheel scrolling"""
        # Get scroll delta (positive = scroll up, negative = scroll down)
        delta = event.angleDelta().y()
        
        # Calculate new scroll position (inverted for natural scrolling)
        scroll_amount = 30  # Pixels per wheel notch
        self.scroll_y -= delta / 120 * scroll_amount
        
        # Clamp scroll_y between 0 and max_scroll
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
        
        self.update()
        event.accept()

    def paintEvent(self, event):
        if self.target_opacity == 0 and self.opacity < 0.01:
            return

        # Smooth fade animation
        self.opacity += (self.target_opacity - self.opacity) * 0.1
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.opacity)
        
        w, h = self.width(), self.height()
        
        # --- Draw Background (Dynamic Shape) ---
        cut = 15
        poly = QPolygonF([
            QPointF(cut, 0), QPointF(w, 0),
            QPointF(w, h - cut), QPointF(w - cut, h),
            QPointF(0, h), QPointF(0, cut)
        ])
        
        grad = QRadialGradient(w/2, h/2, w)
        grad.setColorAt(0, QColor(0, 20, 30, 230))
        grad.setColorAt(1, QColor(0, 10, 20, 250))
        painter.setBrush(QBrush(grad))
        
        # Tech Border Color (Based on state, defaulted to Cyan here)
        pen = QPen(COLOR_CYAN) 
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPolygon(poly)
        
        # --- Draw Text with Scroll Clip ---
        # We must clip the text so it doesn't draw outside the box when scrolling
        painter.setClipRegion(QRegion(poly.toPolygon()))
        
        painter.setPen(COLOR_WHITE)
        painter.setFont(self.font)
        
        # Adjust text position by scroll_y
        text_rect = QRectF(
            self.PADDING, 
            self.PADDING - self.scroll_y, # Shift up
            w - 2*self.PADDING, 
            10000 # Large height to allow full text measurement
        )
        
        painter.drawText(
            text_rect, 
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap), 
            self.displayed_text
        )


class JarvisReactor(QWidget):
    """
    The 'Arc Reactor' visualizer.
    Draws segmented rings and a sine-wave distortion when active.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 140)
        
        # Animation Variables
        self.angle_1 = 0.0
        self.angle_2 = 0.0
        self.angle_3 = 0.0
        self.pulse = 0.0
        self.wave_phase = 0.0
        
        # State: 0=Idle, 1=Active (Wavy)
        self.state = 0 
        
        # Sentiment Color State (Dynamic)
        self.current_color = COLOR_NEUTRAL
        self.target_color = COLOR_NEUTRAL
        
        # Timer (60 FPS smooth animation)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def set_state(self, state):
        self.state = state
    
    def set_color(self, color):
        """Change the reactor's emotion color"""
        self.target_color = color
    
    def interpolate_color(self, color1, color2, t):
        """Smoothly transition between two colors"""
        r = int(color1.red() + (color2.red() - color1.red()) * t)
        g = int(color1.green() + (color2.green() - color1.green()) * t)
        b = int(color1.blue() + (color2.blue() - color1.blue()) * t)
        return QColor(r, g, b)

    def animate(self):
        # Rotate Rings
        speed = 2.0 if self.state == 1 else 0.5
        self.angle_1 = (self.angle_1 + 1.0 * speed) % 360
        self.angle_2 = (self.angle_2 - 1.5 * speed) % 360
        self.angle_3 = (self.angle_3 + 0.8 * speed) % 360
        
        # Pulse Breathing
        self.pulse += 0.05
        
        # Wavy Phase
        self.wave_phase += 0.2
        
        # Smooth color transition (emotional state change)
        if self.current_color != self.target_color:
            self.current_color = self.interpolate_color(self.current_color, self.target_color, 0.15)
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = 70, 70 # Center
        
        # --- 1. CORE GLOW ---
        # A radial gradient to look like a light source
        glow_radius = 20 + math.sin(self.pulse) * 2
        grad = QRadialGradient(cx, cy, 30)
        grad.setColorAt(0, COLOR_WHITE)
        grad.setColorAt(0.5, self.current_color)
        grad.setColorAt(1, Qt.GlobalColor.transparent)
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), glow_radius, glow_radius)

        # --- 2. INNER SEGMENTED RING (Rotating) ---
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle_1)
        
        pen = QPen(self.current_color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        radius = 35
        # Draw 3 segments
        for i in range(3):
            painter.drawArc(QRectF(-radius, -radius, radius*2, radius*2), i*120*16, 80*16)
            
        painter.restore()

        # --- 3. MIDDLE DATA RING (Fast, Thin) ---
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle_2)
        
        middle_color = QColor(self.current_color)
        middle_color.setAlpha(150)
        pen.setColor(middle_color)
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DotLine) # Tech dots
        painter.setPen(pen)
        painter.drawEllipse(QPointF(0, 0), 45, 45)
        painter.restore()

        # --- 4. OUTER WAVY RING (The "Jarvis" Voice Effect) ---
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle_3) # Rotate the whole wave
        self.current_color
        # Logic: If active, wobble the radius using sine waves
        pen.setColor(COLOR_ACTIVE if self.state == 1 else COLOR_CYAN)
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        
        wave_radius = 55
        num_points = 60
        poly = QPolygonF()
        
        for i in range(num_points + 1):
            theta_rad = math.radians(i * (360 / num_points))
            
            # THE MAGIC: Distort radius based on sine wave if active
            distortion = 0
            if self.state == 1:
                # Creates the "Audio Waveform" look
                distortion = math.sin(i * 0.5 + self.wave_phase) * 5 + \
                             math.sin(i * 1.5 - self.wave_phase * 2) * 3
            
            r = wave_radius + distortion
            x = r * math.cos(theta_rad)
            y = r * math.sin(theta_rad)
            poly.append(QPointF(x, y))
            
        painter.drawPolyline(poly)
        painter.restore()


class OverlayWindow(QWidget):
    """
    Main transparent container.
    """
    def __init__(self):
        super().__init__()
        
        # Transparent Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set overall window opacity (0.0 = invisible, 1.0 = fully visible)
        self.setWindowOpacity(0.85)  # 85% opacity - slight transparency
        
        # Fixed size to prevent position shift
        self.setFixedSize(600, 200)  # Width: 450 (bubble) + 10 (spacing) + 140 (reactor)
        
        # Layout - Text box on LEFT, Reactor on RIGHT
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        
        # Widgets - ORDER MATTERS: Bubble first, then Reactor
        self.bubble = TechBubble()
        self.reactor = JarvisReactor()
        
        self.layout.addWidget(self.bubble)  # Left side
        self.layout.addWidget(self.reactor) # Right side
        
        # Dynamic positioning based on screen size
        screen = QApplication.primaryScreen().geometry()
        window_x = screen.width() - 600 - 20  # 20px padding from right edge
        window_y = screen.height() - 200 - 50  # 50px padding from bottom edge
        
        self.move(window_x, window_y)
        
    def set_text(self, text):
        """Called by the main thread to update status"""
        if text:
            self.reactor.set_state(1) # Active Mode
            self.bubble.set_text(text)
            self.bubble.show()
        else:
            self.reactor.set_state(0) # Idle Mode
            self.bubble.set_text("") 
            # We don't hide bubble immediately to allow fade out, 
            # but TechBubble handles empty text by fading.
    
    def set_sentiment_color(self, color):
        """Change reactor color based on sentiment"""
        self.reactor.set_color(color)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OverlayWindow()
    win.set_text("Initializing Core Systems...")
    win.show()
    sys.exit(app.exec())
