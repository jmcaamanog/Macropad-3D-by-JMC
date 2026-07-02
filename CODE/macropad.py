# -*- coding: utf-8 -*-
"""
       ██╗███╗   ███╗ ██████╗
       ██║████╗ ████║██╔════╝
       ██║██╔████╔██║██║
  ██   ██║██║╚██╔╝██║██║    
  █████╔╝ ██║ ╚═╝ ██║╚██████╗
  ╚════╝  ╚═╝     ╚═╝ ╚═════╝
---------------------------------------------------------------------------
 Configurador de Macropad JMC - Versión 6.2 (Interfaz Limpia)
---------------------------------------------------------------------------
 Descripción:
 Versión de mantenimiento centrada en limpiar y simplificar la interfaz
 de la pestaña de Configuración para un aspecto más minimalista y directo.

 Mejoras Clave en v6.2:
  - **Eliminación de Títulos**: Se han eliminado las etiquetas de sección
    superfluas ("Configuración de Botones", "Gestión de Perfiles", etc.).
  - **Simplificación de Etiquetas**: "Perfil Actual" se ha cambiado por
    "PERFIL" y los botones ahora se numeran (1, 2, 3...) con una fuente
    más grande para mayor claridad.
  - **Rediseño Visual**: La pestaña de configuración ahora tiene un look
    más moderno y menos cargado.
---------------------------------------------------------------------------
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import json
import os
import sys
import webbrowser
import re

# --- Dependencias Opcionales ---
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    messagebox.showerror("Error de Librería Crítica", "La librería 'pynput' es esencial. Por favor, instálala ejecutando: pip install pynput")
    PYNPUT_AVAILABLE = False
    sys.exit()

try:
    import obswebsocket, obswebsocket.requests
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False


# --- Configuración Global ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Constantes y Mapeos ---
CONFIG_DIR = "configs"
PRESS_TYPES = ["CORTA", "LARGA", "DOBLE"]

SPECIAL_KEYS_MAP = {
    "F1": keyboard.Key.f1, "F2": keyboard.Key.f2, "F3": keyboard.Key.f3, "F4": keyboard.Key.f4, "F5": keyboard.Key.f5, "F6": keyboard.Key.f6, "F7": keyboard.Key.f7, "F8": keyboard.Key.f8, "F9": keyboard.Key.f9, "F10": keyboard.Key.f10, "F11": keyboard.Key.f11, "F12": keyboard.Key.f12,
    "CTRL": keyboard.Key.ctrl, "ALT": keyboard.Key.alt, "SHIFT": keyboard.Key.shift, "CMD": keyboard.Key.cmd,
    "ESC": keyboard.Key.esc, "TAB": keyboard.Key.tab, "CAPSLOCK": keyboard.Key.caps_lock, "ENTER": keyboard.Key.enter,
    "SPACE": keyboard.Key.space, "BACKSPACE": keyboard.Key.backspace, "INSERT": keyboard.Key.insert, "DELETE": keyboard.Key.delete,
    "HOME": keyboard.Key.home, "END": keyboard.Key.end, "PAGEUP": keyboard.Key.page_up, "PAGEDOWN": keyboard.Key.page_down,
    "UP": keyboard.Key.up, "DOWN": keyboard.Key.down, "LEFT": keyboard.Key.left, "RIGHT": keyboard.Key.right,
    "MUTE": keyboard.Key.media_volume_mute, "VOL_DOWN": keyboard.Key.media_volume_down, "VOL_UP": keyboard.Key.media_volume_up,
    "MEDIA_PLAY": keyboard.Key.media_play_pause, "MEDIA_PREV": keyboard.Key.media_previous, "MEDIA_NEXT": keyboard.Key.media_next
}

REVERSE_SPECIAL_KEYS_MAP = {v: k for k, v in SPECIAL_KEYS_MAP.items()}
MODIFIER_KEYS_SET = {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.cmd}

PREDEFINED_MACROS = {
    "COPIAR": (keyboard.Key.ctrl, 'c'), "PEGAR": (keyboard.Key.ctrl, 'v'), "CORTAR": (keyboard.Key.ctrl, 'x'), "DESHACER": (keyboard.Key.ctrl, 'z'),
    "GUARDAR": (keyboard.Key.ctrl, 's'), "CERRAR_VENTANA": (keyboard.Key.alt, keyboard.Key.f4),
    "CALCULADORA": {"type": "run", "command": "calc"}, "NOTEPAD": {"type": "run", "command": "notepad"}
}

class Tooltip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget; self.text = text; self.delay = delay
        self.tooltip_window = None; self.id = None
        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.schedule_hide)
    def schedule_show(self, event=None): self.id = self.widget.after(self.delay, self.show_tooltip)
    def schedule_hide(self, event=None):
        if self.id: self.widget.after_cancel(self.id); self.id = None
        if self.tooltip_window: self.tooltip_window.destroy(); self.tooltip_window = None
    def show_tooltip(self):
        if self.tooltip_window: return
        x = self.widget.winfo_rootx(); y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = ctk.CTkToplevel(self.widget); self.tooltip_window.wm_overrideredirect(True); self.tooltip_window.wm_geometry(f"+{x}+{y}")
        ctk.CTkLabel(self.tooltip_window, text=self.text, font=("Poppins", 10), fg_color="#1F1F1F", text_color="white", corner_radius=4, padx=8, pady=4).pack()

class FadingToplevel(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.alpha = 0.0; self.attributes("-alpha", self.alpha); self.fade_in()
    def fade_in(self):
        if self.alpha < 1.0: self.alpha += 0.05; self.attributes("-alpha", self.alpha); self.after(15, self.fade_in)
    def close_with_fade(self): self.fade_out()
    def fade_out(self):
        if self.alpha > 0.0: self.alpha -= 0.05; self.attributes("-alpha", self.alpha); self.after(15, self.fade_out)
        else: self.destroy()

class MacropadApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MACROpad by JMC")
        self.icon_path = self._get_asset_path('app_icon.ico')
        if self.icon_path and os.path.exists(self.icon_path): self.iconbitmap(self.icon_path)
        window_width, window_height = 900, 850
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{window_width}x{window_height}+{int(screen_width/2 - window_width/2)}+{int(screen_height/2 - window_height/2)}')
        self.resizable(False, False)
        self.arduino, self.listening_thread, self.is_listening = None, None, False
        self.keyboard_controller = keyboard.Controller()
        self.button_mappings, self.button_entries, self.button_frames = {}, {}, {}
        self.current_profile_name = ctk.StringVar(value="(Vacío)")
        self._define_fonts()
        self._create_icons()
        self.log_textbox = None
        self._create_ui()
        self._ensure_config_directory_exists()
        self.load_profiles()
        self.load_config_on_startup()
        self.update_entries_from_mappings()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(100, self.show_welcome_assistant_if_needed)
        self._log_message("Aplicación iniciada. Versión 6.2.", "info")

    def _get_asset_path(self, asset_name):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, asset_name)
        except Exception: return None

    def _define_fonts(self):
        self.font_small=ctk.CTkFont(family="Poppins",size=10);self.font_normal=ctk.CTkFont(family="Poppins",size=11);self.font_bold=ctk.CTkFont(family="Poppins",size=11,weight="bold");self.font_title=ctk.CTkFont(family="Poppins",size=12,weight="bold");self.font_subtitle=ctk.CTkFont(family="Poppins",size=14);self.font_header=ctk.CTkFont(family="Poppins",size=28,weight="bold");self.font_jmc=ctk.CTkFont(family="Poppins",size=18,weight="bold");self.font_name_bold=ctk.CTkFont(family="Poppins",size=14,weight="bold");self.font_about_text=ctk.CTkFont(family="Poppins",size=12);self.font_author=ctk.CTkFont(family="Poppins",size=13,weight="bold")

    def _create_icons(self):
        if not PILLOW_AVAILABLE: self.arrow_down_icon=self.icon_corta=self.icon_larga=self.icon_doble=None; return
        try:
            arrow_img=Image.new('RGBA',(20,20),(0,0,0,0));ImageDraw.Draw(arrow_img).polygon([(5,7),(15,7),(10,14)],fill=(200,200,200));self.arrow_down_icon=ctk.CTkImage(light_image=arrow_img,dark_image=arrow_img,size=(12,12))
            corta_img=Image.new('RGBA',(20,20),(0,0,0,0));ImageDraw.Draw(corta_img).ellipse((7,7,13,13),fill=(200,200,200));self.icon_corta=ctk.CTkImage(light_image=corta_img,dark_image=corta_img,size=(12,12))
            larga_img=Image.new('RGBA',(20,20),(0,0,0,0));ImageDraw.Draw(larga_img).rectangle((5,9,15,11),fill=(200,200,200));self.icon_larga=ctk.CTkImage(light_image=larga_img,dark_image=larga_img,size=(12,12))
            doble_img=Image.new('RGBA',(20,20),(0,0,0,0));ImageDraw.Draw(doble_img).ellipse((4,7,10,13),fill=(200,200,200));ImageDraw.Draw(doble_img).ellipse((11,7,17,13),fill=(200,200,200));self.icon_doble=ctk.CTkImage(light_image=doble_img,dark_image=doble_img,size=(12,12))
        except Exception as e: self._log_message(f"Error al crear iconos: {e}", "error")

    def _prepare_dropdown_data(self):
        data=[{"type":"header","text":"TECLAS ESPECIALES"}];data.extend([{"type":"item","name":k} for k in sorted(SPECIAL_KEYS_MAP.keys())]);data.append({"type":"header","text":"MACROS PREDEFINIDAS"});data.extend([{"type":"item","name":k} for k in sorted(PREDEFINED_MACROS.keys())])
        if 'custom_sequences' in self.button_mappings and self.button_mappings['custom_sequences']:
            data.append({"type": "header", "text": "MACROS PERSONALIZADAS"})
            data.extend([{"type": "item", "name": k} for k in sorted(self.button_mappings['custom_sequences'].keys())])
        return data

    def _create_ui(self):
        self.tabview = ctk.CTkTabview(self, width=860, height=680); self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        self._create_configuracion_tab(self.tabview.add("CONFIGURACIÓN"))
        self._create_sequence_builder_tab(self.tabview.add("CREADOR DE SECUENCIAS"))
        self._create_macros_tab(self.tabview.add("MACROS PREDEFINIDAS"))
        self._create_integrations_tab(self.tabview.add("INTEGRACIONES"))
        self._create_logs_tab(self.tabview.add("LOGS"))
        self._create_about_tab(self.tabview.add("ACERCA DE"))
        self.status_bar = ctk.CTkLabel(self, text="Listo.", font=self.font_bold, fg_color=("gray75", "gray25"), text_color=("black", "white"), height=25, corner_radius=0); self.status_bar.pack(side="bottom", fill="x")

    def _create_configuracion_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        # --- Frame de Conexión ---
        conn_frame = ctk.CTkFrame(tab); conn_frame.pack(padx=10, pady=10, fill="x")
        self.com_port_var = ctk.StringVar()
        self.com_port_combobox = ctk.CTkComboBox(conn_frame, variable=self.com_port_var, width=150, state="readonly", values=[], font=self.font_normal); self.com_port_combobox.pack(side="left", padx=5)
        self.refresh_ports_button = ctk.CTkButton(conn_frame, text="Refrescar Puertos", command=self.populate_com_ports, font=self.font_normal); self.refresh_ports_button.pack(side="left", padx=5); Tooltip(self.refresh_ports_button, "Busca los dispositivos conectados.")
        self.connect_button = ctk.CTkButton(conn_frame, text="Conectar", command=self.toggle_connection, font=self.font_normal); self.connect_button.pack(side="left", padx=(15, 5)); Tooltip(self.connect_button, "Conectar o desconectar del macropad.")
        self.connection_status_label = ctk.CTkLabel(conn_frame, text="Desconectado", text_color="red", font=self.font_normal); self.connection_status_label.pack(side="left", padx=5, fill="x", expand=True)

        # --- Frame de Botones ---
        buttons_outer_frame=ctk.CTkFrame(tab);buttons_outer_frame.pack(padx=10,pady=10,fill="both",expand=True)
        buttons_grid_frame=ctk.CTkFrame(buttons_outer_frame,fg_color="transparent");buttons_grid_frame.pack(expand=True,fill="both",padx=5,pady=5)
        for i in range(9):
            row,col,button_id=i//3,i%3,f"B{i+1}"
            button_item_frame=ctk.CTkFrame(buttons_grid_frame,border_width=1,corner_radius=8);button_item_frame.grid(row=row,column=col,padx=8,pady=8,sticky="nsew");self.button_frames[button_id]=button_item_frame;buttons_grid_frame.grid_rowconfigure(row,weight=1);buttons_grid_frame.grid_columnconfigure(col,weight=1)
            ctk.CTkLabel(button_item_frame,text=f"{i+1}",font=self.font_header).pack(pady=(10,5))
            self.button_entries[button_id]={}
            icons={"CORTA":self.icon_corta,"LARGA":self.icon_larga,"DOBLE":self.icon_doble}
            for press_type in PRESS_TYPES:
                action_frame=ctk.CTkFrame(button_item_frame,fg_color="transparent");action_frame.pack(pady=2,padx=10,fill="x");action_frame.grid_columnconfigure(1,weight=1)
                ctk.CTkLabel(action_frame,text="",image=icons.get(press_type),width=15).grid(row=0,column=0,padx=(0,5))
                entry=ctk.CTkEntry(action_frame,placeholder_text="Acción...",font=self.font_normal);entry.grid(row=0,column=1,sticky="ew")
                dropdown_btn=ctk.CTkButton(action_frame,text="",image=self.arrow_down_icon,width=20,command=lambda e=entry,b=action_frame:self._show_macros_dropdown(e,b));dropdown_btn.grid(row=0,column=2,padx=(3,0));Tooltip(dropdown_btn,"Seleccionar macro o tecla predefinida")
                self.button_entries[button_id][press_type]=entry
        
        # --- Frame de Perfiles y Apariencia ---
        bottom_frame = ctk.CTkFrame(tab); bottom_frame.pack(padx=10, pady=10, fill="x")
        profile_io_frame=ctk.CTkFrame(bottom_frame);profile_io_frame.pack(side="left", padx=(0, 20), fill="x", expand=True)
        profile_controls_frame=ctk.CTkFrame(profile_io_frame,fg_color="transparent");profile_controls_frame.pack(fill="x",pady=5)
        ctk.CTkLabel(profile_controls_frame,text="PERFIL:",font=self.font_normal).pack(side="left",padx=(0,5));self.profile_combobox=ctk.CTkComboBox(profile_controls_frame,variable=self.current_profile_name,values=[],command=self.on_profile_selected,width=150,font=self.font_normal);self.profile_combobox.pack(side="left",padx=5)
        save_btn=ctk.CTkButton(profile_controls_frame,text="Guardar",command=self.save_current_profile,font=self.font_normal,fg_color="gray60", width=80);save_btn.pack(side="left",padx=(15,5));Tooltip(save_btn,"Guarda la configuración actual en el perfil seleccionado.")
        new_btn=ctk.CTkButton(profile_controls_frame,text="Nuevo",command=self.create_new_profile,font=self.font_normal,fg_color="gray60", width=80);new_btn.pack(side="left",padx=5);Tooltip(new_btn,"Crea un nuevo perfil.")
        del_btn=ctk.CTkButton(profile_controls_frame,text="Eliminar",command=self.delete_current_profile,font=self.font_normal,fg_color="red", width=80);del_btn.pack(side="left",padx=5);Tooltip(del_btn,"Elimina el perfil actual.")
        
        appearance_frame = ctk.CTkFrame(bottom_frame); appearance_frame.pack(side="right", fill="x")
        self.theme_menu = ctk.CTkSegmentedButton(appearance_frame, values=["Claro", "Oscuro", "Sistema"], command=self.change_appearance_mode, font=self.font_normal); self.theme_menu.pack(padx=10, pady=5); self.theme_menu.set("Oscuro")
        self.autosave_var=ctk.BooleanVar(value=True);self.autosave_check=ctk.CTkCheckBox(appearance_frame,text="Autoguardar al salir",variable=self.autosave_var,font=self.font_normal);self.autosave_check.pack(padx=10, pady=10);Tooltip(self.autosave_check,"Guarda el perfil activo al cerrar.")

    def change_appearance_mode(self, new_mode):
        mode_map = {"Claro": "Light", "Oscuro": "Dark", "Sistema": "System"}
        ctk.set_appearance_mode(mode_map.get(new_mode, "Dark"))

    def _show_macros_dropdown(self,target_entry,activating_widget):
        self._cached_dropdown_data = self._prepare_dropdown_data() # Recargar datos con macros personalizadas
        if hasattr(self,'_current_dropdown')and self._current_dropdown.winfo_exists():self._current_dropdown.destroy()
        dropdown=ctk.CTkToplevel(self);self._current_dropdown=dropdown;dropdown.overrideredirect(True);dropdown.grab_set();dropdown.configure(border_width=1,border_color="blue",corner_radius=6)
        x,y=activating_widget.winfo_rootx(),activating_widget.winfo_rooty()+activating_widget.winfo_height();dropdown.geometry(f"250x300+{x}+{y}")
        scroll_frame=ctk.CTkScrollableFrame(dropdown,corner_radius=0);scroll_frame.pack(fill="both",expand=True)
        for item in self._cached_dropdown_data:
            if item["type"]=="header":ctk.CTkLabel(scroll_frame,text=item["text"],font=self.font_bold,text_color="lightblue",anchor="w").pack(fill="x",padx=10,pady=(8,4))
            elif item["type"]=="item":ctk.CTkButton(scroll_frame,text=item["name"],anchor="w",fg_color="transparent",hover_color=ctk.ThemeManager.theme["CTkEntry"]["fg_color"][0],font=self.font_normal,command=lambda name=item['name']:self._select_macro_from_dropdown(name,target_entry,dropdown)).pack(fill="x",padx=5,pady=1)
        dropdown.bind("<FocusOut>",lambda e:dropdown.destroy());dropdown.bind("<Escape>",lambda e:dropdown.destroy())

    def _select_macro_from_dropdown(self,name,entry,window):entry.delete(0,ctk.END);entry.insert(0,name);window.destroy()

    def _create_sequence_builder_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1); tab.grid_columnconfigure(1, weight=2); tab.grid_rowconfigure(0, weight=1)
        left_frame = ctk.CTkFrame(tab); left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe"); left_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(left_frame, text="Macros Personalizadas", font=self.font_title).pack(pady=10)
        self.custom_macro_listbox = ctk.CTkScrollableFrame(left_frame, label_text="Mis Macros"); self.custom_macro_listbox.pack(pady=5, padx=10, fill="both", expand=True)
        management_frame = ctk.CTkFrame(left_frame); management_frame.pack(pady=10, padx=10, fill="x")
        new_button = ctk.CTkButton(management_frame, text="Nueva", command=self.sequence_new); new_button.pack(side="left", expand=True, padx=5); Tooltip(new_button, "Crea una nueva secuencia de macros.")
        delete_button = ctk.CTkButton(management_frame, text="Eliminar", command=self.sequence_delete, fg_color="red"); delete_button.pack(side="left", expand=True, padx=5); Tooltip(delete_button, "Elimina la secuencia seleccionada.")
        right_frame = ctk.CTkFrame(tab); right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe"); right_frame.grid_columnconfigure(0, weight=1); right_frame.grid_rowconfigure(2, weight=1)
        name_frame = ctk.CTkFrame(right_frame); name_frame.pack(fill="x", padx=10, pady=10); name_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(name_frame, text="Nombre:", font=self.font_normal).grid(row=0, column=0, padx=(0,5)); self.sequence_name_entry = ctk.CTkEntry(name_frame, placeholder_text="Nombre de la nueva macro..."); self.sequence_name_entry.grid(row=0, column=1, sticky="ew")
        save_seq_button = ctk.CTkButton(name_frame, text="Guardar Secuencia", command=self.sequence_save); save_seq_button.grid(row=0, column=2, padx=(10,0)); Tooltip(save_seq_button, "Guarda los cambios en esta secuencia.")
        ctk.CTkLabel(right_frame, text="Pasos de la Secuencia", font=self.font_title).pack(pady=(10,0)); self.sequence_steps_frame = ctk.CTkScrollableFrame(right_frame, fg_color="transparent"); self.sequence_steps_frame.pack(pady=5, padx=10, fill="both", expand=True)
        builder_frame = ctk.CTkFrame(right_frame); builder_frame.pack(fill="x", padx=10, pady=10); builder_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(builder_frame, text="Constructor de Pasos", font=self.font_title).grid(row=0, column=0, columnspan=3, pady=(0,10))
        self.step_type_var = ctk.StringVar(value="Pulsar Tecla"); self.step_value_entry = ctk.StringVar()
        action_types = ["Pulsar Tecla", "Escribir Texto", "Añadir Retardo (ms)", "Control del Sistema", "Control de OBS"]
        ctk.CTkLabel(builder_frame, text="Tipo de Acción:", font=self.font_normal).grid(row=1, column=0, padx=5, sticky="e"); self.step_type_combo = ctk.CTkComboBox(builder_frame, variable=self.step_type_var, values=action_types, command=self.on_step_type_change); self.step_type_combo.grid(row=1, column=1, padx=5, sticky="ew")
        self.step_value_frame = ctk.CTkFrame(builder_frame, fg_color="transparent"); self.step_value_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.step_value_entry_widget = ctk.CTkEntry(self.step_value_frame, textvariable=self.step_value_entry, placeholder_text="Ej: CTRL+C, o 'Hola', o 500"); self.step_value_entry_widget.pack(fill="x", expand=True)
        ctk.CTkLabel(builder_frame, text="Valor:", font=self.font_normal).grid(row=2, column=0, padx=5, sticky="e"); add_step_button = ctk.CTkButton(builder_frame, text="Añadir Paso", command=self.sequence_add_step); add_step_button.grid(row=1, column=2, rowspan=2, padx=10); Tooltip(add_step_button, "Añade la acción configurada a la secuencia.")

    def on_step_type_change(self, choice):
        for widget in self.step_value_frame.winfo_children(): widget.destroy()
        
        system_actions = ["Apagar PC", "Reiniciar PC", "Suspender"]; obs_actions = ["Iniciar Grabación", "Detener Grabación", "Iniciar Streaming", "Detener Streaming"]
        
        if choice == "Control del Sistema": ctk.CTkOptionMenu(self.step_value_frame, variable=self.step_value_entry, values=system_actions).pack(fill="x")
        elif choice == "Control de OBS": ctk.CTkOptionMenu(self.step_value_frame, variable=self.step_value_entry, values=obs_actions).pack(fill="x")
        else:
            placeholder_map = {"Pulsar Tecla": "Ej: CTRL+C", "Escribir Texto": "El texto a escribir", "Añadir Retardo (ms)": "500"}
            self.step_value_entry.set("")
            ctk.CTkEntry(self.step_value_frame, textvariable=self.step_value_entry, placeholder_text=placeholder_map.get(choice)).pack(fill="x")
    
    def _create_macros_tab(self,tab):
        main_frame=ctk.CTkFrame(tab,fg_color="transparent");main_frame.pack(fill="both",expand=True,padx=10,pady=10)
        ctk.CTkLabel(main_frame,text="Aquí puedes consultar las macros predefinidas y cómo se usan.",font=self.font_normal).pack(pady=(0,5))
        header_frame=ctk.CTkFrame(main_frame,fg_color="transparent");header_frame.pack(fill="x",padx=5,pady=(0,0));header_bg=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0]
        ctk.CTkLabel(header_frame,text="Tipo",font=self.font_bold,fg_color=header_bg,corner_radius=0,padx=5,pady=5).grid(row=0,column=0,sticky="ew")
        ctk.CTkLabel(header_frame,text="Descripción/Valor",font=self.font_bold,fg_color=header_bg,corner_radius=0,padx=5,pady=5).grid(row=0,column=1,sticky="ew")
        header_frame.grid_columnconfigure(0,weight=1);header_frame.grid_columnconfigure(1,weight=3)
        scroll_frame=ctk.CTkScrollableFrame(main_frame,corner_radius=0,fg_color="transparent");scroll_frame.pack(fill="both",expand=True,padx=5,pady=(0,5))
        row=0;ctk.CTkLabel(scroll_frame,text="TECLAS ESPECIALES",font=self.font_bold,text_color="lightblue").grid(row=row,column=0,columnspan=2,sticky="w",pady=(10,5),padx=5);row+=1
        for k,v in sorted(SPECIAL_KEYS_MAP.items()):desc=f"Simula la tecla {v.name.replace('_',' ').upper()}";ctk.CTkLabel(scroll_frame,text=f"'{k}'",anchor="w",wraplength=140,font=self.font_normal).grid(row=row,column=0,sticky="ew",padx=5,pady=1);ctk.CTkLabel(scroll_frame,text=desc,anchor="w",wraplength=400,font=self.font_normal).grid(row=row,column=1,sticky="ew",padx=5,pady=1);row+=1
        ctk.CTkLabel(scroll_frame,text="MACROS PREDEFINIDAS",font=self.font_bold,text_color="lightblue").grid(row=row,column=0,columnspan=2,sticky="w",pady=(15,5),padx=5);row+=1
        for k,v in sorted(PREDEFINED_MACROS.items()):
            if isinstance(v,tuple):desc=f"Simula: {' + '.join([i.name.replace('_',' ').upper() if hasattr(i,'name')else str(i).upper() for i in v])}"
            elif isinstance(v,str):desc=f"Escribe: \"{v}\""
            elif isinstance(v,dict):desc=f"Ejecuta: \"{v.get('command')}\""
            ctk.CTkLabel(scroll_frame,text=f"'{k}'",anchor="w",wraplength=140,font=self.font_normal).grid(row=row,column=0,sticky="ew",padx=5,pady=1);ctk.CTkLabel(scroll_frame,text=desc,anchor="w",wraplength=400,font=self.font_normal).grid(row=row,column=1,sticky="ew",padx=5,pady=1);row+=1

    def _create_integrations_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(tab, text="Configuración de Integraciones", font=self.font_subtitle).pack(pady=10)
        
        # --- Frame de OBS ---
        obs_frame = ctk.CTkFrame(tab); obs_frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(obs_frame, text="Control de OBS Studio", font=self.font_title).pack(anchor="w", padx=10, pady=5)
        
        obs_conn_frame = ctk.CTkFrame(obs_frame, fg_color="transparent"); obs_conn_frame.pack(padx=10, pady=5, fill="x")
        obs_conn_frame.grid_columnconfigure(1, weight=1); obs_conn_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(obs_conn_frame, text="Host:", font=self.font_normal).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.obs_host_var = ctk.StringVar(); self.obs_host_entry = ctk.CTkEntry(obs_conn_frame, textvariable=self.obs_host_var); self.obs_host_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(obs_conn_frame, text="Puerto:", font=self.font_normal).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.obs_port_var = ctk.StringVar(); self.obs_port_entry = ctk.CTkEntry(obs_conn_frame, textvariable=self.obs_port_var); self.obs_port_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(obs_conn_frame, text="Contraseña:", font=self.font_normal).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.obs_pass_var = ctk.StringVar(); self.obs_pass_entry = ctk.CTkEntry(obs_conn_frame, textvariable=self.obs_pass_var, show="*"); self.obs_pass_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        if not OBS_AVAILABLE:
            ctk.CTkLabel(obs_frame, text="La librería 'obs-websocket-py' no está instalada. Esta función está desactivada.", font=self.font_normal, text_color="orange", wraplength=700).pack(padx=10, pady=5)
            ctk.CTkButton(obs_frame, text="¿Cómo instalar obs-websocket?", command=self.show_obs_help).pack(pady=10)

    def show_obs_help(self):
        help_text = (
            "Para controlar OBS, necesitas dos cosas:\n\n"
            "1. El plugin 'obs-websocket' en tu OBS Studio:\n"
            "   - Ve a Herramientas > obs-websocket Settings.\n"
            "   - Activa 'Enable WebSocket Server'.\n"
            "   - Anota el puerto y establece una contraseña.\n\n"
            "2. La librería de Python:\n"
            "   - Cierra esta aplicación.\n"
            "   - Abre una terminal (cmd o PowerShell).\n"
            "   - Escribe: pip install obs-websocket-py\n\n"
            "Una vez hecho, reinicia esta aplicación y rellena los datos de conexión."
        )
        messagebox.showinfo("Ayuda de OBS", help_text)
    
    def _create_logs_tab(self,tab):tab.grid_columnconfigure(0,weight=1);tab.grid_rowconfigure(0,weight=1);self.log_textbox=ctk.CTkTextbox(tab,wrap="word",state="disabled",font=self.font_small);self.log_textbox.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")
    def _create_about_tab(self,tab):
        tab.grid_columnconfigure(0,weight=1);tab.grid_rowconfigure(0,weight=1);center_frame=ctk.CTkFrame(tab,fg_color="transparent");center_frame.grid(row=0,column=0,sticky="nsew");center_frame.grid_columnconfigure(0,weight=1)
        if PILLOW_AVAILABLE:
            try:
                logo_path=self._get_asset_path('logo.png')
                if logo_path and os.path.exists(logo_path):
                    pil_img=Image.open(logo_path).resize((128,128),Image.Resampling.LANCZOS);self.about_logo_image_tk=ImageTk.PhotoImage(pil_img)
                    ctk.CTkLabel(center_frame,image=self.about_logo_image_tk,text="").pack(pady=(20,15))
            except Exception as e:self._log_message(f"Error al cargar logo: {e}","error")
        ctk.CTkLabel(center_frame,text="MACROpad by JMC",font=self.font_header,text_color="lightblue").pack(pady=(0,5));ctk.CTkLabel(center_frame,text="De un BIM Manager, para todo el mundo.",font=self.font_subtitle).pack();ctk.CTkLabel(center_frame,text="-"*60,text_color="gray").pack(fill="x",pady=25,padx=80)
        about_text="Hecho con código y café desde A Coruña. ☕\n\nEsta aplicación nace de la trinchera, de la mente de un Arquitecto Técnico y BIM Manager\nque cree que las herramientas deben ser potentes, pero también sencillas.\n\nAquí no hay adornos innecesarios, solo la funcionalidad que necesitas\npara automatizar tus tareas repetitivas.";ctk.CTkLabel(center_frame,text=about_text,justify="center",font=self.font_about_text,wraplength=700).pack(pady=10)
        ctk.CTkLabel(center_frame,text="Jose Manuel Caamaño González",font=self.font_author).pack(pady=(20,0));link=ctk.CTkLabel(center_frame,text="josecaamano.io",text_color="lightblue",cursor="hand2",font=self.font_normal);link.pack();link.bind("<Button-1>",lambda e:webbrowser.open_new("http://josecaamano.io"))
        ctk.CTkLabel(center_frame,text="BY JMC",font=self.font_jmc,text_color="gray").pack(pady=(30,0));ctk.CTkLabel(center_frame,text="Copyright 2025",font=self.font_small,text_color="gray").pack();ctk.CTkLabel(center_frame,text="Versión 6.2",font=self.font_small,text_color="gray").pack()
    
    def _log_message(self,msg,lvl="info"):
        if not hasattr(self,'log_textbox')or self.log_textbox is None:return
        ts=time.strftime("%H:%M:%S");formatted=f"[{ts}] [{lvl.upper()}] {msg}\n";self.log_textbox.configure(state="normal");self.log_textbox.insert("end",formatted);self.log_textbox.see("end");self.log_textbox.configure(state="disabled")

    def set_status(self,msg,lvl="info",persist=False):
        self.status_bar.configure(text=msg,text_color={"error":"red","success":"green"}.get(lvl,("#DCE4EE","#FFFFFF")))
        if not persist:self.after(7000,lambda:self.status_bar.configure(text="Listo."))
    
    def show_welcome_assistant_if_needed(self):
        config_dir=self.get_config_dir()
        if not os.path.exists(config_dir)or not any(f.endswith('.json')for f in os.listdir(config_dir)):
            WelcomeAssistant(self)

    def populate_com_ports(self):
        try:
            ports=sorted([p.device for p in serial.tools.list_ports.comports()]);self.com_port_combobox.configure(values=ports)
            if self.button_mappings.get("com_port")in ports:self.com_port_var.set(self.button_mappings.get("com_port"))
            elif ports:self.com_port_var.set(ports[0])
            else:self.com_port_var.set("");self.set_status("No se encontraron puertos COM.","error")
        except:self._log_message("Error al listar puertos COM.","error")

    def toggle_connection(self):
        if self.arduino and self.arduino.is_open:self.disconnect_arduino()
        else:self.connect_arduino()

    def connect_arduino(self):
        port=self.com_port_var.get();
        if not port:messagebox.showerror("Error","Selecciona un puerto COM.");return
        try:
            self.set_status(f"Conectando a {port}...", "info", True); self.arduino=serial.Serial(port=port,baudrate=9600,timeout=1);time.sleep(2)
            self.is_listening=True;self.listening_thread=threading.Thread(target=self.listen_to_arduino,daemon=True);self.listening_thread.start()
            self.connect_button.configure(text="Desconectar",fg_color="red");self.connection_status_label.configure(text="Conectado",text_color="green");self.set_status(f"Conectado a MACROpad en {port}.","success")
            self.com_port_combobox.configure(state="disabled");self.refresh_ports_button.configure(state="disabled")
        except serial.SerialException as e:messagebox.showerror("Error de Conexión",f"No se pudo conectar a {port}.\n{e}");self.set_status(f"Error conectando.","error")

    def disconnect_arduino(self):
        self.is_listening=False
        if self.listening_thread:self.listening_thread.join(0.5)
        if self.arduino and self.arduino.is_open:self.arduino.close()
        self.connect_button.configure(text="Conectar",fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]);self.connection_status_label.configure(text="Desconectado",text_color="red");self.set_status("Desconectado.")
        self.com_port_combobox.configure(state="readonly");self.refresh_ports_button.configure(state="normal")

    def listen_to_arduino(self):
        while self.is_listening:
            try:
                if self.arduino and self.arduino.is_open and self.arduino.in_waiting:
                    line=self.arduino.readline().decode('utf-8').strip()
                    if line:self.after(0,self.process_arduino_input,line)
            except(serial.SerialException,TypeError,UnicodeDecodeError):
                if self.is_listening:self.after(0,self.disconnect_arduino);messagebox.showwarning("Error","Se perdió la conexión.")
                break
    
    def process_arduino_input(self,data):
        parts=data.strip().upper().split('_');
        if len(parts)!=2:return
        button_id,press_type=parts
        if button_id in self.button_frames:
            frame=self.button_frames[button_id];original_color=frame.cget("border_color");frame.configure(border_color="green");self.after(150,lambda:frame.configure(border_color=original_color))
        action=self.button_mappings.get(button_id,{}).get(press_type)
        if action:self._log_message(f"Ejecutando: {action}","info");self.execute_action(action)

    def execute_action(self,action_str):
        if not action_str:return
        action_upper=action_str.strip().upper()
        custom_sequences = self.button_mappings.get('custom_sequences', {})
        if action_str in custom_sequences:
            self.execute_sequence(custom_sequences[action_str])
            return
        if action_upper in PREDEFINED_MACROS:
            action=PREDEFINED_MACROS[action_upper]
            if isinstance(action,tuple):self._press_key_combination(action)
            elif isinstance(action,str):self.keyboard_controller.type(action)
            elif isinstance(action,dict):
                try:os.startfile(action["command"])
                except Exception as e:self._log_message(f"Error ejecutando '{action['command']}': {e}","error")
        elif '+'in action_str:
            keys=[SPECIAL_KEYS_MAP.get(p.strip().upper(),p.strip().lower())for p in action_str.split('+')]
            self._press_key_combination(keys)
        elif action_upper in SPECIAL_KEYS_MAP:
            key=SPECIAL_KEYS_MAP[action_upper]
            if key not in MODIFIER_KEYS_SET:self.keyboard_controller.press(key);self.keyboard_controller.release(key)
        else:self.keyboard_controller.type(action_str)
    
    def execute_sequence(self, steps):
        for step in steps:
            action_type, value = step.get('type'), step.get('value')
            if action_type == "Pulsar Tecla": self._press_key_combination([SPECIAL_KEYS_MAP.get(p.strip().upper(),p.strip().lower()) for p in value.split('+')])
            elif action_type == "Escribir Texto": self.keyboard_controller.type(value)
            elif action_type == "Añadir Retardo (ms)":
                try: time.sleep(float(value)/1000.0)
                except: self._log_message(f"Retardo inválido: {value}", "error")
            elif action_type == "Control del Sistema": self.execute_system_control(value)
            elif action_type == "Control de OBS": self.execute_obs_control(value)

    def execute_system_control(self, command):
        actions = {
            "Apagar PC": "shutdown /s /t 1",
            "Reiniciar PC": "shutdown /r /t 1",
            "Suspender": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        }
        if command in actions and messagebox.askyesno("Confirmación de Acción del Sistema", f"¿Estás seguro de que quieres '{command}' el PC?"):
            os.system(actions[command])
    
    def execute_obs_control(self, command):
        if not OBS_AVAILABLE: self.set_status("Librería de OBS no encontrada.", "error"); return
        
        host = self.button_mappings.get('obs_host', 'localhost')
        port = self.button_mappings.get('obs_port', 4455)
        password = self.button_mappings.get('obs_pass', '')

        try:
            ws = obswebsocket.obsws(host, port, password)
            ws.connect()
            
            if command == "Iniciar Grabación": ws.call(obswebsocket.requests.StartRecord())
            elif command == "Detener Grabación": ws.call(obswebsocket.requests.StopRecord())
            elif command == "Iniciar Streaming": ws.call(obswebsocket.requests.StartStream())
            elif command == "Detener Streaming": ws.call(obswebsocket.requests.StopStream())
                
            ws.disconnect()
            self.set_status(f"Comando OBS '{command}' enviado.", "success")
        except Exception as e:
            self.set_status(f"Error de OBS: {e}", "error"); self._log_message(f"Error de OBS: {e}", "error")

    def _press_key_combination(self, keys):
        try:
            for key in keys: self.keyboard_controller.press(key)
            for key in reversed(keys): self.keyboard_controller.release(key)
        except Exception as e: self._log_message(f"Error al pulsar combinación: {e}", "error")

    def update_mappings_from_entries(self):
        self.button_mappings["com_port"]=self.com_port_var.get()
        for btn,presses in self.button_entries.items():
            self.button_mappings.setdefault(btn,{})
            for p_type,entry in presses.items():self.button_mappings[btn][p_type]=entry.get().strip()
    
    def update_entries_from_mappings(self):
        for btn,presses in self.button_entries.items():
            for p_type,entry in presses.items():
                entry.delete(0,ctk.END);entry.insert(0,self.button_mappings.get(btn,{}).get(p_type,""))
        
        self.obs_host_var.set(self.button_mappings.get('obs_host', 'localhost'))
        self.obs_port_var.set(self.button_mappings.get('obs_port', '4455'))
        self.obs_pass_var.set(self.button_mappings.get('obs_pass', ''))
        
        port=self.button_mappings.get("com_port")
        if port and port in self.com_port_combobox.cget("values"):self.com_port_var.set(port)

    def _ensure_config_directory_exists(self):os.makedirs(os.path.join(getattr(sys,'_MEIPASS','.'),CONFIG_DIR),exist_ok=True)
    def get_config_dir(self):return os.path.join(getattr(sys,'_MEIPASS','.'),CONFIG_DIR)
    
    def load_profiles(self):
        config_path=self.get_config_dir();profiles=["(Vacío)"]
        if os.path.exists(config_path):profiles.extend([os.path.splitext(f)[0]for f in os.listdir(config_path)if f.endswith(".json")])
        self.profile_combobox.configure(values=sorted(profiles))
        self.update_custom_macro_listbox()

    def on_profile_selected(self,name):
        self.save_current_profile(True);self.load_config_from_path(os.path.join(self.get_config_dir(),f"{name}.json"))

    def save_current_profile(self,silent=False):
        name=self.current_profile_name.get()
        if not name or name=="(Vacío)":
            if silent:return
            name=ctk.CTkInputDialog(text="Nombre para el nuevo perfil:",title="Guardar Perfil").get_input();
            if not name:return
        name=re.sub(r'[\\/:*?"<>|]','',name).strip()
        if self.save_config_to_path(os.path.join(self.get_config_dir(),f"{name}.json")):
            if not silent:messagebox.showinfo("Guardado",f"Perfil '{name}' guardado.")
            self.load_profiles();self.current_profile_name.set(name)

    def create_new_profile(self):
        name=ctk.CTkInputDialog(text="Nombre para el nuevo perfil:",title="Nuevo Perfil").get_input()
        if not name:return
        self.save_current_profile(True);self.initialize_empty_mappings();self.update_entries_from_mappings();self.current_profile_name.set(name);self.save_current_profile(True);self.load_profiles()

    def delete_current_profile(self):
        name=self.current_profile_name.get()
        if not name or name=="(Vacío)":return
        if messagebox.askyesno("Confirmar",f"¿Eliminar el perfil '{name}'?"):
            try:
                os.remove(os.path.join(self.get_config_dir(),f"{name}.json"));self.load_profiles();self.initialize_empty_mappings();self.update_entries_from_mappings();self.current_profile_name.set("(Vacío)")
            except OSError as e:messagebox.showerror("Error",f"No se pudo eliminar: {e}")

    def save_config_to_path(self,path):
        self.update_mappings_from_entries()
        # Guardar configuraciones adicionales
        self.button_mappings['obs_host'] = self.obs_host_var.get()
        self.button_mappings['obs_port'] = self.obs_port_var.get()
        self.button_mappings['obs_pass'] = self.obs_pass_var.get()
        self.button_mappings['theme'] = self.theme_menu.get()
        try:
            with open(path,'w',encoding='utf-8')as f:json.dump(self.button_mappings,f,indent=4,sort_keys=True)
            return True
        except IOError:return False

    def load_config_from_path(self,path):
        self.initialize_empty_mappings()
        try:
            with open(path,'r',encoding='utf-8')as f:data=json.load(f)
            self.button_mappings.update(data)
        except(FileNotFoundError,json.JSONDecodeError):pass
        self.update_entries_from_mappings();self.current_profile_name.set(os.path.splitext(os.path.basename(path))[0])
        self.theme_menu.set(self.button_mappings.get('theme', 'Oscuro'))
        self.change_appearance_mode(self.theme_menu.get())
        self.update_custom_macro_listbox()
        self.sequence_new()

    def load_config_on_startup(self):
        path=os.path.join(self.get_config_dir(),"default.json")
        if os.path.exists(path):self.load_config_from_path(path)
        else:self.initialize_empty_mappings();self.update_entries_from_mappings()

    def initialize_empty_mappings(self):
        self.button_mappings={"com_port":"", "custom_sequences": {}, "obs_host": "localhost", "obs_port": "4455", "obs_pass": "", "theme": "Oscuro"}
        for i in range(1,10): self.button_mappings[f"B{i}"] = {pt:"" for pt in PRESS_TYPES}

    def on_closing(self):
        if self.autosave_var.get():
            name=self.current_profile_name.get()
            if name=="(Vacío)":name="default"
            self.save_config_to_path(os.path.join(self.get_config_dir(),f"{name}.json"))
        self.disconnect_arduino();self.destroy()

    # --- Lógica del Creador de Secuencias ---
    def update_custom_macro_listbox(self):
        for widget in self.custom_macro_listbox.winfo_children(): widget.destroy()
        custom_sequences = self.button_mappings.get('custom_sequences', {})
        for name in sorted(custom_sequences.keys()):
            btn = ctk.CTkButton(self.custom_macro_listbox, text=name, fg_color="transparent", command=lambda n=name: self.sequence_load(n))
            btn.pack(fill="x", padx=5)

    def sequence_new(self):
        self.sequence_name_entry.delete(0, ctk.END); self.current_sequence_steps = []
        for widget in self.sequence_steps_frame.winfo_children(): widget.destroy()

    def sequence_load(self, name):
        self.sequence_new(); self.sequence_name_entry.insert(0, name)
        self.current_sequence_steps = self.button_mappings.get('custom_sequences', {}).get(name, [])
        self.sequence_redraw_steps()

    def sequence_save(self):
        name = self.sequence_name_entry.get().strip()
        if not name: messagebox.showerror("Error", "El nombre de la macro no puede estar vacío."); return
        if 'custom_sequences' not in self.button_mappings: self.button_mappings['custom_sequences'] = {}
        self.button_mappings['custom_sequences'][name] = self.current_sequence_steps
        self.update_custom_macro_listbox(); self.set_status(f"Secuencia '{name}' guardada.", "success"); self.save_current_profile(silent=True)

    def sequence_delete(self):
        name = self.sequence_name_entry.get().strip()
        if not name: messagebox.showwarning("Atención", "Selecciona una macro para eliminar."); return
        if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar la secuencia '{name}'?"):
            if 'custom_sequences' in self.button_mappings and name in self.button_mappings['custom_sequences']:
                del self.button_mappings['custom_sequences'][name]
                self.update_custom_macro_listbox(); self.sequence_new(); self.set_status(f"Secuencia '{name}' eliminada.", "info"); self.save_current_profile(silent=True)

    def sequence_add_step(self):
        step_type, step_value = self.step_type_var.get(), self.step_value_entry.get()
        if not step_value: messagebox.showerror("Error", "El valor del paso no puede estar vacío."); return
        if step_type == "Añadir Retardo (ms)" and not step_value.isdigit(): messagebox.showerror("Error", "El retardo debe ser un número entero."); return
        self.current_sequence_steps.append({"type": step_type, "value": step_value}); self.sequence_redraw_steps()

    def sequence_redraw_steps(self):
        for widget in self.sequence_steps_frame.winfo_children(): widget.destroy()
        for i, step in enumerate(self.current_sequence_steps):
            step_frame = ctk.CTkFrame(self.sequence_steps_frame); step_frame.pack(fill="x", pady=2); step_frame.grid_columnconfigure(0, weight=1)
            type_map = {"Pulsar Tecla": "Tecla", "Escribir Texto": "Texto", "Añadir Retardo (ms)": "Pausa", "Control del Sistema": "Sistema", "Control de OBS": "OBS"}
            label_text = f"Paso {i+1}: [{type_map.get(step['type'])}] - {step['value']}"
            ctk.CTkLabel(step_frame, text=label_text, wraplength=400, justify="left").grid(row=0, column=0, padx=5, sticky="w")
            ctk.CTkButton(step_frame, text="X", width=25, fg_color="red", command=lambda index=i: self.sequence_delete_step(index)).grid(row=0, column=1, padx=5, sticky="e")

    def sequence_delete_step(self, index):
        if 0 <= index < len(self.current_sequence_steps): del self.current_sequence_steps[index]; self.sequence_redraw_steps()

class WelcomeAssistant(FadingToplevel):
    def __init__(self,master):
        super().__init__(master)
        self.title("Bienvenido a MACROpad by JMC")
        if master.icon_path and os.path.exists(master.icon_path): self.iconbitmap(master.icon_path)
        self.geometry("500x420");self.resizable(False,False);self.grab_set()
        if PILLOW_AVAILABLE:
            try:
                logo_path=master._get_asset_path('logo.png')
                if logo_path and os.path.exists(logo_path):
                    pil_img=Image.open(logo_path).resize((80,80),Image.Resampling.LANCZOS);self.logo_image=ImageTk.PhotoImage(pil_img)
                    ctk.CTkLabel(self,image=self.logo_image,text="").pack(pady=(20,10))
            except Exception as e:master._log_message(f"Error al cargar logo para bienvenida: {e}","error")
        ctk.CTkLabel(self,text="¡Bienvenido a MACROpad by JMC!",font=master.font_subtitle,text_color="lightblue").pack()
        text_frame=ctk.CTkFrame(self,fg_color="transparent");text_frame.pack(pady=20,padx=30,fill="x")
        welcome_text="Para empezar, sigue estos sencillos pasos:\n\n1. Conecta tu dispositivo MACROpad al PC.\n\n2. Selecciona el puerto COM correcto y pulsa 'Conectar'.\n\n3. ¡Crea tu primer perfil y empieza a configurar tus botones!"
        ctk.CTkLabel(text_frame,text=welcome_text,font=master.font_normal,justify="left").pack()
        link_frame=ctk.CTkFrame(self,fg_color="transparent");link_frame.pack(pady=(10,20))
        ctk.CTkLabel(link_frame,text="Para más información, visita:",font=master.font_small).pack(side="left")
        link=ctk.CTkLabel(link_frame,text="josecaamano.io",text_color="lightblue",cursor="hand2",font=master.font_small);link.pack(side="left",padx=5);link.bind("<Button-1>",lambda e:webbrowser.open_new("http://josecaamano.io"))
        close_button=ctk.CTkButton(self,text="¡Entendido!",command=self.close_with_fade);close_button.pack(pady=10);self.bind("<Escape>",lambda e:self.close_with_fade())

if __name__ == "__main__":
    if PYNPUT_AVAILABLE:
        app = MacropadApp()
        app.mainloop()
