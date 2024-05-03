import tkinter as tk
from compute_distance import Beacons
import time
import csv

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.draw_menu()

        self.beacon_frame = ParametersFrame(self)
        self.logs_frame = LogFrame(self)

        self.title("GNSS")
        self.geometry('1280x720')

    def draw_menu(self):
        """
        Draw top menu
        :return:
        """
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label='Save parameters', command=self.save_params)
        file_menu.add_command(label='Open parameters', command=self.open_params)
        file_menu.add_command(label='Save logs', command=self.save_logs)
        menu.add_cascade(label='File', menu=file_menu)

        computation_menu = tk.Menu(menu, tearoff=False)
        computation_menu.add_command(label='Compute', command=self.compute)
        menu.add_cascade(label='Computation', menu=computation_menu)
        self.configure(menu=menu)

    def save_params(self):
        """
        Save parameters into .csv file
        :return:
        """
        filepath = tk.filedialog.asksaveasfilename(initialfile='parameters.csv',
                                                   defaultextension=".csv",
                                                   filetypes=(('File "SCV"', "*.csv"), ("All Files", "*.*")))
        data = self.beacon_frame.get_data()
        print(data)
        if filepath != "":
            with open(filepath, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([x[0] for x in data[0]]) # beacon x
                writer.writerow([x[1] for x in data[0]]) # beacon y
                writer.writerow(data[1]) # receiver coordinates
                writer.writerow([data[2]]) # tau
                writer.writerow(data[3]) # ri
        print('File saved')

    def open_params(self):
        """
        Open parameters from .csv file
        :return:
        """
        filepath = tk.filedialog.askopenfilename(defaultextension=".csv",
                                                 filetypes=(('File "SCV"', "*.csv"), ("All Files", "*.*")))
        data = []
        with open(filepath) as f:
            reader = csv.reader(f)
            list_reader = list(reader)
            data.append(list(zip(list_reader[0], list_reader[1]))) # beacon coordinates
            data.append((list_reader[2])) # receiver coordinates
            data.append(list_reader[3]) # tau
            data.append(list_reader[4]) # ri
        print(data)
        self.beacon_frame.insert_data(data)
        print('File opened')

    def compute(self):
        """
        Computate distances
        :return: None
        """
        try:
            beacon_coords, receiver_coords, tau, ri = self.beacon_frame.get_data()
            print("Coordinate:", beacon_coords, receiver_coords, tau, ri)
            beacons = Beacons(coordinates=beacon_coords, receiver_x=receiver_coords[0], receiver_y=receiver_coords[1],
                              tau=tau, ri=ri)
        except ValueError:
            self.beacon_frame.show_warnings('float')
        try:
            epoch = self.beacon_frame.get_epoch()
            print(beacons.train(epoch))
            self.logs_frame.display_logs(beacons.get_train_logs())
            beacons.draw()
        except ValueError:
            self.beacon_frame.show_warnings('int')

    def save_logs(self):
        """
        Save logs in .txt file
        :return:
        """
        filepath = tk.filedialog.asksaveasfilename(initialfile='logs.txt',
                                                   defaultextension=".txt",
                                                   filetypes=(("Text file", "*.txt"), ("All Files", "*.*")))
        with open(filepath, 'w') as f:
            current_time = time.time()
            local_time = time.localtime(current_time)
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S\n", local_time)
            f.write(formatted_time)
            f.write(self.logs_frame.log_window['text'])
            f.close()


class LogFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=1, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.log_window = tk.Label(self, text='logs', justify=tk.LEFT, relief=tk.GROOVE, name='logs')
        self.log_window.grid(row=0, column=0, sticky='nsew')

    def display_logs(self, logs):
        """
        Display logs in widget
        :param logs: logs to display
        :return:
        """
        self.log_window.config(anchor='nw')
        self.log_window.config(text=logs)


class ParametersFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure([i for i in range(3)], weight=1)
        for i in range(1, 4):
            self.create_beacon_entry(i, f'r{i}').grid(row=i-1, column=0)

        self.create_receiver_entry().grid(row=0, column=1)

        self.valid_epochs = (self.register(self.validate_epochs),'%P')
        self.invalid_epochs = (self.register(self.on_invalid_epochs),)

        self.create_epoch_entry().grid(row=1, column=1)

        self.add_button = tk.Button(self, text='Add beacon', command=self.add_beacon).grid(row=2, column=1)

    def add_beacon(self):
        beacons = self.grid_size()[1]
        self.rowconfigure(beacons, weight=1)
        self.create_beacon_entry(beacons+1, f'r{beacons}').grid(row=beacons, column=0)

    def create_beacon_entry(self, number, error_text) -> tk.Frame:
        """
        Create frame with entries for beacon
        :param beacon_text: str
        :param error_text: str
        :return: Frame
        """
        beacon_frame = tk.Frame(self, name=f'beacon_frame{number}')
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        beacon_label = tk.Label(beacon_frame, text=f"beacon {number}")
        ri_label = tk.Label(beacon_frame, text=error_text)
        x_entry = tk.Entry(beacon_frame, name='x_entry')
        y_entry = tk.Entry(beacon_frame, name='y_entry')
        ri_entry = tk.Entry(beacon_frame, name='ri_entry')

        beacon_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        ri_label.grid(row=0, column=2, sticky='nsew')
        x_entry.grid(row=1, column=0, sticky='nsew')
        y_entry.grid(row=1, column=1, sticky='nsew')
        ri_entry.grid(row=1, column=2, sticky='nsew')
        return beacon_frame

    def create_receiver_entry(self) -> tk.Frame:
        """
        Create frame with entries for receiver data
        :return:
        """
        receiver_frame = tk.Frame(self, name='receiver_frame')
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        receiver_label = tk.Label(receiver_frame, text='receiver coordinates')
        tau_label = tk.Label(receiver_frame, text='tau')
        receiver_x = tk.Entry(receiver_frame, name='receiver_x')
        receiver_y = tk.Entry(receiver_frame, name='receiver_y')
        tau_entry = tk.Entry(receiver_frame, name='tau')

        receiver_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        tau_label.grid(row=0, column=2, sticky='nsew')
        receiver_x.grid(row=1, column=0, sticky='nsew')
        receiver_y.grid(row=1, column=1, sticky='nsew')
        tau_entry.grid(row=1, column=2, sticky='nsew')
        return receiver_frame

    def create_epoch_entry(self):
        epoch_frame = tk.Frame(self, name='epoch_frame')
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1)

        epochs_label = tk.Label(epoch_frame, text='epochs')
        self.epochs_entry = tk.Entry(epoch_frame, name='epochs_entry')

        epochs_label.grid(row=0, column=0, sticky='nsew')
        self.epochs_entry.grid(row=1, column=0, sticky='nsew')
        return epoch_frame

    def get_data(self):
        """
        Get data from entries
        :return: beacon_coordinates (list[tuple]), (receiver_x, receiver_y), tau (int), ri (list)
        """
        beacons_coordinates = []
        ri_data = []
        for c in self.children.keys():
            if 'x_entry' in self.children[c].children and self.children[c].children['x_entry'].get():
                x_beacon = self.children[c].children['x_entry'].get()
                y_beacon = self.children[c].children['y_entry'].get()
                ri = self.children[c].children['ri_entry'].get()

                beacons_coordinates.append((float(x_beacon), float(y_beacon)))
                ri_data.append(float(ri))
            elif 'receiver_x' in self.children[c].children:
                receiver_x = self.children[c].children['receiver_x'].get()
                receiver_y = self.children[c].children['receiver_y'].get()
                tau = self.children[c].children['tau'].get()
        return beacons_coordinates, (float(receiver_x), float(receiver_y)), float(tau), ri_data

    def insert_data(self, data):
        """
        Insert data in entries
        :param data: data to insert
        :return:
        """
        print(self.children.keys())
        print(self.children['beacon_frame1'].children)
        beacon_frames = [key for key in self.children.keys() if key.startswith('beacon_frame')]
        # insert receiver data
        self.children['receiver_frame'].children['receiver_x'].delete(0, last=tk.END)
        self.children['receiver_frame'].children['receiver_x'].insert(0, data[1][0])
        self.children['receiver_frame'].children['receiver_y'].delete(0, last=tk.END)
        self.children['receiver_frame'].children['receiver_y'].insert(0, data[1][1])
        self.children['receiver_frame'].children['tau'].delete(0, last=tk.END)
        self.children['receiver_frame'].children['tau'].insert(0, data[2][0])

        for i in range(len(data[0])):  # insert beacon data
            frame = beacon_frames[i]
            self.children[frame].children['x_entry'].delete(0, last=tk.END)
            self.children[frame].children['x_entry'].insert(0, data[0][i][0])
            self.children[frame].children['y_entry'].delete(0, last=tk.END)
            self.children[frame].children['y_entry'].insert(0, data[0][i][1])
            self.children[frame].children['ri_entry'].delete(0, last=tk.END)
            self.children[frame].children['ri_entry'].insert(0, data[3][i])

    def get_epoch(self) -> int:
        """
        Return the entered number of epochs
        :return: int: epochs
        """
        return int(self.epochs_entry.get())

    def show_warnings(self, entry_type):
        if entry_type == 'float':
            tk.messagebox.showwarning(title="Warning",
                                      message="Invalid input format\n"
                                              "Coordinates and errors must be a float or an integer")
        elif entry_type == 'int':
            tk.messagebox.showwarning(title="Warning",
                                      message="Invalid input format\nNumber of epochs must be an integer")


if __name__ == '__main__':
    app = App()
    app.mainloop()

