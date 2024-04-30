import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import tkinter as tk
import random


class Beacons():
    def __init__(self, coordinates, distances=[], receiver_x=0, receiver_y=0, tau=0, ri=[]):
        self.coordinates = np.array(coordinates)
        self.receiver_x = receiver_x
        self.receiver_y = receiver_y
        self.tau = tau
        self.ri = np.array(ri)
        self.distances = np.sqrt((self.coordinates[:, 0] - receiver_x) ** 2 + (self.coordinates[:,1] - receiver_y) ** 2) + tau + self.ri[:] if not distances \
            else np.array(distances)
        print(distances)
        self.max_x, self.max_y = self.get_max_coordinates()

    def get_max_coordinates(self):
        max_x = 0
        max_y = 0
        for x, y in self.coordinates:
            if abs(x) > max_x: max_x = abs(x)
            if abs(y) > max_y: max_y = abs(y)
        print(max_x, max_y)
        return max_x, max_y

    def compute_distance(self, x, y, tau, ri):
        pi = []
        for i in range(len(self.coordinates)):
            pi.append(np.sqrt((self.coordinates[i][0] - x) ** 2 + (self.coordinates[i][1] - y) ** 2) + tau)
        return np.array(pi)

    def compute_error(self, pi):
        return np.power(self.distances - pi, 2).sum()

    def compute_gradients(self, pi, x, y):
        dEdp = -2 * (self.distances - pi)
        dpdx = []
        dpdy = []
        for i in range(len(self.coordinates)):
            dpdx.append((-(self.coordinates[i][0] - x)) / np.sqrt((self.coordinates[i][0] - x) ** 2
                                                                  + (self.coordinates[i][1] - y) ** 2))
        for i in range(len(self.coordinates)):
            dpdy.append((-(self.coordinates[i][1] - y)) / np.sqrt((self.coordinates[i][0] - x) ** 2
                                                                  + (self.coordinates[i][1] - y) ** 2))
        dpdx = np.array(dpdx)
        dEdx = np.dot(dEdp, dpdx).sum()
        dpdy = np.array(dpdy)
        dEdy = np.dot(dEdp, dpdy).sum()
        dEdtau = dEdp.sum()
        dEdri = dEdp.sum()
        return [dEdx, dEdy, dEdtau, dEdri]

    def train(self, epochs, lr=0.0005):
        x = random.random()*self.max_x*2-self.max_x
        y = random.random()*self.max_y*2-self.max_y
        print("X=", x, "Y=", y)
        tau = random.random() * 2
        ri = random.random() * 1
        for i in range(epochs):
            pi = self.compute_distance(x, y, tau, ri)
            E = self.compute_error(pi)
            dx, dy, dtau, dri = self.compute_gradients(pi, x, y)
            x -= lr * dx
            y -= lr * dy
            tau -= lr * dtau
            ri -= lr * dri
            if i % 1000 == 1:
                print('epoch: {}, error: {}'.format(i, E / len(pi)))

        self.receiver_x = x
        self.receiver_y = y
        return x, y, tau

    def draw(self):
        app = tk.Tk()

        fig, ax = plt.subplots()
        ax.scatter(self.coordinates[:, 0], self.coordinates[:, 1], c="red", label='beacons')
        ax.scatter(np.array([self.receiver_x]), np.array([self.receiver_y]), c="blue", label='receiver')

        for i in range(len(self.coordinates)):  # отрисовка расстояния
            ax.add_patch(plt.Circle((self.coordinates[i, 0], self.coordinates[i, 1]), self.distances[i], color='g', ls='--', fill=False))

        for i, txt in enumerate(range(1, len(self.coordinates))):  # добавление номера маякам
            ax.annotate(txt, (self.coordinates[i, 0], self.coordinates[i, 1]))
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=app)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, app)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.mainloop()
