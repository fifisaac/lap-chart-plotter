## TO-DO
## Find an effective way to show cars with multiple drivers
## Handle sessions other than race and weekends with many races
## Tidy up horrible GUI (both aesthetically and in code)
## Animate the graph

import matplotlib.pyplot as plt
import requests
import tkinter as tk
from tkinter import ttk, messagebox

def tkinter():
    root = tk.Tk()
    root.title('Lap Chart Plotter')

    root.geometry('300x240')

    def reset():
        root.destroy()
        tkinter()

    resetButton = tk.Button(root, text='Reset', command=reset).place(x=125, y=200)

    def series(seriesUUID, decadeVar, boxSeries):

        def race(yearVar):
            boxYear.configure(state='disabled')

            def load(raceVar):
                boxRace.configure(state='disabled')
                try:
                    plot(f'https://motorsportstats.com/api/result-statistics?sessionSlug={dictRace[raceVar]}_race&sessionFact=LapChart&size=999')
                    root.destroy()
                    tkinter()
                except:
                    messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")
                    root.destroy()
                    tkinter()


            r = requests.get(f'https://motorsportstats.com/api/advanced-search?entity=events&size=999&filterIds={seriesUUID}&filterIds={yearVar}')
            data = r.json()
            if data['totalElements'] == 0:
                messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")
                root.destroy()
                tkinter()

            dictRace = dict((i['name'], i['uuid']) for i in data['content'])

            raceVar = tk.StringVar()
            raceVar.set("")

            boxRace = ttk.OptionMenu(root, raceVar, "Select a race", *dictRace.keys(), command=load)
            boxRace.pack(pady=10)

        boxSeries.configure(state='disabled')
        yearVar = tk.StringVar(root)
        yearVar.set("")

        years = [int(str(decadeVar[:3]) + str(i)) for i in range(0,10)]
        boxYear = ttk.OptionMenu(root, yearVar, "Select a year", *years, command=race)
        boxYear.pack(pady=10)

    def decade(decadeVar):
        boxDecade.configure(state='disabled')
        def submit(seriesVar):
            series(dictSeries[seriesVar], decadeVar, boxSeries)

        r = requests.get(f'https://motorsportstats.com/api/advanced-search?entity=series&size=999&filterIds={decadeVar}')
        data = r.json()
        dictSeries = dict((i['name'], i['uuid']) for i in data['content'])


        seriesVar = tk.StringVar(root)
        seriesVar.set("")

        boxSeries = ttk.OptionMenu(root, seriesVar, "Select a series", *dictSeries.keys(), command=submit)
        boxSeries.pack(pady=10)

    decadeVar = tk.StringVar(root)
    decadeVar.set("")

    boxDecade = ttk.OptionMenu(root, decadeVar, "Select a decade", "2020s", "2010s", "2000s", "1990s", "1980s", "1970s", "1960s", "1950s", command=decade)
    boxDecade.pack(pady=10)


    root.mainloop()

def plot(url):

    def create_arr(num):
        pos = []
        for k, l in enumerate(data['content']):
            for i, j in enumerate(data['content'][k]['cars']):
                if j == str(num):
                    pos.append(i+1)
        
        return pos
    try:
        r = requests.get(url)
    except:
        print('Unable to access lap chart')
        return
    data = r.json()

    cars = [[i['carNumber'], i['drivers'][0]['name']] for i in data['cars']] ##only one name will show for cars with multiple drivers
    positions = [create_arr(i[0]) for i in cars]

    fig, ax = plt.subplots()
    for i, j in enumerate(positions):
        ax.plot(positions[i], label = f'#{cars[i][0]} - {cars[i][1]}')
    ax.set_xticks([])
    ax.set_yticks(range(1, len(cars) +1))
    ax.invert_yaxis()
    ax.set_xlim(left = 0)
    plt.legend(bbox_to_anchor = (1, 1))
    plt.show()

if __name__ == '__main__':
    tkinter()