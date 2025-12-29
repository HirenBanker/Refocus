from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.core.window import Window
from models import DataManager
from blocking_service import BlockingService
from datetime import datetime, timedelta

# Set window size for testing (mobile-like)
Window.size = (360, 640)

class TimeInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('write_tab', False)
        kwargs.setdefault('hint_text', '00:00')
        # Remove input_filter='int' because it prevents inserting ':'
        super().__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        # Only allow 5 characters (HH:MM)
        if len(self.text) >= 5:
            return
        
        # Only allow numbers (and ':' if we are auto-inserting it)
        if not substring.isdigit() and substring != ':':
            return

        # If user types a number at index 2, auto-insert ':' before it
        if len(self.text) == 2 and substring.isdigit():
            super().insert_text(':', from_undo=from_undo)
            
        return super().insert_text(substring, from_undo=from_undo)

    def on_text(self, instance, value):
        # Clean up any non-numeric/colon characters just in case
        cleaned = "".join([c for c in value if c.isdigit() or c == ':'])
        if cleaned != value:
            self.text = cleaned
            return

        # Basic validation as they type
        if len(value) > 5:
            self.text = value[:5]
        
        # Ensure colon is at the right place if text is long enough
        if len(value) >= 3 and value[2] != ':':
            # This handles cases where user deletes the colon or pastes something
            temp = value.replace(':', '')
            self.text = temp[:2] + ':' + temp[2:4]

class AccountPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Account Details"
        self.size_hint = (0.8, 0.6)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=40, write_tab=False)
        layout.add_widget(Label(text="Username", size_hint_y=None, height=30))
        layout.add_widget(self.username_input)
        
        self.email_input = TextInput(hint_text="Email", multiline=False, size_hint_y=None, height=40, write_tab=False)
        layout.add_widget(Label(text="Email", size_hint_y=None, height=30))
        layout.add_widget(self.email_input)

        self.phone_input = TextInput(hint_text="Phone Number", multiline=False, size_hint_y=None, height=40, write_tab=False)
        layout.add_widget(Label(text="Phone Number", size_hint_y=None, height=30))
        layout.add_widget(self.phone_input)
        
        btn_save = Button(text="Save", size_hint_y=None, height=40)
        btn_save.bind(on_press=self.save_profile)
        layout.add_widget(btn_save)
        
        self.content = layout
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        if app:
            user = app.data_manager.get_user()
            self.username_input.text = user.get("username", "")
            self.email_input.text = user.get("email", "")
            self.phone_input.text = user.get("phone", "")

    def save_profile(self, instance):
        app = App.get_running_app()
        if app:
            app.data_manager.update_user(
                username=self.username_input.text.strip(), 
                email=self.email_input.text.strip(),
                phone=self.phone_input.text.strip()
            )
            self.dismiss()

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # --- Header ---
        header = BoxLayout(size_hint_y=None, height=50)
        header.add_widget(Label(text="Refocus", font_size=24, halign='left', size_hint_x=0.7))
        btn_account = Button(text="Account", size_hint_x=0.3)
        btn_account.bind(on_press=self.open_account)
        header.add_widget(btn_account)
        self.add_widget(header)
        
        # --- Timer Controls ---
        self.add_widget(Label(text="Select Duration", size_hint_y=None, height=30))
        
        timer_grid = GridLayout(cols=4, spacing=5, size_hint_y=None, height=50)
        for hour in [1, 2, 3, 4]:
            btn = Button(text=f"{hour}hr")
            btn.bind(on_press=lambda x, h=hour: self.set_timer(h * 60))
            timer_grid.add_widget(btn)
        self.add_widget(timer_grid)
        
        # Custom Timer
        self.add_widget(Label(text="Custom Time Range", size_hint_y=None, height=30))
        custom_box = BoxLayout(size_hint_y=None, height=80, spacing=10)
        
        # Start Time Section
        start_container = BoxLayout(orientation='vertical', spacing=2)
        start_container.add_widget(Label(text="Start Time (HH:MM)", size_hint_y=None, height=20, font_size=12))
        self.start_input = TimeInput(size_hint_y=None, height=35)
        start_container.add_widget(self.start_input)
        
        # End Time Section
        end_container = BoxLayout(orientation='vertical', spacing=2)
        end_container.add_widget(Label(text="End Time (HH:MM)", size_hint_y=None, height=20, font_size=12))
        self.end_input = TimeInput(size_hint_y=None, height=35)
        end_container.add_widget(self.end_input)
        
        custom_box.add_widget(start_container)
        custom_box.add_widget(end_container)
        
        btn_set_custom = Button(text="Set", size_hint_x=0.3, size_hint_y=None, height=35, pos_hint={'center_y': 0.3})
        btn_set_custom.bind(on_press=self.set_custom_timer)
        custom_box.add_widget(btn_set_custom)
        self.add_widget(custom_box)
        
        self.selected_label = Label(text="Selected: None", size_hint_y=None, height=30)
        self.add_widget(self.selected_label)
        self.selected_duration = 0

        # --- Site Management ---
        self.add_widget(Label(text="Blocked Sites", size_hint_y=None, height=30))
        
        # Dropdown (Spinner)
        self.site_spinner = Spinner(text='Select Site', values=(), size_hint_y=None, height=40)
        self.add_widget(self.site_spinner)
        
        # Add/Delete Controls
        site_controls = BoxLayout(size_hint_y=None, height=40, spacing=5)
        self.new_site_input = TextInput(hint_text="New Site URL", multiline=False, write_tab=False)
        site_controls.add_widget(self.new_site_input)
        
        btn_add = Button(text="Add", size_hint_x=0.2)
        btn_add.bind(on_press=self.add_site)
        site_controls.add_widget(btn_add)
        
        btn_del = Button(text="Del", size_hint_x=0.2)
        btn_del.bind(on_press=self.delete_site)
        site_controls.add_widget(btn_del)
        
        self.add_widget(site_controls)
        
        # --- Blocking Status ---
        self.status_label = Label(text="Status: Inactive", font_size=18, size_hint_y=None, height=40)
        self.add_widget(self.status_label)
        
        self.toggle_btn = Button(text="Start Blocking", size_hint_y=None, height=60)
        self.toggle_btn.bind(on_press=self.toggle_blocking)
        self.add_widget(self.toggle_btn)
        
        # Spacer
        self.add_widget(Label())
        
        # --- Footer ---
        footer = Label(text="[ Advertisement Space ]", size_hint_y=None, height=40, color=(0.5, 0.5, 0.5, 1))
        self.add_widget(footer)
        
        # Init
        self.refresh_sites()
        # Schedule update check? For now just check on startup
        
    def open_account(self, instance):
        AccountPopup().open()
        
    def set_timer(self, minutes):
        self.selected_duration = minutes
        self.selected_label.text = f"Selected: {minutes} minutes"
        
    def set_custom_timer(self, instance):
        # Parse Start/End time
        s_text = self.start_input.text.strip()
        e_text = self.end_input.text.strip()
        
        def validate_time(time_str):
            try:
                parts = time_str.split(':')
                if len(parts) != 2: return False
                h, m = int(parts[0]), int(parts[1])
                if not (0 <= h <= 24): return False
                if h == 24 and m > 0: return False # 24:00 is okay, 24:01 is not
                if not (0 <= m <= 59): return False
                return True
            except ValueError:
                return False

        if not validate_time(s_text) or not validate_time(e_text):
            self.selected_label.text = "Error: Use HH:MM (00-24:00-59)"
            return
        
        try:
            now = datetime.now()
            # Handle 24:00 as 00:00 of next day or just 00:00 today? 
            # Usually strptime doesn't like 24:00. Let's normalize it to 23:59 or handle it.
            def parse_dt(t_str):
                if t_str == "24:00":
                    return datetime.strptime("23:59:59", "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
                return datetime.strptime(t_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)

            start_dt = parse_dt(s_text)
            end_dt = parse_dt(e_text)
            
            # Handle crossing midnight or basic validation
            if end_dt <= start_dt:
                # Assuming next day if end < start? Or just error?
                # For simplicity, assume same day and error if invalid
                self.selected_label.text = "Error: End time must be after Start time"
                return

            diff = end_dt - start_dt
            minutes = int(diff.total_seconds() / 60)
            self.set_timer(minutes)
            
        except ValueError:
            self.selected_label.text = "Error: Use HH:MM format"

    def refresh_sites(self):
        app = App.get_running_app()
        if app:
            sites = app.data_manager.get_blocked_sites()
            self.site_spinner.values = sites
            if sites:
                self.site_spinner.text = sites[0]
            else:
                self.site_spinner.text = "No sites"

    def add_site(self, instance):
        site = self.new_site_input.text.strip()
        if site:
            app = App.get_running_app()
            app.data_manager.add_site(site)
            self.new_site_input.text = ""
            self.refresh_sites()
            # Auto-select new site
            self.site_spinner.text = site

    def delete_site(self, instance):
        site = self.site_spinner.text
        if site and site != "No sites":
            app = App.get_running_app()
            app.data_manager.remove_site(site)
            self.refresh_sites()

    def toggle_blocking(self, instance):
        app = App.get_running_app()
        service = app.blocking_service
        
        if service.is_active():
            # Try to stop
            success = service.stop_blocking()
            if not success:
                self.status_label.text = "Status: Locked (Strict Mode)"
                return
            self.update_ui_state(False)
        else:
            # Start
            if self.selected_duration <= 0:
                self.selected_label.text = "Select duration first!"
                return
            
            sites = app.data_manager.get_blocked_sites()
            if not sites:
                self.selected_label.text = "Add sites first!"
                return
                
            service.start_blocking(self.selected_duration, sites, strict=True)
            self.update_ui_state(True)
            
    def update_ui_state(self, is_active):
        if is_active:
            app = App.get_running_app()
            until = app.blocking_service.get_block_until()
            until_str = until.strftime("%H:%M") if until else "??:??"
            
            self.status_label.text = "Status: Active (Strict)"
            self.toggle_btn.text = f"blocked until {until_str}"
            self.toggle_btn.background_color = (1, 0, 0, 1)
            # Disable inputs if strict?
        else:
            self.status_label.text = "Status: Inactive"
            self.toggle_btn.text = "Start Blocking"
            self.toggle_btn.background_color = (1, 1, 1, 1)

class RefocusApp(App):
    def build(self):
        self.data_manager = DataManager()
        self.blocking_service = BlockingService(self.data_manager)
        
        layout = MainLayout()
        
        # Check initial state
        if self.blocking_service.is_active():
            layout.update_ui_state(True)
        
        return layout

if __name__ == '__main__':
    try:
        RefocusApp().run()
    except Exception as e:
        import traceback
        with open("crash_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print(e)
