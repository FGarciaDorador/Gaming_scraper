from bs4 import BeautifulSoup
import requests
import csv
import re
import datetime
import os
import zipfile
import time
from selenium import webdriver

from gscrap.selenium_steam import steam_scrapper

def run():
    sc = steam_scrapper()

    # denominar el archivo de acuerdo a la fecha de raspado web
    date_scrape = datetime.datetime.now().date()
    file_name = 'IG_data_' + str(date_scrape) + '.csv'
    csv_file = open(file_name, 'w', encoding="utf-8")

    # escribir en primera columna del archivo csv el nombre de las columnas
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Id','Título', 'Precio', 'Precio_Steam', 'Descuento', 'Región', 'DLC', 'Plataforma', 'link', 'Disponibilidad', 'Géneros',
                         'Fecha de salida', 'User rating','Comentario', 'Nota comentario'])

    # crear una carpeta llamada imagenes para almacenar las portadas de los juegos
    folder_name = 'imagenes'
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    # inicializar numero_id
    numero_id = 1
    base_link = 'https://www.instant-gaming.com'
    page_link = '/en/search/?all_types=1&all_cats=1&min_price=0&max_price=100&noprice=1&min_discount=0&max_discount=100&min_reviewsavg=10&max_reviewsavg=100&noreviews=1&available_in=ES&gametype=all&sort_by=&query='
    url = base_link + page_link
    source = requests.get(url)
    soup = BeautifulSoup(source.content)
    print(url)

    ### BACKGROUND IMAGE ###
    # la imagen solo se guardara en la primera página ya que el fondo no cambia
    background_url= re.findall('http.*?jpg', soup.find('div', {"id": "backgroundLink"})['style'])[0]
    background_imagen = requests.get(background_url)
    with open('background.jpg', 'wb') as f:
        f.write(background_imagen.content)


    # realizaremos webscraping hasta que no haya más páginas en ese caso romperemos el while loop
    while True:
        #en la pag principal hay 4 mejores juegos y los demas son item mainsadow. En todas las demás paginas,
        #los item deberian ser normales
        best_items = soup.find_all('div', class_='category-best item mainshadow')
        normal_items = soup.find_all('div', class_='item mainshadow')

        items = best_items + normal_items

        for item in items:

            ### NOMBRE DEL JUEGO ###
            titulo = item.find('div', class_='name').text

            ### GUARDAR IMAGEN ###
            imagen_url = item.find('img', class_='picture mainshadow').get('src')

            imagen = requests.get(imagen_url)
            with open(folder_name + '/' + str(numero_id) +'.jpg', 'wb') as f:
                f.write(imagen.content)


            ### PRECIO ###
            # obtener precio del juego - se extrae únicamente el dato numérico (sin caracteres especiales o símbolo del euro)
            try:
                precio = re.findall("\d+\.?\d+", item.find('div', class_='price').text)[0]
            except IndexError:
                precio = ''

            precio_steam = sc.price(titulo) #llamamos a la función del otro script

            ### DESCUENTO ###
            try:
                descuento = item.find('div', class_='discount').text
            except:
                descuento = 'No hay descuento para este juego :('

            region = item['data-region']
            dlc = item['data-dlc']
            link = item.a['href']

            #Hay un link (assassins valhala, que yo sepa) que dice que hay muchos redirects y no puede hacer la request
            #Por eso hago que vaya al siguiente item del loop escribiendo la info de la pag principal unicamente
            try:
                source2 = requests.get(link)
            except:
                plataforma = None
                dispo = None
                generos = None
                rating = None
                release_date = None
                comment = None
                comment_rating = None
                csv_writer.writerow([titulo, precio, precio_steam, descuento, region, dlc, plataforma,
                                     link, dispo, generos, release_date, rating, comment, comment_rating])
                continue

            soup2 = BeautifulSoup(source2.content)

            subinfo = soup2.find('div', class_='subinfos')

            plataforma = subinfo.a.text

            ### DISPONIBILIDAD ###
            # dos nombres posibles download o preorder
            # .strip() eliminar espacios al principio y al final de la string
            dispo = subinfo.find('div', class_=['download', 'preorder']).text.strip()

            try:
                tags = soup2.find('div', class_='tags').text
                generos = tags.split('\n')[1:-2]
            except:
                generos = 'No tags'

            pestañas = soup2.find('div', class_='tabs')

            ### RATING ###
            try:
                rating = pestañas.find('a', class_='tab mainshadow productreviews').span.text

                # algunos productos no tiene rating porque los usuarios aun no han puntuado
                # en este caso el rating se especifica con un ?
                if rating == '?':
                    rating = None
            # otro productos no tiene rating porque no hay opcion de puntuarlos - por ejemplo tarjetas de regalo
            except AttributeError:
                rating = None

            ### RELEASE DATE ###
            release_date = soup2.find('div', class_='release').span.text

            try:
                comment = soup2.find('p', itemprop='reviewBody').text
            except Exception as e:
                comment = None

            try:
                comment_rating = soup2.find('span', itemprop='ratingValue').text
            except Exception as e:
                comment_rating = None

            csv_writer.writerow([numero_id, titulo, precio, precio_steam, descuento, region, dlc,
                                 plataforma, link, dispo, generos, release_date, rating, comment, comment_rating])
            numero_id = numero_id + 1

        # identificar el último boton para acceder a la páginas
        last_element = soup.find(class_='pagination bottom').find_all('li')[-1]

        # si el texto del ultimo elemento es > quiere decir que existe otra página y por lo tanto podemos continuar con el raspado
        if last_element.text == '>':
            page_link = last_element.find('a')['href']
            print('Siguiente página')
        else:
            print('No hay más páginas. Fin del scraping')
            break

        # accedemos a la siguiente página
        url = base_link + page_link
        source = requests.get(url)
        soup = BeautifulSoup(source.content)
        print(url[-8:])


    csv_file.close()
    sc.quit()




