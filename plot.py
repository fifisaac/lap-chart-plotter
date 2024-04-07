## TO-DO
## Find an effective way to show cars with multiple drivers
## Tidy up GUI
## Include other types of graphs. See Issue #1
## Animate the lap chart graph

import matplotlib.pyplot as plt
import requests
import tkinter as tk
from tkinter import ttk, messagebox

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Lap Chart Plotter')

        self.root.geometry('300x300')
        self.root.resizable(False, False)

        resetButton = tk.Button(self.root, text='Reset', command=self.reset)
        resetButton.place(x=175, y=240)

        self.lapChartButton = tk.Button(self.root, text='Load Lap Chart', 
                                        command=self.loadLapChart)
        self.lapChartButton.place(x=75, y=240)
        self.lapChartButton.configure(state='disabled')

        self.chooseDecade()

        tk.mainloop()
    
    def reset(self):
            self.root.destroy()
            GUI()
    
    def chooseDecade(self):
        self.decadeVar = tk.StringVar(self.root)
        self.decadeVar.set("")

        self.boxDecade = ttk.OptionMenu(
            self.root, self.decadeVar, 
            "Select a decade", "2020s", 
            "2010s", "2000s", "1990s", 
            "1980s", "1970s", "1960s", 
            "1950s", command=self.chooseSeries
            )
        self.boxDecade.pack(pady=10)
    
    def chooseSeries(self, decade: str):
        self.boxDecade.configure(state='disabled')

        r = requests.get(f'https://motorsportstats.com/api/advanced-search?entity=series&size=999&filterIds={decade}')
        data = r.json()
        self.dictSeries = dict((i['name'], i['uuid']) for i in data['content'])


        self.seriesVar = tk.StringVar(self.root)
        self.seriesVar.set("")

        self.boxSeries = ttk.OptionMenu(self.root, self.seriesVar, 
                                        "Select a series", 
                                        *self.dictSeries.keys(), 
                                        command=self.chooseYear)
        self.boxSeries.pack(pady=10)

    def chooseYear(self, series: str):
        self.boxSeries.configure(state='disabled')
        self.yearVar = tk.StringVar(self.root)
        self.yearVar.set("")

        years = [int(str(self.decadeVar.get()[:3]) + str(i)) for i in range(0,10)]
        self.boxYear = ttk.OptionMenu(self.root, self.yearVar, 
                                      "Select a year", *years, 
                                      command=self.chooseRace)
        self.boxYear.pack(pady=10)
    
    def chooseRace(self, year: int):
        self.boxYear.configure(state='disabled')

        seriesUUID = self.dictSeries[self.seriesVar.get()]

        r = requests.get(f'https://motorsportstats.com/api/advanced-search?entity=events&size=999&filterIds={seriesUUID}&filterIds={year}')
        data = r.json()
        if data['totalElements'] == 0:
            messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")
            self.reset()

        self.dictRace = dict((i['name'], i['uuid']) for i in data['content'])

        self.raceVar = tk.StringVar()
        self.raceVar.set("")

        self.boxRace = ttk.OptionMenu(self.root, self.raceVar,
                                      "Select a race",
                                      *self.dictRace.keys(), 
                                      command=self.chooseSession)
        self.boxRace.pack(pady=10)
        
    def chooseSession(self, race: str):
        self.boxRace.configure(state='disabled')

        # the only way to find available sessions seems to be trial and error. 
        # only races are available as quali/practice tend to have strange data that doesn't work on the graph
        sessionNames = ['race', 'race-1', 'race-2', 'race-3', 'race-4', 'race-5']     
                                  
        validSessions = []
        for i in sessionNames:
            try:
                r = requests.get(f'https://motorsportstats.com/api/result-statistics?sessionSlug={self.dictRace[self.raceVar.get()]}_{i}&sessionFact=LapChart&size=999')
                data = r.json()
                validSessions.append(i)
            except:
                    pass

        if validSessions == []:
            messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")
            self.reset()

        self.sessionVar = tk.StringVar()
        self.sessionVar.set("")

        boxSession = ttk.OptionMenu(self.root, self.sessionVar, 
                                    "Select a session", 
                                    *validSessions, 
                                    command=self.enableButton)
        boxSession.pack(pady=10)
    
    def enableButton(self, _session):  # session value is ignored, but tk requires it to be passed
        self.lapChartButton.config(state='normal')
    
    def loadLapChart(self):
        try:
            plot(f'https://motorsportstats.com/api/result-statistics?sessionSlug={self.dictRace[self.raceVar.get()]}_{self.sessionVar.get()}&sessionFact=LapChart&size=999', 
                 self.raceVar.get(), self.yearVar.get(), self.sessionVar.get())
        except:
            messagebox.showerror("Error", "An error occured. The lap chart likely doesn't exist for this race")


def plot(url, name, year, session):

    def create_arr(num):  # creates an array for a car from the array of laps
        pos = []
        for k, l in enumerate(data['content']):
            for i, j in enumerate(data['content'][k]['cars']):
                if j == str(num):
                    pos.append(i+1)

        return pos
    
    r = requests.get(url)
    data = r.json()

    cars = [[i['carNumber'], i['drivers'][0]['name']] for i in data['cars']]  #only one name will show for cars with multiple drivers
    positions = [create_arr(i[0]) for i in cars]

    fig, ax = plt.subplots()

    for i, j in enumerate(positions):
        ax.plot(positions[i], label = f'#{cars[i][0]} - {cars[i][1]}')

        ax.annotate(f'#{cars[i][0]}', 
                    xy=(len(positions[i])-0.8,
                    positions[i][-1]+0.1)) # car number annotated at end of line
    
    ax.set_xticks(range(0, data['content'][-1]['lap']+1, 10))
    ax.set_yticks(range(1, len(cars) +1))
    ax.invert_yaxis()
    ax.set_xlim(left = 0)
    plt.legend(bbox_to_anchor = (1, 1))
    fig.suptitle(f'{year} {name} {session.replace("-", " ").title()}')
    ax.set_xlabel('Laps')
    ax.set_ylabel('Positions')
    plt.show()


if __name__ == '__main__':
    GUI()