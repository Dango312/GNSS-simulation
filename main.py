import tkinter as tk
from compute_distance import Beacons
import csv

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.middle_container = tk.Frame(self)
        self.right_container = tk.Frame(self)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self.middle_container.grid(row=0, column=1, sticky='nsew')
        lm = tk.Label(self.middle_container, text='middle', background='red')
        lm.pack(expand=True, fill='both')
        self.right_container.grid(row=0, column=2, sticky='nsew')
        lr = tk.Label(self.right_container, text='right', background='blue')
        lr.pack(expand=True, fill='both')

        self.draw_menu()

        self.beacon_frame = BeaconFrame(self)

        self.title("GNSS")
        self.geometry('1280x720')

    def draw_menu(self):
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label='Save', command=self.save_file)
        file_menu.add_command(label='Open', command=self.open_file)
        menu.add_cascade(label='File', menu=file_menu)

        computation_menu = tk.Menu(menu, tearoff=False)
        computation_menu.add_command(label='Compute', command=self.computate)
        menu.add_cascade(label='Computation', menu=computation_menu)
        self.configure(menu=menu)

    def save_file(self):
        filepath = tk.filedialog.asksaveasfilename()
        data = self.beacon_frame.get_data()
        print(data)
        if filepath != "":
            with open(filepath, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([x[0] for x in data[0]])
                writer.writerow([x[1] for x in data[0]])
                writer.writerow(data[3])
                writer.writerow(data[1])
                writer.writerow([data[2]])
        print('File saved')

    def open_file(self):
        filepath = tk.filedialog.askopenfilename()
        with open(filepath) as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)
        print('File opened')

    def computate(self):
        """
        Computate distances
        :return: None
        """
        beacon_coords, receiver_coords, tau, ri = self.beacon_frame.get_data()
        print("Coordinate:", beacon_coords, receiver_coords, tau, ri)
        beacons = Beacons(coordinates=beacon_coords, receiver_x=receiver_coords[0], receiver_y=receiver_coords[1],
                          tau=tau, ri=ri)
        print(beacons.train(10000))
        beacons.draw()


class BeaconFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure([i for i in range(6)], weight=1)
        for i in range(1, 7):
            self.create_beacon_entry(f'beacon {i}', f'r{i}').grid(row=i-1, column=0)

        self.create_receiver_entry().grid(row=0, column=1)

    def create_beacon_entry(self, beacon_text, error_text) -> tk.Frame:
        frame = tk.Frame(self)
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        beacon_label = tk.Label(frame, text=beacon_text)
        ri_label = tk.Label(frame, text=error_text)
        x_entry = tk.Entry(frame, background='red', name='x_entry')
        y_entry = tk.Entry(frame, background='blue', name='y_entry')
        ri_entry = tk.Entry(frame, background='green', name='ri_entry')

        beacon_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        ri_label.grid(row=0, column=2, sticky='nsew')
        x_entry.grid(row=1, column=0, sticky='nsew')
        y_entry.grid(row=1, column=1, sticky='nsew')
        ri_entry.grid(row=1, column=2, sticky='nsew')
        return frame

    def create_receiver_entry(self) -> tk.Frame:
        frame = tk.Frame(self)
        self.columnconfigure((0, 1, 2), weight=1)
        self.rowconfigure((0, 1), weight=1)

        receiver_label = tk.Label(frame, text='receiver coordinates')
        tau_label = tk.Label(frame, text='tau')
        receiver_x = tk.Entry(frame, background='red', name='receiver_x')
        receiver_y = tk.Entry(frame, background='blue', name='receiver_y')
        tau_entry = tk.Entry(frame, background='green', name='tau')

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


if __name__ == '__main__':
    app = App()
    app.mainloop()

