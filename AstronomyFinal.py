import threading
import tkinter as tk
import random
import requests
from datetime import datetime, timedelta

# -------------------- WINDOW SETUP --------------------
window = tk.Tk()
window.title("Space Weather!!🚀")
window.geometry("1000x600")
window.config(bg="black")

# -------------------- CANVAS FOR STARS --------------------
canvas = tk.Canvas(window, bg="black")
canvas.pack(fill="both", expand=True)

# -------------------- HEADER --------------------
header_label = tk.Label(
    canvas, text="Space Weather Dashboard 🚀☄️",
    font=("Courier New", 26, "bold"),
    fg="white", bg="black"
)
header_window = canvas.create_window(500, 50, window=header_label, anchor="n")

# -------------------- STAR EFFECT --------------------
stars = []
num_stars = 100

def create_star():
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    x = random.randint(0, max(width, 1))
    y = random.randint(0, max(height, 1))
    size = random.randint(1, 3)
    star = canvas.create_oval(x, y, x + size, y + size, fill="white", outline="")
    stars.append(star)

window.update()
for _ in range(num_stars):
    create_star()

def move_stars():
    try:
        if not window.winfo_exists():
            return
        height = canvas.winfo_height()
        for star in stars:
            x1, y1, x2, y2 = canvas.coords(star)
            canvas.move(star, 0, 2)
            if y1 > height:
                canvas.move(star, 0, -height)
        window.after(50, move_stars)
    except tk.TclError:
        return

# -------------------- SCROLLABLE DISPLAY --------------------
display_frame = tk.Frame(canvas, bg="black")
display_canvas = tk.Canvas(display_frame, bg="black", highlightthickness=0)
scrollbar = tk.Scrollbar(display_frame, orient="vertical", command=display_canvas.yview)
display_canvas.configure(yscrollcommand=scrollbar.set)

display_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

display_window = canvas.create_window(
    500, 150, window=display_frame, anchor="n", width=900, height=400
)

display_text = tk.Text(display_canvas, fg="white", bg="black",
                       font=("Courier New", 20), wrap="word")
display_text.pack(fill="both", expand=True)

def update_scroll_region(event=None):
    display_canvas.configure(scrollregion=display_canvas.bbox("all"))

display_text.bind("<Configure>", update_scroll_region)

# -------------------- API SETUP --------------------
apiKey = "0aWq8JafKFtJF4fsI1zzbRcqBs28pAIyKl4HCgh9"
api_cache = {}

# -------------------- DATE RANGE HELPER --------------------
def get_date_range(days_back=10):
    """Return (start_date, end_date) as ISO strings, ending today."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    return start_date.isoformat(), end_date.isoformat()

# -------------------- DESCRIBE FUNCTIONS --------------------
def describe_flares(flare_class):
    flare_class = flare_class.upper()
    if flare_class.startswith("A"):
        return "Very Minor - not noticeable 😛"
    elif flare_class.startswith("B"):
        return "Minor - could affect radio communications 😳"
    elif flare_class.startswith("C"):
        return "Moderate - minor radio disturbances 😬"
    elif flare_class.startswith("M"):
        return "Strong - may affect satellites and communications 😧"
    elif flare_class.startswith("X"):
        return "Extreme - could disrupt satellites and power grids 😨"
    else:
        return "Unknown intensity"

def describe_storm(kp):
    if kp <= 2:
        return "Quiet 🤫"
    elif kp <= 4:
        return "Unsettled 😖"
    elif kp <= 6:
        return "Active 😮"
    elif kp <= 7:
        return "Storm 🌩️"
    else:
        return "Severe Storm 😰"

def describe_cme(speed):
    if speed == "N/A":
        return "Unknown strength"
    try:
        speed = float(speed)
    except:
        return "Unknown strength"
    if speed < 500:
        return "Slow - unlikely to impact Earth 🌤️"
    elif speed < 1000:
        return "Moderate - possible impact, could cause geomagnetic affects 🌥️"
    elif speed < 2000:
        return "Fast - likely impact, may cause geomagnetic storms ⚡"
    else:
        return "Extreme - high impact expected, could disturb Earth's magnetic field 🌪️"

def describe_cme_note(note):
    if not note or note == "N/A":
        return "No additional notes at this time."
    note_lowercase = note.lower()
    if "halo" in note_lowercase:
        return "The CME is wide and may be coming towards Earth."
    elif "partial halo" in note_lowercase:
        return "The CME is somewhat wide and could affect Earth."
    elif "faint" in note_lowercase:
        return "The CME is weak and likely has little impact."
    elif "slow" in note_lowercase:
        return "The CME is moving slow, and is unlikely to cause any problems on Earth."
    elif "fast" in note_lowercase:
        return "The CME is moving fast, and could disturb Earth's magnetic field."
    else:
        return "A CME has been detected, but no specific details are available."

def describe_sep(intensity):
    try:
        intensity = float(intensity)
    except:
        return "Unknown intensity"
    if intensity < 1:
        return "Low  - little to no effect on Earth 🌎"
    elif intensity < 10:
        return "Moderate - Could affect satellites and astronauts in space"
    elif intensity < 100:
        return "High - radiation risk on satellites and astronauts"
    else:
        return "Extreme - Dangerous radiation event"

# -------------------- FORMAT FUNCTIONS --------------------
def format_flare_data(data):
    if not data:
        return "No flares recorded in this time range."
    text = ""
    for flare in data[:]:
        intensity = describe_flares(flare.get('classType', 'N/A'))
        time_str = flare.get('beginTime', 'N/A')
        try:
            time = datetime.strptime(time_str, "%Y-%m-%dT%H:%MZ")
            time_formatted = time.strftime("%b %d %Y %H:%M UTC")
        except:
            time_formatted = time_str
        text += f"- {flare.get('classType', 'N/A')} ({intensity})\n  Time: {time_formatted}\n"
    return text

def format_geomagnetic_storm_data(data):
    if not data:
        return "No geomagnetic storms recorded in this time range."
    text = ""
    for storm in data[:]:
        kp_values = storm.get('kpIndex', [])
        max_kp = max(kp_values) if kp_values else 0
        intensity = describe_storm(max_kp)
        start_str = storm.get('startTime', 'N/A')
        try:
            start_time = datetime.strptime(start_str, "%Y-%m-%dT%H:%MZ")
            start_formatted = start_time.strftime("%b %d %Y %H:%M UTC")
        except:
            start_formatted = start_str
        end_str = storm.get('endTime', 'N/A')
        try:
            end_time = datetime.strptime(end_str, "%Y-%m-%dT%H:%MZ")
            end_formatted = end_time.strftime("%b %d %Y %H:%M UTC")
        except:
            end_formatted = end_str
        text += f"- Max Kp Index: {max_kp} ({intensity})\n  From: {start_formatted}\n  To: {end_formatted}\n\n"
    return text

def format_cme_data(data):
    if not data:
        return "No CMEs recorded in this time range."
    text = ""
    for cme in data[:]:
        start_time = cme.get('startTime', 'N/A')
        source = cme.get('sourceLocation', 'N/A')
        raw_note = cme.get('note', 'N/A')
        note = describe_cme_note(raw_note)
        try:
            dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%MZ")
            start_formatted = dt.strftime("%b %d %Y %H:%M UTC")
        except:
            start_formatted = start_time
        analysis = cme.get('cmeAnalyses', [])
        if analysis:
            speed = analysis[0].get('speed', 'N/A')
            type_cme = analysis[0].get('cmeType')
            if not type_cme:
                type_cme = 'Not classified yet'
        else:
            speed = 'N/A'
            type_cme = 'Not classified yet'
        strength = describe_cme(speed)
        text += f"- CME from {source} on {start_formatted}\n"
        text += f"  Type: {type_cme}\n"
        text += f"  Speed: {speed} km/s ({strength})\n"
        if note and note != 'N/A':
            text += f"  Note: {note}\n"
    return text

def format_sep_data(data):
    if not data:
        return "No SEP events recorded in this time range."
    text = ""
    for sep in data[:5]:
        intensity_value = sep.get('peakInt', 'N/A')
        intensity = describe_sep(intensity_value)
        start_str = sep.get('startTime', 'N/A')
        try:
            start_time = datetime.strptime(start_str, "%Y-%m-%dT%H:%MZ")
            start_formatted = start_time.strftime("%b %d %Y %H:%M UTC")
        except:
            start_formatted = start_str
        peak_str = sep.get('peakTime', 'N/A')
        try:
            peak_time = datetime.strptime(peak_str, "%Y-%m-%dT%H:%MZ")
            peak_formatted = peak_time.strftime("%b %d %Y %H:%M UTC")
        except:
            peak_formatted = peak_str
        end_str = sep.get('endTime', 'N/A')
        try:
            end_time = datetime.strptime(end_str, "%Y-%m-%dT%H:%MZ")
            end_formatted = end_time.strftime("%b %d %Y %H:%M UTC")
        except:
            end_formatted = end_str
        text += f"- Peak Intensity: {intensity_value} pfu ({intensity})\n"
        text += f"  From: {start_formatted}\n  Peak: {peak_formatted}\n  To: {end_formatted}\n\n"
    return text

def format_coronal_holes_data(data):
    if not data:
        return "No coronal holes recorded in this time range."
    text = ""
    for ch in data[:5]:
        start_str = ch.get('startTime', 'N/A')
        try:
            dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%MZ")
            start_formatted = dt.strftime("%b %d %Y %H:%M UTC")
        except:
            start_formatted = start_str
        text += f"- Coronal Hole observed from {start_formatted}, location: {ch.get('location', 'N/A')}\n\n"
    return text

# -------------------- FETCH FUNCTIONS --------------------
def fetch_solar_flares():
    start_date, end_date = get_date_range()
    url = f"https://api.nasa.gov/DONKI/FLR?startDate={start_date}&endDate={end_date}&api_key={apiKey}"
    if url in api_cache:
        display_flares(api_cache[url])
        return
    try:
        data = requests.get(url).json()
        api_cache[url] = data
        display_flares(data)
    except Exception as e:
        display_text.delete("1.0", tk.END)
        display_text.insert(tk.END, f"Error fetching data: {e}")

def fetch_geomagnetic_storm():
    start_date, end_date = get_date_range()
    url = f"https://api.nasa.gov/DONKI/GST?startDate={start_date}&endDate={end_date}&api_key={apiKey}"
    if url in api_cache:
        display_geomagnetic_storm(api_cache[url])
        return
    try:
        data = requests.get(url).json()
        api_cache[url] = data
        display_geomagnetic_storm(data)
    except Exception as e:
        display_text.delete("1.0", tk.END)
        display_text.insert(tk.END, f"Error fetching data: {e}")

def fetch_cme():
    start_date, end_date = get_date_range()
    url = f"https://api.nasa.gov/DONKI/CME?startDate={start_date}&endDate={end_date}&api_key={apiKey}"
    if url in api_cache:
        display_cme(api_cache[url])
        return
    try:
        data = requests.get(url).json()
        api_cache[url] = data
        display_cme(data)
    except Exception as e:
        display_text.delete("1.0", tk.END)
        display_text.insert(tk.END, f"Error fetching data: {e}")

def fetch_sep():
    start_date, end_date = get_date_range()
    url = f"https://api.nasa.gov/DONKI/SEP?startDate={start_date}&endDate={end_date}&api_key={apiKey}"
    if url in api_cache:
        display_sep(api_cache[url])
        return
    try:
        data = requests.get(url).json()
        api_cache[url] = data
        display_sep(data)
    except Exception as e:
        display_text.delete("1.0", tk.END)
        display_text.insert(tk.END, f"Error fetching SEP data: {e}")

def fetch_coronal_holes():
    start_date, end_date = get_date_range()
    url = f"https://api.nasa.gov/DONKI/CH?startDate={start_date}&endDate={end_date}&api_key={apiKey}"
    if url in api_cache:
        display_coronal_holes(api_cache[url])
        return
    try:
        response = requests.get(url)
        if response.status_code != 200 or not response.text.strip():
            display_text.delete("1.0", tk.END)
            display_text.insert(tk.END, "No Coronal Holes data available for this date range.")
            return
        data = response.json()
        api_cache[url] = data
        display_coronal_holes(data)
    except Exception as e:
        display_text.delete("1.0", tk.END)
        display_text.insert(tk.END, f"Error fetching Coronal Holes data: {e}")


# -------------------- DISPLAY FUNCTIONS --------------------
def display_flares(data):
    display_text.delete("1.0", tk.END)
    text = "Solar Flares:\n" + format_flare_data(data)
    display_text.insert(tk.END, text)
    hide_main_buttons()
    back_button.place(x=50, y=80)

def display_geomagnetic_storm(data):
    display_text.delete("1.0", tk.END)
    text = "Geomagnetic Storms:\n" + format_geomagnetic_storm_data(data)
    display_text.insert(tk.END, text)
    hide_main_buttons()
    back_button.place(x=50, y=80)

def display_cme(data):
    display_text.delete("1.0", tk.END)
    text = "CMEs:\n" + format_cme_data(data)
    display_text.insert(tk.END, text)
    hide_main_buttons()
    back_button.place(x=50, y=80)

def display_sep(data):
    display_text.delete("1.0", tk.END)
    text = "SEP Events:\n" + format_sep_data(data)
    display_text.insert(tk.END, text)
    hide_main_buttons()
    back_button.place(x=50, y=80)

def display_coronal_holes(data):
    display_text.delete("1.0", tk.END)
    text = "Coronal Holes:\n" + format_coronal_holes_data(data)
    display_text.insert(tk.END, text)
    hide_main_buttons()
    back_button.place(x=50, y=80)

# -------------------- BUTTON HELPERS --------------------
def hide_main_buttons():
    solar_flare_button.place_forget()
    geomagnetic_storm_button.place_forget()
    cme_button.place_forget()
    sep_button.place_forget()
    coronal_holes_button.place_forget()

def show_main_buttons():
    solar_flare_button.place(x=50, y=200)
    geomagnetic_storm_button.place(x=50, y=260)
    cme_button.place(x=50, y=320)
    sep_button.place(x=50, y=380)
    coronal_holes_button.place(x=50, y=440)

# -------------------- SHOW PAGE FUNCTIONS --------------------
def show_solar_flare_page():
    display_text.delete("1.0", tk.END)
    display_text.insert(tk.END, "Loading...")
    hide_main_buttons()
    back_button.place(x=50, y=80)
    threading.Thread(target=fetch_solar_flares, daemon=True).start()

def show_geomagnetic_storm_page():
    display_text.delete("1.0", tk.END)
    display_text.insert(tk.END, "Loading...")
    hide_main_buttons()
    back_button.place(x=50, y=80)
    threading.Thread(target=fetch_geomagnetic_storm, daemon=True).start()

def show_cme_page():
    display_text.delete("1.0", tk.END)
    display_text.insert(tk.END, "Loading...")
    hide_main_buttons()
    back_button.place(x=50, y=80)
    threading.Thread(target=fetch_cme, daemon=True).start()

def show_sep_page():
    display_text.delete("1.0", tk.END)
    display_text.insert(tk.END, "Loading...")
    hide_main_buttons()
    back_button.place(x=50, y=80)
    threading.Thread(target=fetch_sep, daemon=True).start()

def show_coronal_holes_page():
    display_text.delete("1.0", tk.END)
    display_text.insert(tk.END, "Loading...")
    hide_main_buttons()
    back_button.place(x=50, y=80)
    threading.Thread(target=fetch_coronal_holes, daemon=True).start()

def back_to_menu():
    display_text.delete("1.0", tk.END)
    back_button.place_forget()
    show_main_buttons()

# -------------------- BUTTONS --------------------
button_font = ("Courier New", 26, "bold")

solar_flare_button = tk.Button(canvas, text="Solar Flares", command=show_solar_flare_page,
                               font=button_font, bg="white", fg="black")
geomagnetic_storm_button = tk.Button(canvas, text="Geomagnetic Storms", command=show_geomagnetic_storm_page,
                                    font=button_font, bg="white", fg="black")
cme_button = tk.Button(canvas, text="Coronal Mass Ejections (CMEs)", command=show_cme_page,
                       font=button_font, bg="white", fg="black")
sep_button = tk.Button(canvas, text="Solar Energetic Particles (SEP)", command=show_sep_page,
                       font=button_font, bg="white", fg="black")
coronal_holes_button = tk.Button(canvas, text="Coronal Holes", command=show_coronal_holes_page,
                                 font=button_font, bg="white", fg="black")
back_button = tk.Button(canvas, text="Back", command=back_to_menu,
                        font=button_font, bg="white", fg="black")

show_main_buttons()
move_stars()
window.mainloop()