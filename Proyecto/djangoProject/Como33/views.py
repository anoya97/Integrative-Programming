import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import fastf1
import fastf1.api
import fastf1.plotting
from fastf1.ergast import Ergast
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.utils.decorators import method_decorator
from .forms import UserRegisteredForms
import pendulum
import numpy as np
import pandas as pd
from datetime import date
import wikipediaapi
import requests
import random
import io
from django.contrib.auth.models import User
import urllib, base64
from io import BytesIO
import datetime
import time


#Token para poder ver los videos de youtube
yttoken = 'AIzaSyDaPGB9G-eAogxxAGTUEM-0eqGQ6W3St54'

# ========================================================== REGISTER ==========================================================

def register(request):
    if request.method == 'POST':
        form = UserRegisteredForms(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username,password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('profile')     

    else:
        form = UserRegisteredForms()
    context = {'form' : form}
    return render(request,'register.html', context)


# ========================================================== PROFILE ==========================================================
@login_required
def profile(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        username = request.user.username
        if username is None:
            return redirect('login')
        else:    
            context = {'username': username }
            return render(request,'profile.html', context)



# ========================================================== CLASIFICATION ==========================================================
@login_required
def classification(request):
    try:
        # En caso de que el usuario introduzca un año
        if request.method == 'POST':
            
            # Obtenemos los datos del desplegable
            year = request.POST.get('year')
            years = list(range(1980, date.today().year+1))
            
            # Prevención de errores
            if year is None:
                classification = classificationPlot(date.today().year)
            else:
                classification = classificationPlot(year)
            
            # Hacemos que la tabla obtenga un formato de html
            table = classification.to_html(index=False, classes='table table-striped')
            
            context = {'years': years, 'classification': table}
            
        else:
            
            # Obtenemos los datos del desplegable
            years = list(range(1980, date.today().year+1))
            classification = classificationPlot(date.today().year)
            
            # Hacemos que la tabla obtenga un formato de html
            table = classification.to_html(index=False, classes='table table-striped')
            
            context = {'years': years, 'classification': table}
        
        return render(request, 'classification.html', context)
    except:
        errMsg = 'Error al cargar la clasificación'
        context = {'errMsg' : errMsg}
        return render(request, 'classification.html', context)
    
    
def get_drivers_standings(year):
    ergast = Ergast()
    standings = ergast.get_driver_standings(season=year)
    return standings.content[0]


def calculate_max_points_for_remaining_season():
    POINTS_FOR_SPRINT = 8 + 25 + 1  # Winning the sprint, race and fastest lap
    POINTS_FOR_CONVENTIONAL = 25 + 1  # Winning the race and fastest lap

    events = fastf1.events.get_events_remaining(force_ergast=True)
    # Count how many sprints and conventional races are left
    sprint_events = len(events.loc[events["EventFormat"] == "sprint"])
    conventional_events = len(events.loc[events["EventFormat"] == "conventional"])

    # Calculate points for each
    sprint_points = sprint_events * POINTS_FOR_SPRINT
    conventional_points = conventional_events * POINTS_FOR_CONVENTIONAL

    return sprint_points + conventional_points


def classificationPlot(year):
    driver_standings = get_drivers_standings(year)
    
    actual_year = date.today().year
    position = []
    name = []
    points = []
    constructor = []
    
    # En caso de que sea el año actual tenemos que usar más datos 
    if (int(year) == actual_year):
        LEADER_POINTS = int(driver_standings.loc[0]['points'])
        canwin = []
        maxpoints = []
        
        # Obtenemos los datos necesarios para cada uno de los pilotos
        for i, _ in enumerate(driver_standings.iterrows()):
            driver = driver_standings.loc[i]
            driver_max_points = int(driver["points"]) + calculate_max_points_for_remaining_season()
            can_win = 'No' if driver_max_points < LEADER_POINTS else 'Yes'
            
            position.append(driver['position'])
            name.append(driver['givenName'] + " " + driver['familyName'])
            points.append(driver['points'])
            constructor.append(driver['constructorNames'][-1])
            maxpoints.append(driver_max_points)
            canwin.append(can_win)
        
        data = {'Position':position, 'Name': name, 'Team': constructor, 'Points': points, 'Maxpoints': maxpoints, 'Can win?': canwin}
        classification = pd.DataFrame(data)
        
    else:
        # Obtenemos los datos necesarios para cada uno de los pilotos
        for i, _ in enumerate(driver_standings.iterrows()):
            driver = driver_standings.loc[i]

            position.append(driver['position'])
            name.append(driver['givenName'] + " " + driver['familyName'])
            points.append(driver['points'])
            constructor.append(driver['constructorNames'][-1])


        data = {'Position':position, 'Name': name, 'Team': constructor, 'Points': points}
        classification = pd.DataFrame(data)

    return classification
 

# ========================================================== CALENDAR ==========================================================  
@login_required
def calendar (request):
    calendar = calendarPlot()
    table = calendar.to_html(index=False, classes='table table-striped')
    context = {'calendar': table}
            
    return render(request, 'calendar.html', context)
     
      
def calendarPlot():
    EventSchedule = fastf1.get_event_schedule(date.today().year)
    Columnas = ['RoundNumber','Country','Location','EventDate','Session5DateUtc']
    fecha_actual = time.strftime("%Y-%m-%d")

    final = EventSchedule.loc[:, Columnas]
    final['EventDate'] = pd.to_datetime(final['EventDate'])

    final_actual = final[final['EventDate'] > fecha_actual]
    final_actual['Session5DateUtc'] = final_actual['Session5DateUtc'].apply(lambda x: x.strftime('%H:%M'))
    final_actual['Session5DateUtc'] = final_actual['Session5DateUtc'].apply(lambda x: str(x))
    final_actual['Session5DateUtc'] = final_actual['Session5DateUtc'].apply(lambda x: pendulum.from_format(x,'HH:mm',tz='Europe/Madrid'))
    final_actual['Session5DateUtc'] = final_actual['Session5DateUtc'].apply(lambda x: x.strftime('%H:%M:%S'))
    final_actual.columns = ['Round Number','Country','City','Date','Hour']

    return final_actual;


# ========================================================== DRIVER ==========================================================  
@login_required
def driver(request):
    try:
        # Si hay una peticion de un piloto
        if request.method == 'POST':    
            
            #Recogo el piloto que se ha introducido y cargo la api de wikipedia
            piloto = request.POST.get('Driver') 
            
            #Creo la lista de piloto en el desplegable 
            session = fastf1.get_session(date.today().year,'Bahrein','R') 
            session.load(telemetry=False, weather=False, messages=False)
            pilots = session.drivers
            drivers = []
            idPiloto = ""
            
            #Obtengo nombre de los pilotos y se lo paso al desplegable
            for pilot in pilots:
                driver = session.get_driver(pilot) 
                drivers.append(driver.FullName) 
                if(driver.FullName == piloto):
                    idPiloto = driver.Abbreviation

            #Para coger la foto del piloto
            fotopiloto = session.get_driver(idPiloto)
            imagen = fotopiloto.HeadshotUrl    

            #Cogemos la info del piloto de wikipedia 
            if(piloto == "Carlos Sainz"):
                piloto = "Carlos Sainz Jr."
            if(piloto == "George Russell"):
                piloto = "George Russell (racing driver)"     
            summary = wikipedia(piloto)

            video = ytube(piloto)

            context = {'Drivers' : drivers, 'Summary' : summary, 'Imagen' : imagen, 'Video' : video}

        # Si es la primera vez que se accede a la pagina se muestra la info de Fernando Alonso    
        else: 
            
            summary = wikipedia('Fernando Alonso')

            #Lo mismo que arriba es para el desplegable
            session = fastf1.get_session(date.today().year,'Bahrein','R') 
            session.load(telemetry=False, weather=False, messages=False)
            pilots = session.drivers
            drivers = []
            for pilot in pilots:
                driver = session.get_driver(pilot)
                drivers.append(driver.FullName)

            #Para coger la foto del piloto
            fotopiloto = session.get_driver("ALO")
            imagen = fotopiloto.HeadshotUrl

            #Obtenemos la url del video de youtube
            video = ytube("Fernando Alonso")
            print(video)
        
            context = {'Drivers' : drivers, 'Summary' : summary, "Imagen" : imagen, 'Video' : video} 

        return render(request, 'driver.html',context)  
    except:
        errMsg = 'NO SE HA SELECCIONADO NINGÚN PILOTO'
        context = {'errMsg' : errMsg}
        return render(request, 'driver.html',context)  


def wikipedia(piloto):
    wiki = wikipediaapi.Wikipedia('en')
    if(piloto == ""):
        return None
    else:    
        page = wiki.page(piloto)
        summary = page.summary
        return summary


def ytube(piloto):

    # Cojemos el enlace para la api de youtube
    SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
    query = 'los mejores videos de ' + piloto + 'en la formula 1 sin copy'
    
    # Realizamos la búsqueda
    data = {
        'part': 'snippet',
        'q': query,
        'key': yttoken,
        'maxResults': 20,
        'regionCode': 'ES'
    }

    # Mandamos la petición a la api de youtube
    r = requests.get(SEARCH_URL, params=data)
    response_json = r.json()
    
    # Filtramos la respuesta de la api con json y devuelvemos un vídeo aleatorio de los 20 devueltos
    x=random.randint(0, 19) 
    id = response_json['items'][x]['id']['videoId']
    if(piloto == ""):
        return None
    else:
        return 'https://www.youtube.com/embed/' + id  


# ========================================================== GP INFO ==========================================================  
@login_required
def gpinfo (request):
    try:
        years = list(range(2018, date.today().year))
        if request.method == 'POST':
            year = request.POST.get('year')
            return redirect('gpinfo2', ano=year)

        return render(request, 'gpinfo.html',{ 'years' : years})
        
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg}
        return render(request, 'gpinfo.html', context)   


@login_required
def gpinfo2 (request, ano):
    try:
        
        if request.method == 'POST':
            circuit = request.POST.get('gptag')
            if circuit is None: 
                return redirect('gpinfo')
            else:
                return redirect('gpinfo3', ano=ano, circuit=circuit)

        ergast = Ergast()
        gp = []
        circuits = ergast.get_circuits(int(ano), result_type='raw')
        for circuit in circuits:
            gp.append(circuit['circuitName'])
    
        return render(request, 'gpinfo2.html',{ 'gptag' : gp})
        
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg}
        return render(request, 'gpinfo2.html', context)   


@login_required
def gpinfo3(request, ano, circuit):
    
    try:
        if request.method == 'POST':
            driver = request.POST.get('drivers')
            gptag = request.POST.get('gptag')
            if driver is None and gptag is None:
                return redirect('gpinfo')        

        ergast = Ergast()
        gp = []
        circuits = ergast.get_circuits(int(ano), result_type='raw')
        for circ in circuits:
            gp.append(circ['circuitName'])

        
        session = fastf1.get_session(int(ano), circuit, 'R')
        session.load()
        results = session.results
                
        # Obtenemos los nombres de los pilotos para el desplegable
        drivers = results['FullName']
        
        date = session.date
        weather = pd.DataFrame(session.weather_data)
        track_status = pd.DataFrame(session.track_status)
                
        # Creamos la tabla de las posiciones.
        result_data = {'Position': results['Position'], 'Driver name': results['FullName'], 'Team Name': results['TeamName'], 'Status': results['Status'], 'Points': results['Points']}
        result_data['Position'] = result_data['Position'].astype(int)
        result_table = pd.DataFrame(result_data).to_html(index=False, classes='table table-striped')
                
        # Obtenemos la información que queremos sobre el tiempo
        # Obtenemos la media de la humedad
        humidity = weather['Humidity'].mean().round(2)
                
        # Obtenemos información sobre la lluvia dentro de pista
        rained = weather['Rainfall'].drop_duplicates()
        rainfall = False
                
        for i in rained:
            if bool(i):
                rainfall = True

        if rainfall:
            anterior = weather['Time'].iloc[0]
            rain_time = weather['Time'].iloc[0]
            for indice,fila in weather.iterrows():
                if bool(fila['Rainfall']):
                    rain_time = rain_time + fila['Time'] - anterior

                anterior = fila['Time']
                    
        # Obtenemos la media de la temperatura del asfalto durante la carrera (ºC)
        trackTemp = weather['TrackTemp'].mean().round(2)


        # Obtenemos la información que queremos sobre los mensajes de carrera.

        scd = False
        scd_time = pd.Timedelta(days=0, hours=0, minutes=0, seconds=0) 
        yellow = False
        yellow_time = pd.Timedelta(days=0, hours=0, minutes=0, seconds=0)
        vscd = False
        vscd_time = pd.Timedelta(days=0, hours=0, minutes=0, seconds=0)
        red = False
        red_time = pd.Timedelta(days=0, hours=0, minutes=0, seconds=0)
        
        for indice,fila in track_status.iterrows():
                    
            # Obtenemos el tiempo el momento en el que hubo algún tipo de evento
            if int(fila['Status']) == 2:
                yellow_aux_time = fila['Time']
                yellow = True

            if int(fila['Status']) == 4:
                scd_aux_time = fila['Time']
                scd = True
                    
            # En caso de que haya bandera roja también se quitan los SC y las banderas
            if int(fila['Status']) == 5:
                if yellow:
                    yellow_time = yellow_time + fila['Time'] - yellow_aux_time
                    yellow = False
                        
                if scd:
                    scd_time = scd_time + fila['Time'] - scd_aux_time
                    scd = False
                            
                if vscd:
                    vscd_time = vscd_time + fila['Time'] - vscd_aux_time
                    vscd = False
                        
                red_aux_time = fila['Time']
                red = True

            if int(fila['Status']) == 6:
                vscd_aux_time = fila['Time']
                vscd = True

            # Calculamos el tiempo que ha tardado el evento en parar.
            if int(fila['Status']) == 7:
                if vscd:
                    vscd_time = vscd_time + fila['Time'] - vscd_aux_time
                    vscd = False
                    
            if int(fila['Status']) == 1:
                if yellow:
                    yellow_time = yellow_time + fila['Time'] - yellow_aux_time
                    yellow = False
                        
                if red:
                    red_time = red_time + fila['Time'] - red_aux_time
                    red = False
                        
                if scd:
                    scd_time = scd_time + fila['Time'] - scd_aux_time
                    scd = False

        # Parseamos las fechas
        
        yellow_time = str(yellow_time).split()[-1].split('.')[0]
        red_time = str(red_time).split()[-1].split('.')[0]
        scd_time = str(scd_time).split()[-1].split('.')[0]
        vscd_time = str(vscd_time).split()[-1].split('.')[0]
        
        if rainfall:
            rain_time = str(rain_time).split()[-1].split('.')[0]
            context = {'gptag': gp, 'gpname': circuit, 'result': result_table, 'date': date, 'humidity':humidity, 'rain_time': rain_time, 
                    'trackTemp': trackTemp, 'yellow': yellow_time, 'red': red_time, 'scd': scd_time, 'vscd': vscd_time, 'drivers': drivers}
        else:
            context = {'gptag': gp, 'gpname': circuit, 'result': result_table, 'date': date, 'humidity':humidity, 'trackTemp': trackTemp, 
                    'yellow': yellow_time, 'red': red_time, 'scd': scd_time, 'vscd': vscd_time, 'drivers': drivers}
        
        if request.method == 'POST':
            driver = request.POST.get('drivers')
            gptag = request.POST.get('gptag')
            if driver is None:
                return redirect('gpinfo3', ano=ano, circuit=gptag)
            else:
                return redirect('driverinfo', ano=ano, circuit=circuit, driver=driver)
            
        else:
            return render(request, 'gpinfo3.html', context)
    
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg, 'ano': ano}
        return render(request, 'gpinfo3.html', context)

@login_required
def driverinfo(request, ano, circuit, driver):
    try:
        if request.method == 'POST':
            return redirect('gpinfo3', ano=ano, circuit=circuit)
        
        # Cargamos la información necesaria para obtener la información.
        session = fastf1.get_session(ano, circuit,'R') 
        session.load(weather=False, messages=False)
        pilots = session.drivers
        idPiloto = ""
                
        # Obtenemos la abreviación del nombre del piloto.
        for pilot in pilots:
            driv = session.get_driver(pilot) 
            
            if(driv.FullName == driver):
                finish_position = int(driv['Position'])
                idPiloto = driv.Abbreviation

        # Obtenemos la información del piloto.
        image = session.get_driver(idPiloto).HeadshotUrl
        pilot = session.laps.pick_driver(idPiloto)
        car = pd.DataFrame(pilot.get_car_data())
        
        fastest = str(pilot.pick_fastest()['LapTime']).split()[-1].split('.')[0]
        team = pilot.pick_fastest()['Team']
        
        speeds1 = pd.DataFrame(pilot)['SpeedI1'].mean().round(2)    # Velocidades en el primer sector
        speeds2 = pd.DataFrame(pilot)['SpeedI2'].mean().round(2)    # Velocidades en el segundo sector
        speedFL = pd.DataFrame(pilot)['SpeedFL'].mean().round(2)    # Velocidad en línea de meta
        speedST = pd.DataFrame(pilot)['SpeedST'].mean().round(2)    # Velocidad en la recta más larga del circuito
        
        # Obtenemos información de las posiciones en las que se ha encontrado el piloto:
        positions = pd.DataFrame(pilot)['Position'].dropna().drop_duplicates().astype(int).sort_values()
        max_position = positions.min()
        min_position = positions.max()
        
        # Obtenemos la información del coche
        
        # Obtenemos la información de las ruedas utilizadas.
        tyres_data = {'TyreLife' : pilot['TyreLife'], 'Compound': pilot['Compound'], 'LapNumber': pilot['LapNumber']}
        tyres =  pd.DataFrame(tyres_data).dropna()
        
        # Obtenemos las vueltas que duraron las ruedas
        laps = int(tyres['TyreLife'].iloc[0])
        compound = tyres['Compound'].iloc[0]
        lap = 0
        wheel = []
        life = []
        lapNumber = []
        for indice,fila in tyres.iterrows():
            if int(fila['TyreLife']) < laps:
                wheel.append(compound)
                life.append(laps)
                lapNumber.append(lap)
            
            compound = fila['Compound']
            laps = int(fila['TyreLife'])
            lap = int(fila['LapNumber'])
        
        # Añadimos las últimas ruedas que se usaron.
        wheel.append(compound)
        life.append(laps)
        lapNumber.append('Not changed')
        
        data_tyreChanges = {'Tyre' : wheel, 'Life' : life, 'Change Lap': lapNumber}
        tyreChanges = pd.DataFrame(data_tyreChanges).to_html(index=False, classes='table table-striped')
        
        speed_avg = car['Speed'].mean().round(2)
        rpm_mean = car['RPM'].mean().round(2)
        throttle_mean = car['Throttle'].mean().round(2)
          
        if image == "None":
            context = {'fastest': fastest, 'team': team, 'speeds1': speeds1, 'speeds2': speeds2, 'speedFL': speedFL, 'speedST': speedST, 'positions': positions,
                    'min_position': min_position, 'max_position': max_position, 'finish_position': finish_position, 'tyreChanges': tyreChanges, 'speed_avg': speed_avg, 
                    'rpm_mean': rpm_mean, 'throttle_mean': throttle_mean}  
        else:
            context = {'image': image, 'fastest': fastest, 'team': team, 'speeds1': speeds1, 'speeds2': speeds2, 'speedFL': speedFL, 'speedST': speedST, 'positions': positions,
                    'min_position': min_position, 'max_position': max_position, 'finish_position': finish_position, 'tyreChanges': tyreChanges, 'speed_avg': speed_avg, 
                    'rpm_mean': rpm_mean, 'throttle_mean': throttle_mean}            
        
        return render(request, 'driverinfo.html', context)
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg, 'ano': ano, 'circuit': circuit}
        return render(request, 'driverinfo.html', context)   
    
# ========================================================== SPEED ==========================================================           
@login_required
def speed(request):
    try:
        years = list(range(2018, date.today().year))
        if request.method == 'POST':
            # Datos obtenidos de la segunda gráfica:
            spe_year = request.POST.get('spe_year')
            return redirect('speed2', ano=spe_year)

        return render(request, 'speed.html',{ 'spe_year' : years})
        
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg}
        return render(request, 'speed.html', context)     
    
@login_required
def speed2(request,ano):
    try:
        if request.method == 'POST':
            # Datos obtenidos de los desplegables:
            spe_driver = request.POST.get('spe_driver')
            spe_gptag = request.POST.get('spe_gptag')

            # Datos para los desplegables
            ergast = Ergast()
            spe_circuits = []
            spe_drivers = []
            
            # Datos de los desplegables
            circuits = ergast.get_circuits(int(ano), result_type='raw')
            for circuit in circuits:
                spe_circuits.append(circuit['circuitName'])
            spe_session = fastf1.get_session(int(ano), spe_gptag, 'R')
            spe_session.load(weather=False, messages=False)
            for driver in spe_session.drivers:
                spe_drivers.append(spe_session.get_driver(driver).FullName)  

            
            spe_years = int(ano)
            plot=speedPlot(spe_driver,spe_session,spe_years) 
            
                
            context = {'spe_year': ano, 'spe_driver':spe_drivers, 'spe_gptag': spe_circuits,
                    'plot' : plot}
        
        else:
            # Datos de los desplegables
            ergast = Ergast()
            spe_circuits = []
            spe_drivers = []
            
            
            # Datos de los desplegables
            circuits = ergast.get_circuits(int(ano), result_type='raw')
            for circuit in circuits:
                spe_circuits.append(circuit['circuitName'])
            spe_session = fastf1.get_session(int(ano), spe_circuits[0], 'R')
            spe_session.load(telemetry=False, weather=False, messages=False)
            for driver in spe_session.drivers:
                spe_drivers.append(spe_session.get_driver(driver).FullName)
            
            
            context = {'spe_year': ano, 'spe_driver':spe_drivers, 'spe_gptag': spe_circuits}
        
        return render(request, 'speed2.html', context)
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg, 'ano' : ano}
        return render(request, 'speed2.html', context)   


def speedPlot(driver, session, year):
    try:
        # Obtenemos la vuelta rapida del piloto
        driver_standings = get_drivers_standings(year)
        for i, _ in enumerate(driver_standings.iterrows()):
                driver2 = driver_standings.loc[i]
                driverName = driver2['givenName'] + " " + driver2['familyName']
                if driverName == driver:
                    tag = driver2['driverCode']
        
        lap = session.laps.pick_driver(tag).pick_fastest()

        # Ahora, preparamos el plot
        fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
        fig.suptitle(f'{driver} - Fastest Lap', size=24, y=0.97)
        
        # Ajustamos los márgenes
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
        ax.axis('off')
        
        
        # Obtenemos los datos de telemetria y creamos el DataFrame
        data = {'X': lap.telemetry['X'], 'Y': lap.telemetry['Y'], 'Speed': lap.telemetry['Speed']}
        df = pd.DataFrame(data)

        # Creamos una serie de segmentos
        points = np.array([df['X'],df['Y']]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Después de esto, ploteamos la información
        df.plot(x='X', y='Y', color='black', linestyle='-', linewidth=20, ax=ax, zorder=0)

        # Cramos una norma continua para mapear desde puntos de datos hasta colores
        norm = plt.Normalize(df['Speed'].min(), df['Speed'].max())
        lc = LineCollection(segments, cmap=mpl.cm.plasma, norm=norm, linestyle='-', linewidth=14)
        lc.set_array(df['Speed'])
        ax.add_collection(lc)
        
        
        # Creamos la guía para comprender los datos de los colores
        cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
        normlegend = mpl.colors.Normalize(vmin=df['Speed'].min(), vmax=df['Speed'].max())
        legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=mpl.cm.plasma, orientation="horizontal")
        
        # Obtenemos la figura en formato png
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        buffer = b''.join(buf)
        b2 = base64.b64encode(buffer)
        plot=b2.decode('utf-8')
        
        return plot
    except:
        return None   


# ========================================================== COMPARATION ==========================================================
@login_required 
def comparation(request):
    try:
        years = list(range(2018, date.today().year))
        if request.method == 'POST':
            # Datos obtenidos de la segunda gráfica:
            comp_year = request.POST.get('comp_year')
            return redirect('comparation2', ano=comp_year)

        return render(request, 'comparation.html',{ 'comp_year' : years})
        
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg}
        return render(request, 'comparation.html', context)   

@login_required
def comparation2(request, ano):
    try:
        if request.method == 'POST':
            
            # Datos obtenidos de la primera gráfica:
            comp_driver1 = request.POST.get('comp_driver1')
            comp_driver2 = request.POST.get('comp_driver2')
            comp_gptag = request.POST.get('comp_gptag')
            
            # Datos de los desplegables
            ergast = Ergast()
            comp_circuits = []
            comp_drivers = []
            
            # Datos de los desplegables 
            circuits = ergast.get_circuits(int(ano), result_type='raw')
            for circuit in circuits:
                comp_circuits.append(circuit['circuitName'])
            comp_session = fastf1.get_session(int(ano), comp_gptag, 'R')
            comp_session.load(weather=False, messages=False)
            for driver in comp_session.drivers:
                comp_drivers.append(comp_session.get_driver(driver).FullName)
            
            comp_years = int(ano)
            
            # Obtenemos la imagen que queremos imprimir por pantalla
            plot = comparationPlot(comp_driver1,comp_driver2,comp_session,comp_years) 
            
            context = {'comp_driver1': comp_drivers, 'comp_driver2': comp_drivers,
                        'comp_gptag': comp_circuits, 'plot' : plot}
        
        else:
            # Datos de los desplegables
            ergast = Ergast()
            comp_circuits = []
            comp_drivers = []
            
            circuits = ergast.get_circuits(int(ano), result_type='raw')
            for circuit in circuits:
                comp_circuits.append(circuit['circuitName'])

            comp_session = fastf1.get_session(int(ano), comp_circuits[0], 'R')
            comp_session.load(telemetry=False, weather=False, messages=False)
            for driver in comp_session.drivers:
                comp_drivers.append(comp_session.get_driver(driver).FullName)    
            
            context = {'comp_driver1': comp_drivers, 'comp_driver2': comp_drivers,
                        'comp_gptag': comp_circuits}    
        
        return render(request, 'comparation2.html', context)
    except:
        errMsg = 'La combinación introducida no mostró resultados'
        context = {'errMsg' : errMsg}
        return render(request, 'comparation2.html', context)
    
    
def comparationPlot(driver1, driver2, session, year):
    try:
        # Habilitamos algunos parches de matplotlib
        fastf1.plotting.setup_mpl(misc_mpl_mods=False)

        # Obtenemos una sesion
        driver_standings = get_drivers_standings(year)
        for i, _ in enumerate(driver_standings.iterrows()):
                driveraux = driver_standings.loc[i]
                driverName = driveraux['givenName'] + " " + driveraux['familyName']
                if driverName == driver1:
                    tag1 = driveraux['driverCode']
                
                if driverName == driver2:
                    tag2 = driveraux['driverCode']


        # Obtenemos las vueltas de cada uno de los pilotos
        driver1_lap = session.laps.pick_driver(tag1).pick_fastest()
        driver2_lap = session.laps.pick_driver(tag2).pick_fastest()

        # A continuacion obtenemos los datos de telemetria de cada vuelta. Tambien agregamos una columna de 'Distancia'
        # al marco de datos de telemetria, ya que esto facilita la comparacion de las vueltas.

        driver1_tel = driver1_lap.get_car_data().add_distance()
        driver2_tel = driver2_lap.get_car_data().add_distance()
        
        # Vamos a obtener los colores del equipo para hacer las lineas
        driver1_color = fastf1.plotting.team_color(driver1_lap['Team'])
        driver2_color = fastf1.plotting.team_color(driver2_lap['Team'])
        
        # Creamos un DataFrame con los datos de velocidad y distancia para ambos pilotos
        df1 = pd.DataFrame({
            f'{driver1} Speed': driver1_tel['Speed'],
            f'{driver1} Distance': driver1_tel['Distance']
        })

        df2 = pd.DataFrame({
            f'{driver2} Speed': driver2_tel['Speed'],
            f'{driver2} Distance': driver2_tel['Distance']
        })

        # Utilizamos la función ´plot´ de Pandas para crear la figura
        fig, ax = plt.subplots()
        df1.plot(x=f'{driver1} Distance', ax=ax, color=driver1_color)
        df2.plot(x=f'{driver2} Distance', ax=ax, color=driver2_color)

        ax.set_xlabel('Distance in m')
        ax.set_ylabel('Speed in km/h')

        ax.legend([driver1, driver2])
        
        plt.suptitle("Fastest Lap Comparison")
        
        # Obtenemos la figura en formato png
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        buffer = b''.join(buf)
        b2 = base64.b64encode(buffer)
        plot=b2.decode('utf-8')
        
        return plot
    except:
        return None    


# ========================================================== ABOUT ==========================================================  
@login_required
def about(request):
    return render(request, 'about.html')
