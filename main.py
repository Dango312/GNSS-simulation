import tkinter as tk
from compute_distance import Beacons
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
        filepath = tk.filedialog.asksaveasfilename(initialfile='parameters.scv')
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
        filepath = tk.filedialog.askopenfilename()
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
        beacon_coords, receiver_coords, tau, ri = self.beacon_frame.get_data()
        print("Coordinate:", beacon_coords, receiver_coords, tau, ri)
        beacons = Beacons(coordinates=beacon_coords, receiver_x=receiver_coords[0], receiver_y=receiver_coords[1],
                          tau=tau, ri=ri)
        epoch = self.beacon_frame.get_epoch()
        print(beacons.train(epoch))
        self.logs_frame.display_logs(beacons.get_train_logs())
        beacons.draw()

    def save_logs(self):
        """
        Save logs in .txt file
        :return:
        """
        filepath = tk.filedialog.asksaveasfilename(initialfile='logs.txt')
        with open(filepath, 'w') as f:
            f.write(self.logs_frame.log_window['text'])
            f.close()


class LogFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=1, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.log_window = tk.Label(self, text='Log_window', justify=tk.LEFT, relief=tk.GROOVE, name='logs')
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
        self.rowconfigure([i for i in range(6)], weight=1)
        for i in range(1, 7):
            self.create_beacon_entry(f'beacon {i}', f'r{i}').grid(row=i-1, column=0)

        self.create_receiver_entry().grid(row=0, column=1)

        self.epoch_entry = tk.Entry(self, name='epoch_entry')
        self.epoch_entry.grid(row=1, column=1)

    def create_beacon_entry(self, beacon_text, error_text) -> tk.Frame:
        """
        Create frame with entries for beacon
        :param beacon_text: str
        :param error_text: str
        :return: Frame
        """
        frame = tk.Frame(self)
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        beacon_label = tk.Label(frame, text=beacon_text)
        ri_label = tk.Label(frame, text=error_text)
        x_entry = tk.Entry(frame, name='x_entry')
        y_entry = tk.Entry(frame, name='y_entry')
        ri_entry = tk.Entry(frame, name='ri_entry')

        beacon_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        ri_label.grid(row=0, column=2, sticky='nsew')
        x_entry.grid(row=1, column=0, sticky='nsew')
        y_entry.grid(row=1, column=1, sticky='nsew')
        ri_entry.grid(row=1, column=2, sticky='nsew')
        return frame

    def create_receiver_entry(self) -> tk.Frame:
        """
        Create frame with entries for receiver data
        :return:
        """
        frame = tk.Frame(self)
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        receiver_label = tk.Label(frame, text='receiver coordinates')
        tau_label = tk.Label(frame, text='tau')
        receiver_x = tk.Entry(frame, name='receiver_x')
        receiver_y = tk.Entry(frame, name='receiver_y')
        tau_entry = tk.Entry(frame, name='tau')

        receiver_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        tau_label.grid(row=0, column=2, sticky='nsew')
        receiver_x.grid(row=1, column=0, sticky='nsew')
        receiver_y.grid(row=1, column=1, sticky='nsew')
        tau_entry.grid(row=1, column=2, sticky='nsew')
        return frame

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
        print(self.children['!frame'].children)
        for i in range(len(data[0])):
            frame = list(self.children.keys())[i]
            self.children[frame].children['x_entry'].delete(0, last=tk.END)
            self.children[frame].children['x_entry'].insert(0, data[0][i][0])
            self.children[frame].children['y_entry'].delete(0, last=tk.END)
            self.children[frame].children['y_entry'].insert(0, data[0][i][1])
            self.children[frame].children['ri_entry'].delete(0, last=tk.END)
            self.children[frame].children['ri_entry'].insert(0, data[3][i])
        receiver = list(self.children.keys())[-2]
        self.children[receiver].children['receiver_x'].delete(0, last=tk.END)
        self.children[receiver].children['receiver_x'].insert(0, data[1][0])
        self.children[receiver].children['receiver_y'].delete(0, last=tk.END)
        self.children[receiver].children['receiver_y'].insert(0, data[1][1])
        self.children[receiver].children['tau'].delete(0, last=tk.END)
        self.children[receiver].children['tau'].insert(0, data[2][0])

    def get_epoch(self) -> int:
        """
        Return the entered number of epochs
        :return: int: epochs
        """
        return int(self.epoch_entry.get())

if __name__ == '__main__':
    app = App()
    app.mainloop()

