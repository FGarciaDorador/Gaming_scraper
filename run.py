from gscrap.scraping import scrap_games # in the future it should be 
# from gscrap import scrap

if __name__ == '__main__':
    # TODO(albert): Detect website and pass it as argument and 
    # in that case don't load file. For now we only load file.
    # TODO: Add checks that columns and stores are indeed in config.
    with open('config.ylm', 'r') as cf:
        config = yalm.load(cf)
    cols = config['columns']
    stores = config['stores']

    scrap_games(*stores, cols=cols)
