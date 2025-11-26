from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime, timedelta
import requests


API_BASE_URL = "http://localhost:8000"


class NotificationWidget(QtWidgets.QWidget):
    """Notification dropdown widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.NonModal)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the notification UI"""
        # Main container with shadow
        container = QtWidgets.QFrame(self)
        container.setObjectName("notificationContainer")
        container.setStyleSheet("""
            QFrame#notificationContainer {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
        """)
        
        # Add drop shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        container.setGraphicsEffect(shadow)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(container)
        
        # Container layout
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QtWidgets.QWidget()
        header.setStyleSheet("background-color: #588157; border-top-left-radius: 10px; border-top-right-radius: 10px;")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title = QtWidgets.QLabel("Notifications")
        title.setStyleSheet("color: white; font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Mark all read button
        self.mark_all_btn = QtWidgets.QPushButton("Mark all read")
        self.mark_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.mark_all_btn.clicked.connect(self.mark_all_read)
        header_layout.addWidget(self.mark_all_btn)
        
        layout.addWidget(header)
        
        # Scrollable notification list
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #588157;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.notification_container = QtWidgets.QWidget()
        self.notification_layout = QtWidgets.QVBoxLayout(self.notification_container)
        self.notification_layout.setSpacing(0)
        self.notification_layout.setContentsMargins(0, 0, 0, 0)
        self.notification_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self.scroll_area.setWidget(self.notification_container)
        layout.addWidget(self.scroll_area)
        
        # Footer
        footer = QtWidgets.QWidget()
        footer.setStyleSheet("background-color: #f5f5f5; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        footer_layout = QtWidgets.QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 10, 15, 10)
        
        view_all_btn = QtWidgets.QPushButton("View All Notifications")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #588157;
                border: none;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        footer_layout.addWidget(view_all_btn, alignment=QtCore.Qt.AlignCenter)
        
        layout.addWidget(footer)
        
        # Set size
        self.setFixedSize(400, 500)
    
    def load_notifications(self):
        """Load and display notifications"""
        # Clear existing notifications
        while self.notification_layout.count():
            child = self.notification_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        notifications = []
        
        # Get upcoming calendar events (next 7 days)
        try:
            response = requests.get(f"{API_BASE_URL}/calendar/upcoming", params={"days": 7, "limit": 20})
            if response.status_code == 200:
                data = response.json()
                events = data.get('data', [])
                
                for event in events:
                    event_date = datetime.strptime(event.get('event_date', ''), '%Y-%m-%d')
                    days_until = (event_date.date() - datetime.now().date()).days
                    
                    if days_until <= 2:  # Show events within 2 days
                        notifications.append({
                            'type': 'calendar',
                            'icon': '📅',
                            'title': event.get('title', 'Event'),
                            'message': f"{event.get('event_type', '')} - {event.get('event_date', '')}",
                            'time': event.get('event_date', ''),
                            'priority': 'high' if days_until == 0 else 'medium',
                            'data': event
                        })
        except Exception as e:
            print(f"Error loading calendar notifications: {e}")
        
        # Get overdue events
        try:
            response = requests.get(f"{API_BASE_URL}/calendar/events", 
                                  params={"end_date": datetime.now().strftime('%Y-%m-%d'), 
                                         "status": "Scheduled"})
            if response.status_code == 200:
                data = response.json()
                overdue = data.get('data', [])
                
                for event in overdue[:5]:  # Show max 5 overdue
                    notifications.append({
                        'type': 'overdue',
                        'icon': '⚠️',
                        'title': 'Overdue Event',
                        'message': f"{event.get('title', '')} was due on {event.get('event_date', '')}",
                        'time': event.get('event_date', ''),
                        'priority': 'high',
                        'data': event
                    })
        except Exception as e:
            print(f"Error loading overdue notifications: {e}")
        
        # Get pending reminders
        try:
            response = requests.get(f"{API_BASE_URL}/calendar/events", params={"limit": 100})
            if response.status_code == 200:
                data = response.json()
                all_events = data.get('data', [])
                
                for event in all_events:
                    reminders = event.get('reminders', [])
                    for reminder in reminders:
                        if not reminder.get('sent', False):
                            reminder_time = datetime.strptime(reminder.get('reminder_time', ''), '%Y-%m-%d %H:%M:%S')
                            if reminder_time <= datetime.now() + timedelta(hours=1):
                                notifications.append({
                                    'type': 'reminder',
                                    'icon': '🔔',
                                    'title': f"{reminder.get('type', '')} Reminder",
                                    'message': f"{event.get('title', '')} - {event.get('event_date', '')}",
                                    'time': reminder.get('reminder_time', ''),
                                    'priority': 'medium',
                                    'data': event
                                })
        except Exception as e:
            print(f"Error loading reminder notifications: {e}")
        
        # Sort by priority and time
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        notifications.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['time']), reverse=True)
        
        if not notifications:
            no_notif = QtWidgets.QLabel("No new notifications")
            no_notif.setStyleSheet("color: #999; font-style: italic; padding: 40px; font-size: 11pt;")
            no_notif.setAlignment(QtCore.Qt.AlignCenter)
            self.notification_layout.addWidget(no_notif)
        else:
            for notif in notifications[:20]:  # Show max 20
                notif_widget = self._create_notification_item(notif)
                self.notification_layout.addWidget(notif_widget)
    
    def _create_notification_item(self, notification):
        """Create a single notification item"""
        item = QtWidgets.QFrame()
        
        # Background color based on priority
        if notification['priority'] == 'high':
            bg_color = "#ffebee"
            border_color = "#d32f2f"
        elif notification['priority'] == 'medium':
            bg_color = "#fff3e0"
            border_color = "#ff9800"
        else:
            bg_color = "#f5f5f5"
            border_color = "#ccc"
        
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-left: 4px solid {border_color};
                border-bottom: 1px solid #e0e0e0;
                padding: 10px;
            }}
            QFrame:hover {{
                background-color: #e8f5e9;
            }}
        """)
        item.setCursor(QtCore.Qt.PointingHandCursor)
        
        layout = QtWidgets.QHBoxLayout(item)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QtWidgets.QLabel(notification['icon'])
        icon_label.setStyleSheet("font-size: 24pt;")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Content
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(3)
        
        title = QtWidgets.QLabel(notification['title'])
        title.setStyleSheet("font-weight: bold; font-size: 11pt; color: #333;")
        title.setWordWrap(True)
        content_layout.addWidget(title)
        
        message = QtWidgets.QLabel(notification['message'])
        message.setStyleSheet("font-size: 9pt; color: #666;")
        message.setWordWrap(True)
        content_layout.addWidget(message)
        
        # Time ago
        try:
            notif_time = datetime.strptime(notification['time'][:19], '%Y-%m-%d %H:%M:%S' if ' ' in notification['time'] else '%Y-%m-%d')
        except:
            try:
                notif_time = datetime.strptime(notification['time'][:10], '%Y-%m-%d')
            except:
                notif_time = datetime.now()
        
        time_diff = datetime.now() - notif_time
        if time_diff.days > 0:
            time_str = f"{time_diff.days} day(s) ago"
        elif time_diff.seconds >= 3600:
            time_str = f"{time_diff.seconds // 3600} hour(s) ago"
        elif time_diff.seconds >= 60:
            time_str = f"{time_diff.seconds // 60} minute(s) ago"
        else:
            time_str = "Just now"
        
        time_label = QtWidgets.QLabel(time_str)
        time_label.setStyleSheet("font-size: 8pt; color: #999;")
        content_layout.addWidget(time_label)
        
        layout.addLayout(content_layout, 1)
        
        # Close button
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #999;
                border: none;
                font-size: 18pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #d32f2f;
            }
        """)
        close_btn.clicked.connect(lambda: self._remove_notification(item))
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignTop)
        
        return item
    
    def _remove_notification(self, item):
        """Remove a notification item"""
        item.deleteLater()
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        while self.notification_layout.count():
            child = self.notification_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        no_notif = QtWidgets.QLabel("No new notifications")
        no_notif.setStyleSheet("color: #999; font-style: italic; padding: 40px; font-size: 11pt;")
        no_notif.setAlignment(QtCore.Qt.AlignCenter)
        self.notification_layout.addWidget(no_notif)
    
    def showEvent(self, event):
        """Load notifications when showing"""
        super().showEvent(event)
        self.load_notifications()
