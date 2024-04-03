## TO-DO
## Find an effective way to show cars with multiple drivers
## Tidy up horrible GUI (both aesthetically and in code)
## Animate the graph

import matplotlib.pyplot as plt
import requests
import tkinter as tk
from tkinter import ttk, messagebox

def gui(): #bodged up gui code
    root = tk.Tk()
    root.title('Lap Chart Plotter')

    root.geometry('300x240')

    def reset():
        root.destroy()
        gui()

    resetButton = tk.Button(root, text='Reset', command=reset).place(x=125, y=200)

    def series(seriesUUID, decadeVar, boxSeries):

        def race(yearVar):
            boxYear.configure(state='disabled')

            def session(raceVar):
                boxRace.configure(state='disabled')

                sessionNames = ['race', 'race-1', 'race-2', 'race-3', 'race-4', 'race-5'] # the only way to find available sessions seems to be trial and error using possible session names. only races are available as quali/practice tends to have strange data that doesn't work on the graph
                validSessions = []

                def load(sessionVar):
                    try:
                        plot(f'https://motorsportstats.com/api/result-statistics?sessionSlug={dictRace[raceVar]}_{sessionVar}&sessionFact=LapChart&size=999', raceVar, yearVar, sessionVar)
                        root.destroy()
                        gui()
                    except:
                        messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")
                        reset()

                for i in sessionNames:
                    try:
                        r = requests.get(f'https://motorsportstats.com/api/result-statistics?sessionSlug={dictRace[raceVar]}_{i}&sessionFact=LapChart&size=999')
                        data = r.json()
                        validSessions.append(i)
                    except:
                         pass

                if validSessions == []:
                    messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")
                    reset()

                
                sessionVar = tk.StringVar()
                sessionVar.set("")

                boxSession = ttk.OptionMenu(root, sessionVar, "Select a session", *validSessions, command=load)
                boxSession.pack(pady=10)


            r = requests.get(f'https://motorsportstats.com/api/advanced-search?entity=events&size=999&filterIds={seriesUUID}&filterIds={yearVar}')
            data = r.json()
            if data['totalElements'] == 0:
                messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")
                root.destroy()
                gui()

            dictRace = dict((i['name'], i['uuid']) for i in data['content'])

            raceVar = tk.StringVar()
            raceVar.set("")

            boxRace = ttk.OptionMenu(root, raceVar, "Select a race", *dictRace.keys(), command=session)
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

def plot(url, name, year, session):

    def create_arr(num): #creates an array for a car from the array of laps
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
        ax.annotate(f'#{cars[i][0]}', xy=(len(positions[i])-0.8,positions[i][-1]+0.1))
    ax.set_xticks([0, data['content'][-1]['lap']])
    ax.set_yticks(range(1, len(cars) +1))
    ax.invert_yaxis()
    ax.set_xlim(left = 0)
    plt.legend(bbox_to_anchor = (1, 1))
    fig.suptitle(f'{year} {name} {session.replace("-", " ").title()}')
    ax.set_xlabel('Laps')
    ax.set_ylabel('Positions')
    plt.show()

if __name__ == '__main__':
    gui()