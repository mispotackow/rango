import json
import requests


# Добавьте ключ учетной записи Microsoft в файл с именем bing.key
def read_bing_key():
    """
    читает ключ API BING из файла с именем 'bing.key'
    возвращает: строку, которая либо None, т.е. ключ не найден, либо с ключом
    не забудьте поместить bing.key в файл .gitignore, чтобы избежать его фиксации.
    """
    bing_api_key = None
    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline().strip()
    except:
        try:
            with open('../bing.key') as f:
                bing_api_key = f.readline().strip()
        except:
            raise IOError('bing.key file not found')
    if not bing_api_key:
        raise KeyError('Bing key not found')
    return bing_api_key


def run_query(search_terms):
    """
    См.документацию корпорации Майкрософт по другим параметрам, которые можно задать.
    http://bit.ly/twd-bing-api
    """
    bing_key = read_bing_key()
    search_url = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
    # search_url = 'https://api.bing.microsoft.com/'
    headers = {'Ocp-Apim-Subscription-Key': bing_key}
    params = {'q': search_terms, 'textDecorations': True, 'textFormat':' HTML'}

    # Оформите запрос, учитывая детали выше.
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    # Теперь, когда ответ в игре, создайте список Python.
    results = []
    for result in search_results['webPages']['value']:
        results.append({
            'title': result['name'],
            'link': result['url'],
            'summary': result['snippet']})

    return results


def main():
    print('Добро пожаловать.')
    search_terms = input('Введите запрос: ')
    response = run_query(search_terms)
    return response


if __name__ == '__main__':
    main()
