import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from random import randint
from point_location_with_visualization import Kirkpatrick_with_vis

class interactive_vis:
    def __init__(self, polygon = None, point = None):
        
        def get_polygon_points(max_x=5, max_y=5):
            root = tk.Tk()
            root.title('Polygon Points')

            fig, ax = plt.subplots()
            ax.set_title(f"Please select points for the polygon in counter-clockwise order")
            ax.set_xlim([0, max_x])
            ax.set_ylim([0, max_y])

            def onclick(event):
                if event.button == 1:  # Left mouse button
                    plt.plot(event.xdata, event.ydata, 'bo')
                    points_data.append((event.xdata, event.ydata))
                    ax.annotate(f"{len(points_data)}", xy=(event.xdata, event.ydata))
                    canvas.draw()
                elif event.button == 3:  # Right mouse button
                    if len(point) == 0:
                        plt.plot(event.xdata, event.ydata, 'ro')
                        point.append((event.xdata, event.ydata))
                        ax.annotate(f"{len(point)}", xy=(event.xdata, event.ydata))
                        canvas.draw()


            fig.canvas.mpl_connect('button_press_event', onclick)


            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            root.mainloop()

        def get_polygon():
            nonlocal prep_steps
            nonlocal query_steps
            nonlocal points_data
            nonlocal point
            nonlocal i
            nonlocal j
            prep_steps = []
            query_steps = []
            points_data = []
            point = []
            i = 0
            j = -1
            for widget in frame.winfo_children():
                widget.destroy()
            tk.Button(frame, text = "Preprocess Polygon", command = preprocess).pack(pady = 10)
            frame.pack()
            get_polygon_points()
        
        def preprocess():
            nonlocal prep_steps
            nonlocal point
            nonlocal query_steps
            nonlocal kirkpatrick
            for widget in frame.winfo_children():
                widget.destroy()
            kirkpatrick = Kirkpatrick_with_vis(points_data)
            kirkpatrick.preprocess()
            prep_steps = kirkpatrick.preprocess_steps

            tk.Button(frame, text = "Show prep steps", command = next_prep).pack(pady = 10)

        def next_prep():
            nonlocal i
            i %= len(prep_steps)
            for widget in frame.winfo_children():
                widget.destroy()

            fig, ax = prep_steps[i].get_plot()

            label = tk.Label(text = "Step " + str(i), master = frame)
            label.pack()
            canvas = FigureCanvasTkAgg(fig, master = frame)
            canvas.draw()

            canvas.get_tk_widget().pack()
            
            canvas = FigureCanvasTkAgg(fig, master = frame)
            canvas.draw()
            
            tk.Button(frame, text = "Show prep again" if i == len(prep_steps)-1 else "Next prep step", command = next_prep).pack(pady = 10)
            tk.Button(frame, text = "Query", command = query).pack(pady = 10)
            frame.pack()
            i += 1

        def query():
            nonlocal query_steps
            for widget in frame.winfo_children():
                widget.destroy()
            nonlocal kirkpatrick
            kirkpatrick.query_with_show(point[0])
            query_steps = kirkpatrick.query_steps
            tk.Button(frame, text = "Query Steps", command = next_query).pack(pady = 10)
        def next_query():
            nonlocal j
            nonlocal kirkpatrick
            j %= len(query_steps)
            while j > -1 and not kirkpatrick.is_used[j]:
                j -= 1
            if j > 0:
                for widget in frame.winfo_children():
                    widget.destroy()
                fig, ax = query_steps[j].get_plot()

                label = tk.Label(text = "Dag depth " + str(j), master = frame)
                label.pack()
                canvas = FigureCanvasTkAgg(fig, master = frame)
                canvas.draw()

                canvas.get_tk_widget().pack()
                
                canvas = FigureCanvasTkAgg(fig, master = frame)
                canvas.draw()
                tk.Button(frame, text = "Next query step", command = next_query).pack(pady = 10)
                frame.pack()
            else:
                for widget in frame.winfo_children():
                    widget.destroy()
                fig, ax = query_steps[j].get_plot()

                label = tk.Label(text = "step" + str(j), master = frame)
                label.pack()
                canvas = FigureCanvasTkAgg(fig, master = frame)
                canvas.draw()

                canvas.get_tk_widget().pack()
                
                canvas = FigureCanvasTkAgg(fig, master = frame)
                canvas.draw()
                tk.Button(frame, text = "Query steps again", command = next_query).pack(pady = 10)
                if polygon is None:
                    tk.Button(frame, text = "Kirkpatrick new polygon", command = get_polygon).pack(pady = 10)
                tk.Button(frame, text = "Preprocessing steps again", command = next_prep).pack(pady = 10)
                frame.pack()
            j -= 1
        prep_steps = []
        query_steps = []
        points_data = [] if polygon is None else polygon
        point = [] if point is None else [point]
        kirkpatrick = None
        i = 0
        j = -1
        root = tk.Tk()
        frame = tk.Frame(root)
        tk.Button(frame, text = "Start", command = get_polygon if polygon is None else preprocess).pack(pady = 10)
        frame.pack()

        root.mainloop()
        
        