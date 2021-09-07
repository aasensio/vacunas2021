import numpy as np
import matplotlib.pyplot as pl
import pandas as pd
import scipy.optimize as opt
import datetime
import requests

def f(x, a, c, d):
    return a / (1. + np.exp(-c * (x - d)))

if __name__ == '__main__':
    print('Actualizando datos.')
    data = requests.get('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_vacunas.csv')
    with open('ccaa_vacunas.csv', 'wb') as file:
        file.write(data.content)

    tmp = pd.read_csv('ccaa_vacunas.csv')

    values = tmp.loc[tmp['cod_ine'] == 1]['Fecha publicación'].values    
    last_day = datetime.datetime.strptime(values[-1], '%Y-%m-%d')
    now = datetime.datetime.now()

    menores_14 = [15.25, 13.76, 10.64, 14.38, 12.45, 12.70, 11.66, 14.74, 14.98, 14.36, 13.28, 11.55, 14.89, 16.63, 15.14, 13.61, 14.14, 19.30, 23.13]
        

    pct_completa = []
    pct_unadosis = []
    days = []
    name = []

    for comunidad in range(19):

        values = tmp.loc[tmp['cod_ine'] == comunidad+1]['Porcentaje con pauta completa'].values
        values = np.array([float(i.replace(',', '.')) for i in values])
        pct_completa.append(values)

        values1 = tmp.loc[tmp['cod_ine'] == comunidad+1]['Personas con al menos una dosis'].fillna('0.001').values        
        values1 = np.array([float(i.replace('.', '')) for i in values1])
        values2 = tmp.loc[tmp['cod_ine'] == comunidad+1]['Personas con pauta completa'].fillna('0.001').values
        values2 = np.array([float(i.replace('.', '')) for i in values2]) + 1
        
        values = np.nan_to_num(values1 / values2 * values)
        pct_unadosis.append(values)

        name.append(tmp.loc[tmp['cod_ine'] == comunidad+1]['CCAA'].values[0])

        values = tmp.loc[tmp['cod_ine'] == comunidad+1]['Fecha publicación'].values
        reference = datetime.datetime.strptime(values[0], '%Y-%m-%d')
        values = np.array([(datetime.datetime.strptime(values[i], '%Y-%m-%d') - reference).days for i in range(len(values))])
        days.append(values)

    name = [l.replace('Castilla', 'C.') if 'Castilla' in l else l for l in name]
    name = [l.replace(' y', '') for l in name]
    

    with pl.xkcd():
        fig, ax = pl.subplots(nrows=4, ncols=5, figsize=(17, 13), sharey='row', sharex='col')
        days_full = np.linspace(0.0, 400, 400)
        for i in range(19):

            a, c = np.random.exponential(size=2)
            d = 1.0
            (a_, c_, d_), _ = opt.curve_fit(f, days[i] / 100.0, pct_completa[i] / 100.0)
            
            (a1_, c1_, d1_), _ = opt.curve_fit(f, days[i] / 100.0, pct_unadosis[i] / 100.0)

            y_fit = f(days_full / 100.0, a_, c_, d_)

            if (i == 0):            
                ax.flat[i].plot(days[i], pct_completa[i], linewidth=3, label='2 dosis', color='C0')
                ax.flat[i].plot(days[i], pct_unadosis[i], label='1 dosis', color='C1')            
                ax.flat[i].plot(days_full, y_fit * 100.0, ':', linewidth=3, label='Proyección', color='C2')
                ax.flat[i].axhline(100-menores_14[i], label='Límite >14 años', color='C3')
            else:
                ax.flat[i].plot(days[i], pct_completa[i], linewidth=3, color='C0')
                ax.flat[i].plot(days[i], pct_unadosis[i], color='C1')
                ax.flat[i].plot(days_full, y_fit * 100.0, ':', linewidth=3, color='C2')
                ax.flat[i].axhline(100-menores_14[i], color='C3')

            ax.flat[i].set_ylim([0, 100])            

            print(f' - {name[i]:15s} -> a={a_:5.2f}, c={c_:5.2f}, d={d_:5.2f}')

            ax.flat[i].set_title(f'{name[i]} - {100.0*a_:3.1f}')        

        ax.flat[-1].remove()
        fig.supxlabel('Días desde inicio vacunación')
        fig.supylabel('Porcentaje vacunación completa')
        fig.suptitle(f"Actualizado a {last_day.strftime('%Y-%m-%d')}")
        fig.legend(bbox_to_anchor=(0.9,0.25))
        pl.show()

    pl.savefig('vacunas.png', dpi=300)