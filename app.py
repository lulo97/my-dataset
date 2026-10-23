import ctypes
import json
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk


# Enable DPI awareness before creating the Tk window.
def configure_dpi():
    if sys.platform == "win32":
        try:
            if sys.getwindowsversion().build >= 22000:  # Windows 11
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(1)
                except (AttributeError, OSError):
                    try:
                        ctypes.windll.user32.SetProcessDPIAware()
                    except (AttributeError, OSError):
                        pass
                return 1.25
        except (AttributeError, OSError):
            pass

    return 1.0


UI_SCALE = configure_dpi()


def px(value):
    """Scale pixel-based layout dimensions."""
    return round(value * UI_SCALE)


# Save files in the same directory as this Python script.
APP_DIR = Path(__file__).resolve().parent


root = tk.Tk()
root.title("JSONL Input Logger")

# Tk scaling is expressed in pixels per point.
if UI_SCALE != 1.0:
    root.tk.call("tk", "scaling", (96 / 72) * UI_SCALE)

root.geometry(f"{px(900)}x{px(650)}")
root.minsize(px(650), px(450))


# Configure the resizable layout.
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main = ttk.Frame(root, padding=px(10))
main.grid(row=0, column=0, sticky="nsew")
main.columnconfigure(0, weight=1)
main.rowconfigure(0, weight=1)


fields = ttk.Frame(main)
fields.grid(row=0, column=0, sticky="nsew", pady=(0, px(10)))
fields.columnconfigure(0, weight=1)
fields.columnconfigure(1, weight=1)
fields.rowconfigure(0, weight=1)


def create_multiline_field(parent, name, column):
    frame = ttk.LabelFrame(parent, text=name, padding=px(8))
    frame.grid(
        row=0,
        column=column,
        sticky="nsew",
        padx=(0, px(5)) if column == 0 else (px(5), 0),
    )
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    text = tk.Text(
        frame,
        wrap="word",
        undo=True,
        font=("Segoe UI", 10),
        padx=px(5),
        pady=px(5),
    )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=text.yview,
    )
    text.configure(yscrollcommand=scrollbar.set)

    text.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    return text


input_box = create_multiline_field(fields, "input", 0)
output_box = create_multiline_field(fields, "output", 1)


status_var = tk.StringVar(value="Ready")


def submit():
    input_value = input_box.get("1.0", "end-1c")
    output_value = output_box.get("1.0", "end-1c")

    if not input_value.strip() and not output_value.strip():
        status_var.set("Enter text in at least one field.")
        return

    # Calculate the date at submission time.
    filename = datetime.now().strftime("%Y%m%d") + ".jsonl"
    filepath = APP_DIR / filename

    record = {
        "input": input_value,
        "output": output_value,
    }

    try:
        # Create the file if missing; otherwise append a new JSON line.
        with filepath.open("a", encoding="utf-8", newline="\n") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

        status_var.set(f"Saved to {filename}")

        # Clear fields after a successful save.
        input_box.delete("1.0", tk.END)
        output_box.delete("1.0", tk.END)
        input_box.focus_set()

    except OSError as error:
        messagebox.showerror(
            "Save failed",
            f"Could not write to:\n{filepath}\n\n{error}",
        )


bottom = ttk.Frame(main)
bottom.grid(row=1, column=0, sticky="ew")
bottom.columnconfigure(0, weight=1)

status_label = ttk.Label(bottom, textvariable=status_var)
status_label.grid(row=0, column=0, sticky="w")

submit_button = ttk.Button(
    bottom,
    text="Submit",
    command=submit,
)
submit_button.grid(row=0, column=1, sticky="e", padx=(px(10), 0))

root.bind("<Control-Return>", lambda event: submit())

input_box.focus_set()
root.mainloop()