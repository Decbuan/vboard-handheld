import gi
import uinput
import time
import os
import configparser

os.environ['GDK_BACKEND'] = 'x11'

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

# 键位映射
key_mapping = {
    uinput.KEY_ESC: "Esc", uinput.KEY_1: "1", uinput.KEY_2: "2", uinput.KEY_3: "3", 
    uinput.KEY_4: "4", uinput.KEY_5: "5", uinput.KEY_6: "6", uinput.KEY_7: "7",
    uinput.KEY_8: "8", uinput.KEY_9: "9", uinput.KEY_0: "0", uinput.KEY_MINUS: "-",
    uinput.KEY_EQUAL: "=", uinput.KEY_BACKSPACE: "Backspace", uinput.KEY_TAB: "Tab",
    uinput.KEY_Q: "Q", uinput.KEY_W: "W", uinput.KEY_E: "E", uinput.KEY_R: "R",
    uinput.KEY_T: "T", uinput.KEY_Y: "Y", uinput.KEY_U: "U", uinput.KEY_I: "I",
    uinput.KEY_O: "O", uinput.KEY_P: "P", uinput.KEY_LEFTBRACE: "[", 
    uinput.KEY_RIGHTBRACE: "]", uinput.KEY_ENTER: "Enter", uinput.KEY_LEFTCTRL: "Ctrl",
    uinput.KEY_A: "A", uinput.KEY_S: "S", uinput.KEY_D: "D", uinput.KEY_F: "F",
    uinput.KEY_G: "G", uinput.KEY_H: "H", uinput.KEY_J: "J", uinput.KEY_K: "K",
    uinput.KEY_L: "L", uinput.KEY_SEMICOLON: ";", uinput.KEY_APOSTROPHE: "'",
    uinput.KEY_GRAVE: "`", uinput.KEY_LEFTSHIFT: "Shift", uinput.KEY_BACKSLASH: "\\",
    uinput.KEY_Z: "Z", uinput.KEY_X: "X", uinput.KEY_C: "C", uinput.KEY_V: "V",
    uinput.KEY_B: "B", uinput.KEY_N: "N", uinput.KEY_M: "M", uinput.KEY_COMMA: ",",
    uinput.KEY_DOT: ".", uinput.KEY_SLASH: "/", uinput.KEY_RIGHTSHIFT: "Shift",
    uinput.KEY_SPACE: "Space", uinput.KEY_LEFTALT: "Alt", uinput.KEY_RIGHTALT: "Alt",
    uinput.KEY_LEFTMETA: "Super", uinput.KEY_RIGHTMETA: "Super"
}

# Shift特殊字符映射
shift_mapping = {
    "1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&", "8": "*",
    "9": "(", "0": ")", "-": "_", "=": "+", "[": "{", "]": "}", ";": ":", "'": "\"",
    "`": "~", "\\": "|", ",": "<", ".": ">", "/": "?"
}

class VirtualKeyboard(Gtk.Window):
    def __init__(self):
        super().__init__(title="Virtual Keyboard")
        
        # 初始化配置
        self.CONFIG_DIR = os.path.expanduser("~/.config/vboard")
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "settings.conf")
        self.config = configparser.ConfigParser()
        self.config["DEFAULT"] = {
            "bg_color": "0,0,0",
            "opacity": "0.90",
            "text_color": "white",
            "width": "0",
            "height": "0",
            "pos_x": "-1",
            "pos_y": "-1"
        }
        
        # 窗口设置
        self.set_keep_above(True)
        self.set_resizable(True)
        self.set_border_width(5)
        self.set_default_size(800, 200)
        
        # 状态变量
        self.modifiers = {
            uinput.KEY_LEFTSHIFT: False,
            uinput.KEY_RIGHTSHIFT: False
        }
        self.original_labels = {}
        
        # 加载配置
        self.load_settings()
        
        # 创建UI
        self.setup_ui()
        
        # 初始化键盘设备
        self.device = uinput.Device(list(key_mapping.keys()))
        
        # 显示窗口
        self.show_all()
        self.restore_window_state()

    def setup_ui(self):
        # 创建标题栏
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        
        # 大号ESC按钮
        esc_btn = Gtk.Button(label="ESC")
        esc_btn.set_size_request(80, -1)
        esc_btn.connect("clicked", self.send_esc)
        header.pack_start(esc_btn)
        
        # 设置按钮
        self.setup_header_buttons(header)
        self.set_titlebar(header)
        
        # 主键盘网格
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        self.add(grid)
        
        # 键盘行定义
        rows = [
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
            ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
            ["CapsLock", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
            ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
            ["Ctrl", "Super", "Alt", "Space", "Alt", "Super", "Ctrl"]
        ]
        
        # 创建键盘行
        for row_idx, keys in enumerate(rows):
            self.create_keyboard_row(grid, row_idx, keys)
        
        # 应用样式
        self.apply_styles()

    def create_keyboard_row(self, grid, row_idx, keys):
        col_pos = 0
        for key in keys:
            btn = Gtk.Button(label=key)
            btn.set_hexpand(True)
            
            # 特殊键处理
            if key in ["Shift", "Ctrl", "Alt", "Super"]:
                btn.set_label(key)
                key_event = next(k for k,v in key_mapping.items() if v == key)
            else:
                key_event = next((k for k,v in key_mapping.items() if v.lower() == key.lower()), None)
            
            if key_event:
                self.original_labels[btn] = key
                btn.connect("clicked", self.on_key_press, key_event)
                
                # 设置列宽
                col_span = self.get_key_span(key)
                grid.attach(btn, col_pos, row_idx, col_span, 1)
                col_pos += col_span

    def get_key_span(self, key):
        spans = {
            "Space": 12,
            "Backspace": 5,
            "Enter": 5,
            "Shift": 4,
            "Tab": 3,
            "\\": 4,
            "CapsLock": 3
        }
        return spans.get(key, 2)

    def on_key_press(self, widget, key_event):
        # Shift键处理
        if key_event in [uinput.KEY_LEFTSHIFT, uinput.KEY_RIGHTSHIFT]:
            self.modifiers[key_event] = not self.modifiers[key_event]
            self.update_key_labels()
            return
        
        # 临时修改标签（如果是可Shift字符）
        shift_active = any(self.modifiers.values())
        original_label = self.original_labels.get(widget, "")
        
        if shift_active and original_label in shift_mapping:
            widget.set_label(shift_mapping[original_label])
        
        # 发送按键事件
        self.send_key_event(key_event)
        
        # 恢复标签
        if shift_active and original_label in shift_mapping:
            widget.set_label(original_label)

    def send_key_event(self, key_event):
        # 按下修饰键
        for mod_key, active in self.modifiers.items():
            if active:
                self.device.emit(mod_key, 1)
        
        # 按下主键
        self.device.emit(key_event, 1)
        time.sleep(0.05)
        self.device.emit(key_event, 0)
        
        # 释放修饰键
        for mod_key in self.modifiers:
            if self.modifiers[mod_key]:
                self.device.emit(mod_key, 0)
                self.modifiers[mod_key] = False

    def send_esc(self, widget):
        self.device.emit(uinput.KEY_ESC, 1)
        time.sleep(0.05)
        self.device.emit(uinput.KEY_ESC, 0)

    def update_key_labels(self):
        shift_active = any(self.modifiers.values())
        for btn, original_label in self.original_labels.items():
            if shift_active and original_label in shift_mapping:
                btn.set_label(shift_mapping[original_label])
            else:
                btn.set_label(original_label)

    def setup_header_buttons(self, header):
        # 菜单按钮
        menu_btn = Gtk.Button(label="☰")
        menu_btn.connect("clicked", self.toggle_settings)
        header.pack_end(menu_btn)
        
        # 透明度控制
        self.opacity = float(self.config["DEFAULT"]["opacity"])
        opacity_box = Gtk.Box(spacing=5)
        
        plus_btn = Gtk.Button(label="+")
        plus_btn.connect("clicked", self.adjust_opacity, True)
        
        minus_btn = Gtk.Button(label="-")
        minus_btn.connect("clicked", self.adjust_opacity, False)
        
        self.opacity_label = Gtk.Label(label=f"{self.opacity:.2f}")
        
        opacity_box.pack_start(minus_btn, False, False, 0)
        opacity_box.pack_start(self.opacity_label, False, False, 0)
        opacity_box.pack_start(plus_btn, False, False, 0)
        header.pack_end(opacity_box)
        
        # 颜色选择
        self.color_combo = Gtk.ComboBoxText()
        colors = [
            ("Black", "0,0,0"), ("White", "255,255,255"), 
            ("Blue", "0,0,200"), ("Dark", "40,40,40")
        ]
        for name, color in colors:
            self.color_combo.append_text(name)
        self.color_combo.set_active(0)
        self.color_combo.connect("changed", self.change_color)
        header.pack_end(self.color_combo)

    def toggle_settings(self, widget):
        # 切换设置控件的可见性
        pass

    def adjust_opacity(self, widget, increase):
        self.opacity = max(0.1, min(1.0, self.opacity + (0.1 if increase else -0.1)))
        self.opacity_label.set_label(f"{self.opacity:.1f}")
        self.apply_styles()
        self.save_settings()

    def change_color(self, widget):
        colors = {
            "Black": "0,0,0",
            "White": "255,255,255",
            "Blue": "0,0,200",
            "Dark": "40,40,40"
        }
        self.bg_color = colors[widget.get_active_text()]
        self.apply_styles()
        self.save_settings()

    def apply_styles(self):
        css = f"""
        window {{
            background-color: rgba({self.bg_color}, {self.opacity});
        }}
        button {{
            background: none;
            border: 1px solid #555;
            color: white;
            font-size: 14px;
        }}
        button:hover {{
            border-color: #7af;
        }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def load_settings(self):
        try:
            if not os.path.exists(self.CONFIG_DIR):
                os.makedirs(self.CONFIG_DIR)
            
            if os.path.exists(self.CONFIG_FILE):
                self.config.read(self.CONFIG_FILE)
            
            # 加载配置值
            self.bg_color = self.config["DEFAULT"].get("bg_color", "0,0,0")
            self.opacity = float(self.config["DEFAULT"].get("opacity", "0.9"))
            self.text_color = self.config["DEFAULT"].get("text_color", "white")
            
            # 窗口状态
            self.width = int(self.config["DEFAULT"].get("width", "0"))
            self.height = int(self.config["DEFAULT"].get("height", "0"))
            self.pos_x = int(self.config["DEFAULT"].get("pos_x", "-1"))
            self.pos_y = int(self.config["DEFAULT"].get("pos_y", "-1"))
            
        except Exception as e:
            print(f"加载配置失败: {e}")

    def save_settings(self):
        # 获取当前窗口状态
        self.width, self.height = self.get_size()
        self.pos_x, self.pos_y = self.get_position()
        
        # 更新配置
        self.config["DEFAULT"]["bg_color"] = self.bg_color
        self.config["DEFAULT"]["opacity"] = f"{self.opacity:.2f}"
        self.config["DEFAULT"]["text_color"] = self.text_color
        self.config["DEFAULT"]["width"] = str(self.width)
        self.config["DEFAULT"]["height"] = str(self.height)
        self.config["DEFAULT"]["pos_x"] = str(self.pos_x)
        self.config["DEFAULT"]["pos_y"] = str(self.pos_y)
        
        # 保存到文件
        try:
            with open(self.CONFIG_FILE, "w") as f:
                self.config.write(f)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def restore_window_state(self):
        # 恢复窗口大小
        if self.width > 0 and self.height > 0:
            self.resize(self.width, self.height)
        
        # 恢复窗口位置
        if self.pos_x >= 0 and self.pos_y >= 0:
            self.move(self.pos_x, self.pos_y)
        else:
            self.position_at_bottom()

    def position_at_bottom(self):
        screen = self.get_screen()
        monitor = screen.get_primary_monitor() if hasattr(screen, 'get_primary_monitor') else 0
        geom = screen.get_monitor_geometry(monitor)
        
        # 计算位置（水平居中，距离底部50px）
        width, height = self.get_size()
        x = geom.x + (geom.width - width) // 2
        y = geom.y + geom.height - height - 50
        
        self.move(x, y)

    def on_window_move(self, widget, event):
        # 窗口移动或调整大小时自动保存状态
        self.save_settings()

if __name__ == "__main__":
    win = VirtualKeyboard()
    win.connect("destroy", Gtk.main_quit)
    win.connect("configure-event", win.on_window_move)
    Gtk.main()
