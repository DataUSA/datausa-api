'''
This code is taken from the flickrapi project
See https://github.com/rfaulkner/flickrapi/blob/master/flickrapi/shorturl.py
and http://stuvel.eu/flickrapi
'''

ALPHABET = u'123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
ALPHALEN = len(ALPHABET)
SHORT_URL = u'http://flic.kr/p/%s'

def encode(photo_id):
    '''encode(photo_id) -> short id

    >>> encode(u'4325695128')
    '7Afjsu'
    >>> encode(u'2811466321')
    '5hruZg'
    '''

    photo_id = int(photo_id)

    encoded = u''
    while photo_id >= ALPHALEN:
        div, mod = divmod(photo_id, ALPHALEN)
        encoded = ALPHABET[mod] + encoded
        photo_id = int(div)

    encoded = ALPHABET[photo_id] + encoded

    return encoded
