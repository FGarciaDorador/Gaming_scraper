from gscrap.scraping import scrap_games # in the future it should be 
# from gscrap import scrap

from yaml import load, Loader

if __name__ == '__main__':
    # TODO(albert): Detect website and pass it as argument and 
    # in that case don't load file. For now we only load file.
    # TODO: Add checks that columns and stores are indeed in config.
    with open('config.ylm', 'r') as cf:
        config = load(cf, Loader=Loader)
    cols = config['columns']
    stores = config['stores']

    results = scrap_games(*stores, cols=cols)
    results.to_csv('out.csv')
