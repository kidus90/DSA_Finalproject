import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Node:
    def __init__(self, value): 
        """on this part of the code it create a node with a value and a next value"""
        self.value = value
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        """this function creates a node colled front with a value 
        of none and a size of 0 while the capacity is the storage 
        it would take up for the linked list"""
        self.front = None
        self.size = 0
        self.capacity = capacity

    def is_empty(self):
        return self.front is None

    def search(self, value):
        """this function searches for a value in the linked list using while loop"""
        current = self.front
        while current is not None:
            if current.value == value:
                print("Value found: Ture")
                return True
            if current.next is None:
                break
            current = current.next
        print("Value not found: False")
        return False

    def get(self, value):
        """this function gets a value form the user then checks if the value is in the linked list
        if it is it removes the value and adds it to the front of the linked list"""
        if self.search(value):
            self.remove_node(value)
        self.put(value)

    def put(self, value):
        """this function adds a value to the front of the linked list"""
        new_node = Node(value)
        if self.is_empty():
            self.front = new_node
        else:
            new_node.next = self.front
            self.front = new_node
        self.size += 1

        """ this part of the code checks if the size of the linked list is greater than 
        the capacity if so it would remove the last node in the linked list"""
        if self.size > self.capacity:
            current_node = self.front
            previous_node = None
            while current_node.next is not None:
                previous_node = current_node
                current_node = current_node.next

            if previous_node:
                previous_node.next = None
            else:
                self.front = None
            self.size -= 1

    def remove_node(self, value):
        prev = None
        current_node = self.front

        if current_node is None:
            return

        if current_node.value == value:
            """on this code it removes the value that is a the front of the linked list"""
            """then decreases the size of the linked list"""
            self.front = current_node.next
            self.size -= 1
            return

        while current_node is not None and current_node.value != value:
            """in this code it removes a node that is in between nodes"""
            prev = current_node
            current_node = current_node.next

        prev.next = current_node.next 
        """removing the current node"""
        self.size -= 1

    def display(self):
        f = self.front
        print("LRU Cache starts here")
        print("_______________________")
        while f is not None:
            print(f.value)
            f = f.next
        print("_______________________\n")

def add_word():
    """this function adds a word to the linked list 
    it also checks if the capacity is set or not if not raises error message"""
    if lru_cache is None:
        messagebox.showerror("Error", "Please set the capacity first.")
        return
    word = entry.get()
    lru_cache.get(word)
    lru_cache.display()
    update_table()

def set_capacity():
    """this function sets the capacity of the linked list"""
    global lru_cache
    try:
        cap = int(capacity_entry.get())
        lru_cache = LRUCache(cap)
        capacity_entry.config(state='disabled')
        set_capacity_button.config(state='disabled')
        create_table(cap)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid capacity")

def reset():
    """this function resets the linked list and the table"""
    global lru_cache
    lru_cache = None
    capacity_entry.config(state='normal')
    capacity_entry.delete(0, tk.END)
    set_capacity_button.config(state='normal')
    for i in table.get_children():
        table.delete(i)

def create_table(capacity):
    """creates a table with the capacity of the linked list"""
    global table
    table = ttk.Treeview(UI_frame, columns=["0"], show='headings', height=capacity)
    table.heading("0", text="LRU Cache")
    table.column("0", width=100)
    table.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

def update_table():
    """updates the tables on every entery of nodes"""
    global table
    for i in table.get_children():
        table.delete(i)
    values = []
    current = lru_cache.front
    while current is not None:
        values.append(current.value)
        current = current.next
    for value in values:
        table.insert('', 'end', values=[value])

root = tk.Tk()
root.title('LRU Cache')
root.maxsize(1000, 900)

UI_frame = tk.Frame(root, width=600, height=200, bg='light grey')
UI_frame.pack(padx=10, pady=10)

tk.Label(UI_frame, text="Please enter a word: ", bg='light grey').grid(row=0, column=0, padx=10, pady=5)
entry = tk.Entry(UI_frame)
entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(UI_frame, text="Please enter capacity: ", bg='light grey').grid(row=1, column=0, padx=10, pady=5)
capacity_entry = tk.Entry(UI_frame)
capacity_entry.grid(row=1, column=1, padx=10, pady=5)

set_capacity_button = tk.Button(UI_frame, text="Set Capacity", command=set_capacity)
set_capacity_button.grid(row=1, column=2, padx=10, pady=5)

tk.Button(UI_frame, text="Add Word", command=add_word).grid(row=0, column=2, padx=10, pady=5)

reset_button = tk.Button(UI_frame, text="Reset", command=reset)
reset_button.grid(row=3, column=2, padx=10, pady=5)

lru_cache = None

if __name__ == "__main__":
    root.mainloop()