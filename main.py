import tkinter as tk

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

        setting = Settings(self)

        self.title("GNSS")
        self.geometry('1280x720')

    def draw_menu(self):
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label='Save', command=self.save_file)
        menu.add_cascade(label='File', menu=file_menu)
        self.configure(menu=menu)

    def draw_widgets(self):
        pass

    def save_file(self):
        print('saved')


class Settings(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure([i for i in range(6)], weight=1)
        for i in range(1, 7):
            EntryBeacon(self, f'beacon {i}', i-1)


class EntryBeacon(tk.Frame):
    def __init__(self, parent, label_text, y):
        super().__init__(parent)

        self.columnconfigure((0,1), weight=1)
        self.rowconfigure((0,1), weight=1)

        label = tk.Label(self, text=label_text)
        x_entry = tk.Entry(self, background='red')
        y_entry = tk.Entry(self, background='blue')

        label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        x_entry.grid(row=1, column=0, sticky='nsew')
        y_entry.grid(row=1, column=1, sticky='nsew')
        self.grid(row=y, column=0, sticky='nsew')


if __name__ == '__main__':
    app = App()
    app.mainloop()

