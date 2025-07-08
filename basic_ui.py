import tkinter as tk
from tkinter import *
from tkinter import messagebox

import asyncio
import threading

from protocol import requests
from client_async import Client

root = tk.Tk()
root.withdraw() 

# Create a new event loop
loop = asyncio.new_event_loop()

# Start the loop in a background thread
def run_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=run_loop, daemon=True).start()

client: Client | None = None

call_active = False  # Keeps track of whether a call is ongoing
user_verified = True # Keeps track of whether user has a name


async def create_and_connect_client(user_id):
    global client
    client = Client(user_id)
    await client.connect('localhost', 6969)
    print("Client connected:", client)

    client.set_event_handlers(
        on_incoming_call=notify_incoming_call,
        on_call_ended=lambda: status_var.set("Call Ended"),
        # on_placing_call=open_call_window
        scheduler=root.after
    )

    asyncio.create_task(client.listen())

def send_to_server(message_dict):
    global conn
    if not conn:
        print("Not connected to server.")
        return

    asyncio.run_coroutine_threadsafe(conn.write_prefixed_json(message_dict), loop)

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
    close_btn = tk.Button(call_window, text="End Call", bg="#3d3434", fg="white", font=("Helvetica", 10),
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

def enter_username():
    popup = tk.Toplevel()
    popup.geometry("400x200")
    popup.title("Enter Username")
    popup.configure(bg="#1fb230")

    label = tk.Label(popup, text="Please enter your username", font=("Helvetica", 11), bg="#1fb230")
    label.pack(pady=20)

    user_name_entry = tk.Entry(popup)
    user_name_entry.pack(pady=20)

    def set_username():
        entered_name = user_name_entry.get().strip()
        if entered_name:
            name_var.set(entered_name)
            print(f"Username set to: {entered_name}")
            popup.destroy()
            root.deiconify()  # Show the main window
            # Create and connect the client asynchronously
            asyncio.run_coroutine_threadsafe(create_and_connect_client(entered_name), loop)
        else:
            messagebox.showwarning("Input Error", "Username cannot be empty.")

    done_btn = tk.Button(popup, text="Done", bg="#27ae60", fg="white",
                         font=("Helvetica", 10), command=set_username)
    done_btn.pack(pady=20)

def start_call():
    global call_active
    call_active = True
    status_var.set("Calling...")
    print("Start Call clicked")
    send_to_server("CALL_INIT")
    update_buttons()


def place_call():
    """Open a dialog to enter the ID of the user to call."""
    popup = tk.Toplevel(root)
    popup.title("Place Call")
    popup.geometry("350x180")
    popup.configure(bg="#dff9fb")

    label = tk.Label(popup, text="Enter the ID of the user to call:", font=("Helvetica", 11), bg="#dff9fb")
    label.pack(pady=15)

    entry = tk.Entry(popup, font=("Helvetica", 11))
    entry.pack(pady=10)

    def do_call():
        callee_id = entry.get().strip()
        if callee_id:
            popup.destroy()
            # This should be an async call; use run_coroutine_threadsafe
            future = asyncio.run_coroutine_threadsafe(client.place_call(callee_id), loop)
            try:
                isplaced = future.result
                if isplaced:
                    open_call_window()
            except Exception as e:
                print("Call failed:", e)
                messagebox.showerror("Error", f"Call failed: {e}")
            status_var.set(f"Calling {callee_id}...")
        else:
            messagebox.showwarning("Input Error", "User ID cannot be empty.")

    call_btn = tk.Button(popup, text="Call", command=do_call, bg="#2980b9", fg="white")
    call_btn.pack(pady=10)

def place_call_alt():
    """Open a dialog with a dropdown of online users to call."""
    try:
        future = asyncio.run_coroutine_threadsafe(client.show_online_users(), loop)
        online_users = future.result(timeout=3)
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch online users: {e}")
        return

    if not online_users:
        messagebox.showinfo("No Users", "No users are currently online.")
        return

    popup = tk.Toplevel(root)
    popup.title("Place Call (Dropdown)")
    popup.geometry("350x180")
    popup.configure(bg="#dff9fb")

    label = tk.Label(popup, text="Select a user to call:", font=("Helvetica", 11), bg="#dff9fb")
    label.pack(pady=15)

    selected_user = tk.StringVar(popup)
    selected_user.set(online_users[0])

    dropdown = tk.OptionMenu(popup, selected_user, *online_users)
    dropdown.config(font=("Helvetica", 11))
    dropdown.pack(pady=10)

    def do_call():
        callee_id = selected_user.get()
        popup.destroy()
        asyncio.run_coroutine_threadsafe(client.place_call(callee_id), loop)
        status_var.set(f"Calling {callee_id}...")

    call_btn = tk.Button(popup, text="Call", command=do_call, bg="#2980b9", fg="white")
    call_btn.pack(pady=10)

def accept_call():
    global call_active
    call_active = True
    status_var.set("Call accepted")
    print("Call accepted")
    update_buttons()
    open_call_window()

def reject_call():
    global call_active
    status_var.set("Call rejected")
    print("Call rejected")
    open_reject_popup()


def end_call():
    global call_active
    call_active = False
    status_var.set("Call ended")
    print("Call ended")
    send_to_server("CALL_END")
    update_buttons()

def show_online_users():
    """Show a popup with the list of currently online users."""
    # This assumes you have a client object with a show_online_users() method that returns a list.
    try:
        # This should be an async call in reality; here we use run_coroutine_threadsafe for the thread.
        future = asyncio.run_coroutine_threadsafe(client.show_online_users(), loop)
        online_users = future.result(timeout=3)
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch online users: {e}")
        return

    popup = tk.Toplevel(root)
    popup.title("Online Users")
    popup.geometry("300x400")
    popup.configure(bg="#f1f2f6")

    label = tk.Label(popup, text="Online Users", font=("Helvetica", 13, "bold"), bg="#f1f2f6")
    label.pack(pady=10)

    users_listbox = tk.Listbox(popup, font=("Helvetica", 11), width=30)
    users_listbox.pack(pady=10, fill="both", expand=True)

    for user in online_users:
        users_listbox.insert(tk.END, user)

    close_btn = tk.Button(popup, text="Close", command=popup.destroy, bg="#636e72", fg="white")
    close_btn.pack(pady=10)

def notify_incoming_call(caller_id, room_id):
    print("notify_incoming_call called with:", caller_id)
    root.deiconify()
    response = messagebox.askquestion("Incoming Call", f"{caller_id} is calling. Accept?")
    if response == 'yes':
        print("Incoming call accepted")
        accept_call()
        asyncio.run_coroutine_threadsafe(
            client.respond_to_call(caller_ID=caller_id, is_accepted=True, room_id=room_id), loop
        )
    else:
        print("Incoming call rejected")
        asyncio.run_coroutine_threadsafe(
            client.respond_to_call(caller_ID=caller_id, is_accepted=False, room_id=room_id), loop
        )
        reject_call()

if __name__ == "__main__":
    # Main GUI setup
    root.title("Teams Lite")
    root.geometry("500x700")
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

    name_var = tk.StringVar()
    name_var.set("Please enter your name first!")

    status_label = tk.Label(root, textvariable=status_var, font=('Helvetica', 12), bg="#dfe6e9", fg="#2c3e50",
                            width=30, relief="sunken")
    status_label.pack(pady=20)

    user_name_label = tk.Label(root, textvariable=name_var, font=('Helvetica', 12), bg="#dfe6e9", fg="#2c3e50",
                            width=30, relief="sunken")
    user_name_label.pack(pady=20)

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
    # test_btn = make_button("Simulate Incoming Call", simulate_incoming_call, "#8e44ad")
    entername_btn = make_button("Set Username", enter_username, "#90b228")
    mute_rad_btn = Radiobutton(root, text = "Mute")

    show_online_btn = make_button("Show Online Users", show_online_users, "#16a085")
    place_call_btn = make_button("Place Call", place_call, "#2980b9")
    place_call_alt_btn = make_button("Place Call (Dropdown)", place_call_alt, "#27ae60")



    # Pack initial buttons
    # entername_btn.pack(pady=7)
    # start_btn.pack(pady=7)
    # accept_btn.pack(pady=7)
    # reject_btn.pack(pady=7)
    show_online_btn.pack(pady=7)
    place_call_btn.pack(pady=7)
    place_call_alt_btn.pack(pady=7)
    # test_btn.pack(pady=10)
    update_buttons()  # Handle end_btn visibility

    # start_btn.config(state="disabled")
    # accept_btn.config(state="disabled")
    # reject_btn.config(state="disabled")

    # Footer
    footer = tk.Label(root, text="Video call", font=("Helvetica", 9), bg="#ecf0f1", fg="#7f8c8d")
    footer.pack(side="bottom", pady=10)

    enter_username()
    root.mainloop()