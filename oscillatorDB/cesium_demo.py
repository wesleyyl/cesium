import os
import tellurium as te
import zipfile
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

path = '/home/hellsbells/Desktop/test.zip'
unzip_path = path+'_unzipped'

with zipfile.ZipFile(path, 'r') as z:
    z.extractall(unzip_path)

row, col = len(os.listdir(unzip_path)), 1

fig, ax = plt.subplots(row, col, constrained_layout=True)
fig.suptitle('Examples of 3-Node Oscillators Time Series Data')
fig.set_size_inches((5,10))

for i, file in enumerate(os.listdir(unzip_path)):
    antimony = te.readFromFile(os.path.join(unzip_path, file))
    r = te.loada(antimony)
    timeseries = r.simulate(0, 5, 1000)
    ax[i].plot(timeseries['time'], timeseries['[S0]'], label='[S0]')
    ax[i].plot(timeseries['time'], timeseries['[S1]'], label='[S1]')
    ax[i].plot(timeseries['time'], timeseries['[S2]'], label='[S2]')
    ax[i].legend(loc='right')
    if i >= 15:
        break
plt.show()
