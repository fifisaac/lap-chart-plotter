## TO-DO
## Find an effective way to show cars with multiple drivers
## Handle sessions other than race and weekends with many races
## GUI
## Animate the graph

import matplotlib.pyplot as plt
import requests
import tkinter

def get_slug():
    decade = input('decade: ')
    r = requests.get(f'https://motorsportstats.com/api/advanced-search?entity=series&size=999&filterIds={decade}s')
    data = r.json()

    series_names = [(i['name'], i['uuid']) for i in data['content']]
    print([i[0] for i in series_names])

    series_name = input('name: ')
    for i in series_names:
        if i[0] == series_name:
            series_uuid = i[1]
            break
    year = input('year: ')
    print(f'https://motorsportstats.com/api/advanced-search?entity=events&size=999&filterIds={series_uuid}&filterIds={year}')
    r = requests.get(f'https://motorsportstats.com/api/advanced-search?entity=events&size=999&filterIds={series_uuid}&filterIds={year}')
    data = r.json()

    race_names = [(i['name'], i['uuid']) for i in data['content']]
    print([i[0] for i in race_names])
    race_name = input('name: ')
    for i in race_names:
        if i[0] == race_name:
            race_uuid = i[1]
            break

    race = f'https://motorsportstats.com/api/result-statistics?sessionSlug={race_uuid}_race&sessionFact=LapChart&size=999'
    
    return (plot(race))


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
    get_slug()