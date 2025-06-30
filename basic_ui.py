import tkinter as tk
from tkinter import *
from tkinter import messagebox


call_active = False  # Keeps track of whether a call is ongoing


def send_to_server(message):
    print(f"[Sent to server] {message}")


def update_buttons():
    if call_active:
        start_btn.config(state="disabled")
        accept_btn.config(state="disabled")
        reject_btn.config(state="disabled")
        end_btn.pack(pady=10)
    else:
        start_btn.config(state="normal")
        accept_btn.config(state="normal")
        reject_btn.config(state="normal")
        end_btn.pack_forget()

def open_call_window():

    # call_window is like root, but since are opening a new window with TopLevel, we are giving it a new name
    call_window = tk.Toplevel(root)
    call_window.title("Call in Progress")
    call_window.geometry("1200x600")
    call_window.configure(bg="#dff9fb")
    call_window.resizable(True, True)

    video_frame = tk.Frame(call_window)
    video_frame.pack(pady = 20)

    # Caller video placeholder
    caller_video = tk.Label(video_frame, text="Your Video", bg="black", fg="white",
                            width=50, height=20, font=("Helvetica", 10))
    caller_video.grid(row=0, column=0, padx=10)

    # Callee video placeholder
    callee_video = tk.Label(video_frame, text="Caller Video", bg="gray", fg="white",
                            width=50, height=20, font=("Helvetica", 10))
    callee_video.grid(row=0, column=1, padx=10)

    # Call status message
    msg = tk.Label(call_window, text="You're on a call.", font=("Helvetica", 14), bg="#dff9fb")
    msg.pack(pady=40)

    # Mute button
    

    # End call button
    close_btn = tk.Button(call_window, text="End Call", bg="#eb4d4b", fg="white", font=("Helvetica", 10),
                          width=20, command=lambda: [call_window.destroy(), end_call()])
    close_btn.pack(pady=20)

def open_reject_popup():
    popup = tk.Toplevel(root)
    popup.title("Call Rejected")
    popup.geometry("250x120")
    popup.configure(bg="#ffeaa7")

    label = tk.Label(popup, text="Call rejected.", font=("Helvetica", 11), bg="#ffeaa7")
    label.pack(pady=20)

    popup.after(2000, popup.destroy)  # Auto close after 2 seconds

def start_call():
    global call_active
    call_active = True
    status_var.set("Calling...")
    print("Start Call clicked")
    send_to_server("CALL_INIT")
    update_buttons()

def accept_call():
    global call_active
    call_active = True
    status_var.set("Call accepted")
    print("Call accepted")
    send_to_server("CALL_ACCEPT")
    update_buttons()
    open_call_window()

def reject_call():
    global call_active
    status_var.set("Call rejected")
    print("Call rejected")
    send_to_server("CALL_REJECT")
    open_reject_popup()

def end_call():
    global call_active
    call_active = False
    status_var.set("Call ended")
    print("Call ended")
    send_to_server("CALL_END")
    update_buttons()

def simulate_incoming_call():
    response = messagebox.askquestion("Incoming Call", "You have an incoming call. Accept?")
    if response == 'yes':
        print("Incoming call accepted")
        accept_call()
    else:
        print("Incoming call rejected")
        reject_call()

# Main GUI setup
root = tk.Tk()
root.title("Teams Lite")
root.geometry("350x470")
root.configure(bg="#ecf0f1")
root.resizable(False, False)

# Top "profile bar"
header = tk.Frame(root, bg="#34495e", height=60)
header.pack(fill="x")

title_label = tk.Label(header, text="Video Call UI", font=("Helvetica", 14, "bold"), fg="white", bg="#34495e")
title_label.pack(pady=15)

# Status
status_var = tk.StringVar()
status_var.set("Idle")

status_label = tk.Label(root, textvariable=status_var, font=('Helvetica', 12), bg="#dfe6e9", fg="#2c3e50",
                        width=30, relief="sunken")
status_label.pack(pady=20)

# Button styling helper
def make_button(text, command, color):
    return tk.Button(
        root, text=text, command=command,
        font=("Helvetica", 11), bg=color, fg="white",
        activebackground="#2c3e50", relief="ridge",
        width=25, height=2, bd=0, cursor="hand2"
    )

# Buttons
start_btn = make_button("Start Call", start_call, "#2980b9")
accept_btn = make_button("Accept Call", accept_call, "#27ae60")
reject_btn = make_button("Reject Call", reject_call, "#c0392b")
end_btn = make_button("End Call", end_call, "#7f8c8d")
test_btn = make_button("Simulate Incoming Call", simulate_incoming_call, "#8e44ad")
mute_rad_btn = Radiobutton(root, text = "Mute")

# Pack initial buttons
start_btn.pack(pady=7)
accept_btn.pack(pady=7)
reject_btn.pack(pady=7)
test_btn.pack(pady=10)
update_buttons()  # Handle end_btn visibility

# Footer
footer = tk.Label(root, text="Video call", font=("Helvetica", 9), bg="#ecf0f1", fg="#7f8c8d")
footer.pack(side="bottom", pady=10)

root.mainloop()


