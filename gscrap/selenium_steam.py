from selenium import webdriver
import time
import yalm

class Scrapper:
    def __init__(self):
        with open('config.yml', 'r') as config_file:
            config = yalm.load(config_file)
            executable_path = config['webdriver']['geckodriver_path']
            driver = config['webdriver']['browser']

class SteamScrapper(Scrapper):

    def __init__(self):
        super(self, SteamScrapper).__init__()
        self.driver = webdriver.Firefox(executable_path = r"C:\Users\Fernando\Desktop\geckodriver-v0.27.0-win64\geckodriver.exe")
        self.url = "https://store.steampowered.com/"
        self.driver.get(self.url)


    def price(self,item):

        searchbox = self.driver.find_element_by_id("store_nav_search_term")
        searchbox.send_keys(item)
        #caja donde se ve la imagen, título y precio del juego
        suggestion_box = self.driver.find_element_by_id("search_suggestion_contents")

        time.sleep(0.5) #necesita reposar para encontrar más info
        #hacemos try except para aquellos juegos que no se encuentren en steam o quizá estén mal escritos
        try:
            price = suggestion_box.find_element_by_class_name("match_price").text
        except:
            price = None

        searchbox.clear()
        return price

    def quit(self):

        self.driver.quit()
