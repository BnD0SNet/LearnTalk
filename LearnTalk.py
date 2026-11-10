import re
import os
import sys
import json
import time
import queue
import requests
import threading
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import scrolledtext

FILE = "memory.json"
last_question = ""
command_queue = queue.Queue()

def load_data():
	if os.path.exists(FILE):
		with open(FILE, "r", encoding="utf-8") as read_file:
			data = json.load(read_file)
			return data
	else:
		default_memory = {"hello": "hello!"}
		messagebox.showinfo("Memory System", f"File {FILE} not found! Created a new database.")
		with open(FILE, "w", encoding="utf-8") as file:
			json.dump(default_memory, file, ensure_ascii=False, indent=4)
			return default_memory


def save_data(data):
	if os.path.exists(FILE):
		with open(FILE, "w", encoding="utf-8") as rewritten_file:
			json.dump(data, rewritten_file, ensure_ascii=False, indent=4)
	else:
		messagebox.showwarning("Memory System", f"File {FILE} not found! Created a new database.")

current_memory = load_data()

window = tk.Tk()
window.title("LearnTalk AI")
window.geometry("800x624")
window.config(bg="#2c3e50")

def bot_thinking(clean_command):
	global last_question
	chat_history.config(state=tk.NORMAL)
	chat_history.insert(tk.END, f"You: {clean_command}\n")

	if last_question == "":
		if clean_command == "exit":
			chat_history.insert(tk.END, "Bot: Exiting...\n\n")
			window.destroy()
			sys.exit()

		elif clean_command == "commands":
			chat_history.insert(tk.END, "Bot: exit, commands, fact, calculator, time\n\n")

		elif clean_command == "fact":
			url = "https://jsph.pl"
			response = requests.get(url)
			if response.status_code == 200:
				fact_data = response.json()
				fact_text = fact_data.get("text", "Could not retrieve fact text.")
				chat_history.insert(tk.END, f"Bot: {fact_text}\n\n")
			else:
				chat_history.insert(tk.END, f"Bot: Website error ({response.status_code})\n\n")

		elif clean_command == "calculator":
			chat_history.insert(tk.END, "Bot: Opening calculator...\n\n")
			subprocess.Popen("calc.exe")

		elif clean_command == "time":
			filtered_time = datetime.now().strftime("%H:%M")
			chat_history.insert(tk.END, f"Bot: Current time is {filtered_time}\n\n")

		elif clean_command in current_memory:
			time.sleep(0.2)
			chat_history.insert(tk.END, f"Bot: {current_memory[clean_command]}\n\n")

		else:
			time.sleep(0.2)
			chat_history.insert(tk.END, "Bot: I don't know the answer. What should I reply?\n\n")
			last_question = clean_command

	else:
		current_memory[last_question] = clean_command
		save_data(current_memory)
		chat_history.insert(tk.END, "Bot: Got it, remembered.\n\n")
		last_question = ""

	chat_history.see(tk.END)
	chat_history.config(state=tk.DISABLED)

def send_message(event=None):
	command = user_input.get().lower()
	clean_command = re.sub(r'[^\w\s]', '', command)
	command_queue.put(clean_command)
	think = threading.Thread(target=bot_thinking, args=(clean_command,))
	think.start()
	user_input.delete(0, tk.END)

def log_monitor():
	while True:
		if not command_queue.empty():
			log_command = command_queue.get()
			print(f"[LOG]: {log_command}")
		else:
			continue
		time.sleep(1)

chat_history = scrolledtext.ScrolledText(window, width=80, height=30)
chat_history.config(state=tk.DISABLED)
chat_history.pack(pady=10)

user_input = tk.Entry(window)
user_input.pack()

send_button = tk.Button(window, text="➤", command=send_message)
send_button.config(bg="#3498db", fg="#90EE90", font=("Arial", 10, "bold"), width=10)
send_button.pack()

monitoring = threading.Thread(target=log_monitor, daemon=True)
monitoring.start()

window.bind('<Return>', send_message)
window.mainloop()
