#!/usr/bin/env python3
import requests as req
import os
import csv
import re
from time import sleep
from tqdm import tqdm


key = os.environ['APIKEY']
searchurl = ("https://api.themoviedb.org/3/search/movie/?api_key=" + key)
appendurl = ("&append_to_response=images,details,credits")
last_url = searchurl + appendurl

mydir = os.path.dirname(__file__)
print(f"\n Current Project Dirctory Is: {mydir}")
file_path = input("\n Save As: ")
filename_csv = str(file_path) + str('_new_.csv')
filename_img = str(file_path) + str('_new_image')
titlelist = input("\n Locate List: ")
year_selector = input("\n Select the year: ")

if not os.path.exists(filename_img):
    os.mkdir(filename_img)

if os.path.exists(filename_csv):
    print("\n WARNING File Already Exisits: Appending to existing file. \n")

server_test = ("https://api.themoviedb.org/3/search/movie?api_key=" + key + "&language=en-US&query=Homeland")

re = req.get(server_test)
if re.status_code == 200:
    print ('\n Server Test Successful!\n')
else:
    print ('Server Test Failed ... Please Check Internet Connection Or Script ... ')

with open(filename_csv,'a',newline='',encoding='UTF-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Plot", "Rating", "Year", "Genre", "Casts", "Image"])
    title_file = open(titlelist,'r',encoding='UTF-8')
    title_lines = title_file.readlines()
    for title_line in tqdm(title_lines[104:],desc=" Request Progress: ",total=len(title_lines)):
        movie_titles = title_line[:-1]
        movie_titles.replace(" ","%20")
        params = {'query' : movie_titles, 'year' : year_selector}
        requests_data = req.get('https://api.themoviedb.org/3/search/movie?api_key='+ key +'&language=en-US&page=1&include_adult=false', params=params)
        response = requests_data.json()
        try:
            requests_data_id = response['results'][0]['id']
            requests_data_details = req.get(f"https://api.themoviedb.org/3/movie/{requests_data_id}?api_key={key}{appendurl}")
            detail_response = requests_data_details.json()
            response_img_link = response['results'][0]['poster_path']
            title = detail_response['original_title']
            plot = detail_response['overview']
            rating = detail_response['vote_average']
            year = detail_response['release_date']
            year_short = year[:4]
            genre = detail_response['genres']
            credit = detail_response['credits']['cast']
            full_cast_names = []
            genre_short =[]
            for q in credit:
                g = q["original_name"]
                full_cast_names.append(g)
            for gg in genre:
                ww = gg['name']
                genre_short.append(ww)
            short_cast_name = full_cast_names[:5]
            img_link = f"https://image.tmdb.org/t/p/w500{response_img_link}"
            title_str = re.sub(r'[/?<>\:*|"!]', '', title)
            with req.get(img_link, stream=True) as r:
                with open(os.path.join(filename_img, title_str + ".jpg"), "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            poster = os.path.join(filename_img,title_str + ".jpg")
            writer.writerow([title, plot, rating, year_short, genre_short, short_cast_name, poster])

        except IndexError:
            print("Loggin Error")
            error =f"Error Detected API URL: {requests_data.url}\n"
            with open('ERROR_LOGS.txt', 'a') as Error_Log:
                Error_Log.write(error)
        except KeyboardInterrupt:
            print('Keyboard Interrupter Deteceted Exiting Program...Please Wait.... ')
            sleep(3)
            Error_Log.close()
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception as e:
            print("Error:", e)
            print("Trying to continue...")
            with open('ERROR_LOGS.txt', 'a') as Error_Log:
                Error_Log.write(e)
            continue
        finally:
            print("Script is Done.... Please Check Your File.")
