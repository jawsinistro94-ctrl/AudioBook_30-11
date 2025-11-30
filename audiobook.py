import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import json
import os
import sys
from pynput import mouse
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
import keyboard as kb  # More robust hotkey library for Windows
import pyautogui
import threading
import time
import mss
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AudioBook:
    def __init__(self, root):
        self.root = root
        self.root.title("AudioBook - Automation System")
        self.root.geometry("520x620")
        
        # Harmonized EMBER/BRASAS color palette
        self.colors = {
            'bg_primary': '#1B0F0B',    # Deep ember brown (main background)
            'bg_secondary': '#29140E',  # Secondary panels
            'bg_inset': '#3A1C10',      # Inset surfaces
            'bg_card': '#2D1810',       # Card backgrounds (slightly lighter)
            'border': '#7A2E1B',        # Rusted iron borders
            'border_highlight': '#D4631C',  # Highlight trim
            'text_header': '#FFE3AA',   # Headers
            'text_body': '#F9D8A0',     # Body text
            'text_subdued': '#DAB273',  # Subdued labels
            'button_default': '#8F3A1C', # Default button
            'button_hover': '#B44C1E',   # Button hover
            'button_destructive': '#611B1C', # Destructive actions
            'selection': '#C2551E',      # Selection highlight
            'focus_glow': '#ED9444',     # Focus glow
            'status_on': '#E8B449',      # Molten gold ON
            'status_off': '#5A1F1F',     # Banked ember OFF
            'switch_on': '#22c55e',      # Green switch ON
            'switch_off': '#4a4a4a',     # Gray switch OFF
            'slider_progress': '#D4631C', # Slider progress color
            'slider_button': '#FFE3AA'   # Slider button color
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Load magma texture (original psychedelic version)
        try:
            magma_img = Image.open(resource_path('magma_background.jpg'))
            magma_img = magma_img.resize((900, 1050), Image.Resampling.LANCZOS)
            # Keep original psychedelic colors - just darken slightly for contrast
            magma_img = Image.eval(magma_img, lambda x: int(x * 0.6))
            self.magma_bg = ImageTk.PhotoImage(magma_img)
        except Exception as e:
            print(f"Failed to load magma: {e}")
            self.magma_bg = None
        
        # Load power icon
        try:
            power_img = Image.open(resource_path('power_icon.png'))
            power_img = power_img.resize((32, 32), Image.Resampling.LANCZOS)
            self.power_icon = ImageTk.PhotoImage(power_img)
        except Exception as e:
            print(f"Failed to load power icon: {e}")
            self.power_icon = None
        
        # Load fire icon
        try:
            fire_img = Image.open(resource_path('fire_icon.png'))
            fire_img = fire_img.resize((24, 24), Image.Resampling.LANCZOS)
            self.fire_icon = ImageTk.PhotoImage(fire_img)
        except Exception as e:
            print(f"Failed to load fire icon: {e}")
            self.fire_icon = None
        
        # Load turtle icon (main logo)
        try:
            turtle_img = Image.open(resource_path('turtle_icon.png'))
            turtle_img = turtle_img.resize((28, 28), Image.Resampling.LANCZOS)
            self.turtle_icon = ImageTk.PhotoImage(turtle_img)
        except Exception as e:
            print(f"Failed to load turtle icon: {e}")
            self.turtle_icon = None
        
        # Load trophy icon
        try:
            trophy_img = Image.open(resource_path('trophy_icon.png'))
            trophy_img = trophy_img.resize((24, 24), Image.Resampling.LANCZOS)
            self.trophy_icon = ImageTk.PhotoImage(trophy_img)
        except Exception as e:
            print(f"Failed to load trophy icon: {e}")
            self.trophy_icon = None
        
        # Load sword icon
        try:
            sword_img = Image.open(resource_path('sword_icon.png'))
            sword_img = sword_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.sword_icon = ImageTk.PhotoImage(sword_img)
        except Exception as e:
            print(f"Failed to load sword icon: {e}")
            self.sword_icon = None
        
        # Load location pin icon (for record positions button)
        try:
            location_img = Image.open(resource_path('location_icon.png'))
            location_img = location_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.location_icon = ImageTk.PhotoImage(location_img)
        except Exception as e:
            print(f"Failed to load location icon: {e}")
            self.location_icon = None
        
        # Load target/crosshair icon (for auto-target button)
        try:
            target_img = Image.open(resource_path('target_icon.png'))
            target_img = target_img.resize((32, 32), Image.Resampling.LANCZOS)
            self.target_icon = ImageTk.PhotoImage(target_img)
        except Exception as e:
            print(f"Failed to load target icon: {e}")
            self.target_icon = None
        
        # Load checkbox icons (green ON, red OFF)
        try:
            checkbox_on_img = Image.open(resource_path('checkbox_on.png'))
            checkbox_on_img = checkbox_on_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.checkbox_on = ImageTk.PhotoImage(checkbox_on_img)
        except Exception as e:
            print(f"Failed to load checkbox ON icon: {e}")
            self.checkbox_on = None
        
        try:
            checkbox_off_img = Image.open(resource_path('checkbox_off.png'))
            checkbox_off_img = checkbox_off_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.checkbox_off = ImageTk.PhotoImage(checkbox_off_img)
        except Exception as e:
            print(f"Failed to load checkbox OFF icon: {e}")
            self.checkbox_off = None
        
        # Data structures
        self.hotkeys = []
        self.config_file = "audiobook_config.json"
        self.recording_mode = False
        self.recorded_clicks = []
        self.active = True
        self.currently_pressed = set()
        self.triggered_hotkeys = set()
        self.triggered_quick_keys = set()
        
        # Thread-safe UI dispatcher lock
        self._ui_lock = threading.Lock()
        self._ui_running = True
        
        # Auto-target HSV configuration (default values)
        self.hsv_config = {
            'lower_h1': 0, 'upper_h1': 10,
            'lower_h2': 170, 'upper_h2': 180,
            'lower_s': 100, 'upper_s': 255,
            'lower_v': 100, 'upper_v': 255,
            'calibrated': False,
            'template': None  # Will be loaded from config if calibrated
        }
        self.outline_template = None  # Numpy array for template matching
        self.outline_shape_signature = None  # Hu Moments for shape matching
        
        # Controllers
        self.mouse_controller = MouseController()
        
        # Load saved configuration
        self.load_config()
        
        # Create UI
        self.create_ui()
        
        # Start hotkey listener
        self.start_hotkey_listener()
    
    def ui_safe(self, func, *args, **kwargs):
        """Thread-safe UI update dispatcher - prevents Tkinter deadlocks.
        Call this from any thread to safely update UI elements."""
        if not self._ui_running:
            return
        try:
            self.root.after(0, lambda: func(*args, **kwargs))
        except Exception as e:
            print(f"[UI_SAFE] Error scheduling UI update: {e}")
    
    def ui_configure(self, widget, **kwargs):
        """Thread-safe widget.configure() - use this from threads instead of direct configure()"""
        if not self._ui_running:
            return
        try:
            self.root.after(0, lambda: widget.configure(**kwargs))
        except Exception as e:
            print(f"[UI_SAFE] Error configuring widget: {e}")
    
    def create_ui(self):
        # Custom style for ttk elements we still need
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview colors for hotkey list
        style.configure("Treeview", background=self.colors['bg_secondary'], fieldbackground=self.colors['bg_secondary'],
                       foreground=self.colors['text_body'], font=('Consolas', 8))
        style.configure("Treeview.Heading", background=self.colors['border'],
                       foreground=self.colors['text_header'], font=('Georgia', 9, 'bold'))
        style.map('Treeview', background=[('selected', self.colors['selection'])])
        
        # Main container frame with rounded corners
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors['bg_primary'], corner_radius=0)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # ===== MODERN HEADER BAR =====
        header_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_secondary'], 
                                    corner_radius=12, border_width=2, border_color=self.colors['border_highlight'])
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill=tk.X, padx=12, pady=8)
        
        # Left side - Title with turtle icon
        title_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_frame.pack(side=tk.LEFT)
        
        if self.turtle_icon:
            tk.Label(title_frame, image=self.turtle_icon, bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=2)
        
        ctk.CTkLabel(title_frame, text="AudioBook v2.0", 
                    font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
                    text_color=self.colors['text_header']).pack(side=tk.LEFT, padx=6)
        
        # Right side - Status toggle
        status_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        status_frame.pack(side=tk.RIGHT)
        
        # Alt+F12 hint
        ctk.CTkLabel(status_frame, text="Alt+F12: Pausar", 
                    font=ctk.CTkFont(family="Consolas", size=10),
                    text_color=self.colors['text_subdued']).pack(side=tk.LEFT, padx=10)
        
        self.status_label = ctk.CTkLabel(status_frame, text="ON", 
                                         font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
                                         text_color=self.colors['status_on'])
        self.status_label.pack(side=tk.LEFT, padx=6)
        
        # Modern toggle switch for ON/OFF
        self.global_toggle = ctk.CTkSwitch(status_frame, text="", width=50, height=26,
                                           switch_width=44, switch_height=22,
                                           progress_color=self.colors['switch_on'],
                                           button_color=self.colors['slider_button'],
                                           button_hover_color="#FFFFFF",
                                           fg_color=self.colors['switch_off'],
                                           command=self.toggle_active)
        self.global_toggle.select()  # Start as ON
        self.global_toggle.pack(side=tk.LEFT, padx=4)
        
        # ===== MODERN PROFILE BAR =====
        profile_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_card'], 
                                     corner_radius=10, border_width=1, border_color=self.colors['border'])
        profile_frame.pack(fill=tk.X, pady=(0, 6))
        
        profile_inner = ctk.CTkFrame(profile_frame, fg_color="transparent")
        profile_inner.pack(fill=tk.X, padx=10, pady=6)
        
        ctk.CTkLabel(profile_inner, text="Perfil:", 
                    font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
                    text_color=self.colors['text_header']).pack(side=tk.LEFT, padx=4)
        
        self.current_profile = tk.StringVar(value="Padrão")
        self.profile_dropdown = ctk.CTkOptionMenu(profile_inner, variable=self.current_profile,
                                                  values=list(self.config.get('profiles', {'Padrão': {}}).keys()),
                                                  width=140, height=28,
                                                  fg_color=self.colors['bg_inset'],
                                                  button_color=self.colors['button_default'],
                                                  button_hover_color=self.colors['button_hover'],
                                                  dropdown_fg_color=self.colors['bg_secondary'],
                                                  dropdown_hover_color=self.colors['selection'],
                                                  text_color=self.colors['text_body'],
                                                  font=ctk.CTkFont(family="Georgia", size=10),
                                                  command=lambda x: self.switch_profile())
        self.profile_dropdown.pack(side=tk.LEFT, padx=6)
        
        ctk.CTkButton(profile_inner, text="+", width=32, height=28, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     text_color=self.colors['text_header'], font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.create_profile).pack(side=tk.LEFT, padx=2)
        
        ctk.CTkButton(profile_inner, text="Ren", width=40, height=28, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     text_color=self.colors['text_header'], font=ctk.CTkFont(size=10),
                     command=self.rename_profile).pack(side=tk.LEFT, padx=2)
        
        ctk.CTkButton(profile_inner, text="X", width=32, height=28, corner_radius=6,
                     fg_color=self.colors['button_destructive'], hover_color="#8B2020",
                     text_color=self.colors['text_header'], font=ctk.CTkFont(size=12, weight="bold"),
                     command=self.delete_profile).pack(side=tk.LEFT, padx=2)
        
        # ===== MODERN TABVIEW =====
        self.tabview = ctk.CTkTabview(main_frame, corner_radius=10,
                                      fg_color=self.colors['bg_card'],
                                      segmented_button_fg_color=self.colors['bg_secondary'],
                                      segmented_button_selected_color=self.colors['border_highlight'],
                                      segmented_button_selected_hover_color=self.colors['button_hover'],
                                      segmented_button_unselected_color=self.colors['bg_inset'],
                                      segmented_button_unselected_hover_color=self.colors['button_default'],
                                      text_color=self.colors['text_body'],
                                      text_color_disabled=self.colors['text_subdued'])
        self.tabview.pack(fill=tk.BOTH, expand=True, pady=4)
        
        # Add tabs
        self.tab_best_sellers = self.tabview.add("Best Sellers")
        self.tab_runemaker = self.tabview.add("Runemaker")
        self.tab_hyper_grab = self.tabview.add("Hyper Grab")
        self.tab_targeting = self.tabview.add("Targeting")
        self.tab_settings = self.tabview.add("Settings")
        
        # ===== BEST SELLERS TAB CONTENT =====
        quick_frame = ctk.CTkScrollableFrame(self.tab_best_sellers, fg_color="transparent")
        quick_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Initialize variables
        self.auto_sd_enabled = tk.BooleanVar(value=False)
        self.auto_sd_hotkey = tk.StringVar(value="F1")
        self.auto_sd_delay = tk.IntVar(value=100)
        
        # Load SD icon
        try:
            sd_img = Image.open(resource_path('sd_rune_icon.png'))
            sd_img = sd_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.sd_icon_photo = ImageTk.PhotoImage(sd_img)
        except:
            self.sd_icon_photo = None
        
        # Auto SD Row - Modern Card Style
        self.sd_frame = ctk.CTkFrame(quick_frame, fg_color=self.colors['bg_secondary'], 
                                     corner_radius=8, border_width=1, border_color=self.colors['border'])
        self.sd_frame.pack(fill=tk.X, pady=3, padx=2)
        
        sd_inner = ctk.CTkFrame(self.sd_frame, fg_color="transparent")
        sd_inner.pack(fill=tk.X, padx=8, pady=6)
        
        # Modern Switch
        self.sd_switch = ctk.CTkSwitch(sd_inner, text="", width=40, height=20,
                                       switch_width=36, switch_height=18,
                                       progress_color=self.colors['switch_on'],
                                       button_color="#FFFFFF",
                                       fg_color=self.colors['switch_off'],
                                       variable=self.auto_sd_enabled,
                                       command=self.save_quick_configs)
        self.sd_switch.pack(side=tk.LEFT, padx=4)
        
        # Icon
        if self.sd_icon_photo:
            tk.Label(sd_inner, image=self.sd_icon_photo, bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=4)
        
        # Name label
        ctk.CTkLabel(sd_inner, text="Auto SD", font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
                    text_color=self.colors['text_header'], width=70).pack(side=tk.LEFT, padx=4)
        
        # Hotkey badge (gradient style)
        self.sd_hotkey_btn = ctk.CTkButton(sd_inner, text=self.auto_sd_hotkey.get(), width=50, height=24,
                                           corner_radius=6, fg_color=self.colors['button_default'],
                                           hover_color=self.colors['button_hover'],
                                           text_color=self.colors['text_body'],
                                           font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                           command=lambda: self.change_quick_hotkey('sd'))
        self.sd_hotkey_btn.pack(side=tk.LEFT, padx=4)
        
        # Location button
        ctk.CTkButton(sd_inner, text="📍", width=28, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.record_quick_positions('sd')).pack(side=tk.LEFT, padx=2)
        
        # Modern Slider
        self.sd_slider = ctk.CTkSlider(sd_inner, from_=10, to=500, number_of_steps=49,
                                       width=100, height=16, variable=self.auto_sd_delay,
                                       progress_color=self.colors['slider_progress'],
                                       button_color=self.colors['slider_button'],
                                       button_hover_color="#FFFFFF",
                                       fg_color=self.colors['bg_inset'],
                                       command=lambda v: self.save_quick_configs())
        self.sd_slider.pack(side=tk.LEFT, padx=6)
        
        self.sd_delay_label = ctk.CTkLabel(sd_inner, text=f"{self.auto_sd_delay.get()}ms", width=50,
                                           font=ctk.CTkFont(family="Consolas", size=10),
                                           text_color=self.colors['text_subdued'])
        self.sd_delay_label.pack(side=tk.LEFT)
        self.auto_sd_delay.trace('w', lambda *args: self.sd_delay_label.configure(text=f"{self.auto_sd_delay.get()}ms"))
        
        # Auto EXPLO Row - Modern Card Style
        self.auto_explo_enabled = tk.BooleanVar(value=False)
        self.auto_explo_hotkey = tk.StringVar(value="F4")
        self.auto_explo_delay = tk.IntVar(value=100)
        
        try:
            explo_img = Image.open(resource_path('explo_rune_icon.png'))
            explo_img = explo_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.explo_icon_photo = ImageTk.PhotoImage(explo_img)
        except:
            self.explo_icon_photo = None
        
        self.explo_frame = ctk.CTkFrame(quick_frame, fg_color=self.colors['bg_secondary'], 
                                        corner_radius=8, border_width=1, border_color=self.colors['border'])
        self.explo_frame.pack(fill=tk.X, pady=3, padx=2)
        
        explo_inner = ctk.CTkFrame(self.explo_frame, fg_color="transparent")
        explo_inner.pack(fill=tk.X, padx=8, pady=6)
        
        self.explo_switch = ctk.CTkSwitch(explo_inner, text="", width=40, height=20,
                                          switch_width=36, switch_height=18,
                                          progress_color=self.colors['switch_on'],
                                          button_color="#FFFFFF", fg_color=self.colors['switch_off'],
                                          variable=self.auto_explo_enabled, command=self.save_quick_configs)
        self.explo_switch.pack(side=tk.LEFT, padx=4)
        
        if self.explo_icon_photo:
            tk.Label(explo_inner, image=self.explo_icon_photo, bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(explo_inner, text="Auto EXPLO", font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
                    text_color=self.colors['text_header'], width=70).pack(side=tk.LEFT, padx=4)
        
        self.explo_hotkey_btn = ctk.CTkButton(explo_inner, text=self.auto_explo_hotkey.get(), width=50, height=24,
                                              corner_radius=6, fg_color=self.colors['button_default'],
                                              hover_color=self.colors['button_hover'],
                                              text_color=self.colors['text_body'],
                                              font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                              command=lambda: self.change_quick_hotkey('explo'))
        self.explo_hotkey_btn.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkButton(explo_inner, text="📍", width=28, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.record_quick_positions('explo')).pack(side=tk.LEFT, padx=2)
        
        self.explo_slider = ctk.CTkSlider(explo_inner, from_=10, to=500, number_of_steps=49,
                                          width=100, height=16, variable=self.auto_explo_delay,
                                          progress_color=self.colors['slider_progress'],
                                          button_color=self.colors['slider_button'],
                                          button_hover_color="#FFFFFF", fg_color=self.colors['bg_inset'],
                                          command=lambda v: self.save_quick_configs())
        self.explo_slider.pack(side=tk.LEFT, padx=6)
        
        self.explo_delay_label = ctk.CTkLabel(explo_inner, text=f"{self.auto_explo_delay.get()}ms", width=50,
                                              font=ctk.CTkFont(family="Consolas", size=10),
                                              text_color=self.colors['text_subdued'])
        self.explo_delay_label.pack(side=tk.LEFT)
        self.auto_explo_delay.trace('w', lambda *args: self.explo_delay_label.configure(text=f"{self.auto_explo_delay.get()}ms"))
        
        # Auto UH Row - Modern Card Style
        self.auto_uh_enabled = tk.BooleanVar(value=False)
        self.auto_uh_hotkey = tk.StringVar(value="F2")
        self.auto_uh_delay = tk.IntVar(value=100)
        
        try:
            uh_img = Image.open(resource_path('uh_rune_icon.png'))
            uh_img = uh_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.uh_icon_photo = ImageTk.PhotoImage(uh_img)
        except:
            self.uh_icon_photo = None
        
        self.uh_frame = ctk.CTkFrame(quick_frame, fg_color=self.colors['bg_secondary'], 
                                     corner_radius=8, border_width=1, border_color=self.colors['border'])
        self.uh_frame.pack(fill=tk.X, pady=3, padx=2)
        
        uh_inner = ctk.CTkFrame(self.uh_frame, fg_color="transparent")
        uh_inner.pack(fill=tk.X, padx=8, pady=6)
        
        self.uh_switch = ctk.CTkSwitch(uh_inner, text="", width=40, height=20,
                                       switch_width=36, switch_height=18,
                                       progress_color=self.colors['switch_on'],
                                       button_color="#FFFFFF", fg_color=self.colors['switch_off'],
                                       variable=self.auto_uh_enabled, command=self.save_quick_configs)
        self.uh_switch.pack(side=tk.LEFT, padx=4)
        
        if self.uh_icon_photo:
            tk.Label(uh_inner, image=self.uh_icon_photo, bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(uh_inner, text="Auto UH", font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
                    text_color=self.colors['text_header'], width=70).pack(side=tk.LEFT, padx=4)
        
        self.uh_hotkey_btn = ctk.CTkButton(uh_inner, text=self.auto_uh_hotkey.get(), width=50, height=24,
                                           corner_radius=6, fg_color=self.colors['button_default'],
                                           hover_color=self.colors['button_hover'],
                                           text_color=self.colors['text_body'],
                                           font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                           command=lambda: self.change_quick_hotkey('uh'))
        self.uh_hotkey_btn.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkButton(uh_inner, text="📍", width=28, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.record_quick_positions('uh')).pack(side=tk.LEFT, padx=2)
        
        self.uh_slider = ctk.CTkSlider(uh_inner, from_=10, to=500, number_of_steps=49,
                                       width=100, height=16, variable=self.auto_uh_delay,
                                       progress_color=self.colors['slider_progress'],
                                       button_color=self.colors['slider_button'],
                                       button_hover_color="#FFFFFF", fg_color=self.colors['bg_inset'],
                                       command=lambda v: self.save_quick_configs())
        self.uh_slider.pack(side=tk.LEFT, padx=6)
        
        self.uh_delay_label = ctk.CTkLabel(uh_inner, text=f"{self.auto_uh_delay.get()}ms", width=50,
                                           font=ctk.CTkFont(family="Consolas", size=10),
                                           text_color=self.colors['text_subdued'])
        self.uh_delay_label.pack(side=tk.LEFT)
        self.auto_uh_delay.trace('w', lambda *args: self.uh_delay_label.configure(text=f"{self.auto_uh_delay.get()}ms"))
        
        # Auto MANA Row - Modern Card Style
        self.auto_mana_enabled = tk.BooleanVar(value=False)
        self.auto_mana_hotkey = tk.StringVar(value="F3")
        self.auto_mana_delay = tk.IntVar(value=100)
        
        try:
            mana_img = Image.open(resource_path('mana_icon.png'))
            mana_img = mana_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.mana_icon_photo = ImageTk.PhotoImage(mana_img)
        except:
            self.mana_icon_photo = None
        
        self.mana_frame = ctk.CTkFrame(quick_frame, fg_color=self.colors['bg_secondary'], 
                                       corner_radius=8, border_width=1, border_color=self.colors['border'])
        self.mana_frame.pack(fill=tk.X, pady=3, padx=2)
        
        mana_inner = ctk.CTkFrame(self.mana_frame, fg_color="transparent")
        mana_inner.pack(fill=tk.X, padx=8, pady=6)
        
        self.mana_switch = ctk.CTkSwitch(mana_inner, text="", width=40, height=20,
                                         switch_width=36, switch_height=18,
                                         progress_color=self.colors['switch_on'],
                                         button_color="#FFFFFF", fg_color=self.colors['switch_off'],
                                         variable=self.auto_mana_enabled, command=self.save_quick_configs)
        self.mana_switch.pack(side=tk.LEFT, padx=4)
        
        if self.mana_icon_photo:
            tk.Label(mana_inner, image=self.mana_icon_photo, bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(mana_inner, text="Auto Mana", font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
                    text_color=self.colors['text_header'], width=70).pack(side=tk.LEFT, padx=4)
        
        self.mana_hotkey_btn = ctk.CTkButton(mana_inner, text=self.auto_mana_hotkey.get(), width=50, height=24,
                                             corner_radius=6, fg_color=self.colors['button_default'],
                                             hover_color=self.colors['button_hover'],
                                             text_color=self.colors['text_body'],
                                             font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                             command=lambda: self.change_quick_hotkey('mana'))
        self.mana_hotkey_btn.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkButton(mana_inner, text="📍", width=28, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.record_quick_positions('mana')).pack(side=tk.LEFT, padx=2)
        
        self.mana_slider = ctk.CTkSlider(mana_inner, from_=10, to=500, number_of_steps=49,
                                         width=100, height=16, variable=self.auto_mana_delay,
                                         progress_color=self.colors['slider_progress'],
                                         button_color=self.colors['slider_button'],
                                         button_hover_color="#FFFFFF", fg_color=self.colors['bg_inset'],
                                         command=lambda v: self.save_quick_configs())
        self.mana_slider.pack(side=tk.LEFT, padx=6)
        
        self.mana_delay_label = ctk.CTkLabel(mana_inner, text=f"{self.auto_mana_delay.get()}ms", width=50,
                                             font=ctk.CTkFont(family="Consolas", size=10),
                                             text_color=self.colors['text_subdued'])
        self.mana_delay_label.pack(side=tk.LEFT)
        self.auto_mana_delay.trace('w', lambda *args: self.mana_delay_label.configure(text=f"{self.auto_mana_delay.get()}ms"))
        
        # ========== RUNEMAKER TAB CONTENT ==========
        runemaker_scroll = ctk.CTkScrollableFrame(self.tab_runemaker, fg_color="transparent")
        runemaker_scroll.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Runemaker enabled toggle
        self.runemaker_enabled = tk.BooleanVar(value=False)
        self.runemaker_running = False
        self.runemaker_paused = False
        self.runemaker_thread = None
        self.rm_pause_hotkey = tk.StringVar(value="F9")
        
        # Toggle card
        rm_toggle_card = ctk.CTkFrame(runemaker_scroll, fg_color=self.colors['bg_secondary'],
                                      corner_radius=8, border_width=1, border_color=self.colors['border'])
        rm_toggle_card.pack(fill=tk.X, pady=3, padx=2)
        
        rm_toggle_inner = ctk.CTkFrame(rm_toggle_card, fg_color="transparent")
        rm_toggle_inner.pack(fill=tk.X, padx=10, pady=8)
        
        self.rm_switch = ctk.CTkSwitch(rm_toggle_inner, text="", width=40, height=20,
                                       switch_width=36, switch_height=18,
                                       progress_color=self.colors['switch_on'],
                                       button_color="#FFFFFF", fg_color=self.colors['switch_off'],
                                       variable=self.runemaker_enabled, command=self.toggle_runemaker)
        self.rm_switch.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(rm_toggle_inner, text="Runemaker Ativo", 
                    font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
                    text_color=self.colors['text_header']).pack(side=tk.LEFT, padx=8)
        
        self.rm_status_label = ctk.CTkLabel(rm_toggle_inner, text="[PARADO]", 
                                            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                            text_color=self.colors['status_off'])
        self.rm_status_label.pack(side=tk.RIGHT, padx=10)
        
        # Config frame for Runemaker options
        rm_config_card = ctk.CTkFrame(runemaker_scroll, fg_color=self.colors['bg_secondary'],
                                      corner_radius=8, border_width=1, border_color=self.colors['border'])
        rm_config_card.pack(fill=tk.X, pady=3, padx=2)
        
        rm_config_inner = ctk.CTkFrame(rm_config_card, fg_color="transparent")
        rm_config_inner.pack(fill=tk.X, padx=10, pady=8)
        
        # Row 1: Potion positions
        rm_row1 = ctk.CTkFrame(rm_config_inner, fg_color="transparent")
        rm_row1.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(rm_row1, text="Potion:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        ctk.CTkButton(rm_row1, text="📍 Gravar", width=80, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     text_color=self.colors['text_body'], font=ctk.CTkFont(size=10),
                     command=self.record_runemaker_potion).pack(side=tk.LEFT, padx=4)
        
        self.rm_potion_status = ctk.CTkLabel(rm_row1, text="[Nao gravado]", width=120,
                                             font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                                             text_color=self.colors['text_subdued'])
        self.rm_potion_status.pack(side=tk.LEFT, padx=8)
        
        # Row 2: Spell hotkey
        rm_row2 = ctk.CTkFrame(rm_config_inner, fg_color="transparent")
        rm_row2.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(rm_row2, text="Spell:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        self.rm_spell_hotkey = tk.StringVar(value="F6")
        self.rm_spell_btn = ctk.CTkButton(rm_row2, text=self.rm_spell_hotkey.get(), width=50, height=24,
                                          corner_radius=6, fg_color=self.colors['selection'],
                                          hover_color=self.colors['button_hover'],
                                          text_color="#FFFFFF", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                          command=lambda: self.change_runemaker_hotkey('spell'))
        self.rm_spell_btn.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(rm_row2, text="(tecla spell)", font=ctk.CTkFont(family="Consolas", size=9),
                    text_color=self.colors['text_subdued']).pack(side=tk.LEFT, padx=8)
        
        # Row 3: Delay slider
        rm_row3 = ctk.CTkFrame(rm_config_inner, fg_color="transparent")
        rm_row3.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(rm_row3, text="Delay:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        self.rm_delay = tk.IntVar(value=500)
        self.rm_delay_slider = ctk.CTkSlider(rm_row3, from_=100, to=2000, number_of_steps=38,
                                             width=140, height=16, variable=self.rm_delay,
                                             progress_color=self.colors['slider_progress'],
                                             button_color=self.colors['slider_button'],
                                             button_hover_color="#FFFFFF", fg_color=self.colors['bg_inset'])
        self.rm_delay_slider.pack(side=tk.LEFT, padx=4)
        
        self.rm_delay_label = ctk.CTkLabel(rm_row3, text="500ms", width=60,
                                           font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                           text_color=self.colors['status_on'])
        self.rm_delay_label.pack(side=tk.LEFT, padx=4)
        self.rm_delay.trace('w', lambda *args: self.rm_delay_label.configure(text=f"{self.rm_delay.get()}ms"))
        
        # Row 4: Potions per cycle
        rm_row4 = ctk.CTkFrame(rm_config_inner, fg_color="transparent")
        rm_row4.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(rm_row4, text="Potions:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        self.rm_potions_count = tk.IntVar(value=3)
        ctk.CTkButton(rm_row4, text="-", width=28, height=24, corner_radius=4,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.rm_potions_count.set(max(1, self.rm_potions_count.get()-1))).pack(side=tk.LEFT)
        self.rm_potions_label = ctk.CTkLabel(rm_row4, text="3", width=30,
                                             font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                                             text_color=self.colors['status_on'])
        self.rm_potions_label.pack(side=tk.LEFT)
        ctk.CTkButton(rm_row4, text="+", width=28, height=24, corner_radius=4,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.rm_potions_count.set(min(20, self.rm_potions_count.get()+1))).pack(side=tk.LEFT)
        self.rm_potions_count.trace('w', lambda *args: self.rm_potions_label.configure(text=str(self.rm_potions_count.get())))
        
        ctk.CTkLabel(rm_row4, text="por ciclo", font=ctk.CTkFont(family="Consolas", size=9),
                    text_color=self.colors['text_subdued']).pack(side=tk.LEFT, padx=8)
        
        # Row 5: Casts per cycle
        rm_row5 = ctk.CTkFrame(rm_config_inner, fg_color="transparent")
        rm_row5.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(rm_row5, text="Casts:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        self.rm_casts_count = tk.IntVar(value=1)
        ctk.CTkButton(rm_row5, text="-", width=28, height=24, corner_radius=4,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.rm_casts_count.set(max(1, self.rm_casts_count.get()-1))).pack(side=tk.LEFT)
        self.rm_casts_label = ctk.CTkLabel(rm_row5, text="1", width=30,
                                           font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                                           text_color=self.colors['status_on'])
        self.rm_casts_label.pack(side=tk.LEFT)
        ctk.CTkButton(rm_row5, text="+", width=28, height=24, corner_radius=4,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     command=lambda: self.rm_casts_count.set(min(20, self.rm_casts_count.get()+1))).pack(side=tk.LEFT)
        self.rm_casts_count.trace('w', lambda *args: self.rm_casts_label.configure(text=str(self.rm_casts_count.get())))
        
        ctk.CTkLabel(rm_row5, text="por ciclo", font=ctk.CTkFont(family="Consolas", size=9),
                    text_color=self.colors['text_subdued']).pack(side=tk.LEFT, padx=8)
        
        # Row 6: Pause hotkey
        rm_row6 = ctk.CTkFrame(rm_config_inner, fg_color="transparent")
        rm_row6.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(rm_row6, text="Pausar:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        self.rm_pause_btn = ctk.CTkButton(rm_row6, text=self.rm_pause_hotkey.get(), width=50, height=24,
                                          corner_radius=6, fg_color=self.colors['button_default'],
                                          hover_color=self.colors['button_hover'],
                                          text_color="#FFFFFF", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                          command=self.change_runemaker_pause_hotkey)
        self.rm_pause_btn.pack(side=tk.LEFT, padx=4)
        
        self.rm_pause_status = ctk.CTkLabel(rm_row6, text="", width=80,
                                            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                                            text_color=self.colors['status_off'])
        self.rm_pause_status.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(rm_row6, text="(pausar/continuar)", font=ctk.CTkFont(family="Consolas", size=8),
                    text_color=self.colors['text_subdued']).pack(side=tk.LEFT, padx=5)
        
        # Cycle info box
        rm_info_card = ctk.CTkFrame(runemaker_scroll, fg_color=self.colors['bg_primary'],
                                    corner_radius=8, border_width=1, border_color=self.colors['border'])
        rm_info_card.pack(fill=tk.X, pady=3, padx=2)
        
        self.rm_cycle_info = ctk.CTkLabel(rm_info_card, text="Ciclo: 3 potions + 1 cast -> repete",
                                          font=ctk.CTkFont(family="Consolas", size=9),
                                          text_color=self.colors['text_body'])
        self.rm_cycle_info.pack(pady=4)
        
        self.rm_cycle_label = ctk.CTkLabel(rm_info_card, text="",
                                           font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                           text_color=self.colors['status_on'])
        self.rm_cycle_label.pack(pady=2)
        
        # ========== HYPER GRAB TAB CONTENT ==========
        hypergrab_scroll = ctk.CTkScrollableFrame(self.tab_hyper_grab, fg_color="transparent")
        hypergrab_scroll.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Hyper Grab enabled toggle
        self.hypergrab_enabled = tk.BooleanVar(value=False)
        self.hypergrab_hotkey = tk.StringVar(value="F5")
        self.hypergrab_bp_pos = None
        
        # Toggle card
        hg_toggle_card = ctk.CTkFrame(hypergrab_scroll, fg_color=self.colors['bg_secondary'],
                                      corner_radius=8, border_width=1, border_color=self.colors['border'])
        hg_toggle_card.pack(fill=tk.X, pady=3, padx=2)
        
        hg_toggle_inner = ctk.CTkFrame(hg_toggle_card, fg_color="transparent")
        hg_toggle_inner.pack(fill=tk.X, padx=10, pady=8)
        
        self.hg_switch = ctk.CTkSwitch(hg_toggle_inner, text="", width=40, height=20,
                                       switch_width=36, switch_height=18,
                                       progress_color=self.colors['switch_on'],
                                       button_color="#FFFFFF", fg_color=self.colors['switch_off'],
                                       variable=self.hypergrab_enabled, command=self.toggle_hypergrab)
        self.hg_switch.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(hg_toggle_inner, text="Hyper Grab", 
                    font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
                    text_color=self.colors['text_header']).pack(side=tk.LEFT, padx=8)
        
        self.hg_status_label = ctk.CTkLabel(hg_toggle_inner, text="[OFF]",
                                            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                            text_color=self.colors['status_off'])
        self.hg_status_label.pack(side=tk.RIGHT, padx=10)
        
        # Config card
        hg_config_card = ctk.CTkFrame(hypergrab_scroll, fg_color=self.colors['bg_secondary'],
                                      corner_radius=8, border_width=1, border_color=self.colors['border'])
        hg_config_card.pack(fill=tk.X, pady=3, padx=2)
        
        hg_config_inner = ctk.CTkFrame(hg_config_card, fg_color="transparent")
        hg_config_inner.pack(fill=tk.X, padx=10, pady=8)
        
        # Row 1: Hotkey
        hg_row1 = ctk.CTkFrame(hg_config_inner, fg_color="transparent")
        hg_row1.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(hg_row1, text="Hotkey:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        self.hg_hotkey_btn = ctk.CTkButton(hg_row1, text=self.hypergrab_hotkey.get(), width=50, height=24,
                                           corner_radius=6, fg_color=self.colors['selection'],
                                           hover_color=self.colors['button_hover'],
                                           text_color="#FFFFFF", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                           command=self.change_hypergrab_hotkey)
        self.hg_hotkey_btn.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(hg_row1, text="(arrasta item pra BP)", font=ctk.CTkFont(family="Consolas", size=9),
                    text_color=self.colors['text_subdued']).pack(side=tk.LEFT, padx=8)
        
        # Row 2: Backpack slot position
        hg_row2 = ctk.CTkFrame(hg_config_inner, fg_color="transparent")
        hg_row2.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(hg_row2, text="Slot BP:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        ctk.CTkButton(hg_row2, text="📍 Gravar", width=80, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     text_color=self.colors['text_body'], font=ctk.CTkFont(size=10),
                     command=self.record_hypergrab_bp).pack(side=tk.LEFT, padx=4)
        
        self.hg_bp_status = ctk.CTkLabel(hg_row2, text="[Nao gravado]", width=120,
                                         font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                                         text_color=self.colors['text_subdued'])
        self.hg_bp_status.pack(side=tk.LEFT, padx=8)
        
        # Info box
        hg_info_card = ctk.CTkFrame(hypergrab_scroll, fg_color=self.colors['bg_primary'],
                                    corner_radius=8, border_width=1, border_color=self.colors['border'])
        hg_info_card.pack(fill=tk.X, pady=3, padx=2)
        
        ctk.CTkLabel(hg_info_card, text="Aperte hotkey -> item sob o mouse vai INSTANTANEAMENTE pra BP",
                    font=ctk.CTkFont(family="Consolas", size=9),
                    text_color=self.colors['text_body']).pack(pady=6)
        
        # ========== DRAG HOTKEY SECTION ==========
        drag_header = ctk.CTkFrame(hypergrab_scroll, fg_color=self.colors['border_highlight'],
                                   corner_radius=6)
        drag_header.pack(fill=tk.X, pady=(10, 3), padx=2)
        
        ctk.CTkLabel(drag_header, text="⚡ DRAG HOTKEY", 
                    font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
                    text_color="#FFFFFF").pack(pady=4)
        
        # Drag Hotkey variables
        self.drag_enabled = tk.BooleanVar(value=False)
        self.drag_hotkey = tk.StringVar(value="F8")
        self.drag_start_pos = None
        self.drag_end_pos = None
        
        # Drag toggle card
        drag_toggle_card = ctk.CTkFrame(hypergrab_scroll, fg_color=self.colors['bg_secondary'],
                                        corner_radius=8, border_width=1, border_color=self.colors['border'])
        drag_toggle_card.pack(fill=tk.X, pady=3, padx=2)
        
        drag_toggle_inner = ctk.CTkFrame(drag_toggle_card, fg_color="transparent")
        drag_toggle_inner.pack(fill=tk.X, padx=10, pady=8)
        
        self.drag_switch = ctk.CTkSwitch(drag_toggle_inner, text="", width=40, height=20,
                                         switch_width=36, switch_height=18,
                                         progress_color=self.colors['switch_on'],
                                         button_color="#FFFFFF", fg_color=self.colors['switch_off'],
                                         variable=self.drag_enabled, command=self.toggle_drag_hotkey)
        self.drag_switch.pack(side=tk.LEFT, padx=4)
        
        ctk.CTkLabel(drag_toggle_inner, text="Drag Hotkey", 
                    font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
                    text_color=self.colors['text_header']).pack(side=tk.LEFT, padx=8)
        
        self.drag_status_label = ctk.CTkLabel(drag_toggle_inner, text="[OFF]",
                                              font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                              text_color=self.colors['status_off'])
        self.drag_status_label.pack(side=tk.RIGHT, padx=10)
        
        # Drag config card
        drag_config_card = ctk.CTkFrame(hypergrab_scroll, fg_color=self.colors['bg_secondary'],
                                        corner_radius=8, border_width=1, border_color=self.colors['border'])
        drag_config_card.pack(fill=tk.X, pady=3, padx=2)
        
        drag_config_inner = ctk.CTkFrame(drag_config_card, fg_color="transparent")
        drag_config_inner.pack(fill=tk.X, padx=10, pady=8)
        
        # Row 1: Hotkey
        drag_row1 = ctk.CTkFrame(drag_config_inner, fg_color="transparent")
        drag_row1.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(drag_row1, text="Hotkey:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        self.drag_hotkey_btn = ctk.CTkButton(drag_row1, text=self.drag_hotkey.get(), width=50, height=24,
                                             corner_radius=6, fg_color=self.colors['selection'],
                                             hover_color=self.colors['button_hover'],
                                             text_color="#FFFFFF", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                                             command=self.change_drag_hotkey)
        self.drag_hotkey_btn.pack(side=tk.LEFT, padx=4)
        
        # Row 2: Destination position (onde vai soltar)
        drag_row2 = ctk.CTkFrame(drag_config_inner, fg_color="transparent")
        drag_row2.pack(fill=tk.X, pady=4)
        
        ctk.CTkLabel(drag_row2, text="Destino:", font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_body'], width=80).pack(side=tk.LEFT)
        
        ctk.CTkButton(drag_row2, text="📍 Gravar", width=80, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     text_color=self.colors['text_body'], font=ctk.CTkFont(size=10),
                     command=self.record_drag_destination).pack(side=tk.LEFT, padx=4)
        
        self.drag_dest_status = ctk.CTkLabel(drag_row2, text="[Nao gravado]", width=120,
                                              font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                                              text_color=self.colors['text_subdued'])
        self.drag_dest_status.pack(side=tk.LEFT, padx=8)
        
        ctk.CTkLabel(drag_row2, text="(onde solta)", font=ctk.CTkFont(family="Consolas", size=8),
                    text_color=self.colors['text_subdued']).pack(side=tk.LEFT)
        
        # Drag info box
        drag_info_card = ctk.CTkFrame(hypergrab_scroll, fg_color=self.colors['bg_primary'],
                                      corner_radius=8, border_width=1, border_color=self.colors['border'])
        drag_info_card.pack(fill=tk.X, pady=3, padx=2)
        
        ctk.CTkLabel(drag_info_card, text="Hotkey → De onde o mouse esta, arrasta ate o destino gravado",
                    font=ctk.CTkFont(family="Consolas", size=9),
                    text_color=self.colors['text_body']).pack(pady=6)
        
        # ========== SETTINGS TAB CONTENT ==========
        settings_scroll = ctk.CTkScrollableFrame(self.tab_settings, fg_color="transparent")
        settings_scroll.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Movement mode card
        movement_card = ctk.CTkFrame(settings_scroll, fg_color=self.colors['bg_secondary'],
                                     corner_radius=8, border_width=1, border_color=self.colors['border'])
        movement_card.pack(fill=tk.X, pady=3, padx=2)
        
        movement_inner = ctk.CTkFrame(movement_card, fg_color="transparent")
        movement_inner.pack(fill=tk.X, padx=10, pady=8)
        
        self.instant_movement = tk.BooleanVar(value=False)
        
        ctk.CTkLabel(movement_inner, text="Modo de Movimento:", 
                    font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_header']).pack(side=tk.LEFT, padx=4)
        
        ctk.CTkSwitch(movement_inner, text="Teleporte Instantaneo", width=40, height=20,
                     switch_width=36, switch_height=18,
                     progress_color=self.colors['switch_on'],
                     button_color="#FFFFFF", fg_color=self.colors['switch_off'],
                     variable=self.instant_movement, font=ctk.CTkFont(family="Georgia", size=9),
                     text_color=self.colors['text_body']).pack(side=tk.LEFT, padx=8)
        
        # Custom hotkey management card
        hotkey_card = ctk.CTkFrame(settings_scroll, fg_color=self.colors['bg_secondary'],
                                   corner_radius=8, border_width=1, border_color=self.colors['border'])
        hotkey_card.pack(fill=tk.X, pady=3, padx=2)
        
        hotkey_inner = ctk.CTkFrame(hotkey_card, fg_color="transparent")
        hotkey_inner.pack(fill=tk.X, padx=10, pady=8)
        
        ctk.CTkLabel(hotkey_inner, text="Custom Hotkeys:", 
                    font=ctk.CTkFont(family="Georgia", size=10, weight="bold"),
                    text_color=self.colors['text_header']).pack(side=tk.LEFT, padx=4)
        
        ctk.CTkButton(hotkey_inner, text="+", width=32, height=24, corner_radius=6,
                     fg_color=self.colors['selection'], hover_color=self.colors['button_hover'],
                     font=ctk.CTkFont(size=12, weight="bold"), command=self.add_hotkey_dialog).pack(side=tk.LEFT, padx=3)
        ctk.CTkButton(hotkey_inner, text="Edit", width=50, height=24, corner_radius=6,
                     fg_color=self.colors['button_default'], hover_color=self.colors['button_hover'],
                     font=ctk.CTkFont(size=10), command=self.edit_hotkey).pack(side=tk.LEFT, padx=3)
        ctk.CTkButton(hotkey_inner, text="Del", width=50, height=24, corner_radius=6,
                     fg_color=self.colors['button_destructive'], hover_color="#8B0000",
                     font=ctk.CTkFont(size=10), command=self.delete_hotkey).pack(side=tk.LEFT, padx=3)
        ctk.CTkButton(hotkey_inner, text="Clear", width=50, height=24, corner_radius=6,
                     fg_color=self.colors['button_destructive'], hover_color="#8B0000",
                     font=ctk.CTkFont(size=10), command=self.clear_all).pack(side=tk.LEFT, padx=3)
        
        # Hotkey list (Treeview - keeping tk.ttk as no CTk equivalent)
        list_frame = ctk.CTkFrame(settings_scroll, fg_color=self.colors['bg_inset'],
                                  corner_radius=8, border_width=1, border_color=self.colors['border'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=3, padx=2)
        
        list_inner = tk.Frame(list_frame, bg=self.colors['bg_inset'], padx=4, pady=4)
        list_inner.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Hotkey', 'Clicks', 'Delay')
        self.tree = ttk.Treeview(list_inner, columns=columns, show='headings', height=6)
        
        self.tree.heading('Hotkey', text='Hotkey')
        self.tree.heading('Clicks', text='Clicks')
        self.tree.heading('Delay', text='Delay')
        
        self.tree.column('Hotkey', width=80)
        self.tree.column('Clicks', width=250)
        self.tree.column('Delay', width=70)
        
        scrollbar = ttk.Scrollbar(list_inner, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ========== TARGETING TAB CONTENT ==========
        targeting_scroll = ctk.CTkScrollableFrame(self.tab_targeting, fg_color="transparent")
        targeting_scroll.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Header card
        targeting_header = ctk.CTkFrame(targeting_scroll, fg_color=self.colors['bg_secondary'],
                                        corner_radius=8, border_width=1, border_color=self.colors['border'])
        targeting_header.pack(fill=tk.X, pady=3, padx=2)
        
        ctk.CTkLabel(targeting_header, text="Auto-Target Configuration",
                    font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
                    text_color=self.colors['text_header']).pack(pady=8)
        
        ctk.CTkLabel(targeting_header, text="Use o botao de calibrar para configurar o auto-target",
                    font=ctk.CTkFont(family="Georgia", size=9),
                    text_color=self.colors['text_body']).pack(pady=4)
        
        # Load quick configs from saved data
        self.load_quick_configs()
        
        # Load runemaker config
        self.load_runemaker_config()
        
        # Load hypergrab config
        self.load_hypergrab_config()
        
        # Load drag hotkey config
        self.load_drag_config()
        
        self.refresh_tree()
    
    def load_quick_configs(self):
        """Load quick config settings from config file"""
        quick = self.config.get('quick_configs', {})
        
        # Auto SD
        sd = quick.get('auto_sd', {})
        self.auto_sd_enabled.set(sd.get('enabled', False))
        self.auto_sd_hotkey.set(sd.get('hotkey', 'F1'))
        self.auto_sd_delay.set(sd.get('delay', 100))
        
        # Auto EXPLO
        explo = quick.get('auto_explo', {})
        self.auto_explo_enabled.set(explo.get('enabled', False))
        self.auto_explo_hotkey.set(explo.get('hotkey', 'F4'))
        self.auto_explo_delay.set(explo.get('delay', 100))
        
        # Auto UH
        uh = quick.get('auto_uh', {})
        self.auto_uh_enabled.set(uh.get('enabled', False))
        self.auto_uh_hotkey.set(uh.get('hotkey', 'F2'))
        self.auto_uh_delay.set(uh.get('delay', 100))
        
        # Auto MANA
        mana = quick.get('auto_mana', {})
        self.auto_mana_enabled.set(mana.get('enabled', False))
        self.auto_mana_hotkey.set(mana.get('hotkey', 'F3'))
        self.auto_mana_delay.set(mana.get('delay', 100))
        
        # Update visual buttons after loading
        if hasattr(self, 'sd_enabled_btn'):
            self.update_checkbox_icon(self.sd_enabled_btn, self.auto_sd_enabled)
        if hasattr(self, 'explo_enabled_btn'):
            self.update_checkbox_icon(self.explo_enabled_btn, self.auto_explo_enabled)
        if hasattr(self, 'uh_enabled_btn'):
            self.update_checkbox_icon(self.uh_enabled_btn, self.auto_uh_enabled)
        if hasattr(self, 'mana_enabled_btn'):
            self.update_checkbox_icon(self.mana_enabled_btn, self.auto_mana_enabled)
        if hasattr(self, 'sd_hotkey_btn'):
            self.sd_hotkey_btn.configure(text=f"{self.auto_sd_hotkey.get()}")
        if hasattr(self, 'explo_hotkey_btn'):
            self.explo_hotkey_btn.configure(text=f"{self.auto_explo_hotkey.get()}")
        if hasattr(self, 'uh_hotkey_btn'):
            self.uh_hotkey_btn.configure(text=f"{self.auto_uh_hotkey.get()}")
        if hasattr(self, 'mana_hotkey_btn'):
            self.mana_hotkey_btn.configure(text=f"{self.auto_mana_hotkey.get()}")
    
    def save_quick_configs(self):
        """Save quick config settings to config file"""
        if 'quick_configs' not in self.config:
            self.config['quick_configs'] = {}
        
        # Auto SD (auto-target always enabled)
        self.config['quick_configs']['auto_sd'] = {
            'enabled': self.auto_sd_enabled.get(),
            'hotkey': self.auto_sd_hotkey.get(),
            'auto_target': True,
            'delay': self.auto_sd_delay.get(),
            'clicks': self.config.get('quick_configs', {}).get('auto_sd', {}).get('clicks', [])
        }
        
        # Auto EXPLO (auto-target always enabled)
        self.config['quick_configs']['auto_explo'] = {
            'enabled': self.auto_explo_enabled.get(),
            'hotkey': self.auto_explo_hotkey.get(),
            'auto_target': True,
            'delay': self.auto_explo_delay.get(),
            'clicks': self.config.get('quick_configs', {}).get('auto_explo', {}).get('clicks', [])
        }
        
        # Auto MANA
        self.config['quick_configs']['auto_mana'] = {
            'enabled': self.auto_mana_enabled.get(),
            'hotkey': self.auto_mana_hotkey.get(),
            'delay': self.auto_mana_delay.get(),
            'clicks': self.config.get('quick_configs', {}).get('auto_mana', {}).get('clicks', [])
        }
        
        # Auto UH
        self.config['quick_configs']['auto_uh'] = {
            'enabled': self.auto_uh_enabled.get(),
            'hotkey': self.auto_uh_hotkey.get(),
            'delay': self.auto_uh_delay.get(),
            'clicks': self.config.get('quick_configs', {}).get('auto_uh', {}).get('clicks', [])
        }
        
        self.save_config()
    
    def toggle_runemaker(self):
        """Toggle runemaker on/off"""
        if self.runemaker_enabled.get():
            # Starting runemaker
            if self.runemaker_running:
                return  # Already running
            
            self.runemaker_running = True
            self.rm_status_label.configure(text="[RODANDO]", text_color=self.colors['status_on'])
            
            # Start runemaker thread
            self.runemaker_thread = threading.Thread(target=self.execute_runemaker_cycle, daemon=True)
            self.runemaker_thread.start()
            print("[RUNEMAKER] Iniciado!")
        else:
            # Stopping runemaker
            self.runemaker_running = False
            self.rm_status_label.configure(text="[PARADO]", text_color=self.colors['status_off'])
            self.rm_cycle_label.configure(text="")
            print("[RUNEMAKER] Parado!")
        
        self.save_runemaker_config()
    
    def record_runemaker_potion(self):
        """Record potion and character positions for runemaker (like UH)"""
        dialog = self.create_ember_dialog("Gravar Posicoes - Potion", 450, 300)
        
        tk.Label(dialog, text="Gravar Posicoes da Potion", font=('Georgia', 12, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=10)
        
        instruction = """1. Clique em "Iniciar Gravacao"
2. Clique na POTION (sera clique direito)
3. Clique no seu PERSONAGEM (sera clique esquerdo)"""
        
        tk.Label(dialog, text=instruction, font=('Consolas', 9), justify=tk.LEFT,
                bg=self.colors['bg_primary'], fg=self.colors['text_body']).pack(pady=10)
        
        status_var = tk.StringVar(value="Pronto para gravar...")
        tk.Label(dialog, textvariable=status_var, font=('Consolas', 10, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['status_on']).pack(pady=10)
        
        clicks_recorded = []
        
        def on_click(x, y, button, pressed):
            if pressed and len(clicks_recorded) < 2:
                clicks_recorded.append({'x': x, 'y': y})
                if len(clicks_recorded) == 1:
                    status_var.set(f"Potion: ({x}, {y})\nAgora clique no PERSONAGEM...")
                elif len(clicks_recorded) == 2:
                    status_var.set(f"Potion: ({clicks_recorded[0]['x']}, {clicks_recorded[0]['y']})\nChar: ({x}, {y})\nPronto!")
                    return False
        
        def start_recording():
            clicks_recorded.clear()
            status_var.set("Clique na POTION...")
            dialog.after(100, lambda: mouse.Listener(on_click=on_click).start())
        
        tk.Button(dialog, text="Iniciar Gravacao", command=start_recording,
                 bg=self.colors['button_default'], fg=self.colors['text_body'],
                 font=('Georgia', 10, 'bold'), padx=15, pady=5).pack(pady=10)
        
        def save_positions():
            if len(clicks_recorded) < 2:
                self.ember_warning("Incompleto", "Grave as 2 posicoes primeiro!")
                return
            
            # Save to config
            if 'runemaker' not in self.config:
                self.config['runemaker'] = {}
            self.config['runemaker']['potion_clicks'] = clicks_recorded
            self.save_config()
            
            self.rm_potion_status.configure(text=f"[OK] ({clicks_recorded[0]['x']},{clicks_recorded[0]['y']})", 
                                         text_color=self.colors['status_on'])
            dialog.destroy()
            self.ember_info("Sucesso", "Posicoes da potion gravadas!")
        
        tk.Button(dialog, text="Salvar", command=save_positions,
                 bg=self.colors['selection'], fg=self.colors['text_header'],
                 font=('Georgia', 10, 'bold'), padx=20, pady=5).pack(pady=5)
        tk.Button(dialog, text="Cancelar", command=dialog.destroy,
                 bg=self.colors['button_destructive'], fg=self.colors['text_body'],
                 font=('Georgia', 9), padx=15, pady=3).pack()
    
    def change_runemaker_hotkey(self, hotkey_type):
        """Change runemaker spell hotkey"""
        dialog = self.create_ember_dialog("Alterar Hotkey Spell", 400, 200)
        
        tk.Label(dialog, text="Pressione a nova hotkey...", font=('Georgia', 12, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=20)
        
        hotkey_var = tk.StringVar(value="Aguardando...")
        tk.Label(dialog, textvariable=hotkey_var, font=('Consolas', 14, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['status_on']).pack(pady=10)
        
        pressed_keys = {'key': None}
        
        def on_press(key):
            try:
                k = key.char.lower() if hasattr(key, 'char') and key.char else key.name.lower()
                pressed_keys['key'] = k.upper()
                hotkey_var.set(pressed_keys['key'])
            except:
                pass
        
        def on_release(key):
            if pressed_keys['key']:
                return False
        
        listener = KeyboardListener(on_press=on_press, on_release=on_release)
        listener.start()
        
        def save_hotkey():
            if pressed_keys['key']:
                listener.stop()
                self.rm_spell_hotkey.set(pressed_keys['key'])
                self.save_runemaker_config()
                dialog.destroy()
        
        tk.Button(dialog, text="Salvar", command=save_hotkey,
                 bg=self.colors['button_default'], fg=self.colors['text_body'],
                 font=('Georgia', 10, 'bold'), padx=20, pady=5).pack(pady=15)
        tk.Button(dialog, text="Cancelar", command=lambda: [listener.stop(), dialog.destroy()],
                 bg=self.colors['button_destructive'], fg=self.colors['text_body'],
                 font=('Georgia', 10), padx=15, pady=3).pack()
    
    def change_runemaker_pause_hotkey(self):
        """Change runemaker pause hotkey"""
        dialog = self.create_ember_dialog("Alterar Hotkey Pausar", 400, 200)
        
        tk.Label(dialog, text="Pressione a nova hotkey...", font=('Georgia', 12, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=20)
        
        hotkey_var = tk.StringVar(value="Aguardando...")
        tk.Label(dialog, textvariable=hotkey_var, font=('Consolas', 14, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['status_on']).pack(pady=10)
        
        pressed_keys = {'key': None}
        
        def on_press(key):
            try:
                k = key.char.lower() if hasattr(key, 'char') and key.char else key.name.lower()
                pressed_keys['key'] = k.upper()
                hotkey_var.set(pressed_keys['key'])
            except:
                pass
        
        def on_release(key):
            if pressed_keys['key']:
                return False
        
        listener = KeyboardListener(on_press=on_press, on_release=on_release)
        listener.start()
        
        def save_hotkey():
            if pressed_keys['key']:
                listener.stop()
                self.rm_pause_hotkey.set(pressed_keys['key'])
                self.save_runemaker_config()
                dialog.destroy()
        
        tk.Button(dialog, text="Salvar", command=save_hotkey,
                 bg=self.colors['button_default'], fg=self.colors['text_body'],
                 font=('Georgia', 10, 'bold'), padx=20, pady=5).pack(pady=15)
        tk.Button(dialog, text="Cancelar", command=lambda: [listener.stop(), dialog.destroy()],
                 bg=self.colors['button_destructive'], fg=self.colors['text_body'],
                 font=('Georgia', 10), padx=15, pady=3).pack()
    
    def toggle_runemaker_pause(self):
        """Toggle pause state for runemaker"""
        if not self.runemaker_running:
            return
        
        self.runemaker_paused = not self.runemaker_paused
        
        if self.runemaker_paused:
            self.ui_configure(self.rm_status_label, text="[PAUSADO]", text_color='#FFA500')
            self.ui_configure(self.rm_pause_status, text="[PAUSADO]", text_color='#FFA500')
            print("[RUNEMAKER] Pausado!")
        else:
            self.ui_configure(self.rm_status_label, text="[RODANDO]", text_color=self.colors['status_on'])
            self.ui_configure(self.rm_pause_status, text="", text_color=self.colors['status_off'])
            print("[RUNEMAKER] Continuando!")
    
    def execute_runemaker_cycle(self):
        """Execute the runemaker cycle: 2x(3pot+1spell) + 1x(3pot+3spell) repeat"""
        keyboard_ctrl = KeyboardController()
        cycle_count = 0
        
        def should_stop():
            """Check if runemaker should stop - called frequently for fast response"""
            return not self.runemaker_running
        
        def wait_with_check(seconds):
            """Sleep but check for stop signal every 50ms for fast response to Alt+F12"""
            elapsed = 0
            step = 0.05  # Check every 50ms
            while elapsed < seconds:
                if should_stop():
                    return False  # Signal to stop
                time.sleep(step)
                elapsed += step
            return True  # Continue
        
        def press_key(key_name):
            """Press a key using pynput"""
            if should_stop():
                return False
            try:
                key_name_lower = key_name.lower()
                if key_name_lower.startswith('f') and key_name_lower[1:].isdigit():
                    fn = int(key_name_lower[1:])
                    key = getattr(Key, f'f{fn}', None)
                    if key:
                        keyboard_ctrl.press(key)
                        keyboard_ctrl.release(key)
                        return True
                else:
                    keyboard_ctrl.press(key_name_lower)
                    keyboard_ctrl.release(key_name_lower)
                    return True
            except Exception as e:
                print(f"[RUNEMAKER] Erro ao pressionar tecla {key_name}: {e}")
                return False
        
        def use_potion():
            """Use potion: right-click potion, left-click character (like UH)"""
            try:
                rm_config = self.config.get('runemaker', {})
                clicks = rm_config.get('potion_clicks', [])
                if len(clicks) < 2:
                    print("[RUNEMAKER] Posicoes da potion nao gravadas!")
                    return False
                
                # Right-click on potion
                x1, y1 = clicks[0]['x'], clicks[0]['y']
                if self.instant_movement.get():
                    pyautogui.moveTo(x1, y1, duration=0)
                else:
                    pyautogui.moveTo(x1, y1, duration=random.uniform(0.04, 0.08))
                    time.sleep(random.uniform(0.01, 0.03))
                pyautogui.rightClick(x1, y1)
                
                # Small delay
                time.sleep(random.uniform(0.05, 0.10))
                
                # Left-click on character
                x2, y2 = clicks[1]['x'], clicks[1]['y']
                if self.instant_movement.get():
                    pyautogui.moveTo(x2, y2, duration=0)
                else:
                    pyautogui.moveTo(x2, y2, duration=random.uniform(0.04, 0.08))
                    time.sleep(random.uniform(0.01, 0.03))
                pyautogui.leftClick(x2, y2)
                
                return True
            except Exception as e:
                print(f"[RUNEMAKER] Erro ao usar potion: {e}")
                return False
        
        # Verify potion positions are recorded
        rm_config = self.config.get('runemaker', {})
        if not rm_config.get('potion_clicks'):
            print("[RUNEMAKER] ERRO: Grave as posicoes da potion primeiro!")
            self.runemaker_enabled.set(False)
            self.runemaker_running = False
            self.ui_configure(self.rm_status_label, text="[ERRO: Grave potion]", text_color='#FF6B35')
            return
        
        while self.runemaker_running:
            # Check for stop signal at start of each cycle
            if should_stop():
                print("[RUNEMAKER] Sinal de parada detectado!")
                break
            
            cycle_count += 1
            delay = self.rm_delay.get() / 1000.0
            spell_key = self.rm_spell_hotkey.get()
            num_potions = self.rm_potions_count.get()
            num_casts = self.rm_casts_count.get()
            
            # Check if paused (with fast stop check)
            while self.runemaker_paused and self.runemaker_running:
                if should_stop():
                    break
                time.sleep(0.05)  # Check every 50ms
            
            if should_stop():
                break
            
            # Update cycle display (thread-safe)
            self.ui_configure(self.rm_cycle_label, text=f"Ciclo {cycle_count}: {num_potions} pot + {num_casts} cast")
            
            # Execute configured number of potions (mouse clicks)
            for p in range(num_potions):
                if should_stop():
                    break
                while self.runemaker_paused and self.runemaker_running:
                    if should_stop():
                        break
                    time.sleep(0.05)
                if should_stop():
                    break
                self.ui_configure(self.rm_cycle_label, text=f"Ciclo {cycle_count}: Potion {p+1}/{num_potions}")
                use_potion()
                if not wait_with_check(delay):
                    break
            
            if should_stop():
                break
            
            # Execute configured number of casts (keypresses)
            for s in range(num_casts):
                if should_stop():
                    break
                while self.runemaker_paused and self.runemaker_running:
                    if should_stop():
                        break
                    time.sleep(0.05)
                if should_stop():
                    break
                self.ui_configure(self.rm_cycle_label, text=f"Ciclo {cycle_count}: Cast {s+1}/{num_casts}")
                press_key(spell_key)
                if not wait_with_check(delay):
                    break
            
            if not should_stop():
                print(f"[RUNEMAKER] Ciclo {cycle_count} completo! ({num_potions} pot + {num_casts} cast)")
        
        print("[RUNEMAKER] Thread finalizada!")
        self.ui_configure(self.rm_cycle_label, text="")
    
    def save_runemaker_config(self):
        """Save runemaker settings to config"""
        if 'runemaker' not in self.config:
            self.config['runemaker'] = {}
        
        # Preserve existing potion_clicks if they exist
        existing_clicks = self.config.get('runemaker', {}).get('potion_clicks', [])
        
        self.config['runemaker'] = {
            'enabled': self.runemaker_enabled.get(),
            'spell_hotkey': self.rm_spell_hotkey.get(),
            'pause_hotkey': self.rm_pause_hotkey.get(),
            'delay': self.rm_delay.get(),
            'potions_count': self.rm_potions_count.get(),
            'casts_count': self.rm_casts_count.get(),
            'potion_clicks': existing_clicks
        }
        
        self.save_config()
    
    def update_cycle_display(self):
        """Update the cycle info display based on current potions/casts settings"""
        potions = self.rm_potions_count.get()
        casts = self.rm_casts_count.get()
        self.rm_cycle_info.configure(text=f"Ciclo: {potions} potions + {casts} cast(s) -> repete")
        self.save_runemaker_config()
    
    def load_runemaker_config(self):
        """Load runemaker settings from config"""
        rm = self.config.get('runemaker', {})
        
        if hasattr(self, 'rm_spell_hotkey'):
            self.rm_spell_hotkey.set(rm.get('spell_hotkey', 'F6'))
        if hasattr(self, 'rm_pause_hotkey'):
            self.rm_pause_hotkey.set(rm.get('pause_hotkey', 'F9'))
        if hasattr(self, 'rm_delay'):
            self.rm_delay.set(rm.get('delay', 500))
        if hasattr(self, 'rm_potions_count'):
            self.rm_potions_count.set(rm.get('potions_count', 3))
        if hasattr(self, 'rm_casts_count'):
            self.rm_casts_count.set(rm.get('casts_count', 1))
        
        # Update cycle display
        if hasattr(self, 'rm_cycle_info'):
            potions = rm.get('potions_count', 3)
            casts = rm.get('casts_count', 1)
            self.rm_cycle_info.configure(text=f"Ciclo: {potions} potions + {casts} cast(s) -> repete")
        
        # Update potion status label if positions are saved
        if hasattr(self, 'rm_potion_status'):
            clicks = rm.get('potion_clicks', [])
            if clicks and len(clicks) >= 2:
                self.rm_potion_status.configure(text=f"[OK] ({clicks[0]['x']},{clicks[0]['y']})", 
                                             text_color=self.colors['status_on'])
            else:
                self.rm_potion_status.configure(text="[Nao gravado]", text_color=self.colors['text_subdued'])
        
        # Don't auto-enable on load for safety
        if hasattr(self, 'runemaker_enabled'):
            self.runemaker_enabled.set(False)
        if hasattr(self, 'rm_enabled_btn'):
            self.update_checkbox_icon(self.rm_enabled_btn, self.runemaker_enabled)
    
    # ========== HYPER GRAB CHRONICLES METHODS ==========
    
    def toggle_hypergrab(self):
        """Toggle Hyper Grab on/off"""
        if self.hypergrab_enabled.get():
            self.hg_status_label.configure(text="[ATIVO]", text_color=self.colors['status_on'])
        else:
            self.hg_status_label.configure(text="[OFF]", text_color=self.colors['status_off'])
        
        self.save_hypergrab_config()
    
    def change_hypergrab_hotkey(self):
        """Change the Hyper Grab hotkey"""
        dialog = self.create_ember_dialog("Hyper Grab Hotkey", 400, 200)
        
        tk.Label(dialog, text="Hyper Grab Hotkey", font=('Georgia', 14, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=15)
        
        tk.Label(dialog, text="Pressione qualquer tecla...", font=('Arial', 11),
                bg=self.colors['bg_primary'], fg=self.colors['text_body']).pack(pady=10)
        
        key_label = tk.Label(dialog, text=self.hypergrab_hotkey.get(), font=('Consolas', 16, 'bold'),
                bg=self.colors['bg_inset'], fg=self.colors['status_on'], padx=20, pady=10)
        key_label.pack(pady=10)
        
        def on_key(event):
            key_name = event.keysym
            self.hypergrab_hotkey.set(key_name)
            key_label.config(text=key_name)
            self.save_hypergrab_config()
            dialog.after(300, dialog.destroy)
        
        dialog.bind('<Key>', on_key)
        dialog.focus_force()
    
    def record_hypergrab_bp(self):
        """Record backpack slot position for Hyper Grab"""
        dialog = self.create_ember_dialog("Gravar Slot BP", 450, 200)
        
        tk.Label(dialog, text="Gravar Posicao do Slot da BP", font=('Georgia', 12, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=10)
        
        tk.Label(dialog, text="Clique no slot SUPERIOR DIREITO da sua backpack", 
                font=('Arial', 10), bg=self.colors['bg_primary'], fg=self.colors['text_body']).pack(pady=5)
        
        status = tk.Label(dialog, text="Aguardando clique...", font=('Consolas', 11, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['status_on'])
        status.pack(pady=10)
        
        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                self.hypergrab_bp_pos = {'x': x, 'y': y}
                
                # Save to config
                if 'hypergrab' not in self.config:
                    self.config['hypergrab'] = {}
                self.config['hypergrab']['bp_pos'] = self.hypergrab_bp_pos
                self.ui_safe(self.save_config)
                
                # Update UI (thread-safe)
                self.ui_configure(self.hg_bp_status, text=f"[OK] ({x},{y})", text_color=self.colors['status_on'])
                self.ui_safe(lambda: status.config(text=f"Gravado: ({x},{y})"))
                
                listener.stop()
                self.ui_safe(lambda: dialog.after(500, dialog.destroy))
                return False
        
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def execute_hypergrab(self):
        """Execute instant drag from current mouse position to backpack slot
        and return mouse to original position"""
        if not self.hypergrab_enabled.get():
            return
        
        # Get backpack position from config
        hg_config = self.config.get('hypergrab', {})
        bp_pos = hg_config.get('bp_pos')
        
        if not bp_pos:
            print("[HYPERGRAB] ERRO: Grave a posicao do slot da BP primeiro!")
            return
        
        try:
            # SAVE original mouse position BEFORE doing anything
            original_x, original_y = pyautogui.position()
            target_x, target_y = bp_pos['x'], bp_pos['y']
            
            # INSTANT DRAG: left click down -> move instant -> left click up
            pyautogui.mouseDown(button='left')
            pyautogui.moveTo(target_x, target_y, duration=0)  # INSTANT - 0ms
            pyautogui.mouseUp(button='left')
            
            # RETURN MOUSE to original position (instant)
            pyautogui.moveTo(original_x, original_y, duration=0)
            
            print(f"[HYPERGRAB] Item arrastado de ({original_x},{original_y}) para BP ({target_x},{target_y}) - mouse retornou")
            
        except Exception as e:
            print(f"[HYPERGRAB] Erro: {e}")
    
    def save_hypergrab_config(self):
        """Save Hyper Grab settings to config"""
        if 'hypergrab' not in self.config:
            self.config['hypergrab'] = {}
        
        # Preserve existing bp_pos
        existing_pos = self.config.get('hypergrab', {}).get('bp_pos')
        
        self.config['hypergrab'] = {
            'enabled': self.hypergrab_enabled.get(),
            'hotkey': self.hypergrab_hotkey.get(),
            'bp_pos': existing_pos
        }
        
        self.save_config()
    
    def load_hypergrab_config(self):
        """Load Hyper Grab settings from config"""
        hg = self.config.get('hypergrab', {})
        
        if hasattr(self, 'hypergrab_hotkey'):
            self.hypergrab_hotkey.set(hg.get('hotkey', 'F5'))
        
        # Update BP status label
        if hasattr(self, 'hg_bp_status'):
            bp_pos = hg.get('bp_pos')
            if bp_pos:
                self.hg_bp_status.configure(text=f"[OK] ({bp_pos['x']},{bp_pos['y']})", 
                                         text_color=self.colors['status_on'])
                self.hypergrab_bp_pos = bp_pos
            else:
                self.hg_bp_status.configure(text="[Nao gravado]", text_color=self.colors['text_subdued'])
        
        # Don't auto-enable on load
        if hasattr(self, 'hypergrab_enabled'):
            self.hypergrab_enabled.set(False)
        if hasattr(self, 'hg_enabled_btn'):
            self.update_checkbox_icon(self.hg_enabled_btn, self.hypergrab_enabled)
    
    # ========== DRAG HOTKEY METHODS ==========
    
    def toggle_drag_hotkey(self):
        """Toggle Drag Hotkey on/off"""
        if self.drag_enabled.get():
            self.drag_status_label.configure(text="[ATIVO]", text_color=self.colors['status_on'])
        else:
            self.drag_status_label.configure(text="[OFF]", text_color=self.colors['status_off'])
        
        self.save_drag_config()
    
    def change_drag_hotkey(self):
        """Change the Drag Hotkey"""
        dialog = self.create_ember_dialog("Drag Hotkey", 400, 200)
        
        tk.Label(dialog, text="Drag Hotkey", font=('Georgia', 14, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=15)
        
        tk.Label(dialog, text="Pressione qualquer tecla...", font=('Arial', 11),
                bg=self.colors['bg_primary'], fg=self.colors['text_body']).pack(pady=10)
        
        key_label = tk.Label(dialog, text=self.drag_hotkey.get(), font=('Consolas', 16, 'bold'),
                bg=self.colors['bg_inset'], fg=self.colors['status_on'], padx=20, pady=10)
        key_label.pack(pady=10)
        
        def on_key(event):
            key_name = event.keysym
            self.drag_hotkey.set(key_name)
            key_label.config(text=key_name)
            self.drag_hotkey_btn.configure(text=key_name)
            self.save_drag_config()
            dialog.after(300, dialog.destroy)
        
        dialog.bind('<Key>', on_key)
        dialog.focus_force()
    
    def record_drag_destination(self):
        """Record destination position for Drag Hotkey
        
        The origin is always where the mouse is when hotkey is pressed.
        This only records where items will be DRAGGED TO.
        """
        dialog = self.create_ember_dialog("Gravar Destino", 450, 200)
        
        tk.Label(dialog, text="Gravar Posicao de DESTINO", font=('Georgia', 12, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=10)
        
        tk.Label(dialog, text="Clique onde os itens serao SOLTOS (destino do arraste)", 
                font=('Arial', 10), bg=self.colors['bg_primary'], fg=self.colors['text_body']).pack(pady=5)
        
        status = tk.Label(dialog, text="Aguardando clique...", font=('Consolas', 11, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['status_on'])
        status.pack(pady=10)
        
        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                pos = {'x': x, 'y': y}
                
                # Save to config
                if 'drag_hotkey' not in self.config:
                    self.config['drag_hotkey'] = {}
                
                self.drag_dest_pos = pos
                self.config['drag_hotkey']['dest_pos'] = pos
                
                # Thread-safe UI updates via root.after
                self.ui_configure(self.drag_dest_status, text=f"[OK] ({x},{y})", text_color=self.colors['status_on'])
                self.ui_safe(self.save_config)
                self.ui_safe(lambda: status.config(text=f"Gravado: ({x},{y})"))
                
                listener.stop()
                self.ui_safe(lambda: dialog.after(500, dialog.destroy))
                return False
        
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def execute_drag_hotkey(self):
        """Execute instant drag from CURRENT mouse position to saved destination
        
        How it works:
        - Origin = wherever the mouse is when hotkey is pressed
        - Destination = the saved position (gravada pelo usuario)
        - Action: click down at current pos, drag to destination, release
        """
        if not self.drag_enabled.get():
            return
        
        # Get destination position from config
        drag_config = self.config.get('drag_hotkey', {})
        dest_pos = drag_config.get('dest_pos')
        
        if not dest_pos:
            print("[DRAG_HOTKEY] ERRO: Grave a posicao de DESTINO primeiro!")
            return
        
        try:
            # Current mouse position = ORIGIN (where user is hovering)
            origin_x, origin_y = pyautogui.position()
            dest_x, dest_y = dest_pos['x'], dest_pos['y']
            
            # INSTANT DRAG: click down at current pos -> drag to destination -> release
            pyautogui.mouseDown(button='left')
            pyautogui.moveTo(dest_x, dest_y, duration=0)  # INSTANT drag
            pyautogui.mouseUp(button='left')
            
            # RETURN MOUSE to original position (instant)
            pyautogui.moveTo(origin_x, origin_y, duration=0)
            
            print(f"[DRAG_HOTKEY] Arrastado de ({origin_x},{origin_y}) para ({dest_x},{dest_y}) - mouse retornou")
            
        except Exception as e:
            print(f"[DRAG_HOTKEY] Erro: {e}")
    
    def save_drag_config(self):
        """Save Drag Hotkey settings to config"""
        if 'drag_hotkey' not in self.config:
            self.config['drag_hotkey'] = {}
        
        # Preserve existing destination position
        existing_dest = self.config.get('drag_hotkey', {}).get('dest_pos')
        
        self.config['drag_hotkey'] = {
            'enabled': self.drag_enabled.get(),
            'hotkey': self.drag_hotkey.get(),
            'dest_pos': existing_dest
        }
        
        self.save_config()
    
    def load_drag_config(self):
        """Load Drag Hotkey settings from config"""
        drag = self.config.get('drag_hotkey', {})
        
        if hasattr(self, 'drag_hotkey'):
            self.drag_hotkey.set(drag.get('hotkey', 'F8'))
            if hasattr(self, 'drag_hotkey_btn'):
                self.drag_hotkey_btn.configure(text=drag.get('hotkey', 'F8'))
        
        # Update destination position status label
        if hasattr(self, 'drag_dest_status'):
            dest_pos = drag.get('dest_pos')
            if dest_pos:
                self.drag_dest_status.configure(text=f"[OK] ({dest_pos['x']},{dest_pos['y']})", 
                                                text_color=self.colors['status_on'])
                self.drag_dest_pos = dest_pos
            else:
                self.drag_dest_status.configure(text="[Nao gravado]", text_color=self.colors['text_subdued'])
        
        # Don't auto-enable on load
        if hasattr(self, 'drag_enabled'):
            self.drag_enabled.set(False)
    
    def create_ember_dialog(self, title, width=400, height=250):
        """Create a dialog with ember theme colors and proper focus"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.transient(self.root)
        dialog.attributes('-topmost', True)
        dialog.configure(bg=self.colors['bg_primary'])
        return dialog
    
    def ember_info(self, title, message):
        """Show info dialog with ember theme"""
        dialog = self.create_ember_dialog(title, 400, 200)
        
        tk.Label(dialog, text=title, font=('Georgia', 14, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=15)
        
        tk.Label(dialog, text=message, font=('Arial', 10), wraplength=350,
                bg=self.colors['bg_primary'], fg=self.colors['text_body'], justify=tk.CENTER).pack(pady=10)
        
        btn = tk.Button(dialog, text="✓ OK", width=10,
                       command=dialog.destroy,
                       bg=self.colors['button_default'], fg=self.colors['text_body'],
                       font=('Arial', 10, 'bold'), relief=tk.RAISED, borderwidth=2,
                       activebackground=self.colors['button_hover'])
        btn.pack(pady=15)
        
        dialog.bind('<Return>', lambda e: dialog.destroy())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        btn.focus_set()
    
    def ember_warning(self, title, message):
        """Show warning dialog with ember theme"""
        dialog = self.create_ember_dialog(title, 400, 200)
        
        tk.Label(dialog, text=f"⚠ {title}", font=('Georgia', 14, 'bold'),
                bg=self.colors['bg_primary'], fg='#FF6B35').pack(pady=15)
        
        tk.Label(dialog, text=message, font=('Arial', 10), wraplength=350,
                bg=self.colors['bg_primary'], fg=self.colors['text_body'], justify=tk.CENTER).pack(pady=10)
        
        btn = tk.Button(dialog, text="OK", width=10,
                       command=dialog.destroy,
                       bg=self.colors['border_dark'], fg=self.colors['text_body'],
                       font=('Arial', 10, 'bold'), relief=tk.RAISED, borderwidth=2,
                       activebackground=self.colors['button_hover'])
        btn.pack(pady=15)
        
        dialog.bind('<Return>', lambda e: dialog.destroy())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        btn.focus_set()
    
    def update_checkbox_icon(self, button, var):
        """Update checkbox icon based on ON/OFF state (green/red squares with orange glow)"""
        if var.get():
            # ON: Green square with orange highlight glow (from ember palette)
            button.config(image=self.checkbox_on, bg=self.colors['bg_secondary'],
                         highlightbackground=self.colors['border_highlight'], 
                         highlightcolor=self.colors['border_highlight'], highlightthickness=2)
        else:
            # OFF: Red square with dim ember glow (from ember palette)
            button.config(image=self.checkbox_off, bg=self.colors['bg_secondary'],
                         highlightbackground=self.colors['border'], 
                         highlightcolor=self.colors['border'], highlightthickness=2)
        self.save_quick_configs()
    
    def update_target_button(self, button, var):
        """Update target/crosshair button style based on ON/OFF state"""
        if var.get():
            # ON: Green border (active/armed)
            button.config(bg=self.colors['bg_secondary'], relief=tk.RAISED, borderwidth=4, 
                         highlightbackground='#00FF00', highlightcolor='#00FF00', highlightthickness=3)
        else:
            # OFF: Red border (inactive/disarmed)
            button.config(bg=self.colors['bg_secondary'], relief=tk.SUNKEN, borderwidth=4,
                         highlightbackground='#FF0000', highlightcolor='#FF0000', highlightthickness=3)
        self.save_quick_configs()
    
    def change_quick_hotkey(self, macro_type):
        """Quick dialog to change hotkey for Auto SD, Auto EXPLO, Auto UH, or Auto MANA - Ember themed"""
        # All options now allow key combinations (Ctrl+, Alt+, Shift+)
        allow_combinations = True
        
        if macro_type == 'sd':
            title = "Auto SD Hotkey"
        elif macro_type == 'explo':
            title = "Auto EXPLO Hotkey"
        elif macro_type == 'uh':
            title = "Auto UH Hotkey"
        else:
            title = "Auto Mana Hotkey"
        
        dialog = self.create_ember_dialog(title, 450, 280)
        
        # Title with ember colors
        tk.Label(dialog, text=title, font=('Georgia', 14, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=15)
        
        # Instructions
        instruction_text = f"Pressione a nova hotkey\n(Pode usar Ctrl, Alt ou Shift)"
        tk.Label(dialog, text=instruction_text, font=('Arial', 10),
                bg=self.colors['bg_primary'], fg=self.colors['text_body'], justify=tk.CENTER).pack(pady=10)
        
        # Status display
        hotkey_var = tk.StringVar(value="Aguardando...")
        status_label = tk.Label(dialog, textvariable=hotkey_var, font=('Consolas', 12, 'bold'),
                               bg=self.colors['bg_secondary'], fg=self.colors['focus_glow'],
                               relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
        status_label.pack(pady=10, padx=20, fill=tk.X)
        
        pressed_keys = {'combo': None, 'modifiers': set()}
        
        def update_status(text):
            """Thread-safe status update using dialog.after()"""
            try:
                dialog.after(0, lambda: hotkey_var.set(text))
            except:
                pass
        
        def on_press(key):
            try:
                # Check for modifier keys
                if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                    if allow_combinations:
                        pressed_keys['modifiers'].add('ctrl')
                    else:
                        update_status("❌ Apenas teclas simples!")
                elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                    if allow_combinations:
                        pressed_keys['modifiers'].add('alt')
                    else:
                        update_status("❌ Apenas teclas simples!")
                elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                    if allow_combinations:
                        pressed_keys['modifiers'].add('shift')
                    else:
                        update_status("❌ Apenas teclas simples!")
                else:
                    # Regular key
                    k = key.char.lower() if hasattr(key, 'char') else key.name.lower()
                    
                    # Build combo string (only for display)
                    combo_parts = []
                    if allow_combinations:
                        if 'ctrl' in pressed_keys['modifiers']:
                            combo_parts.append('Ctrl')
                        if 'alt' in pressed_keys['modifiers']:
                            combo_parts.append('Alt')
                        if 'shift' in pressed_keys['modifiers']:
                            combo_parts.append('Shift')
                    combo_parts.append(k.upper())
                    
                    combo_str = '+'.join(combo_parts)
                    update_status(combo_str)
            except:
                pass
        
        def on_release(key):
            try:
                # Check if it's a modifier key being released
                if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                    if allow_combinations:
                        pressed_keys['modifiers'].discard('ctrl')
                    return
                elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                    if allow_combinations:
                        pressed_keys['modifiers'].discard('alt')
                    return
                elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                    if allow_combinations:
                        pressed_keys['modifiers'].discard('shift')
                    return
                
                # Regular key released - save combo
                k = key.char.lower() if hasattr(key, 'char') else key.name.lower()
                
                # Reject if modifiers are used but not allowed
                if not allow_combinations and pressed_keys['modifiers']:
                    hotkey_var.set("❌ Apenas teclas simples!")
                    pressed_keys['modifiers'].clear()
                    return
                
                # Build combo string
                combo_parts = []
                if allow_combinations:
                    if 'ctrl' in pressed_keys['modifiers']:
                        combo_parts.append('ctrl')
                    if 'alt' in pressed_keys['modifiers']:
                        combo_parts.append('alt')
                    if 'shift' in pressed_keys['modifiers']:
                        combo_parts.append('shift')
                combo_parts.append(k)
                
                pressed_keys['combo'] = '+'.join(combo_parts)
                
                # Display version
                display_parts = []
                if allow_combinations:
                    if 'ctrl' in pressed_keys['modifiers']:
                        display_parts.append('Ctrl')
                    if 'alt' in pressed_keys['modifiers']:
                        display_parts.append('Alt')
                    if 'shift' in pressed_keys['modifiers']:
                        display_parts.append('Shift')
                display_parts.append(k.upper())
                
                hotkey_var.set(f"{'+'.join(display_parts)} ✓")
                return False
            except:
                pass
        
        listener = KeyboardListener(on_press=on_press, on_release=on_release)
        listener.start()
        
        def save_new_hotkey():
            if pressed_keys['combo']:
                if macro_type == 'sd':
                    self.auto_sd_hotkey.set(pressed_keys['combo'])
                    self.sd_hotkey_btn.configure(text=f"{pressed_keys['combo']}")
                elif macro_type == 'explo':
                    self.auto_explo_hotkey.set(pressed_keys['combo'])
                    self.explo_hotkey_btn.configure(text=f"{pressed_keys['combo']}")
                elif macro_type == 'uh':
                    self.auto_uh_hotkey.set(pressed_keys['combo'])
                    self.uh_hotkey_btn.configure(text=f"{pressed_keys['combo']}")
                else:
                    self.auto_mana_hotkey.set(pressed_keys['combo'])
                    self.mana_hotkey_btn.configure(text=f"{pressed_keys['combo']}")
                
                self.save_quick_configs()
                listener.stop()
                dialog.destroy()
                messagebox.showinfo("✓ Sucesso!", f"Hotkey alterada para {pressed_keys['combo']}!")
            else:
                messagebox.showwarning("Erro", "Pressione uma tecla primeiro!")
        
        ttk.Button(dialog, text="💾 Salvar", command=save_new_hotkey, 
                  style='Accent.TButton').pack(pady=10)
        ttk.Button(dialog, text="Cancelar", 
                  command=lambda: [listener.stop(), dialog.destroy()]).pack()
    
    def record_quick_positions(self, macro_type):
        """Record click positions for Auto SD, Auto UH, or Auto MANA - Ember themed"""
        if macro_type == 'sd':
            title = "Auto SD"
        elif macro_type == 'explo':
            title = "Auto EXPLO"
        elif macro_type == 'uh':
            title = "Auto UH"
        else:
            title = "Auto Mana"
        is_sd = macro_type == 'sd'
        is_explo = macro_type == 'explo'
        
        dialog = self.create_ember_dialog(f"{title} - Gravar Posições", 550, 380)
        
        # Title with ember colors
        tk.Label(dialog, text=f"{title} - Gravação de Posições", 
                font=('Georgia', 16, 'bold'), bg=self.colors['bg_primary'], 
                fg=self.colors['text_header']).pack(pady=15)
        
        if is_sd:
            instructions = "1. Clique na posição da RUNA SD\n2. Sistema irá detectar targets automaticamente!"
            max_clicks = 1
        elif is_explo:
            instructions = "1. Clique na posição da RUNA EXPLO\n2. Sistema irá detectar targets automaticamente!"
            max_clicks = 1
        elif macro_type == 'uh':
            instructions = "1. Clique na posição da RUNA UH\n2. Clique no PERSONAGEM"
            max_clicks = 2
        else:  # mana
            instructions = "1. Clique na posição do MANA POTION\n2. Clique no PERSONAGEM"
            max_clicks = 2
        
        # Instructions with ember colors
        tk.Label(dialog, text=instructions, font=('Arial', 11), bg=self.colors['bg_primary'],
                fg=self.colors['text_body'], justify=tk.LEFT).pack(pady=10)
        
        status_var = tk.StringVar(value="Clique 'Iniciar' para começar a gravar...")
        status_label = tk.Label(dialog, textvariable=status_var, font=('Consolas', 10, 'bold'), 
                               bg=self.colors['bg_secondary'], fg=self.colors['focus_glow'],
                               wraplength=500, relief=tk.GROOVE, borderwidth=2, padx=10, pady=10)
        status_label.pack(pady=15, padx=15, fill=tk.X)
        
        clicks_recorded = []
        
        def on_click(x, y, button, pressed):
            if pressed and len(clicks_recorded) < max_clicks:
                clicks_recorded.append({'x': x, 'y': y})
                
                if is_sd:
                    status_var.set(f"✓ SD Rune: ({x}, {y})\n\nPronto! Sistema irá detectar targets automaticamente.")
                elif is_explo:
                    status_var.set(f"✓ EXPLO Rune: ({x}, {y})\n\nPronto! Sistema irá detectar targets automaticamente.")
                elif macro_type == 'uh':
                    if len(clicks_recorded) == 1:
                        status_var.set(f"✓ UH Rune: ({x}, {y})\n\nAgora clique no PERSONAGEM")
                    elif len(clicks_recorded) == 2:
                        status_var.set(f"✓ UH: ({clicks_recorded[0]['x']}, {clicks_recorded[0]['y']})\n✓ Personagem: ({x}, {y})\n\nPronto!")
                else:  # mana
                    if len(clicks_recorded) == 1:
                        status_var.set(f"✓ Mana Potion: ({x}, {y})\n\nAgora clique no PERSONAGEM")
                    elif len(clicks_recorded) == 2:
                        status_var.set(f"✓ Mana: ({clicks_recorded[0]['x']}, {clicks_recorded[0]['y']})\n✓ Personagem: ({x}, {y})\n\nPronto!")
                
                if len(clicks_recorded) >= max_clicks:
                    return False
        
        def start_recording():
            clicks_recorded.clear()
            if is_sd:
                status_var.set("Clique na posição da SD RUNE...")
            elif is_explo:
                status_var.set("Clique na posição da EXPLO RUNE...")
            elif macro_type == 'uh':
                status_var.set("Clique na posição da UH RUNE...")
            else:
                status_var.set("Clique na posição do MANA POTION...")
            dialog.after(100, lambda: mouse.Listener(on_click=on_click).start())
        
        def save_positions():
            if len(clicks_recorded) < max_clicks:
                self.ember_warning("Erro", f"Grave todas as {max_clicks} posições primeiro!")
                return
            
            # Save to quick configs
            if is_sd:
                key = 'auto_sd'
            elif is_explo:
                key = 'auto_explo'
            elif macro_type == 'uh':
                key = 'auto_uh'
            else:
                key = 'auto_mana'
            
            print(f"[DEBUG] Recording {title}: macro_type={macro_type}, is_sd={is_sd}, key={key}")
            print(f"[DEBUG] Clicks recorded: {clicks_recorded}")
            
            if 'quick_configs' not in self.config:
                self.config['quick_configs'] = {}
            if key not in self.config['quick_configs']:
                self.config['quick_configs'][key] = {}
            
            self.config['quick_configs'][key]['clicks'] = clicks_recorded
            print(f"[DEBUG] Saved to config['{key}']['clicks']: {self.config['quick_configs'][key]['clicks']}")
            self.save_config()
            print(f"[DEBUG] Config saved successfully!")
            
            dialog.destroy()
            self.ember_info("Sucesso!", f"Posições gravadas para {title}!")
        
        # Ember-themed buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['bg_primary'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="📍 Iniciar Gravação", command=start_recording,
                 bg=self.colors['button_default'], fg=self.colors['text_body'],
                 font=('Arial', 10, 'bold'), relief=tk.RAISED, borderwidth=2,
                 activebackground=self.colors['button_hover'], padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(btn_frame, text="💾 Salvar", command=save_positions,
                            bg=self.colors['focus_glow'], fg='#000000',
                            font=('Arial', 10, 'bold'), relief=tk.RAISED, borderwidth=2,
                            activebackground=self.colors['status_on'], padx=10, pady=5)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancelar", command=dialog.destroy,
                 bg=self.colors['button_destructive'], fg=self.colors['text_body'],
                 font=('Arial', 10, 'bold'), relief=tk.RAISED, borderwidth=2,
                 activebackground=self.colors['border'], padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter and Escape keys
        dialog.bind('<Return>', lambda e: save_positions())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def toggle_active(self):
        # Get current state from the switch
        self.active = self.global_toggle.get() == 1
        if self.active:
            self.status_label.configure(text="ON", text_color=self.colors['status_on'])
        else:
            self.status_label.configure(text="OFF", text_color=self.colors['status_off'])
    
    def pause_all(self):
        """Global pause triggered by Alt+F12 - forces ALL automations to stop IMMEDIATELY
        NOTE: This runs in a hotkey thread, so all UI updates MUST use ui_safe/ui_configure"""
        print("[ALT+F12] PAUSA GLOBAL ATIVADA!")
        
        # 1. STOP GLOBAL TOGGLE (thread-safe)
        self.active = False
        self.ui_safe(self.global_toggle.deselect)
        self.ui_configure(self.status_label, text="OFF", text_color=self.colors['status_off'])
        
        # 2. FORCE STOP RUNEMAKER (critical - runs in separate thread!)
        if hasattr(self, 'runemaker_running') and self.runemaker_running:
            self.runemaker_running = False
            self.runemaker_paused = False
            if hasattr(self, 'runemaker_enabled'):
                self.runemaker_enabled.set(False)
            if hasattr(self, 'rm_enabled_btn'):
                self.ui_safe(self.update_checkbox_icon, self.rm_enabled_btn, self.runemaker_enabled)
            if hasattr(self, 'rm_status_label'):
                self.ui_configure(self.rm_status_label, text="[PARADO]", text_color=self.colors['status_off'])
            if hasattr(self, 'rm_cycle_label'):
                self.ui_configure(self.rm_cycle_label, text="")
            print("[ALT+F12] Runemaker FORÇADO a parar!")
        
        # 3. STOP ALL BEST SELLERS (Auto SD, EXPLO, UH, Mana)
        if hasattr(self, 'auto_sd_enabled'):
            self.auto_sd_enabled.set(False)
            if hasattr(self, 'sd_enabled_btn'):
                self.ui_safe(self.update_checkbox_icon, self.sd_enabled_btn, self.auto_sd_enabled)
        if hasattr(self, 'auto_explo_enabled'):
            self.auto_explo_enabled.set(False)
            if hasattr(self, 'explo_enabled_btn'):
                self.ui_safe(self.update_checkbox_icon, self.explo_enabled_btn, self.auto_explo_enabled)
        if hasattr(self, 'auto_uh_enabled'):
            self.auto_uh_enabled.set(False)
            if hasattr(self, 'uh_enabled_btn'):
                self.ui_safe(self.update_checkbox_icon, self.uh_enabled_btn, self.auto_uh_enabled)
        if hasattr(self, 'auto_mana_enabled'):
            self.auto_mana_enabled.set(False)
            if hasattr(self, 'mana_enabled_btn'):
                self.ui_safe(self.update_checkbox_icon, self.mana_enabled_btn, self.auto_mana_enabled)
        
        # 4. STOP HYPER GRAB
        if hasattr(self, 'hypergrab_enabled'):
            self.hypergrab_enabled.set(False)
            if hasattr(self, 'hg_enabled_btn'):
                self.ui_safe(self.update_checkbox_icon, self.hg_enabled_btn, self.hypergrab_enabled)
            if hasattr(self, 'hg_status_label'):
                self.ui_configure(self.hg_status_label, text="[OFF]", text_color=self.colors['status_off'])
        
        # 5. STOP DRAG HOTKEY
        if hasattr(self, 'drag_enabled'):
            self.drag_enabled.set(False)
            if hasattr(self, 'drag_status_label'):
                self.ui_configure(self.drag_status_label, text="[OFF]", text_color=self.colors['status_off'])
        
        # 6. CLEAR ALL TRIGGERED FLAGS to reset hotkey states
        self.triggered_quick_keys.clear()
        self.triggered_hotkeys.clear()
        
        # 7. Save config to persist the OFF state (thread-safe via after)
        self.ui_safe(self.save_config)
        
        print("[ALT+F12] TODAS as automações foram PARADAS!")
        # Show visual feedback (non-blocking, thread-safe)
        self.ui_safe(lambda: messagebox.showinfo("PAUSA GLOBAL", "Alt+F12: Todas as automações foram PARADAS!"))
    
    def refresh_tree(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add hotkeys
        for hk in self.hotkeys:
            hotkey_str = '+'.join([k.upper() for k in hk['hotkey']])
            hk_type = hk.get('type', 'normal')
            
            if hk_type == 'offensive':
                auto_target = hk.get('auto_target', False)
                
                if auto_target:
                    # Auto-target: only 1 position (rune), scans screen
                    clicks_str = f"[AUTO-TARGET] Rune: ({hk['clicks'][0]['x']}, {hk['clicks'][0]['y']}) → Scans entire screen"
                else:
                    # Manual: 2 positions (rune + destination)
                    if len(hk['clicks']) >= 2:
                        clicks_str = f"[MANUAL] Rune: ({hk['clicks'][0]['x']}, {hk['clicks'][0]['y']}) → Dest: ({hk['clicks'][1]['x']}, {hk['clicks'][1]['y']})"
                    else:
                        clicks_str = f"[MANUAL] Rune: ({hk['clicks'][0]['x']}, {hk['clicks'][0]['y']}) → Center"
                delay_str = "N/A"
            else:
                clicks_str = f"Right-click ({hk['clicks'][0]['x']}, {hk['clicks'][0]['y']}) -> Left-click ({hk['clicks'][1]['x']}, {hk['clicks'][1]['y']})"
                delay_str = str(hk['delay'])
            
            self.tree.insert('', tk.END, values=(hotkey_str, clicks_str, delay_str))
    
    def calibrate_by_clicking(self):
        """Interactive click-based calibration - user clicks 4 corners of red outline"""
        import mss
        import colorsys
        
        # Minimize main window
        self.root.iconify()
        
        # Create fullscreen overlay window (INVISIBLE so colors stay true!)
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.01)  # Nearly invisible - doesn't change screen colors!
        overlay.configure(bg='black')
        overlay.attributes('-topmost', True)
        
        # Tracking variables
        click_points = []
        click_colors_rgb = []
        
        # Instruction label (with solid background so it's visible!)
        instruction_text = tk.StringVar(value="🎯 Clique 1/2: QUINA SUL-ESQUERDA (inferior-esquerda) do outline")
        instruction_bg = tk.Frame(overlay, bg='black', bd=5, relief=tk.RAISED)
        instruction_bg.place(relx=0.5, y=50, anchor='n')
        
        instruction_label = tk.Label(
            instruction_bg, 
            textvariable=instruction_text,
            font=('Arial', 18, 'bold'),
            bg='black',
            fg='yellow',
            padx=20,
            pady=15
        )
        instruction_label.pack()
        
        # Status label (with solid background)
        status_bg = tk.Frame(overlay, bg='black', bd=3, relief=tk.RAISED)
        status_bg.place(relx=0.5, y=130, anchor='n')
        
        status_text = tk.StringVar(value="⚠️ Tela quase invisível - cores verdadeiras! ESC = cancelar")
        status_label = tk.Label(
            status_bg,
            textvariable=status_text,
            font=('Arial', 12),
            bg='black',
            fg='cyan',
            padx=15,
            pady=10
        )
        status_label.pack()
        
        # Mini-display frame for real-time color preview (with solid background)
        preview_frame = tk.Frame(overlay, bg='white', bd=3, relief=tk.RAISED)
        preview_frame.place(x=20, y=20)
        
        # Color preview box
        color_box = tk.Label(preview_frame, text="", width=8, height=3, bg='black')
        color_box.grid(row=0, column=0, rowspan=3, padx=5, pady=5)
        
        # Info labels
        pos_label = tk.Label(preview_frame, text="Pos: (0, 0)", font=('Courier', 10), bg='white', anchor='w')
        pos_label.grid(row=0, column=1, sticky='w', padx=5)
        
        rgb_label = tk.Label(preview_frame, text="RGB: (0, 0, 0)", font=('Courier', 10), bg='white', anchor='w')
        rgb_label.grid(row=1, column=1, sticky='w', padx=5)
        
        hsv_label = tk.Label(preview_frame, text="HSV: (0, 0, 0)", font=('Courier', 10), bg='white', anchor='w')
        hsv_label.grid(row=2, column=1, sticky='w', padx=5)
        
        def on_click(event):
            nonlocal click_points, click_colors_rgb
            
            # Get click position (absolute screen coordinates)
            x, y = event.x_root, event.y_root
            
            instruction_text.set("⏳ Capturando área da quina... aguarde!")
            overlay.update()
            
            # Capture 12x12 area around click (entire corner of outline)
            capture_size = 12
            half_size = capture_size // 2
            
            with mss.mss() as sct:
                region = {
                    'left': x - half_size,
                    'top': y - half_size,
                    'width': capture_size,
                    'height': capture_size,
                    'mon': 1
                }
                
                screenshot = sct.grab(region)
                area_pixels = np.array(screenshot)
            
            # Extract all red pixels from this area
            red_pixels_hsv = []
            red_pixels_rgb = []
            
            for py in range(capture_size):
                for px in range(capture_size):
                    # Get RGB (MSS returns BGRA)
                    b, g, r = area_pixels[py, px, :3]
                    rgb = (int(r), int(g), int(b))
                    
                    # Convert to HSV
                    r_norm, g_norm, b_norm = [c / 255.0 for c in rgb]
                    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
                    h_cv = int(h * 179)
                    s_cv = int(s * 255)
                    v_cv = int(v * 255)
                    
                    # Is this pixel red?
                    is_red = ((0 <= h_cv <= 15) or (165 <= h_cv <= 179)) and s_cv > 80 and v_cv > 80
                    
                    if is_red:
                        red_pixels_hsv.append((h_cv, s_cv, v_cv))
                        red_pixels_rgb.append(rgb)
            
            # VALIDATE: Did we find enough red pixels?
            num_clicks = len(click_points)
            if len(red_pixels_hsv) < 10:
                corner_name = "SUL-ESQUERDA" if num_clicks == 0 else "NORTE-DIREITA"
                status_text.set(f"❌ Poucos pixels vermelhos ({len(red_pixels_hsv)})! Clique na quina {corner_name} do outline!")
                return
            
            # Store this corner's pixels
            click_points.append((x, y))
            
            # Check if we need second click
            num_clicks = len(click_points)
            
            if num_clicks == 1:
                # First corner captured, need second!
                status_text.set(f"✅ Quina 1/2 capturada ({len(red_pixels_hsv)} pixels)!")
                instruction_text.set("🎯 Clique 2/2: QUINA NORTE-DIREITA (superior-direita) do outline")
                
                # Store first corner's pixels temporarily
                self.temp_corner1_hsv = red_pixels_hsv
                self.temp_corner1_rgb = red_pixels_rgb
                return  # Wait for second click
            
            # BOTH corners captured! Combine pixels from both
            instruction_text.set("✅ Ambas quinas capturadas! Calculando range HSV...")
            overlay.update()
            
            # Combine pixels from BOTH corners
            all_red_pixels_hsv = self.temp_corner1_hsv + red_pixels_hsv
            click_colors_rgb = self.temp_corner1_rgb + red_pixels_rgb
            
            status_text.set(f"✅ Total: {len(all_red_pixels_hsv)} pixels vermelhos de 2 quinas!")
            overlay.update()
            
            # Calculate HSV range from ALL pixels from BOTH corners!
            h_values = [hsv[0] for hsv in all_red_pixels_hsv]
            s_values = [hsv[1] for hsv in all_red_pixels_hsv]
            v_values = [hsv[2] for hsv in all_red_pixels_hsv]
            
            # Use min/max to cover 100% of variation
            # For RED: need generous margins because red wraps around (0-10 and 170-179)
            lower_h = max(0, min(h_values) - 10)  # Bigger margin for red wraparound
            upper_h = min(179, max(h_values) + 10)
            lower_s = max(60, min(s_values) - 30)  # More permissive
            upper_s = 255  # Always max for saturation
            lower_v = max(50, min(v_values) - 30)  # More permissive
            upper_v = 255  # Always max for value
            
            # Calculate median for display
            h_median = int(np.median(h_values))
            s_median = int(np.median(s_values))
            v_median = int(np.median(v_values))
                
            # Save calibration to self.hsv_config
            self.hsv_config = {
                'lower_hsv': [int(lower_h), int(lower_s), int(lower_v)],
                'upper_hsv': [int(upper_h), int(upper_s), int(upper_v)],
                'calibrated': True,
                'calibration_method': 'two_corner_capture',
                'pixels_captured': len(all_red_pixels_hsv),
                'corner1_position': click_points[0],
                'corner2_position': click_points[1],
                'hsv_median': [int(h_median), int(s_median), int(v_median)]
            }
            
            self.save_config()
            
            # Show success message
            result_msg = f"""
✅ CALIBRAÇÃO COMPLETA - 2 QUINAS!

📊 Dados capturados:
   Quina 1 (Sul-Esquerda): {click_points[0]}
   Quina 2 (Norte-Direita): {click_points[1]}
   Total pixels vermelhos: {len(all_red_pixels_hsv)} pixels
   Área por quina: {capture_size}x{capture_size}

🎨 HSV Mediano: H={h_median}, S={s_median}, V={v_median}

📏 Range HSV (cobre 100% de AMBAS as quinas!):
   H: {lower_h} - {upper_h}
   S: {lower_s} - {upper_s}
   V: {lower_v} - {upper_v}

✅ Calibração salva! Auto-target usa dados de 2 extremidades!
            """
            
            messagebox.showinfo("🎯 Calibração Completa!", result_msg)
            
            # Close overlay and restore main window
            overlay.destroy()
            self.root.deiconify()
        
        # Real-time color preview on mouse movement
        def on_mouse_move(event):
            try:
                x, y = event.x_root, event.y_root
                
                # Capture pixel color at mouse position
                with mss.mss() as sct:
                    region = {
                        'left': x,
                        'top': y,
                        'width': 1,
                        'height': 1,
                        'mon': 1
                    }
                    
                    screenshot = sct.grab(region)
                    pixel = np.array(screenshot)
                    
                    # Get RGB (MSS returns BGRA)
                    b, g, r = pixel[0, 0, :3]
                    rgb = (int(r), int(g), int(b))
                
                # Convert to HSV
                r_norm, g_norm, b_norm = [c / 255.0 for c in rgb]
                h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
                h_cv = int(h * 179)
                s_cv = int(s * 255)
                v_cv = int(v * 255)
                
                # Check if this is RED (H: 0-10 or 170-179, S > 100, V > 100)
                is_red = ((0 <= h_cv <= 10) or (170 <= h_cv <= 179)) and s_cv > 100 and v_cv > 100
                
                # Update mini-display
                color_hex = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
                color_box.configure(bg=color_hex)
                pos_label.configure(text=f"Pos: ({x}, {y})")
                rgb_label.configure(text=f"RGB: {rgb}")
                
                if is_red:
                    hsv_label.configure(text=f"HSV: ({h_cv}, {s_cv}, {v_cv}) ✅ VERMELHO!", fg='green')
                else:
                    hsv_label.configure(text=f"HSV: ({h_cv}, {s_cv}, {v_cv}) ❌ NÃO vermelho", fg='red')
                
            except Exception as e:
                pass  # Ignore errors during mouse movement
        
        # Bind events
        overlay.bind('<Button-1>', on_click)
        overlay.bind('<Motion>', on_mouse_move)
        
        # ESC to cancel
        def cancel(event):
            overlay.destroy()
            self.root.deiconify()
        
        overlay.bind('<Escape>', cancel)
        
        # Start overlay
        overlay.mainloop()
    
    def calibrate_auto_target(self):
        """Interactive tool to calibrate auto-target by clicking corner pairs - SIX CLICKS (2 per lighting)"""
        import mss
        
        # Show instruction dialog first
        instruction_dialog = self.create_ember_dialog("Calibração Auto-Target", 580, 420)
        
        tk.Label(instruction_dialog, text="🎯 Calibração Automática - 2 Cliques", font=('Georgia', 14, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_header']).pack(pady=15)
        
        instructions = """APENAS 2 CLIQUES! O sistema gera as 3 iluminações automaticamente:

☀️  Calibre com o jogo DE DIA (área iluminada):
   • Clique 1: Quina superior esquerda do outline vermelho
   • Clique 2: Quina oposta (inferior direita)

🤖  O sistema automaticamente cria:
   🌤️  Iluminação MÉDIA (simula meia-luz)
   🌑  Iluminação NOITE (simula escuro/sombras)

IMPORTANTE:
• Calibre DE DIA (luz normal)
• Clique nas BORDAS do quadrado vermelho
• Não precisa mais clicar em 3 monstros diferentes!

Pressione 'Iniciar' quando estiver pronto!"""
        
        tk.Label(instruction_dialog, text=instructions, justify=tk.LEFT, wraplength=540,
                bg=self.colors['bg_primary'], fg=self.colors['text_body'], font=('Arial', 9)).pack(pady=10, padx=20)
        
        # Start calibration function
        def start_calibration():
            instruction_dialog.destroy()
            self.root.withdraw()  # Hide main window temporarily
            
            # State machine for 2-click calibration (auto-generates 3 profiles)
            corner_buffer = []  # Store 2 corners
            total_clicks = [0]  # Total clicks counter (0-1)
            
            # Create fullscreen overlay
            overlay = tk.Toplevel()
            overlay.attributes('-fullscreen', True)
            overlay.attributes('-alpha', 0.3)
            overlay.attributes('-topmost', True)
            overlay.configure(bg='black')
            
            # Status label
            status_label = tk.Label(overlay, text=f"CLIQUE 1/2: Quina superior esquerda (DE DIA)", 
                                   font=('Arial', 22, 'bold'), bg='black', fg='yellow')
            status_label.pack(expand=True)
            
            def capture_click(event):
                """Capture corner clicks and process pairs to extract HSV from border pixels"""
                try:
                    click_x, click_y = event.x_root, event.y_root
                    corner_buffer.append((click_x, click_y))
                    total_clicks[0] += 1
                    
                    print(f"[CALIBRAÇÃO] Clique {total_clicks[0]}/2: Quina {len(corner_buffer)} em ({click_x}, {click_y})")
                    
                    # Check if we have a complete pair (2 corners)
                    if len(corner_buffer) == 2:
                        # HIDE OVERLAY BEFORE CAPTURE to avoid darkening the screenshot
                        overlay.withdraw()
                        overlay.update()  # Force update
                        
                        # Small delay to ensure overlay is fully hidden
                        import time
                        time.sleep(0.05)
                        
                        # Process the pair
                        x1, y1 = corner_buffer[0]
                        x2, y2 = corner_buffer[1]
                        
                        # Normalize corners (ensure x1<x2 and y1<y2)
                        left = min(x1, x2)
                        top = min(y1, y2)
                        right = max(x1, x2)
                        bottom = max(y1, y2)
                        width = right - left
                        height = bottom - top
                        
                        print(f"[CALIBRAÇÃO] Região: ({left},{top}) até ({right},{bottom}), tamanho: {width}x{height}")
                        
                        # Capture the rectangular region (NOW WITHOUT DARK OVERLAY)
                        with mss.mss() as sct:
                            region = {
                                'left': left,
                                'top': top,
                                'width': width,
                                'height': height
                            }
                            screenshot = sct.grab(region)
                            img = np.array(screenshot)[:, :, :3]
                            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                        
                        # Show overlay again
                        overlay.deiconify()
                        
                        # Convert to HSV
                        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
                        
                        # Find red pixels in the entire region
                        lower_red1 = np.array([0, 70, 70])
                        upper_red1 = np.array([10, 255, 255])
                        lower_red2 = np.array([160, 70, 70])
                        upper_red2 = np.array([180, 255, 255])
                        
                        mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
                        mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)
                        red_mask = cv2.bitwise_or(mask1, mask2)
                        
                        # Create border-only mask (extract outline, not filled interior)
                        # Find contours of red regions
                        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        if len(contours) == 0:
                            status_label.config(text="❌ Nenhum outline vermelho detectado! Tente novamente.", fg='red')
                            corner_buffer.clear()
                            total_clicks[0] = 0  # Revert clicks
                            overlay.after(2000, lambda: status_label.config(text="CLIQUE 1/2: Quina superior esquerda (DE DIA)", fg='yellow'))
                            return
                        
                        # Draw only the border of contours (not filled)
                        border_mask = np.zeros_like(red_mask)
                        cv2.drawContours(border_mask, contours, -1, 255, thickness=2)
                        
                        # AND with original red mask to get only red border pixels
                        border_mask = cv2.bitwise_and(border_mask, red_mask)
                        
                        # Extract border pixels
                        border_pixels = img_hsv[border_mask > 0]
                        
                        if len(border_pixels) == 0:
                            status_label.config(text="❌ Erro ao extrair pixels da borda! Tente novamente.", fg='red')
                            corner_buffer.clear()
                            total_clicks[0] = 0
                            overlay.after(2000, lambda: status_label.config(text="CLIQUE 1/2: Quina superior esquerda (DE DIA)", fg='yellow'))
                            return
                        
                        # Calculate median HSV from border pixels (BASE PROFILE - DAY/BRIGHT)
                        base_h = int(np.median(border_pixels[:, 0]))
                        base_s = int(np.median(border_pixels[:, 1]))
                        base_v = int(np.median(border_pixels[:, 2]))
                        
                        # Calculate base tolerances
                        std_s = max(30, int(np.std(border_pixels[:, 1]) * 2))
                        std_v = max(30, int(np.std(border_pixels[:, 2]) * 2))
                        
                        print(f"[CALIBRAÇÃO] BASE (DIA): H={base_h}, S={base_s}, V={base_v} ({len(border_pixels)} pixels)")
                        
                        # GENERATE 3 PROFILES AUTOMATICALLY FROM SINGLE DAY CAPTURE
                        
                        # Profile 1: BRIGHT (original day capture)
                        bright_profile = {
                            'lower_s': max(0, base_s - std_s),
                            'upper_s': 255,
                            'lower_v': max(0, base_v - std_v),
                            'upper_v': 255,
                            'median_h': base_h,
                            'median_s': base_s,
                            'median_v': base_v,
                            'pixels': len(border_pixels)
                        }
                        
                        # Profile 2: MEDIUM (simulate twilight - 70% brightness, 85% saturation)
                        medium_s = int(base_s * 0.85)
                        medium_v = int(base_v * 0.70)
                        medium_std_s = int(std_s * 0.85)
                        medium_std_v = int(std_v * 0.70)
                        
                        medium_profile = {
                            'lower_s': max(0, medium_s - medium_std_s),
                            'upper_s': 255,
                            'lower_v': max(0, medium_v - medium_std_v),
                            'upper_v': 255,
                            'median_h': base_h,  # Hue stays same
                            'median_s': medium_s,
                            'median_v': medium_v,
                            'pixels': len(border_pixels)
                        }
                        
                        # Profile 3: DARK (simulate night - 50% brightness, 70% saturation)
                        dark_s = int(base_s * 0.70)
                        dark_v = int(base_v * 0.50)
                        dark_std_s = int(std_s * 0.70)
                        dark_std_v = int(std_v * 0.50)
                        
                        dark_profile = {
                            'lower_s': max(0, dark_s - dark_std_s),
                            'upper_s': 255,
                            'lower_v': max(0, dark_v - dark_std_v),
                            'upper_v': 255,
                            'median_h': base_h,  # Hue stays same
                            'median_s': dark_s,
                            'median_v': dark_v,
                            'pixels': len(border_pixels)
                        }
                        
                        profiles_data = [bright_profile, medium_profile, dark_profile]
                        
                        print(f"[CALIBRAÇÃO] ✅ BRIGHT: S={base_s}, V={base_v}")
                        print(f"[CALIBRAÇÃO] ✅ MEDIUM: S={medium_s}, V={medium_v} (auto-gerado)")
                        print(f"[CALIBRAÇÃO] ✅ DARK: S={dark_s}, V={dark_v} (auto-gerado)")
                        
                        # All done! Save immediately
                        status_label.config(text="✅ Calibração concluída! Gerando 3 perfis automaticamente...", fg='green')
                        overlay.after(1000, lambda: finalize_calibration(profiles_data, overlay))
                    
                    else:
                        # First click done - waiting for second corner
                        status_label.config(text="CLIQUE 2/2: Quina oposta (canto diagonal)", fg='yellow')
                
                except Exception as e:
                    print(f"[CALIBRAÇÃO] Erro: {e}")
                    import traceback
                    traceback.print_exc()
                    corner_buffer.clear()
            
            def finalize_calibration(data, overlay_window):
                """Save all 3 profiles and close"""
                try:
                    if not hasattr(self, 'hsv_config') or not isinstance(self.hsv_config, dict):
                        self.hsv_config = {}
                    
                    print(f"[CALIBRAÇÃO] hsv_config ANTES de adicionar perfis: {list(self.hsv_config.keys())}")
                    
                    self.hsv_config['profiles'] = {
                        'bright': data[0],
                        'medium': data[1],
                        'dark': data[2]
                    }
                    self.hsv_config['calibrated'] = True
                    self.hsv_config['multi_profile'] = True
                    
                    print(f"[CALIBRAÇÃO] hsv_config DEPOIS de adicionar perfis: {list(self.hsv_config.keys())}")
                    print(f"[CALIBRAÇÃO] Perfis adicionados: {list(self.hsv_config['profiles'].keys())}")
                    
                    self.save_config()
                    print("[CALIBRAÇÃO] ✅ save_config() executado!")
                    
                    # Verify it was actually saved to self
                    if 'profiles' in self.hsv_config:
                        print(f"[CALIBRAÇÃO] ✅ Confirmado: self.hsv_config tem perfis!")
                    else:
                        print(f"[CALIBRAÇÃO] ❌ ERRO: self.hsv_config NÃO tem perfis após save!")
                    
                    # Verify it was actually saved to FILE
                    import json
                    with open(self.config_file, 'r') as f:
                        saved_config = json.load(f)
                        if 'profiles' in saved_config.get('hsv_config', {}):
                            print(f"[CALIBRAÇÃO] ✅ ARQUIVO TEM PERFIS: {list(saved_config['hsv_config']['profiles'].keys())}")
                        else:
                            print(f"[CALIBRAÇÃO] ❌ ARQUIVO NÃO TEM PERFIS!")
                            print(f"[CALIBRAÇÃO] Arquivo contém: {list(saved_config.get('hsv_config', {}).keys())}")
                    
                    overlay_window.destroy()
                    self.root.deiconify()
                    self.ember_info("Sucesso!", "✅ Calibração automática concluída!\n\n3 perfis gerados (DIA, MEIA-LUZ, NOITE)\nO sistema detecta targets em QUALQUER iluminação!")
                    
                except Exception as e:
                    print(f"[CALIBRAÇÃO] Erro ao salvar: {e}")
                    import traceback
                    traceback.print_exc()
                    overlay_window.destroy()
                    self.root.deiconify()
            
            # Bind click event
            overlay.bind('<Button-1>', capture_click)
            
            # ESC to cancel
            def cancel(event):
                overlay.destroy()
                self.root.deiconify()
            
            overlay.bind('<Escape>', cancel)
        
        # Start button
        tk.Button(instruction_dialog, text="▶ Iniciar Calibração", command=start_calibration,
                 bg=self.colors['focus_glow'], fg='black', font=('Arial', 12, 'bold'),
                 padx=30, pady=10, relief=tk.RAISED, borderwidth=3).pack(pady=15)
        
        # Cancel button
        tk.Button(instruction_dialog, text="Cancelar", command=instruction_dialog.destroy,
                 bg=self.colors['button_destructive'], fg=self.colors['text_body'],
                 font=('Arial', 10), padx=20, pady=5).pack(pady=5)
    
    def open_auto_uh_config(self):
        """Quick config dialog for Auto UH (Ultimate Healing)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚕️ Auto UH - Ultimate Healing Config")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        ttk.Label(dialog, text="⚕️ Auto UH Configuration", font=('Arial', 16, 'bold')).pack(pady=15)
        ttk.Label(dialog, text="Configure hotkey para usar Ultimate Healing automaticamente", 
                 font=('Arial', 10)).pack(pady=5)
        
        # Step 1: Hotkey
        hotkey_frame = ttk.LabelFrame(dialog, text="1️⃣ Escolha a Hotkey", padding="15")
        hotkey_frame.pack(pady=10, padx=20, fill=tk.X)
        
        hotkey_var = tk.StringVar(value="Pressione uma tecla...")
        ttk.Label(hotkey_frame, textvariable=hotkey_var, font=('Arial', 12, 'bold'), 
                 foreground='blue').pack(pady=10)
        
        pressed_keys = {'keys': set(), 'combo': []}
        
        def on_press(key):
            try:
                k = key.char.lower() if hasattr(key, 'char') else key.name.lower()
                pressed_keys['keys'].add(k)
                hotkey_var.set('+'.join(sorted([k.upper() for k in pressed_keys['keys']])))
            except:
                pass
        
        def on_release(key):
            if pressed_keys['keys']:
                pressed_keys['combo'] = sorted(list(pressed_keys['keys']))
                hotkey_var.set('+'.join([k.upper() for k in pressed_keys['combo']]) + " ✓")
                return False
        
        listener = KeyboardListener(on_press=on_press, on_release=on_release)
        listener.start()
        
        # Step 2: Click recording
        click_frame = ttk.LabelFrame(dialog, text="2️⃣ Gravar Posições", padding="15")
        click_frame.pack(pady=10, padx=20, fill=tk.X)
        
        status_var = tk.StringVar(value="Clique 'Gravar' para começar")
        ttk.Label(click_frame, textvariable=status_var, wraplength=500).pack(pady=5)
        
        clicks_recorded = []
        
        def on_click(x, y, button, pressed):
            if pressed and len(clicks_recorded) < 2:
                clicks_recorded.append({'x': x, 'y': y})
                if len(clicks_recorded) == 1:
                    status_var.set(f"✓ UH Rune: ({x}, {y})\nAgora clique no PERSONAGEM")
                elif len(clicks_recorded) == 2:
                    status_var.set(f"✓ UH: ({clicks_recorded[0]['x']}, {clicks_recorded[0]['y']})\n✓ Personagem: ({x}, {y})")
                    return False
        
        def start_recording():
            clicks_recorded.clear()
            status_var.set("Clique na posição da UH RUNE...")
            dialog.after(100, lambda: mouse.Listener(on_click=on_click).start())
        
        ttk.Button(click_frame, text="📍 Gravar Posições", command=start_recording).pack(pady=10)
        
        # Step 3: Delay
        delay_frame = ttk.LabelFrame(dialog, text="3️⃣ Delay entre cliques", padding="15")
        delay_frame.pack(pady=10, padx=20, fill=tk.X)
        
        delay_var = tk.IntVar(value=100)
        
        delay_slider_frame = ttk.Frame(delay_frame)
        delay_slider_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(delay_slider_frame, text="Delay (ms):").pack(side=tk.LEFT, padx=5)
        ttk.Scale(delay_slider_frame, from_=10, to=500, variable=delay_var, orient=tk.HORIZONTAL, 
                 length=300).pack(side=tk.LEFT, padx=5)
        delay_label = ttk.Label(delay_slider_frame, textvariable=delay_var, width=5)
        delay_label.pack(side=tk.LEFT, padx=5)
        
        # Save button
        def save_uh_config():
            if not pressed_keys['combo']:
                messagebox.showwarning("Erro", "Escolha uma hotkey primeiro!")
                return
            if len(clicks_recorded) != 2:
                messagebox.showwarning("Erro", "Grave as 2 posições (UH + Personagem)!")
                return
            
            listener.stop()
            
            new_hotkey = {
                'hotkey': pressed_keys['combo'],
                'clicks': clicks_recorded,
                'delay': delay_var.get(),
                'type': 'normal'
            }
            
            self.hotkeys.append(new_hotkey)
            self.save_config()
            self.refresh_tree()
            dialog.destroy()
            messagebox.showinfo("✓ Sucesso!", f"Auto UH configurado em {'+'.join([k.upper() for k in pressed_keys['combo']])}!")
        
        ttk.Button(dialog, text="💾 Salvar Auto UH", command=save_uh_config, 
                  style='Accent.TButton').pack(pady=15)
        ttk.Button(dialog, text="Cancelar", command=lambda: [listener.stop(), dialog.destroy()]).pack()
    
    def open_auto_sd_config(self):
        """Quick config dialog for Auto SD (Sudden Death with auto-target)"""
        messagebox.showinfo("Em desenvolvimento", 
                          "Interface Auto SD com calibração integrada será adicionada em breve!\n\n"
                          "Por enquanto, use:\n"
                          "1. 'Add New Hotkey' → Offensive\n"
                          "2. 'Calibrar Clicando' para ajustar cores")
    
    def add_hotkey_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Hotkey")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Step 1: Press your desired hotkey combination", font=('Arial', 12)).pack(pady=10)
        
        hotkey_var = tk.StringVar(value="Waiting for hotkey...")
        hotkey_label = ttk.Label(dialog, textvariable=hotkey_var, font=('Arial', 10, 'bold'), foreground='blue')
        hotkey_label.pack(pady=5)
        
        pressed_keys = {'keys': set(), 'combo': None}
        
        def on_press(key):
            try:
                k = key.char.lower() if hasattr(key, 'char') else key.name.lower()
                pressed_keys['keys'].add(k)
                hotkey_var.set('+'.join(sorted([k.upper() for k in pressed_keys['keys']])))
            except:
                pass
        
        def on_release(key):
            if pressed_keys['keys']:
                pressed_keys['combo'] = sorted(list(pressed_keys['keys']))
                hotkey_var.set('+'.join([k.upper() for k in pressed_keys['combo']]) + " (Saved!)")
                return False  # Stop listener
        
        listener = KeyboardListener(on_press=on_press, on_release=on_release)
        listener.start()
        
        def continue_to_clicks():
            if not pressed_keys['combo']:
                messagebox.showwarning("No Hotkey", "Please press a hotkey combination first!")
                return
            
            listener.stop()
            dialog.destroy()
            self.record_clicks_dialog(pressed_keys['combo'])
        
        ttk.Button(dialog, text="Continue to Click Recording", command=continue_to_clicks).pack(pady=20)
        ttk.Button(dialog, text="Cancel", command=lambda: [listener.stop(), dialog.destroy()]).pack()
    
    def record_clicks_dialog(self, hotkey_combo):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Hotkey Type")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Step 2: Choose Hotkey Type", font=('Arial', 14, 'bold')).pack(pady=15)
        
        type_frame = ttk.LabelFrame(dialog, text="Select Type", padding="15")
        type_frame.pack(pady=10, padx=20, fill=tk.BOTH)
        
        type_var = tk.StringVar(value="normal")
        
        ttk.Radiobutton(
            type_frame,
            text="Normal (Runes/Fluids): Right-click item → Left-click character",
            variable=type_var,
            value="normal"
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(
            type_frame,
            text="Offensive (Runas Ofensivas): Right-click item → Move to center (manual click)",
            variable=type_var,
            value="offensive"
        ).pack(anchor=tk.W, pady=5)
        
        def continue_to_recording():
            dialog.destroy()
            if type_var.get() == "normal":
                self.record_normal_clicks(hotkey_combo)
            else:
                self.record_offensive_clicks(hotkey_combo)
        
        ttk.Button(dialog, text="Continue to Recording", command=continue_to_recording).pack(pady=20)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def record_normal_clicks(self, hotkey_combo):
        dialog = tk.Toplevel(self.root)
        dialog.title("Record Click Positions - Normal")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Step 3: Record Click Positions", font=('Arial', 12)).pack(pady=10)
        
        instruction_text = """
1. Click "Start Recording"
2. Move your mouse to the ITEM position (rune/mana fluid)
3. Click to record the first position (will be RIGHT-CLICK)
4. Move your mouse to your CHARACTER position (center)
5. Click to record the second position (will be LEFT-CLICK)
        """
        
        ttk.Label(dialog, text=instruction_text, justify=tk.LEFT).pack(pady=10)
        
        status_var = tk.StringVar(value="Ready to record...")
        status_label = ttk.Label(dialog, textvariable=status_var, font=('Arial', 10, 'bold'))
        status_label.pack(pady=5)
        
        clicks_recorded = []
        
        def on_click(x, y, button, pressed):
            if pressed and len(clicks_recorded) < 2:
                clicks_recorded.append({'x': x, 'y': y})
                if len(clicks_recorded) == 1:
                    status_var.set(f"Position 1 recorded: ({x}, {y})\nNow click on your character position...")
                elif len(clicks_recorded) == 2:
                    status_var.set(f"Position 2 recorded: ({x}, {y})\nBoth positions saved!")
                    return False  # Stop listener
        
        def start_recording():
            status_var.set("Recording... Click on ITEM position first")
            dialog.after(100, lambda: mouse.Listener(on_click=on_click).start())
        
        ttk.Button(dialog, text="Start Recording", command=start_recording).pack(pady=10)
        
        # Delay configuration
        delay_frame = ttk.Frame(dialog)
        delay_frame.pack(pady=10)
        
        ttk.Label(delay_frame, text="Delay between clicks (ms):").pack(side=tk.LEFT)
        delay_var = tk.IntVar(value=100)
        delay_spinbox = ttk.Spinbox(delay_frame, from_=10, to=2000, textvariable=delay_var, width=10)
        delay_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Return to position option
        return_frame = ttk.Frame(dialog)
        return_frame.pack(pady=10)
        
        return_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            return_frame,
            text="Retornar mouse a posicao original",
            variable=return_var
        ).pack()
        ttk.Label(return_frame, text="(Apos executar, volta o mouse pra onde estava)", 
                 font=('Arial', 8), foreground='gray').pack()
        
        def save_hotkey():
            if len(clicks_recorded) != 2:
                messagebox.showwarning("Incomplete", "Please record both click positions!")
                return
            
            new_hotkey = {
                'hotkey': hotkey_combo,
                'clicks': clicks_recorded,
                'delay': delay_var.get(),
                'type': 'normal',
                'return_to_position': return_var.get()
            }
            
            self.hotkeys.append(new_hotkey)
            self.save_config()
            self.refresh_tree()
            dialog.destroy()
            messagebox.showinfo("Success", f"Hotkey {'+'.join([k.upper() for k in hotkey_combo])} added successfully!")
        
        ttk.Button(dialog, text="Save Hotkey", command=save_hotkey).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def record_offensive_clicks(self, hotkey_combo):
        dialog = tk.Toplevel(self.root)
        dialog.title("Record Positions - Offensive Rune")
        dialog.geometry("550x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Step 3: Choose Auto-Target Mode", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Auto-target option at TOP
        auto_target_frame = ttk.LabelFrame(dialog, text="Target Detection Mode", padding="15")
        auto_target_frame.pack(pady=10, padx=20, fill=tk.X)
        
        auto_target_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            auto_target_frame,
            text="✓ Enable Auto-Target (RECOMMENDED)",
            variable=auto_target_var,
            command=lambda: update_instructions()
        ).pack(anchor=tk.W)
        
        ttk.Label(
            auto_target_frame,
            text="✓ Scans ENTIRE screen for red target outline (32x32px)\n✓ Automatically clicks on detected target\n✓ Works even when monster MOVES around!",
            font=('Arial', 9),
            foreground='green'
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Label(
            auto_target_frame,
            text="✗ Manual Mode: Fixed destination position (manual click required)",
            font=('Arial', 9),
            foreground='gray'
        ).pack(anchor=tk.W)
        
        # Instructions change based on mode
        instruction_frame = ttk.LabelFrame(dialog, text="Recording Instructions", padding="10")
        instruction_frame.pack(pady=10, padx=20, fill=tk.X)
        
        instruction_var = tk.StringVar()
        ttk.Label(instruction_frame, textvariable=instruction_var, justify=tk.LEFT, wraplength=480).pack()
        
        def update_instructions():
            if auto_target_var.get():
                instruction_var.set(
                    "AUTO-TARGET MODE:\n"
                    "1. Click 'Start Recording'\n"
                    "2. Click ONLY the RUNE position (1 click)\n"
                    "3. Done!\n\n"
                    "When you press hotkey:\n"
                    "• Right-click on rune\n"
                    "• Scans screen for red outline\n"
                    "• Auto-clicks on target!"
                )
            else:
                instruction_var.set(
                    "MANUAL MODE:\n"
                    "1. Click 'Start Recording'\n"
                    "2. Click the RUNE position (1st click)\n"
                    "3. Click destination position (2nd click)\n\n"
                    "When you press hotkey:\n"
                    "• Right-click on rune\n"
                    "• Moves to destination\n"
                    "• You click manually"
                )
        
        update_instructions()
        
        status_var = tk.StringVar(value="Ready to record...")
        ttk.Label(dialog, textvariable=status_var, font=('Arial', 10, 'bold'), foreground='blue').pack(pady=10)
        
        clicks_recorded = []
        
        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                clicks_recorded.append({'x': x, 'y': y})
                
                if auto_target_var.get():
                    # Auto-target: only 1 click needed
                    status_var.set(f"✓ Rune position recorded: ({x}, {y})\nReady to save!")
                    return False
                else:
                    # Manual: 2 clicks needed
                    if len(clicks_recorded) == 1:
                        status_var.set(f"✓ Rune recorded: ({x}, {y})\nNow click destination position...")
                    elif len(clicks_recorded) == 2:
                        status_var.set(f"✓ Complete! Rune: {clicks_recorded[0]}\nDestination: ({x}, {y})")
                        return False
        
        def start_recording():
            clicks_recorded.clear()
            if auto_target_var.get():
                status_var.set("Recording... Click RUNE position (1 click only)")
            else:
                status_var.set("Recording... Click RUNE position first")
            dialog.after(100, lambda: mouse.Listener(on_click=on_click).start())
        
        ttk.Button(dialog, text="Start Recording", command=start_recording, style='Accent.TButton').pack(pady=15)
        
        def save_hotkey():
            required_clicks = 1 if auto_target_var.get() else 2
            if len(clicks_recorded) != required_clicks:
                messagebox.showwarning("Incomplete", f"Please record {required_clicks} position(s)!")
                return
            
            new_hotkey = {
                'hotkey': hotkey_combo,
                'clicks': clicks_recorded,
                'delay': 0,
                'type': 'offensive',
                'auto_target': auto_target_var.get()
            }
            
            self.hotkeys.append(new_hotkey)
            self.save_config()
            self.refresh_tree()
            dialog.destroy()
            
            mode_desc = "AUTO-TARGET (scans screen)" if auto_target_var.get() else "MANUAL (fixed position)"
            messagebox.showinfo("Success", f"Offensive hotkey {'+'.join([k.upper() for k in hotkey_combo])} added!\n\nMode: {mode_desc}")
        
        ttk.Button(dialog, text="Save Hotkey", command=save_hotkey).pack(pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)
    
    def edit_hotkey(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a hotkey to edit")
            return
        
        index = self.tree.index(selection[0])
        existing_hotkey = self.hotkeys[index]
        hk_type = existing_hotkey.get('type', 'normal')
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Hotkey")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Edit Hotkey Configuration", font=('Arial', 12)).pack(pady=10)
        
        # Display current hotkey
        current_hotkey_str = '+'.join([k.upper() for k in existing_hotkey['hotkey']])
        type_str = "OFFENSIVE" if hk_type == 'offensive' else "NORMAL"
        ttk.Label(dialog, text=f"Current Hotkey: {current_hotkey_str} [{type_str}]", font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Click positions
        ttk.Label(dialog, text="Click Positions:", font=('Arial', 10)).pack(pady=5)
        if hk_type == 'offensive':
            clicks_str = f"Rune Position (Right-click): ({existing_hotkey['clicks'][0]['x']}, {existing_hotkey['clicks'][0]['y']})\n"
            if len(existing_hotkey['clicks']) >= 2:
                clicks_str += f"Destination Position: ({existing_hotkey['clicks'][1]['x']}, {existing_hotkey['clicks'][1]['y']})"
            else:
                clicks_str += "Destination: Center of screen (old format)"
        else:
            clicks_str = f"Position 1 (Right-click): ({existing_hotkey['clicks'][0]['x']}, {existing_hotkey['clicks'][0]['y']})\n"
            clicks_str += f"Position 2 (Left-click): ({existing_hotkey['clicks'][1]['x']}, {existing_hotkey['clicks'][1]['y']})"
        ttk.Label(dialog, text=clicks_str, justify=tk.LEFT).pack(pady=5)
        
        # Delay configuration (only for normal type)
        if hk_type == 'normal':
            delay_frame = ttk.Frame(dialog)
            delay_frame.pack(pady=10)
            
            ttk.Label(delay_frame, text="Delay between clicks (ms):").pack(side=tk.LEFT)
            delay_var = tk.IntVar(value=existing_hotkey['delay'])
            delay_spinbox = ttk.Spinbox(delay_frame, from_=10, to=2000, textvariable=delay_var, width=10)
            delay_spinbox.pack(side=tk.LEFT, padx=5)
        else:
            delay_var = tk.IntVar(value=0)
        
        # Options
        ttk.Label(dialog, text="\nWhat would you like to edit?", font=('Arial', 10)).pack(pady=10)
        
        def update_delay_only():
            if hk_type == 'normal':
                self.hotkeys[index]['delay'] = delay_var.get()
                self.save_config()
                self.refresh_tree()
                dialog.destroy()
                messagebox.showinfo("Success", "Delay updated successfully!")
        
        def re_record_clicks():
            dialog.destroy()
            if hk_type == 'offensive':
                self.record_offensive_clicks_edit(index, existing_hotkey['hotkey'])
            else:
                self.record_normal_clicks_edit(index, existing_hotkey['hotkey'], delay_var.get())
        
        def change_hotkey_combo():
            dialog.destroy()
            self.add_hotkey_dialog_edit(index, existing_hotkey['clicks'], delay_var.get(), hk_type)
        
        if hk_type == 'normal':
            ttk.Button(dialog, text="Update Delay Only", command=update_delay_only).pack(pady=5)
        ttk.Button(dialog, text="Re-record Click Positions", command=re_record_clicks).pack(pady=5)
        ttk.Button(dialog, text="Change Hotkey Combination", command=change_hotkey_combo).pack(pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=10)
    
    def record_normal_clicks_edit(self, index, hotkey_combo, delay):
        """Edit mode: re-record clicks for existing normal hotkey"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Re-record Click Positions - Normal")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Re-record Click Positions", font=('Arial', 12)).pack(pady=10)
        
        instruction_text = """
1. Click "Start Recording"
2. Move your mouse to the ITEM position (rune/mana fluid)
3. Click to record the first position (will be RIGHT-CLICK)
4. Move your mouse to your CHARACTER position (center)
5. Click to record the second position (will be LEFT-CLICK)
        """
        
        ttk.Label(dialog, text=instruction_text, justify=tk.LEFT).pack(pady=10)
        
        status_var = tk.StringVar(value="Ready to record...")
        status_label = ttk.Label(dialog, textvariable=status_var, font=('Arial', 10, 'bold'))
        status_label.pack(pady=5)
        
        clicks_recorded = []
        
        def on_click(x, y, button, pressed):
            if pressed and len(clicks_recorded) < 2:
                clicks_recorded.append({'x': x, 'y': y})
                if len(clicks_recorded) == 1:
                    status_var.set(f"Position 1 recorded: ({x}, {y})\nNow click on your character position...")
                elif len(clicks_recorded) == 2:
                    status_var.set(f"Position 2 recorded: ({x}, {y})\nBoth positions saved!")
                    return False
        
        def start_recording():
            status_var.set("Recording... Click on ITEM position first")
            dialog.after(100, lambda: mouse.Listener(on_click=on_click).start())
        
        ttk.Button(dialog, text="Start Recording", command=start_recording).pack(pady=10)
        
        def save_changes():
            if len(clicks_recorded) != 2:
                messagebox.showwarning("Incomplete", "Please record both click positions!")
                return
            
            self.hotkeys[index]['clicks'] = clicks_recorded
            self.hotkeys[index]['delay'] = delay
            self.save_config()
            self.refresh_tree()
            dialog.destroy()
            messagebox.showinfo("Success", "Click positions updated successfully!")
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def record_offensive_clicks_edit(self, index, hotkey_combo):
        """Edit mode: re-record positions for existing offensive hotkey"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Re-record Positions - Offensive")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Re-record Offensive Positions", font=('Arial', 12)).pack(pady=10)
        
        instruction_text = """
1. Click "Start Recording"
2. Move your mouse to the OFFENSIVE RUNE position
3. Click to record the rune position (will be RIGHT-CLICK)
4. Move your mouse to where you want the cursor to stop
5. Click to record the destination position
        """
        
        ttk.Label(dialog, text=instruction_text, justify=tk.LEFT).pack(pady=10)
        
        status_var = tk.StringVar(value="Ready to record...")
        status_label = ttk.Label(dialog, textvariable=status_var, font=('Arial', 10, 'bold'))
        status_label.pack(pady=5)
        
        clicks_recorded = []
        
        def on_click(x, y, button, pressed):
            if pressed and len(clicks_recorded) < 2:
                clicks_recorded.append({'x': x, 'y': y})
                if len(clicks_recorded) == 1:
                    status_var.set(f"Rune position recorded: ({x}, {y})\nNow click where you want the mouse to stop...")
                elif len(clicks_recorded) == 2:
                    status_var.set(f"Destination recorded: ({x}, {y})\nBoth positions saved!")
                    return False
        
        def start_recording():
            status_var.set("Recording... Click on OFFENSIVE RUNE position first")
            dialog.after(100, lambda: mouse.Listener(on_click=on_click).start())
        
        ttk.Button(dialog, text="Start Recording", command=start_recording).pack(pady=10)
        
        def save_changes():
            if len(clicks_recorded) != 2:
                messagebox.showwarning("Incomplete", "Please record both positions!")
                return
            
            self.hotkeys[index]['clicks'] = clicks_recorded
            self.save_config()
            self.refresh_tree()
            dialog.destroy()
            messagebox.showinfo("Success", "Positions updated successfully!")
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def add_hotkey_dialog_edit(self, index, clicks, delay, hk_type):
        """Edit mode: change hotkey combination for existing hotkey"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Hotkey Combination")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Press your new hotkey combination", font=('Arial', 12)).pack(pady=10)
        
        hotkey_var = tk.StringVar(value="Waiting for hotkey...")
        hotkey_label = ttk.Label(dialog, textvariable=hotkey_var, font=('Arial', 10, 'bold'), foreground='blue')
        hotkey_label.pack(pady=5)
        
        pressed_keys = {'keys': set(), 'combo': None}
        
        def on_press(key):
            try:
                k = key.char.lower() if hasattr(key, 'char') else key.name.lower()
                pressed_keys['keys'].add(k)
                hotkey_var.set('+'.join(sorted([k.upper() for k in pressed_keys['keys']])))
            except:
                pass
        
        def on_release(key):
            if pressed_keys['keys']:
                pressed_keys['combo'] = sorted(list(pressed_keys['keys']))
                hotkey_var.set('+'.join([k.upper() for k in pressed_keys['combo']]) + " (Saved!)")
                return False
        
        listener = KeyboardListener(on_press=on_press, on_release=on_release)
        listener.start()
        
        def save_changes():
            if not pressed_keys['combo']:
                messagebox.showwarning("No Hotkey", "Please press a hotkey combination first!")
                return
            
            listener.stop()
            self.hotkeys[index]['hotkey'] = pressed_keys['combo']
            self.hotkeys[index]['delay'] = delay
            self.hotkeys[index]['type'] = hk_type
            self.save_config()
            self.refresh_tree()
            dialog.destroy()
            messagebox.showinfo("Success", "Hotkey combination updated successfully!")
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=20)
        ttk.Button(dialog, text="Cancel", command=lambda: [listener.stop(), dialog.destroy()]).pack()
    
    def delete_hotkey(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a hotkey to delete")
            return
        
        index = self.tree.index(selection[0])
        del self.hotkeys[index]
        self.save_config()
        self.refresh_tree()
    
    def clear_all(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to delete all hotkeys?"):
            self.hotkeys = []
            self.save_config()
            self.refresh_tree()
    
    def start_hotkey_listener(self):
        """
        NEW ROBUST HOTKEY SYSTEM using 'keyboard' library
        More reliable on Windows, especially when switching windows
        """
        # Track currently pressed keys
        self.currently_pressed = set()
        self.triggered_quick_keys = set()
        self.triggered_hotkeys = set()
        
        def on_key_event(event):
            """Handle all keyboard events"""
            try:
                key_name = event.name.lower() if event.name else None
                if not key_name:
                    return
                
                # Normalize modifier key names
                if key_name in ('left ctrl', 'right ctrl'):
                    key_name = 'ctrl'
                elif key_name in ('left alt', 'right alt'):
                    key_name = 'alt'
                elif key_name in ('left shift', 'right shift'):
                    key_name = 'shift'
                
                if event.event_type == 'down':
                    # === GLOBAL PAUSE HOTKEY: Alt+F12 ===
                    # This works even when automations are OFF
                    if key_name == 'f12' and 'alt' in self.currently_pressed:
                        self.ui_safe(self.pause_all)
                        return
                    
                    # Add key to currently pressed set
                    self.currently_pressed.add(key_name)
                    
                    # Skip processing if automation is OFF
                    if not self.active:
                        return
                    
                    # Build current combo string
                    current_combo = self._build_combo_string(self.currently_pressed)
                    
                    # Check Quick Configs FIRST (priority over custom hotkeys)
                    quick_configs = self.config.get('quick_configs', {})
                    
                    # Check Auto SD
                    if 'auto_sd' in quick_configs:
                        sd_config = quick_configs['auto_sd']
                        sd_hotkey = sd_config.get('hotkey', 'f1').lower()
                        if current_combo == sd_hotkey and sd_config.get('enabled', False):
                            if sd_hotkey not in self.triggered_quick_keys:
                                self.triggered_quick_keys.add(sd_hotkey)
                                threading.Thread(target=self.execute_quick_sd, daemon=True).start()
                    
                    # Check Auto EXPLO
                    if 'auto_explo' in quick_configs:
                        explo_config = quick_configs['auto_explo']
                        explo_hotkey = explo_config.get('hotkey', 'f4').lower()
                        if current_combo == explo_hotkey and explo_config.get('enabled', False):
                            if explo_hotkey not in self.triggered_quick_keys:
                                self.triggered_quick_keys.add(explo_hotkey)
                                threading.Thread(target=self.execute_quick_explo, daemon=True).start()
                    
                    # Check Auto UH
                    if 'auto_uh' in quick_configs:
                        uh_config = quick_configs['auto_uh']
                        uh_hotkey = uh_config.get('hotkey', 'f2').lower()
                        if current_combo == uh_hotkey and uh_config.get('enabled', False):
                            if uh_hotkey not in self.triggered_quick_keys:
                                self.triggered_quick_keys.add(uh_hotkey)
                                threading.Thread(target=self.execute_quick_uh, daemon=True).start()
                    
                    # Check Auto MANA
                    if 'auto_mana' in quick_configs:
                        mana_config = quick_configs['auto_mana']
                        mana_hotkey = mana_config.get('hotkey', 'f3').lower()
                        if current_combo == mana_hotkey and mana_config.get('enabled', False):
                            if mana_hotkey not in self.triggered_quick_keys:
                                self.triggered_quick_keys.add(mana_hotkey)
                                threading.Thread(target=self.execute_quick_mana, daemon=True).start()
                    
                    # Check Hyper Grab
                    hg_config = self.config.get('hypergrab', {})
                    if hg_config.get('enabled', False):
                        hg_hotkey = hg_config.get('hotkey', 'f5').lower()
                        if current_combo == hg_hotkey:
                            if 'hypergrab' not in self.triggered_quick_keys:
                                self.triggered_quick_keys.add('hypergrab')
                                threading.Thread(target=self.execute_hypergrab, daemon=True).start()
                    
                    # Check Drag Hotkey
                    drag_config = self.config.get('drag_hotkey', {})
                    if drag_config.get('enabled', False):
                        drag_hk = drag_config.get('hotkey', 'f8').lower()
                        if current_combo == drag_hk:
                            if 'drag_hotkey' not in self.triggered_quick_keys:
                                self.triggered_quick_keys.add('drag_hotkey')
                                threading.Thread(target=self.execute_drag_hotkey, daemon=True).start()
                    
                    # Check Runemaker Pause Hotkey
                    if hasattr(self, 'rm_pause_hotkey') and self.runemaker_running:
                        pause_hotkey = self.rm_pause_hotkey.get().lower()
                        if current_combo == pause_hotkey:
                            if 'rm_pause' not in self.triggered_quick_keys:
                                self.triggered_quick_keys.add('rm_pause')
                                self.ui_safe(self.toggle_runemaker_pause)
                    
                    # Check custom hotkeys
                    matching_hotkeys = []
                    for idx, hk in enumerate(self.hotkeys):
                        hotkey_set = set(hk['hotkey'])
                        if hotkey_set.issubset(self.currently_pressed) and idx not in self.triggered_hotkeys:
                            matching_hotkeys.append((idx, hk, len(hk['hotkey'])))
                    
                    if matching_hotkeys:
                        matching_hotkeys.sort(key=lambda x: x[2], reverse=True)
                        idx, hk, _ = matching_hotkeys[0]
                        for match_idx, _, _ in matching_hotkeys:
                            self.triggered_hotkeys.add(match_idx)
                        threading.Thread(target=self.execute_clicks, args=(hk,), daemon=True).start()
                
                elif event.event_type == 'up':
                    # Remove key from currently pressed set
                    self.currently_pressed.discard(key_name)
                    
                    # Reset quick config keys
                    current_combo = self._build_combo_string(self.currently_pressed)
                    quick_configs = self.config.get('quick_configs', {})
                    
                    for config_key in ['auto_sd', 'auto_explo', 'auto_uh', 'auto_mana']:
                        if config_key in quick_configs:
                            hotkey = quick_configs[config_key].get('hotkey', '').lower()
                            if hotkey and hotkey != current_combo:
                                self.triggered_quick_keys.discard(hotkey)
                    
                    # Reset other hotkeys
                    if hasattr(self, 'rm_pause_hotkey'):
                        pause_hotkey = self.rm_pause_hotkey.get().lower()
                        if pause_hotkey != current_combo:
                            self.triggered_quick_keys.discard('rm_pause')
                    
                    hg_config = self.config.get('hypergrab', {})
                    hg_hotkey = hg_config.get('hotkey', 'f5').lower()
                    if hg_hotkey != current_combo:
                        self.triggered_quick_keys.discard('hypergrab')
                    
                    drag_config = self.config.get('drag_hotkey', {})
                    drag_hk = drag_config.get('hotkey', 'f8').lower()
                    if drag_hk != current_combo:
                        self.triggered_quick_keys.discard('drag_hotkey')
                    
                    # Reset custom hotkeys
                    for idx, hk in enumerate(self.hotkeys):
                        hotkey_set = set(hk['hotkey'])
                        if not hotkey_set.issubset(self.currently_pressed):
                            self.triggered_hotkeys.discard(idx)
                            
            except Exception as e:
                pass  # Silently ignore errors to prevent crashes
        
        # Hook the keyboard events globally
        kb.hook(on_key_event)
        print("[KEYBOARD] Hotkey listener started (using 'keyboard' library)")
    
    def stop_hotkey_listener(self):
        """Stop the keyboard listener"""
        try:
            kb.unhook_all()
            print("[KEYBOARD] Hotkey listener stopped")
        except:
            pass
    
    def _build_combo_string(self, pressed_keys):
        """Build a combo string from currently pressed keys (e.g., 'ctrl+alt+f1')"""
        modifiers = []
        regular_keys = []
        
        for k in pressed_keys:
            if k in ('ctrl', 'alt', 'shift'):
                modifiers.append(k)
            else:
                regular_keys.append(k)
        
        # Sort to ensure consistent ordering
        modifiers.sort()
        regular_keys.sort()
        
        # Build combo: modifiers first, then regular keys
        combo_parts = modifiers + regular_keys
        return '+'.join(combo_parts) if combo_parts else ''
    
    def detect_red_target(self):
        """
        STRAIGHT LINE DETECTION: Find 4 red lines forming 64x64 square
        
        Detects ONLY the outline (4 straight red lines), ignoring content:
        - Detect red pixels (calibrated HSV)
        - Find straight lines in red regions (Hough transform)
        - Verify 4 lines form a ~64x64 square at 90° angles
        - Ignore content inside (monsters, character, etc.)
        
        This ONLY detects the geometric outline pattern!
        Roses/pillars don't have 4 perfect straight lines at 90°.
        
        Returns (x, y) coordinates of target center, or None if not found
        """
        try:
            print(f"\n🔍 STRAIGHT LINE DETECTION (Outline-Only)")
            
            with mss.mss() as sct:
                # Capture screen
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                
                # Convert to BGR and HSV
                img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
                
                screen_width = monitor['width']
                screen_height = monitor['height']
                center_x = screen_width // 2
                center_y = screen_height // 2
                
                # STEP 1: DETECT RED PIXELS ONLY (using multi-profile calibration if available)
                if self.hsv_config and self.hsv_config.get('multi_profile', False):
                    # MULTI-PROFILE DETECTION: Test all 3 lighting profiles
                    print(f"   Using MULTI-PROFILE calibration (bright/medium/dark)")
                    profiles = self.hsv_config.get('profiles', {})
                    
                    masks = []
                    for profile_name in ['bright', 'medium', 'dark']:
                        if profile_name in profiles:
                            prof = profiles[profile_name]
                            # Dual range for red wraparound
                            lower_red_low = np.array([0, prof['lower_s'], prof['lower_v']])
                            upper_red_low = np.array([15, prof['upper_s'], prof['upper_v']])
                            mask_low = cv2.inRange(img_hsv, lower_red_low, upper_red_low)
                            
                            lower_red_high = np.array([165, prof['lower_s'], prof['lower_v']])
                            upper_red_high = np.array([179, prof['upper_s'], prof['upper_v']])
                            mask_high = cv2.inRange(img_hsv, lower_red_high, upper_red_high)
                            
                            profile_mask = cv2.bitwise_or(mask_low, mask_high)
                            masks.append(profile_mask)
                            print(f"     {profile_name}: S:{prof['lower_s']}-{prof['upper_s']}, V:{prof['lower_v']}-{prof['upper_v']}")
                    
                    # Combine all profile masks (ANY profile match = detected)
                    if masks:
                        red_mask = masks[0]
                        for m in masks[1:]:
                            red_mask = cv2.bitwise_or(red_mask, m)
                    else:
                        # Fallback to default if no profiles loaded
                        lower_red1 = np.array([0, 70, 70])
                        upper_red1 = np.array([12, 255, 255])
                        lower_red2 = np.array([168, 70, 70])
                        upper_red2 = np.array([180, 255, 255])
                        mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
                        mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)
                        red_mask = cv2.bitwise_or(mask1, mask2)
                else:
                    # Default red detection - VERY permissive for different lighting/distance
                    lower_red1 = np.array([0, 70, 70])  # Lower S,V for dim reds
                    upper_red1 = np.array([12, 255, 255])  # Wider H range
                    lower_red2 = np.array([168, 70, 70])  # Lower S,V for dim reds
                    upper_red2 = np.array([180, 255, 255])
                    
                    mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
                    mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)
                    red_mask = cv2.bitwise_or(mask1, mask2)
                    print(f"   Using default HSV ranges")
                
                # STEP 2: FIND CONTOURS in red pixels ONLY
                contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                print(f"   Found {len(contours)} red contours")
                
                candidates = []
                debug_count = 0
                debug_rejects = []
                
                for c in contours:
                    # Bounding box
                    x, y, w, h = cv2.boundingRect(c)
                    
                    # FILTER 1: SIZE - Attack outline is 64x64px (stricter: 58-72px)
                    if not (58 <= w <= 72 and 58 <= h <= 72):
                        debug_count += 1
                        if debug_count <= 5:
                            debug_rejects.append(f"Size: {w}x{h} (need 58-72)")
                        continue
                    
                    # FILTER 2: SQUARE aspect ratio (stricter: 0.85-1.18 for more square shapes)
                    aspect = w / h if h > 0 else 0
                    if not (0.85 <= aspect <= 1.18):
                        debug_count += 1
                        if debug_count <= 5:
                            debug_rejects.append(f"Aspect: {aspect:.2f} (need 0.85-1.18)")
                        continue
                    
                    # FILTER 3: Must be HOLLOW (check center vs border red ratio)
                    roi_red = red_mask[y:y+h, x:x+w]
                    
                    # Border pixels
                    border_width = max(2, min(w, h) // 8)
                    border_mask = np.zeros_like(roi_red)
                    border_mask[:border_width, :] = 255
                    border_mask[-border_width:, :] = 255
                    border_mask[:, :border_width] = 255
                    border_mask[:, -border_width:] = 255
                    
                    border_red = cv2.bitwise_and(roi_red, border_mask)
                    border_ratio = cv2.countNonZero(border_red) / cv2.countNonZero(border_mask) if cv2.countNonZero(border_mask) > 0 else 0
                    
                    # Center pixels
                    margin = max(border_width + 2, min(w, h) // 4)
                    if w > margin * 2 and h > margin * 2:
                        center_red = roi_red[margin:-margin, margin:-margin]
                        center_ratio = cv2.countNonZero(center_red) / center_red.size if center_red.size > 0 else 0
                    else:
                        center_ratio = 0.0
                    
                    # Must have red border (>12%) and hollow center (<50%) - STRICTER!
                    if not (border_ratio > 0.12 and center_ratio < 0.50):
                        debug_count += 1
                        if debug_count <= 5:
                            debug_rejects.append(f"Hollow: border={border_ratio:.0%} (need >12%), center={center_ratio:.0%} (need <50%)")
                        continue
                    
                    # FILTER 4: Proximity to center (game area, not UI)
                    cx = x + w // 2
                    cy = y + h // 2
                    distance = ((cx - center_x)**2 + (cy - center_y)**2)**0.5
                    
                    # Exclude far edges (battle list, taskbar) - 75% coverage for wider detection
                    max_dist = min(screen_width, screen_height) * 0.75
                    if distance > max_dist:
                        continue
                    
                    # Calculate PATTERN score
                    size_score = 1.0 - abs(((w + h) / 2) - 64) / 64  # Closer to 64px = better
                    square_score = 1.0 - abs(aspect - 1.0)  # Closer to perfect square = better
                    hollow_score = border_ratio / max(center_ratio, 0.01)  # High ratio = more hollow
                    hollow_score = min(hollow_score / 4.0, 1.0)  # Normalize
                    proximity_score = 1.0 - (distance / max_dist)
                    
                    score = (hollow_score * 0.40 +        # 40%: hollow is KEY feature
                             proximity_score * 0.30 +     # 30%: central location
                             size_score * 0.20 +          # 20%: right size
                             square_score * 0.10)         # 10%: square shape
                    
                    candidates.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'center_x': cx, 'center_y': cy,
                        'border_ratio': border_ratio,
                        'center_ratio': center_ratio,
                        'distance': distance,
                        'score': score
                    })
                
                if not candidates:
                    print(f"   ❌ No hollow squares found (checked {debug_count} contours)")
                    if debug_rejects:
                        print(f"   Sample rejects: {debug_rejects[:5]}")
                    return None
                
                # Sort by score (best pattern first)
                candidates.sort(key=lambda c: c['score'], reverse=True)
                
                print(f"   Found {len(candidates)} hollow square candidates:")
                for i, c in enumerate(candidates[:3]):
                    print(f"      {i+1}. Pos({c['x']},{c['y']}), Size:{c['w']}x{c['h']}, "
                          f"Border:{c['border_ratio']:.0%}, Center:{c['center_ratio']:.0%}, "
                          f"Dist:{c['distance']:.0f}px, Score:{c['score']:.3f}")
                
                # Pick best if score is good enough (STRICTER threshold to avoid false positives)
                best = candidates[0]
                if best['score'] >= 0.45:  # Higher threshold = more selective (avoids pillars/roses)
                    screen_x = monitor['left'] + best['center_x']
                    screen_y = monitor['top'] + best['center_y']
                    
                    print(f"   ✅ OUTLINE FOUND at ({screen_x}, {screen_y})")
                    print(f"      Size: {best['w']}x{best['h']}, Score: {best['score']:.3f}")
                    return (screen_x, screen_y)
                else:
                    print(f"   ⚠️ Best score too low: {best['score']:.3f} < 0.45")
                    if debug_rejects:
                        print(f"   Rejected reasons: {debug_rejects[:3]}")
                    return None
                
        except Exception as e:
            print(f"❌ Error detecting target: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def detect_red_target_fallback(self):
        """Fallback detection if template not available"""
        print(f"   ⚠️ Using fallback detection (calibration-based)")
        
        # Simple fallback - just return None for now
        # Could implement basic HSV detection here if needed
        return None
    
    def execute_clicks(self, hotkey_config):
        """Execute the click sequence for a hotkey"""
        try:
            clicks = hotkey_config['clicks']
            hk_type = hotkey_config.get('type', 'normal')
            
            if hk_type == 'offensive':
                # NEW SIMPLIFIED MODE: Save mouse position → Click rune → Return to position → Click target
                # Get CURRENT mouse position (where user is hovering over target)
                current_pos = pyautogui.position()
                target_x, target_y = current_pos.x, current_pos.y
                print(f"🎯 Target position saved: ({target_x}, {target_y})")
                
                # Step 1: Click on rune (right-click)
                x1, y1 = clicks[0]['x'], clicks[0]['y']
                print(f"🎯 Moving to rune at ({x1}, {y1})...")
                
                if self.instant_movement.get():
                    # INSTANT mode (teleport)
                    pyautogui.moveTo(x1, y1, duration=0)
                else:
                    # HUMANIZED mode (gradual)
                    move_duration = random.uniform(0.08, 0.12)
                    pyautogui.moveTo(x1, y1, duration=move_duration)
                    time.sleep(random.uniform(0.02, 0.04))
                
                print(f"🎯 Right-clicking rune...")
                pyautogui.click(x1, y1, button='right')
                
                if not self.instant_movement.get():
                    time.sleep(random.uniform(0.05, 0.08))
                print(f"✅ Right-clicked rune")
                
                # Step 2: Return mouse to original target position
                print(f"🎯 Returning to target at ({target_x}, {target_y})...")
                
                if self.instant_movement.get():
                    # INSTANT mode
                    pyautogui.moveTo(target_x, target_y, duration=0)
                else:
                    # HUMANIZED mode
                    move_duration = random.uniform(0.06, 0.10)
                    pyautogui.moveTo(target_x, target_y, duration=move_duration)
                    time.sleep(random.uniform(0.02, 0.03))
                
                # Step 3: Left-click on target (instant attack!)
                print(f"🎯 Left-clicking target...")
                pyautogui.click(target_x, target_y, button='left')
                print(f"✅ Attack executed at ({target_x}, {target_y})!")
                
            else:
                # Normal: Right-click on item, then left-click on character - HUMANIZED
                delay = hotkey_config['delay'] / 1000.0
                return_to_position = hotkey_config.get('return_to_position', False)
                
                # Save original position if return_to_position is enabled
                original_x, original_y = None, None
                if return_to_position:
                    original_x, original_y = pyautogui.position()
                    print(f"🎯 Custom Hotkey: Saved original position ({original_x}, {original_y})")
                
                # First click - RIGHT CLICK on item position
                x1, y1 = clicks[0]['x'], clicks[0]['y']
                
                if self.instant_movement.get():
                    pyautogui.moveTo(x1, y1, duration=0)
                else:
                    move_duration = random.uniform(0.05, 0.08)
                    pyautogui.moveTo(x1, y1, duration=move_duration)
                    time.sleep(random.uniform(0.01, 0.03))
                
                pyautogui.rightClick(x1, y1)
                
                # Delay between clicks
                if self.instant_movement.get():
                    time.sleep(delay)
                else:
                    actual_delay = delay + random.uniform(-0.01, 0.01)
                    time.sleep(max(0.01, actual_delay))
                
                # Second click - LEFT CLICK on character position
                x2, y2 = clicks[1]['x'], clicks[1]['y']
                
                if self.instant_movement.get():
                    pyautogui.moveTo(x2, y2, duration=0)
                else:
                    move_duration = random.uniform(0.05, 0.08)
                    pyautogui.moveTo(x2, y2, duration=move_duration)
                    time.sleep(random.uniform(0.01, 0.03))
                
                pyautogui.leftClick(x2, y2)
                
                # Return to original position if enabled
                if return_to_position and original_x is not None:
                    if self.instant_movement.get():
                        pyautogui.moveTo(original_x, original_y, duration=0)
                    else:
                        time.sleep(random.uniform(0.02, 0.05))
                        pyautogui.moveTo(original_x, original_y, duration=random.uniform(0.04, 0.08))
                    print(f"🔙 Custom Hotkey: Returned to ({original_x}, {original_y})")
            
        except Exception as e:
            print(f"Error executing clicks: {e}")
    
    def execute_quick_sd(self):
        """Execute Auto SD - Simplified mode: save position → click rune → return → attack"""
        try:
            quick_configs = self.config.get('quick_configs', {})
            sd_config = quick_configs.get('auto_sd', {})
            
            clicks = sd_config.get('clicks', [])
            if not clicks:
                print("⚠️ Auto SD: Posições não gravadas! Use 'Gravar' primeiro.")
                return
            
            # SIMPLIFIED MODE: Save position → Click rune → Return → Attack
            current_pos = pyautogui.position()
            target_x, target_y = current_pos.x, current_pos.y
            print(f"🎯 Auto SD: Target position saved: ({target_x}, {target_y})")
            
            # Click on SD rune (right-click)
            x1, y1 = clicks[0]['x'], clicks[0]['y']
            print(f"⚔️ Auto SD: Moving to rune at ({x1}, {y1})...")
            
            if self.instant_movement.get():
                pyautogui.moveTo(x1, y1, duration=0)
            else:
                move_duration = random.uniform(0.08, 0.12)
                pyautogui.moveTo(x1, y1, duration=move_duration)
                time.sleep(random.uniform(0.02, 0.04))
            
            pyautogui.click(x1, y1, button='right')
            
            if not self.instant_movement.get():
                time.sleep(random.uniform(0.05, 0.08))
            print(f"✅ Auto SD: Right-clicked rune")
            
            # Return mouse to original target position
            print(f"🎯 Auto SD: Returning to target at ({target_x}, {target_y})...")
            
            if self.instant_movement.get():
                pyautogui.moveTo(target_x, target_y, duration=0)
            else:
                move_duration = random.uniform(0.06, 0.10)
                pyautogui.moveTo(target_x, target_y, duration=move_duration)
                time.sleep(random.uniform(0.02, 0.03))
            
            # Left-click on target (instant attack!)
            print(f"⚔️ Auto SD: Left-clicking target...")
            pyautogui.click(target_x, target_y, button='left')
            print(f"✅ Auto SD: Attack executed at ({target_x}, {target_y})!")
                
        except Exception as e:
            print(f"❌ Auto SD error: {e}")
    
    def execute_quick_explo(self):
        """Execute Auto EXPLO quick config (duplicate of Auto SD)"""
        try:
            quick_configs = self.config.get('quick_configs', {})
            explo_config = quick_configs.get('auto_explo', {})
            
            clicks = explo_config.get('clicks', [])
            if not clicks:
                print("⚠️ Auto EXPLO: Posições não gravadas! Use 'Gravar' primeiro.")
                return
            
            # SIMPLIFIED MODE: Save position → Click rune → Return → Attack
            current_pos = pyautogui.position()
            target_x, target_y = current_pos.x, current_pos.y
            print(f"🎯 Auto EXPLO: Target position saved: ({target_x}, {target_y})")
            
            # Click on EXPLO rune (right-click)
            x1, y1 = clicks[0]['x'], clicks[0]['y']
            print(f"💥 Auto EXPLO: Moving to rune at ({x1}, {y1})...")
            
            if self.instant_movement.get():
                pyautogui.moveTo(x1, y1, duration=0)
            else:
                move_duration = random.uniform(0.08, 0.12)
                pyautogui.moveTo(x1, y1, duration=move_duration)
                time.sleep(random.uniform(0.02, 0.04))
            
            pyautogui.click(x1, y1, button='right')
            
            if not self.instant_movement.get():
                time.sleep(random.uniform(0.05, 0.08))
            print(f"✅ Auto EXPLO: Right-clicked rune")
            
            # Return mouse to original target position
            print(f"🎯 Auto EXPLO: Returning to target at ({target_x}, {target_y})...")
            
            if self.instant_movement.get():
                pyautogui.moveTo(target_x, target_y, duration=0)
            else:
                move_duration = random.uniform(0.06, 0.10)
                pyautogui.moveTo(target_x, target_y, duration=move_duration)
                time.sleep(random.uniform(0.02, 0.03))
            
            # Left-click on target (instant attack!)
            print(f"💥 Auto EXPLO: Left-clicking target...")
            pyautogui.click(target_x, target_y, button='left')
            print(f"✅ Auto EXPLO: Attack executed at ({target_x}, {target_y})!")
                
        except Exception as e:
            print(f"❌ Auto EXPLO error: {e}")
    
    def execute_quick_uh(self):
        """Execute Auto UH quick config - returns mouse to original position"""
        try:
            # Save original mouse position FIRST
            original_x, original_y = pyautogui.position()
            print(f"🎯 Auto UH: Saved original position ({original_x}, {original_y})")
            
            quick_configs = self.config.get('quick_configs', {})
            uh_config = quick_configs.get('auto_uh', {})
            
            clicks = uh_config.get('clicks', [])
            if len(clicks) < 2:
                print("⚠️ Auto UH: Posições não gravadas! Use 'Gravar' primeiro.")
                return
            
            delay = uh_config.get('delay', 100) / 1000.0
            
            # Right-click on UH rune
            x1, y1 = clicks[0]['x'], clicks[0]['y']
            if self.instant_movement.get():
                pyautogui.moveTo(x1, y1, duration=0)
            else:
                pyautogui.moveTo(x1, y1, duration=random.uniform(0.04, 0.08))
                time.sleep(random.uniform(0.01, 0.03))
            pyautogui.rightClick(x1, y1)
            print(f"⚕️ Auto UH: Right-clicked rune at ({x1}, {y1})")
            
            # Delay
            time.sleep(delay)
            
            # Left-click on character
            x2, y2 = clicks[1]['x'], clicks[1]['y']
            if self.instant_movement.get():
                pyautogui.moveTo(x2, y2, duration=0)
            else:
                pyautogui.moveTo(x2, y2, duration=random.uniform(0.04, 0.08))
                time.sleep(random.uniform(0.01, 0.03))
            pyautogui.leftClick(x2, y2)
            print(f"✅ Auto UH: Clicked character at ({x2}, {y2})")
            
            # Return mouse to original position
            if self.instant_movement.get():
                pyautogui.moveTo(original_x, original_y, duration=0)
            else:
                time.sleep(random.uniform(0.02, 0.05))
                pyautogui.moveTo(original_x, original_y, duration=random.uniform(0.04, 0.08))
            print(f"🔙 Auto UH: Returned to ({original_x}, {original_y})")
            
        except Exception as e:
            print(f"❌ Auto UH error: {e}")
    
    def execute_quick_mana(self):
        """Execute Auto MANA quick config - returns mouse to original position"""
        try:
            # Save original mouse position FIRST
            original_x, original_y = pyautogui.position()
            print(f"🎯 Auto Mana: Saved original position ({original_x}, {original_y})")
            
            quick_configs = self.config.get('quick_configs', {})
            mana_config = quick_configs.get('auto_mana', {})
            
            clicks = mana_config.get('clicks', [])
            if len(clicks) < 2:
                print(f"⚠️ Auto Mana: Posições não gravadas! Use 'Gravar' primeiro.")
                return
            
            delay = mana_config.get('delay', 100) / 1000.0
            
            # Right-click on MANA potion
            x1, y1 = clicks[0]['x'], clicks[0]['y']
            if self.instant_movement.get():
                pyautogui.moveTo(x1, y1, duration=0)
            else:
                pyautogui.moveTo(x1, y1, duration=random.uniform(0.04, 0.08))
                time.sleep(random.uniform(0.01, 0.03))
            pyautogui.rightClick(x1, y1)
            print(f"💙 Auto Mana: Right-clicked potion at ({x1}, {y1})")
            
            # Delay
            time.sleep(delay)
            
            # Left-click on character
            x2, y2 = clicks[1]['x'], clicks[1]['y']
            if self.instant_movement.get():
                pyautogui.moveTo(x2, y2, duration=0)
            else:
                pyautogui.moveTo(x2, y2, duration=random.uniform(0.04, 0.08))
                time.sleep(random.uniform(0.01, 0.03))
            pyautogui.leftClick(x2, y2)
            print(f"✅ Auto Mana: Clicked character at ({x2}, {y2})")
            
            # Return mouse to original position
            if self.instant_movement.get():
                pyautogui.moveTo(original_x, original_y, duration=0)
            else:
                time.sleep(random.uniform(0.02, 0.05))
                pyautogui.moveTo(original_x, original_y, duration=random.uniform(0.04, 0.08))
            print(f"🔙 Auto Mana: Returned to ({original_x}, {original_y})")
            
        except Exception as e:
            print(f"❌ Auto Mana error: {e}")
    
    def save_current_profile(self):
        """Save current state to the active profile"""
        if not hasattr(self, 'current_profile'):
            return
        
        profile_name = self.current_profile.get()
        
        # Capture current state
        current_state = {
            'hotkeys': self.hotkeys.copy(),
            'quick_configs': self.config.get('quick_configs', {}).copy(),
            'instant_movement': self.instant_movement.get()
        }
        
        # Save to profiles dict
        if 'profiles' not in self.config:
            self.config['profiles'] = {}
        
        self.config['profiles'][profile_name] = current_state
        self.config['current_profile'] = profile_name
        
        print(f"✅ Perfil '{profile_name}' salvo!")
    
    def save_config(self):
        """Save all profiles and config to JSON file"""
        try:
            # Save current state to active profile first (if UI is ready)
            if hasattr(self, 'current_profile'):
                self.save_current_profile()
            
            # Preserve HSV calibration
            if not hasattr(self, 'hsv_config'):
                self.hsv_config = {}
            
            # Reload HSV from file if needed
            if 'profiles' not in self.hsv_config:
                try:
                    if os.path.exists(self.config_file):
                        with open(self.config_file, 'r') as f:
                            existing = json.load(f)
                            if 'profiles' in existing.get('hsv_config', {}):
                                self.hsv_config['profiles'] = existing['hsv_config']['profiles']
                                self.hsv_config['calibrated'] = existing['hsv_config'].get('calibrated', True)
                                self.hsv_config['multi_profile'] = existing['hsv_config'].get('multi_profile', True)
                except:
                    pass
            
            # Build complete config
            save_data = {
                'current_profile': self.current_profile.get(),
                'profiles': self.config.get('profiles', {}),
                'hsv_config': self.hsv_config
            }
            
            # DEBUG: Log what's being saved
            if 'profiles' in self.hsv_config:
                print(f"[SAVE] Salvando HSV config com PERFIS: {list(self.hsv_config['profiles'].keys())}")
            else:
                print(f"[SAVE] Salvando HSV config SEM perfis (calibrated={self.hsv_config.get('calibrated', False)})")
            
            with open(self.config_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"[SAVE] ✅ Config salvo: {len(self.config.get('profiles', {}))} perfis")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            import traceback
            traceback.print_exc()
    
    def load_config(self):
        """Load profiles and config from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_data = json.load(f)
                    print(f"[LOAD] Config carregado do arquivo")
                    
                # Handle old format (dict with hotkeys + hsv_config + quick_configs)
                if 'profiles' not in loaded_data and 'hotkeys' in loaded_data:
                    # Convert old format to new profile format
                    print("[LOAD] Convertendo formato antigo para perfis...")
                    default_profile = {
                        'hotkeys': loaded_data.get('hotkeys', []),
                        'quick_configs': loaded_data.get('quick_configs', {}),
                        'instant_movement': False
                    }
                    self.config = {
                        'current_profile': 'Padrão',
                        'profiles': {'Padrão': default_profile},
                        'hsv_config': loaded_data.get('hsv_config', {})
                    }
                    self.save_config()  # Save in new format
                else:
                    # New format with profiles
                    self.config = loaded_data
                
                # Load HSV config
                loaded_hsv = self.config.get('hsv_config', None)
                if loaded_hsv:
                    self.hsv_config = loaded_hsv
                        
                
                # Load current profile
                profile_name = self.config.get('current_profile', 'Padrão')
                if profile_name not in self.config.get('profiles', {}):
                    profile_name = 'Padrão'
                
                self.load_profile(profile_name, update_dropdown=False)
                
                print(f"[LOAD] ✅ Perfil '{profile_name}' carregado")
            else:
                # Create default profile
                self.config = {
                    'current_profile': 'Padrão',
                    'profiles': {
                        'Padrão': {
                            'hotkeys': [],
                            'quick_configs': {},
                            'instant_movement': False
                        }
                    },
                    'hsv_config': {}
                }
                self.hotkeys = []
        except Exception as e:
            print(f"Error loading config: {e}")
            import traceback
            traceback.print_exc()
            self.hotkeys = []
            self.config = {'hotkeys': [], 'quick_configs': {}}
    
    def load_profile(self, profile_name, update_dropdown=True):
        """Load a specific profile"""
        profiles = self.config.get('profiles', {})
        if profile_name not in profiles:
            print(f"⚠️ Perfil '{profile_name}' não encontrado!")
            return
        
        profile = profiles[profile_name]
        
        # Load profile data
        self.hotkeys = profile.get('hotkeys', []).copy()
        
        # Load quick configs
        quick_configs = profile.get('quick_configs', {})
        if not hasattr(self, 'config'):
            self.config = {}
        self.config['quick_configs'] = quick_configs
        
        # Update UI with quick configs
        for key in ['auto_sd', 'auto_explo', 'auto_uh', 'auto_mana']:
            if key in quick_configs:
                qc = quick_configs[key]
                # Update delays
                if key == 'auto_sd' and hasattr(self, 'auto_sd_delay'):
                    self.auto_sd_delay.set(qc.get('delay', 100))
                elif key == 'auto_explo' and hasattr(self, 'auto_explo_delay'):
                    self.auto_explo_delay.set(qc.get('delay', 100))
                elif key == 'auto_uh' and hasattr(self, 'auto_uh_delay'):
                    self.auto_uh_delay.set(qc.get('delay', 100))
                elif key == 'auto_mana' and hasattr(self, 'auto_mana_delay'):
                    self.auto_mana_delay.set(qc.get('delay', 100))
        
        # Load instant movement setting
        if hasattr(self, 'instant_movement'):
            self.instant_movement.set(profile.get('instant_movement', False))
        
        # Update hotkey list
        if hasattr(self, 'tree'):
            self.refresh_tree()
        
        # Update dropdown if needed
        if update_dropdown and hasattr(self, 'current_profile'):
            self.current_profile.set(profile_name)
        
        print(f"✅ Perfil '{profile_name}' carregado!")
    
    def switch_profile(self):
        """Switch to selected profile"""
        # Save current profile first
        self.save_current_profile()
        
        # Load new profile
        new_profile = self.current_profile.get()
        self.load_profile(new_profile, update_dropdown=False)
    
    def create_profile(self):
        """Create a new profile"""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Perfil")
        dialog.geometry("400x150")
        dialog.configure(bg=self.colors['bg_secondary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Nome do novo perfil:", bg=self.colors['bg_secondary'],
                fg=self.colors['text_header'], font=('Georgia', 11)).pack(pady=10)
        
        name_entry = tk.Entry(dialog, font=('Georgia', 11), width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Erro", "Nome não pode estar vazio!")
                return
            
            if name in self.config.get('profiles', {}):
                messagebox.showerror("Erro", f"Perfil '{name}' já existe!")
                return
            
            # Create new profile (copy of current)
            if 'profiles' not in self.config:
                self.config['profiles'] = {}
            
            self.config['profiles'][name] = {
                'hotkeys': self.hotkeys.copy(),
                'quick_configs': self.config.get('quick_configs', {}).copy(),
                'instant_movement': self.instant_movement.get()
            }
            
            # Update dropdown
            self.profile_dropdown['values'] = list(self.config['profiles'].keys())
            self.current_profile.set(name)
            
            # Save and load
            self.save_config()
            
            messagebox.showinfo("Sucesso", f"Perfil '{name}' criado!")
            dialog.destroy()
        
        tk.Button(dialog, text="Criar", command=create, bg=self.colors['button_default'],
                 fg=self.colors['text_header'], font=('Georgia', 10, 'bold'),
                 padx=20, pady=5).pack(pady=10)
    
    def rename_profile(self):
        """Rename current profile"""
        old_name = self.current_profile.get()
        
        if old_name == "Padrão":
            messagebox.showwarning("Aviso", "Não é possível renomear o perfil 'Padrão'!")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Renomear Perfil")
        dialog.geometry("400x150")
        dialog.configure(bg=self.colors['bg_secondary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Novo nome para '{old_name}':", bg=self.colors['bg_secondary'],
                fg=self.colors['text_header'], font=('Georgia', 11)).pack(pady=10)
        
        name_entry = tk.Entry(dialog, font=('Georgia', 11), width=30)
        name_entry.insert(0, old_name)
        name_entry.pack(pady=5)
        name_entry.focus()
        name_entry.select_range(0, tk.END)
        
        def rename():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Erro", "Nome não pode estar vazio!")
                return
            
            if new_name in self.config.get('profiles', {}) and new_name != old_name:
                messagebox.showerror("Erro", f"Perfil '{new_name}' já existe!")
                return
            
            # Rename profile
            profiles = self.config.get('profiles', {})
            profiles[new_name] = profiles.pop(old_name)
            
            # Update dropdown and current selection
            self.profile_dropdown['values'] = list(profiles.keys())
            self.current_profile.set(new_name)
            self.config['current_profile'] = new_name
            
            # Save
            self.save_config()
            
            messagebox.showinfo("Sucesso", f"Perfil renomeado para '{new_name}'!")
            dialog.destroy()
        
        tk.Button(dialog, text="Renomear", command=rename, bg=self.colors['button_default'],
                 fg=self.colors['text_header'], font=('Georgia', 10, 'bold'),
                 padx=20, pady=5).pack(pady=10)
    
    def delete_profile(self):
        """Delete current profile"""
        profile_name = self.current_profile.get()
        
        if profile_name == "Padrão":
            messagebox.showwarning("Aviso", "Não é possível deletar o perfil 'Padrão'!")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirmar", f"Deletar perfil '{profile_name}'?"):
            return
        
        # Delete profile
        profiles = self.config.get('profiles', {})
        if profile_name in profiles:
            del profiles[profile_name]
        
        # Switch to default profile
        self.profile_dropdown['values'] = list(profiles.keys())
        self.current_profile.set("Padrão")
        self.load_profile("Padrão")
        
        # Save
        self.save_config()
        
        messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' deletado!")

def main():
    root = tk.Tk()
    app = AudioBook(root)
    root.mainloop()

if __name__ == "__main__":
    main()
