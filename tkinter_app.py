import threading
import time
from threading import Thread
from tkinter import *
from datetime import datetime

import app
from tkinter_utils import execute_query
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from conf import DELAY
def get_info():

    query = "SELECT ON_TEMP FROM heat_configuration WHERE id = 0"
    result = execute_query(query)
    low_temp_label.config(text="Low Temp:" + str(result[0][0]))

    query = "SELECT OFF_TEMP FROM heat_configuration WHERE id = 0"
    result = execute_query(query)
    high_temp_label.config(text="High Temp:" + str(result[0][0]))

    query = "SELECT TEMP FROM heat_configuration WHERE id = 0"
    result = execute_query(query)


    print(result[0][0])
    if result:
        temp_label.config(text=f"Current Temperature: {result[0][0]}")
        global timestamps
        global temperatures
        global graph,fig,ax
        timestamps.append(str(datetime.now().strftime("%H:%M:%S")))
        temperatures.append(result[0][0])
        graph.set_xdata(timestamps)
        graph.set_ydata(temperatures)
        ax.clear()
        if len(timestamps) > 5:
            del timestamps[0]
            del temperatures[0]
        ax.plot(timestamps, temperatures)
        plt.xlim(timestamps[0], timestamps[-1])
        fig = canvas.draw()

        window.after(DELAY, get_info)


def change_thresholds():
    if len(low_temp_entry.get()) != 0:
        execute_query("UPDATE heat_configuration SET ON_TEMP = %s WHERE ID = 0", params=(float(low_temp_entry.get()),))
        low_temp_label.config(text="Low Temp:" + str(low_temp_entry.get()))
        low_temp_entry.delete(0, END)

    if len(high_temp_entry.get()) != 0:
        execute_query("UPDATE heat_configuration SET OFF_TEMP = %s WHERE ID = 0", params=(float(high_temp_entry.get()),))
        high_temp_label.config(text="High Temp:" + str(high_temp_entry.get()))
        high_temp_entry.delete(0, END)


        
if __name__ == '__main__':
    thread = Thread(target=app.start_flask)
    thread.start()
    window = Tk()
    ON_TEMP = DoubleVar()
    OFF_TEMP = DoubleVar()
    TEMP = DoubleVar()

    temp_label = Label(window)
    temp_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    high_temp_label = Label(window, text="High Temp:")
    high_temp_label.grid(row=1, column=0, padx=5, pady=5)

    high_temp_entry = Entry(window)
    high_temp_entry.grid(row=1, column=2, padx=5, pady=5)

    change_button = Button(window, text="Change thresholds", command=change_thresholds)
    change_button.grid(row=2, column=1, padx=5, pady=5)

    low_temp_label = Label(window,text="Low Temp:")
    low_temp_label.grid(row=2, column=0, padx=5, pady=5)

    low_temp_entry = Entry(window)
    low_temp_entry.grid(row=2, column=2, padx=5, pady=5)

    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    timestamps = []
    temperatures = []
    graph = ax.plot(timestamps, temperatures)[0]

    window.after(DELAY, get_info)
    window.mainloop()
