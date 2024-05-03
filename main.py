import tkinter as tk
from compute_distance import Beacons
import ttkbootstrap as ttk
import time
import csv


class App(ttk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(themename='darkly')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.draw_menu()

        self.beacon_frame = ParametersFrame(self)
        self.logs_frame = LogFrame(self)

        self.title("GNSS")
        self.geometry('1440x720')

    def draw_menu(self):
        """
        Draw top menu
        :return:
        """
        menu = ttk.Menu(self)
        file_menu = ttk.Menu(menu, tearoff=False)
        file_menu.add_command(label='Save parameters', command=self.save_params)
        file_menu.add_command(label='Open parameters', command=self.open_params)
        file_menu.add_command(label='Save logs', command=self.save_logs)
        menu.add_cascade(label='File', menu=file_menu)

        settings_menu = ttk.Menu(menu, tearoff=False)
        settings_menu.add_command(label='Dark theme', command=self.set_dark_theme)
        settings_menu.add_command(label='Light theme', command=self.set_light_theme)
        settings_menu.add_command(label='About', command=self.open_about)
        menu.add_cascade(label='Settings', menu=settings_menu)

        computation_menu = ttk.Menu(menu, tearoff=False)
        computation_menu.add_command(label='Compute', command=self.compute)
        menu.add_cascade(label='Computation', menu=computation_menu)
        self.configure(menu=menu)

    def set_dark_theme(self):
        self.style.theme_use('darkly')

    def set_light_theme(self):
        self.style.theme_use('cosmo')

    def open_settings(self):
        pass

    def open_about(self):
        print('about')

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
        try:
            self.beacon_frame.insert_data(data)
        except IndexError:
            self.beacon_frame.show_warnings('insufficient_entries')
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
            self.beacon_frame.show_warnings('beacon_input')
        try:
            epoch = self.beacon_frame.get_epoch()
            print(beacons.train(epoch))
            self.logs_frame.display_logs(beacons.get_train_logs())
            beacons.draw()
        except ValueError:
            self.beacon_frame.show_warnings('epochs_input')

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


class LogFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=1, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.log_window = ttk.Label(self, text='logs', justify=ttk.LEFT, relief=ttk.GROOVE,
                                    font='Courier 10', name='logs')
        self.log_window.grid(row=0, column=0, sticky='nsew')

    def display_logs(self, logs):
        """
        Display logs in widget

        :param logs: logs to display
        :return:
        """
        self.log_window.config(anchor='nw')
        self.log_window.config(text=logs)


class ParametersFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure([i for i in range(3)], weight=1)
        for i in range(1, 4):
            self.create_beacon_entry(i, f'r{i}').grid(row=i-1, column=0)

        self.create_receiver_entry().grid(row=0, column=1)

        self.create_epoch_entry().grid(row=1, column=1)

        self.add_button = ttk.Button(self, text='Add beacon',
                                     command=self.add_beacon, bootstyle=ttk.PRIMARY).grid(row=2, column=1)

    def add_beacon(self):
        beacons = self.grid_size()[1]
        self.rowconfigure(beacons, weight=1)
        self.create_beacon_entry(beacons+1, f'r{beacons}').grid(row=beacons, column=0)

    def create_beacon_entry(self, number: int, error_text: str) -> ttk.Frame:
        """
        Create frame with entries for beacon

        :param number:
        :param error_text:
        :return: Frame with entries for beacon
        """
        beacon_frame = ttk.Frame(self, name=f'beacon_frame{number}')
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        beacon_label = ttk.Label(beacon_frame, text=f"beacon {number} coordinates")
        ri_label = ttk.Label(beacon_frame, text=error_text)
        x_entry = ttk.Entry(beacon_frame, width=10, name='x_entry')
        y_entry = ttk.Entry(beacon_frame, width=10, name='y_entry')
        ri_entry = ttk.Entry(beacon_frame, width=10, name='ri_entry')

        beacon_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        ri_label.grid(row=0, column=2, sticky='nsew' )
        x_entry.grid(row=1, column=0, sticky='nsew' )
        y_entry.grid(row=1, column=1, sticky='nsew' )
        ri_entry.grid(row=1, column=2, sticky='nsew')
        return beacon_frame

    def create_receiver_entry(self) -> ttk.Frame:
        """
        Create frame with entries for receiver data
        :return:
        """
        receiver_frame = ttk.Frame(self, name='receiver_frame')
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        receiver_label = ttk.Label(receiver_frame, text='receiver coordinates')
        tau_label = ttk.Label(receiver_frame, text='tau')
        receiver_x = ttk.Entry(receiver_frame, width=10, name='receiver_x')
        receiver_y = ttk.Entry(receiver_frame, width=10, name='receiver_y')
        tau_entry = ttk.Entry(receiver_frame, width=10, name='tau')

        receiver_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        tau_label.grid(row=0, column=2, sticky='nsew')
        receiver_x.grid(row=1, column=0, sticky='nsew')
        receiver_y.grid(row=1, column=1, sticky='nsew')
        tau_entry.grid(row=1, column=2, sticky='nsew')
        return receiver_frame

    def create_epoch_entry(self):
        epoch_frame = ttk.Frame(self, name='epoch_frame')
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1)

        epochs_label = ttk.Label(epoch_frame, text='epochs')
        self.epochs_entry = ttk.Entry(epoch_frame, name='epochs_entry')

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
        self.children['receiver_frame'].children['receiver_x'].delete(0, last=ttk.END)
        self.children['receiver_frame'].children['receiver_x'].insert(0, data[1][0])
        self.children['receiver_frame'].children['receiver_y'].delete(0, last=ttk.END)
        self.children['receiver_frame'].children['receiver_y'].insert(0, data[1][1])
        self.children['receiver_frame'].children['tau'].delete(0, last=ttk.END)
        self.children['receiver_frame'].children['tau'].insert(0, data[2][0])

        for i in range(len(data[0])):  # insert beacon data
            frame = beacon_frames[i]
            self.children[frame].children['x_entry'].delete(0, last=ttk.END)
            self.children[frame].children['x_entry'].insert(0, data[0][i][0])
            self.children[frame].children['y_entry'].delete(0, last=ttk.END)
            self.children[frame].children['y_entry'].insert(0, data[0][i][1])
            self.children[frame].children['ri_entry'].delete(0, last=ttk.END)
            self.children[frame].children['ri_entry'].insert(0, data[3][i])

    def get_epoch(self) -> int:
        """
        Return the entered number of epochs
        :return: int: epochs
        """
        return int(self.epochs_entry.get())

    def show_warnings(self, warning_type):
        if warning_type == 'beacon_input':
            tk.messagebox.showwarning(title="Warning",
                                      message="Invalid input format.\n"
                                              "Coordinates and errors must be a float or an integer.")
        elif warning_type == 'epochs_input':
            tk.messagebox.showwarning(title="Warning",
                                      message="Invalid input format.\nNumber of epochs must be an integer.")
        elif warning_type == 'insufficient_entries':
            tk.messagebox.showwarning(title="Warning",
                                      message="Not enough data entry fields.")


if __name__ == '__main__':
    app = App()
    app.mainloop()

