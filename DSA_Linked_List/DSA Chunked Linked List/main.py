import sys
import os
import asyncio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget,
                             QPushButton, QFileDialog, QHBoxLayout, QCheckBox, QInputDialog, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject
import threading
import hashlib

class SignalEmitter(QObject):
    """
    SignalEmitter class is used to emit signals for various events such as devices discovered,
    file sent, file received, and error occurred.
    """
    devices_discovered = pyqtSignal(list)
    file_sent = pyqtSignal()
    file_received = pyqtSignal()
    error_occurred = pyqtSignal(str)

class LinkedList:
    """
    LinkedList class represents a singly linked list where each node stores a chunk of data,
    the SHA-256 hash of the next node's data, and a pointer to the next node.
    """
    class Node:
        def __init__(self, data):
            self.data = data
            self.next_checksum = None  # SHA-256 hash of the next node’s data
            self.next = None

    def __init__(self):
        self.head = None

    def add(self, data):
        """
        Adds a new node with the given data to the end of the linked list.
        """
        new_node = self.Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
            # Compute the SHA-256 hash of the new node's data
            current.next_checksum = hashlib.sha256(new_node.data).hexdigest()
            #If the linked list is not empty, it initializes current to the head of the linked list.
            #It then iterates through the linked list until it finds the last node (where current.next is None). (the while loop iterates until current.next is None. Then adds the new node to the end of the linked list.)
            #The new node is added to the end of the linked list by setting current.next to new_node.

    def delete(self, data):
        """
        Deletes the node with the given data from the linked list.
        """
        if not self.head:
            return
        if self.head.data == data:
            self.head = self.head.next
            return
        #This checks if the data of the head node matches the data to be deleted.
        #If the head node contains the data to be deleted, the head is updated to point to the next node, effectively removing the head node from the linked list.
        #The method then returns because the node has been deleted.
        current = self.head
        while current.next and current.next.data != data:
            current = current.next
        #If the head node does not contain the data to be deleted, the method initializes current to the head of the linked list.
        #It then iterates through the linked list to find the node whose next node contains the data to be deleted.
        #The loop continues until current.next is None (end of the list) or current.next.data matches the data to be deleted.
        if current.next:
            current.next = current.next.next
            #If the next node contains the data to be deleted, the current node is updated to point to the node after the next node, effectively removing the next node from the linked list.
            if current.next:
                current.next_checksum = hashlib.sha256(current.next.data).hexdigest()
            else:
                current.next_checksum = None
            #If the next node exists, the current node's next_checksum is updated to the SHA-256 hash of the next node's data.

    def to_list(self):
        """
        Converts the linked list to a list of data chunks.
        """
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def is_empty(self):
        """
        Checks if the linked list is empty.
        """
        return self.head is None

    def verify_integrity(self):
        """
        Verifies the integrity of the linked list by checking if the next_checksum matches
        the actual hash of the next node's data.
        """
        current = self.head
        while current and current.next:
            expected_checksum = hashlib.sha256(current.next.data).hexdigest()
            if current.next_checksum != expected_checksum:
                raise ValueError("Data corruption detected")
            current = current.next

    @staticmethod
    def split_file(file_data, chunk_size):
        """
        Splits the given file data into chunks of the specified size.
        def split_file(file_data, chunk_size): This is the definition of the split_file method. It takes two parameters: file_data (the data of the file to be split) and chunk_size (the size of each chunk).
        """
        chunks = [file_data[i:i + chunk_size] for i in range(0, len(file_data), chunk_size)]
        "List Comprehension: This line uses a list comprehension to create a list of chunks from file_data.range(0, len(file_data), chunk_size): range(start, stop, step): Generates a sequence of numbers starting from 0 to len(file_data) (exclusive) with a step size of chunk_size.This means it will generate indices 0, chunk_size, 2*chunk_size, 3*chunk_size, ... up to the length of file_data. file_data[i:i + chunk_size]:For each index i generated by the range, this slices file_data from index i to i + chunk_size.This creates a chunk of data of size chunk_size.List Construction:The list comprehension collects all these chunks into a list called chunks."
        return chunks

class ChunkListWindow(QMainWindow):
    """
    ChunkListWindow class represents the main window of the application. It provides a UI for
    loading a file, splitting it into chunks, adding chunks to a linked list, verifying integrity,
    and displaying the chunks.
    """
    def __init__(self, file_path, chunk_size):
        super().__init__()
        self.setWindowTitle("Chunk List Viewer")
        self.setGeometry(100, 100, 600, 400)
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.received_file_path = "received_file.bin"  # Path to store received data

        # Create an empty file to store received data
        open(self.received_file_path, 'wb').close()

        self.chunk_list_widget = QListWidget()
        self.load_chunks()

        self.signal_emitter = SignalEmitter()
        self.signal_emitter.devices_discovered.connect(self.on_devices_discovered)
        self.signal_emitter.file_sent.connect(self.on_file_sent)
        self.signal_emitter.file_received.connect(self.on_file_received)
        self.signal_emitter.error_occurred.connect(self.on_error_occurred)
        send_button = QPushButton("Send Data")
        send_button.setFixedSize(100, 30)
        send_button.clicked.connect(self.send_data)

        receive_button = QPushButton("Receive Data")
        receive_button.setFixedSize(100, 30)
        receive_button.clicked.connect(self.show_received_data)

        input_word_button = QPushButton("Input Word")
        input_word_button.setFixedSize(100, 30)
        input_word_button.clicked.connect(self.input_word)

        delete_selected_button = QPushButton("Delete Selected")
        delete_selected_button.setFixedSize(100, 30)
        delete_selected_button.clicked.connect(self.delete_selected)

        dark_mode_checkbox = QCheckBox("Dark Mode")
        dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(send_button)
        button_layout.addWidget(receive_button)
        button_layout.addWidget(input_word_button)
        button_layout.addWidget(delete_selected_button)
        button_layout.addStretch(1)

        layout = QVBoxLayout()
        layout.addWidget(self.chunk_list_widget)
        layout.addLayout(button_layout)
        layout.addWidget(dark_mode_checkbox)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.apply_stylesheet()

    def apply_stylesheet(self):
        """
        Applies a stylesheet to the application for a modern look.
        """
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

    def load_chunks(self):
        """
        Loads the file and splits it into chunks, then adds the chunks to the linked list.
        """
        if not os.path.exists(self.file_path):
            QMessageBox.critical(self, "Error", f"File not found: {self.file_path}")
            return
        with open(self.file_path, 'rb') as file:
            file_data = file.read()
        self.linked_list = LinkedList()
        chunks = LinkedList.split_file(file_data, self.chunk_size)
        for chunk in chunks:
            self.linked_list.add(chunk)
        self.update_list_widget()

    def send_data(self):
        """
        Sends the data in the linked list by writing it to the received file.
        """
        if self.linked_list.is_empty():
            QMessageBox.information(self, "Error", "No data in linked list")
            return
        threading.Thread(target=self.run_async_task, args=(self._send_data,)).start()

    def show_received_data(self):
        """
        Displays the contents of the received file.
        """
        if os.path.exists(self.received_file_path):
            with open(self.received_file_path, 'rb') as f:
                data = f.read()
                QMessageBox.information(self, "Data Received", f"Received data contents:\n{data.decode('utf-8', errors='ignore')}")
        else:
            QMessageBox.information(self, "Error", "No data received yet.")

    def read_file_in_chunks(self):
        """
        Reads the file in chunks and adds each chunk to the linked list.
        """
        try:
            with open(self.file_path, 'rb') as file:
                linked_list = LinkedList()
                while chunk := file.read(self.chunk_size):
                    linked_list.add(chunk)
                return linked_list
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"File not found: {self.file_path}")
            return None

    def run_async_task(self, async_func, *args):
        """
        Runs an asynchronous task.
        """
        asyncio.run(async_func(*args))

    async def _send_data(self):
        """
        Asynchronous function to send data by writing it to the received file.
        """
        try:
            data = b''.join(self.linked_list.to_list())
            # Store the sent data in the received file for demonstration
            with open(self.received_file_path, 'wb') as received_file:
                received_file.write(data)
            self.signal_emitter.file_sent.emit()
        except Exception as e:
            self.signal_emitter.error_occurred.emit(f"Failed to send data: {e}")

    def on_devices_discovered(self, device_list):
        """
        Handles the event when devices are discovered.
        """
        pass  # No need to implement for local transfer

    def on_file_sent(self):
        """
        Handles the event when a file is sent.
        """
        QMessageBox.information(self, "Success", "Data sent successfully.")

    def on_file_received(self):
        """
        Handles the event when a file is received.
        """
        pass  # No need to implement for local transfer

    def on_error_occurred(self, error_message):
        """
        Handles the event when an error occurs.
        """
        QMessageBox.critical(self, "Error", error_message)

    def toggle_dark_mode(self, state):
        """
        Toggles dark mode on or off based on the state of the checkbox.
        """
        if state == 2:  # Checked
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2e2e2e;
                    color: #ffffff;
                }
                QListWidget {
                    background-color: #2e2e2e;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
                QCheckBox {
                    color: #ffffff;
                }
            """)
        else:  # Unchecked
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QListWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QCheckBox {
                    color: #000000;
                }
            """)

    def input_word(self):
        """
        Prompts the user to input a word and adds each character of the word as a chunk to the linked list.
        """
        word, ok = QInputDialog.getText(self, "Input Word", "Enter a word:")
        if ok and word:
            self.linked_list = LinkedList()
            for char in word:
                self.linked_list.add(char.encode('utf-8'))
            self.update_list_widget()
        else:
            QMessageBox.information(self, "Error", "No word entered")

    def delete_selected(self):
        """
        Deletes the selected chunks from the linked list.
        """
        selected_items = self.chunk_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Error", "No items selected")
            return
        for item in selected_items:
            data = item.text().encode('utf-8')
            self.linked_list.delete(data)
            self.chunk_list_widget.takeItem(self.chunk_list_widget.row(item))
        self.update_received_file()

    def update_received_file(self):
        """
        Updates the received file with the current data in the linked list.
        """
        data = b''.join(self.linked_list.to_list())
        with open(self.received_file_path, 'wb') as received_file:
            received_file.write(data)

    def update_list_widget(self):
        """
        Updates the list widget to display the current chunks in the linked list.
        """
        self.chunk_list_widget.clear()
        for data in self.linked_list.to_list():
            self.chunk_list_widget.addItem(data.decode('utf-8'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_path = "C:\\Users\\ASUS-ROG\\Downloads\\Telegram Desktop\\DSA project - Copy\\DSA project - Copy\\example.bin"  # Update this path as needed
    chunk_size = 2 * 1024 * 1024  # 2MB chunks
    window = ChunkListWindow(file_path, chunk_size)
    window.show()
    sys.exit(app.exec_())
