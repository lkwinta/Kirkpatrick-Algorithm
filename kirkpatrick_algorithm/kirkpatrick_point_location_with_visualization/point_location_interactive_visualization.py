import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from kirkpatrick_algorithm.kirkpatrick_point_location_with_visualization.point_location_visualization import KirkpatrickVisualization

class KirkpatrickInteractiveVisualization:
    def __init__(self, polygon = None, point = None):
        self.__prep_steps = []
        self.__query_steps = []
        self.__points_data = [] if polygon is None else polygon
        self.__point = [] if point is None else [point]
        self.__kirkpatrick = None
        self.__i = 0
        self.__j = -1
        self.__polygon = polygon
        
        self.__root = tk.Tk()
        self.__frame = tk.Frame(self.__root)
        tk.Button(self.__frame, text = "Start", command = self.__get_polygon if polygon is None else self.__preprocess).pack(pady = 10)
        self.__frame.pack()

        self.__root.mainloop()

    def __get_polygon_points(self, max_x=5, max_y=5):
        root = tk.Tk()
        root.title('Polygon Points')

        fig, ax = plt.subplots()
        ax.set_title(f"Please select points for the polygon in counter-clockwise order")
        ax.set_xlim([0, max_x])
        ax.set_ylim([0, max_y])

        def onclick(event):
            if event.button == 1:  # Left mouse button
                plt.plot(event.xdata, event.ydata, 'bo')
                self.__points_data.append((event.xdata, event.ydata))
                ax.annotate(f"{len(self.__points_data)}", xy=(event.xdata, event.ydata))
                canvas.draw()
            elif event.button == 3:  # Right mouse button
                if len(self.__point) == 0:
                    plt.plot(event.xdata, event.ydata, 'ro')
                    self.__point.append((event.xdata, event.ydata))
                    ax.annotate(f"{len(self.__point)}", xy=(event.xdata, event.ydata))
                    canvas.draw()


        fig.canvas.mpl_connect('button_press_event', onclick)


        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        root.mainloop()

    def __get_polygon(self):
        self.__prep_steps = []
        self.__query_steps = []
        self.__points_data = []
        self.__point = []
        self.__i = 0
        self.__j = -1
        for widget in self.__frame.winfo_children():
            widget.destroy()
        tk.Button(self.__frame, text = "Preprocess Polygon", command = self.__preprocess).pack(pady = 10)
        self.__frame.pack()
        self.__get_polygon_points()
    
    def __preprocess(self):
        for widget in self.__frame.winfo_children():
            widget.destroy()
        self.__kirkpatrick = KirkpatrickVisualization(self.__points_data)
        self.__kirkpatrick.preprocess()
        self.__prep_steps = self.__kirkpatrick.preprocess_steps

        tk.Button(self.__frame, text = "Show prep steps", command = self.__next_prep).pack(pady = 10)

    def __next_prep(self):
        self.__i %= len(self.__prep_steps)
        for widget in self.__frame.winfo_children():
            widget.destroy()

        fig, ax = self.__prep_steps[self.__i].get_plot()

        label = tk.Label(text = "Step " + str(self.__i), master = self.__frame)
        label.pack()
        canvas = FigureCanvasTkAgg(fig, master = self.__frame)
        canvas.draw()

        canvas.get_tk_widget().pack()
        
        canvas = FigureCanvasTkAgg(fig, master = self.__frame)
        canvas.draw()
        
        tk.Button(self.__frame, text = "Show prep again" if self.__i == len(self.__prep_steps)-1 else "Next prep step", command = self.__next_prep).pack(pady = 10)
        tk.Button(self.__frame, text = "Query", command = self.__query).pack(pady = 10)
        self.__frame.pack()
        self.__i += 1

    def __query(self):
        for widget in self.__frame.winfo_children():
            widget.destroy()
        self.__kirkpatrick.query_with_show(self.__point[0])
        self.__query_steps = self.__kirkpatrick.query_steps

        tk.Button(self.__frame, text = "Query Steps", command = self.__next_query).pack(pady = 10)

    def __next_query(self):
        self.__j %= len(self.__query_steps)
        while self.__j > -1 and not self.__kirkpatrick.is_used[self.__j]:
            self.__j -= 1
        if self.__j > 0:
            for widget in self.__frame.winfo_children():
                widget.destroy()
            fig, ax = self.__query_steps[self.__j].get_plot()

            label = tk.Label(text = "Dag depth " + str(self.__j), master = self.__frame)
            label.pack()
            canvas = FigureCanvasTkAgg(fig, master = self.__frame)
            canvas.draw()

            canvas.get_tk_widget().pack()
            
            canvas = FigureCanvasTkAgg(fig, master = self.__frame)
            canvas.draw()
            tk.Button(self.__frame, text = "Next query step", command = self.__next_query).pack(pady = 10)
            self.__frame.pack()
        else:
            for widget in self.__frame.winfo_children():
                widget.destroy()
            fig, ax = self.__query_steps[self.__j].get_plot()

            label = tk.Label(text = "step" + str(self.__j), master = self.__frame)
            label.pack()
            canvas = FigureCanvasTkAgg(fig, master = self.__frame)
            canvas.draw()

            canvas.get_tk_widget().pack()
            
            canvas = FigureCanvasTkAgg(fig, master = self.__frame)
            canvas.draw()
            tk.Button(self.__frame, text = "Query steps again", command = self.__next_query).pack(pady = 10)
            if self.__polygon is None:
                tk.Button(self.__frame, text = "Kirkpatrick new polygon", command = self.__get_polygon).pack(pady = 10)
            tk.Button(self.__frame, text = "Preprocessing steps again", command = self.__next_prep).pack(pady = 10)
            self.__frame.pack()
        self.__j -= 1
        
        