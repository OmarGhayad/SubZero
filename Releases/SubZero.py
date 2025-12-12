import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress
import platform

# --- Utility Functions ---
def ip_to_binary(ip):
    """Converts a standard IPv4 address string to its dotted binary representation."""
    
    return ".".join([bin(int(o))[2:].zfill(8) for o in ip.split(".")])


current_font_size = 11 


def adjust_font_size(delta):
    global current_font_size
    min_size = 9
    max_size = 14
    new_size = current_font_size + delta
    
    if min_size <= new_size <= max_size:
        current_font_size = new_size
        
        style.configure("Dark.TLabel", font=("Consolas", current_font_size))
        style.configure("TButton", font=("Consolas", current_font_size + 1, "bold"))
        style.configure("Treeview.Heading", font=("Consolas", current_font_size + 1, "bold"))
        style.configure("Treeview", font=("Consolas", current_font_size))
        style.configure("TEntry", font=("Consolas", current_font_size + 1))
        style.configure("Header.Dark.TLabel", font=("Consolas", current_font_size + 13, "bold"))

def zoom_in(event=None):
    adjust_font_size(1)

def zoom_out(event=None):
    adjust_font_size(-1)

# --- COPY FUNCTIONALITY (REMAINS THE same) ---
def copy_selected_cell(event=None):
    """
    Copies the value of the currently focused cell or row in the Treeview
    when Ctrl+C or Right-Click is pressed.
    """
    focus_widget = root.focus_get()
    
    if focus_widget == tree or focus_widget == basic_tree:
        selected_items = focus_widget.selection()
        
        if not selected_items:
            if event and event.x and event.y:
                try:
                    selected_items = (focus_widget.identify_row(event.y),)
                except:
                    return

        if not selected_items:
            return

        item_id = selected_items[0]
        item = focus_widget.item(item_id)
        
        text_to_copy = ""
        
        col_index = None
        try:
            if event and event.x is not None:
                column_id = focus_widget.identify_column(event.x)
                col_index = int(column_id.replace("#", "")) - 1
        except:
            pass

        if col_index is not None and item.get('values') and 0 <= col_index < len(item['values']):
            text_to_copy = str(item['values'][col_index])
        elif item.get('values'):
            text_to_copy = "\t".join(map(str, item['values']))
        else:
            text_to_copy = str(item['text'])

        if text_to_copy:
            root.clipboard_clear()
            root.clipboard_append(text_to_copy)
            try:
                pass
            except:
                pass
            
# --- Main Calculate Function (Merged Rules and Results) ---
def calculate():
    # Clear tables
    for i in tree.get_children():
        tree.delete(i)
    for i in basic_tree.get_children():
        basic_tree.delete(i)

    raw = ip_entry.get().strip()

    if "/" not in raw:
        messagebox.showerror("Error", "Enter IP in format: 192.168.1.0/26")
        return

    try:
        network_address, new_prefix_str = raw.split('/')
        new_prefix = int(new_prefix_str)
        
        if not (1 <= new_prefix <= 32):
             messagebox.showerror("Error", "Prefix must be between 1 and 32.")
             return
             
        
        target_net = ipaddress.ip_network(f"{network_address}/{new_prefix}", strict=False)
        
        
        ip_addr = ipaddress.IPv4Address(network_address)
        base_network_prefix = 24 
        if ip_addr in ipaddress.ip_network('172.16.0.0/12'):
            base_network_prefix = 16 
        elif ip_addr in ipaddress.ip_network('10.0.0.0/8'):
            base_network_prefix = 8 
        base_network_str = f"{ip_addr.exploded[:ip_addr.exploded.rfind('.') + 1]}0/{base_network_prefix}"
        base_net = ipaddress.ip_network(base_network_str, strict=False)


    except ValueError as e:
        messagebox.showerror("Error", f"Invalid IP format or prefix: {e}")
        return

    # --- Calculations ---
    
    host_bits = 32 - new_prefix
    
    hosts_per_subnet = (2 ** host_bits) - 2
    block_size = 2 ** host_bits
    
    
    
    if new_prefix > base_network_prefix:
        
        try:
            max_subnets_to_show = 256 
            subnets = list(base_net.subnets(new_prefix=new_prefix))
            num_subnets = len(subnets)
            subnets_to_display = subnets[:max_subnets_to_show]
            subnet_bits = new_prefix - base_network_prefix
        except ValueError:
            messagebox.showerror("Error", "Cannot calculate subnets. Check IP and Prefix values.")
            return
    else:
        
        subnets = [target_net]
        subnets_to_display = [target_net]
        num_subnets = 1
        subnet_bits = "N/A" 


   
    
    ip_bin = ip_to_binary(str(target_net.network_address))
    mask_bin = ip_to_binary(str(target_net.netmask))
    broadcast_bin = ip_to_binary(str(target_net.broadcast_address))

    
    
    hosts_info = f"{hosts_per_subnet} (Rule: 2^{host_bits} - 2, N={host_bits} = Host Bits)"
    block_info = f"{block_size} IPs (Rule: 2^{host_bits}, N={host_bits} = Host Bits)"
    
    if new_prefix > base_network_prefix:
        subnets_info = f"{num_subnets} (Rule: 2^{subnet_bits}, N={subnet_bits} = Subnet Bits)"
    else:
        subnets_info = "N/A (No Subnetting performed)"

    basic_info = [
        
        ("Network Address", str(target_net.network_address)),
        ("New Prefix Length", f"/{new_prefix}"),
        ("New Netmask", str(target_net.netmask)),
        ("Broadcast Address", str(target_net.broadcast_address)),
        
     
        ("Hosts per Subnet", hosts_info),
        ("Block Size", block_info),
        ("Number of Subnets", subnets_info),
        
        ("----", "---- Binary Representation (New Mask) ----"),
        ("IP (Calculated Network Binary)", ip_bin),
        ("Mask (New Prefix Binary)", mask_bin),
        ("Broadcast (Calculated Network Binary)", broadcast_bin),
    ]

    for i, row in enumerate(basic_info):
        tag = "binary_highlight" if i == 7 else ("oddrow" if i % 2 else "evenrow")
        basic_tree.insert("", "end", values=row, tags=(tag,))

    # 5. Insert Subnet Info (Optimized)
    for i, s in enumerate(subnets_to_display, start=1):
        
        hosts_iterator = s.hosts()
        
        try:
            first = str(next(hosts_iterator))
        except StopIteration:
            first = "N/A"

        if hosts_per_subnet > 0:
            last = str(ipaddress.IPv4Address(s.broadcast_address) - 1)
        else:
            last = "N/A"
        
        if hosts_per_subnet < 0:
             first = "N/A"
             last = "N/A"
        elif hosts_per_subnet == 0:
             last = "N/A"
        
        tree.insert(
            "",
            "end",
            values=(
                i,
                str(s.network_address) + f"/{new_prefix}",
                first,
                last,
                str(s.broadcast_address),
                hosts_per_subnet 
            ),
            tags=("oddrow" if i % 2 else "evenrow",),
        )

    
    if new_prefix > base_network_prefix and num_subnets > len(subnets_to_display):
        tree.insert("", "end", values=("...", f"Only showing first {len(subnets_to_display)} of {num_subnets} total subnets. The rest are calculated correctly.", "", "", "", ""), tags=("binary_highlight",))

# -------------------------------- GUI ----------------------------------

root = tk.Tk()
root.title("SubZero") 
root.geometry("1100x750")

OS_SYSTEM = platform.system()
mod_key = "Control" if OS_SYSTEM != "Darwin" else "Command"

# --- Theme Colors ---
DARK_BG = "#1c1c1c" 
BRIGHT_ACCENT = "#cc3b18" 
MID_ACCENT = "#a83015" 
ACCENT_BG = "#2c2c2c" 
LIGHT_TEXT = "#ffffff" 

style = ttk.Style()
style.theme_use("clam")
root.configure(bg=DARK_BG)

# ---------- Styles ----------
style.configure("Dark.TFrame", background=ACCENT_BG)
style.configure(
    "Dark.TLabel",
    font=("Consolas", current_font_size),
    background=DARK_BG,
    foreground=LIGHT_TEXT,
)
style.configure(
    "Header.Dark.TLabel",
    font=("Consolas", current_font_size + 13, "bold"), 
    background=DARK_BG,
    foreground=BRIGHT_ACCENT, 
)
style.configure(
    "TButton",
    font=("Consolas", current_font_size + 1, "bold"),
    background=BRIGHT_ACCENT,
    foreground=LIGHT_TEXT,
    padding=6,
    relief="flat",
)
style.map(
    "TButton",
    background=[("active", MID_ACCENT)], 
    foreground=[("active", LIGHT_TEXT)]
)
style.configure(
    "Treeview.Heading",
    font=("Consolas", current_font_size + 1, "bold"),
    background=BRIGHT_ACCENT,
    foreground=LIGHT_TEXT,
    relief="flat",
)
style.configure(
    "Treeview",
    font=("Consolas", current_font_size),
    rowheight=25,
    relief="flat",
    background=ACCENT_BG,
    foreground=LIGHT_TEXT,
    fieldbackground=ACCENT_BG, 
)
style.map("Treeview", background=[("selected", MID_ACCENT)], foreground=[("selected", LIGHT_TEXT)])
root.option_add("*Treeview*RowHeight", 25)

style.configure(
    "TEntry",
    fieldbackground="#331c00", 
    foreground=LIGHT_TEXT,
    bordercolor=BRIGHT_ACCENT,
    font=("Consolas", current_font_size + 1),
)
style.map("TEntry", fieldbackground=[("focus", "#552c00")]) 

# ---------------- Footer Frame (Packed FIRST with side='bottom') ----------------
footer_frame = ttk.Frame(root, style="Dark.TFrame", height=30)
footer_frame.pack(side="bottom", fill="x", padx=0, pady=0) 


author_credit = ttk.Label(
    footer_frame,
    text="Developed by Omar Ghayad From AREAV",
    font=("Consolas", 9, "bold"),
    style="Dark.TLabel",
    background=DARK_BG,
    foreground=BRIGHT_ACCENT
)
author_credit.pack(side="left", padx=30, pady=5) 


zoom_info = ttk.Label(
    footer_frame,
    text=f"Zoom: {mod_key}+ / {mod_key}-",
    font=("Consolas", 9, "italic"),
    style="Dark.TLabel",
    background=DARK_BG,
    foreground="#999999"
)
zoom_info.pack(side="right", padx=30, pady=5) 

# ---------------- Title (Logo/Icon & Text) ----------------
title_frame = ttk.Frame(root, style="Dark.TFrame")
title_frame.pack(pady=(20, 10), padx=30, fill="x") 

title_details_frame = ttk.Frame(title_frame, style="Dark.TFrame")
title_details_frame.pack(anchor="center") 

# 1. الأيقونة (🌐)
ttk.Label(
    title_details_frame, 
    text="🌐", 
    style="Header.Dark.TLabel",
    foreground=LIGHT_TEXT 
).pack(side="left", padx=(0, 10))

# 2. العنوان (SubZero)
title = ttk.Label(
    title_details_frame, 
    text="SubZero", 
    style="Header.Dark.TLabel",
)
title.pack(side="left")


# ---------------- Input Frame ----------------
frame_top = ttk.Frame(root, padding="15 15 15 15", style="Dark.TFrame")
frame_top.pack(fill="x", padx=30, pady=10)

ttk.Label(
    frame_top,
    text="Enter IP with NEW Prefix (Ex: 192.168.1.50/26):",
    font=("Consolas", 12, "bold"),
    style="Dark.TLabel",
    background=ACCENT_BG
).grid(row=0, column=0, sticky="w", padx=10)

ip_entry = ttk.Entry(frame_top, width=30, style="TEntry")
ip_entry.grid(row=0, column=1, padx=10, ipady=3)
ip_entry.insert(0, "") 

btn_calc = ttk.Button(
    frame_top,
    text="Calculate",
    command=calculate,
    cursor="hand2",
)
btn_calc.grid(row=0, column=2, padx=10)

frame_top.grid_columnconfigure(1, weight=1)

# ---------------- Basic Info Frame ----------------
basic_frame = ttk.Frame(root, padding="10", style="Dark.TFrame")
basic_frame.pack(fill="x", padx=30, pady=10)

ttk.Label(
    basic_frame,
    text="📊 Basic Network Information (Rules & Results)",
    font=("Consolas", 14, "bold"),
    style="Dark.TLabel",
    background=ACCENT_BG
).pack(pady=5, anchor="w")

basic_columns = ("Property", "Value")

basic_tree = ttk.Treeview(
    basic_frame, columns=basic_columns, show="headings", height=12
)
basic_tree.pack(side="left", fill="both", expand=True)

for col in basic_columns:
    basic_tree.heading(col, text=col)
    basic_tree.column(col, anchor="w", width=350)

basic_scroll = ttk.Scrollbar(
    basic_frame, orient="vertical", command=basic_tree.yview
)
basic_scroll.pack(side="right", fill="y")
basic_tree.configure(yscrollcommand=basic_scroll.set)

# ---------------- Subnet Table Frame ----------------
tree_frame = ttk.Frame(root, padding="10", style="Dark.TFrame")
tree_frame.pack(fill="both", expand=True, padx=30, pady=10)

ttk.Label(
    tree_frame,
    text="➗ Split Subnets Details", 
    font=("Consolas", 14, "bold"),
    style="Dark.TLabel",
    background=ACCENT_BG
).pack(pady=5, anchor="w")

columns = (
    "Subnet #",
    "Network Address",
    "First Host",
    "Last Host",
    "Broadcast Address",
    "Usable Hosts",
)

tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
tree.pack(side="left", fill="both", expand=True)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=100)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# ---------------- Row Tags ----------------
tree.tag_configure("oddrow", background="#2c2c2c", foreground=LIGHT_TEXT)
tree.tag_configure("evenrow", background="#1c1c1c", foreground=LIGHT_TEXT)
basic_tree.tag_configure("oddrow", background="#2c2c2c", foreground=LIGHT_TEXT)
basic_tree.tag_configure("evenrow", background="#1c1c1c", foreground=LIGHT_TEXT)
basic_tree.tag_configure(
    "binary_highlight", background=BRIGHT_ACCENT, foreground=LIGHT_TEXT, font=("Consolas", 10, "bold")
)

# ---------------- Key Bindings (Zoom & Copy/Paste) ----------------
root.bind(f"<{mod_key}-plus>", zoom_in)
root.bind(f"<{mod_key}-equal>", zoom_in)
root.bind(f"<{mod_key}-minus>", zoom_out)
root.bind(f"<{mod_key}-underscore>", zoom_out)
tree.bind(f"<{mod_key}-c>", copy_selected_cell)
basic_tree.bind(f"<{mod_key}-c>", copy_selected_cell)
tree.bind("<Button-3>", copy_selected_cell)
basic_tree.bind("<Button-3>", copy_selected_cell)

root.mainloop()