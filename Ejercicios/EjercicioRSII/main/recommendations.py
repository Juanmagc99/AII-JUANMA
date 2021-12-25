from main.models import Artist, UserTagArtist, UserArtist
from collections import Counter
import shelve

def load_similarities():
    shelf = shelve.open('dataRS.dat')
    artist_tags = top_artist_tags()
    user_tags = top_users_tags(artist_tags)
    shelf['similarities'] = compute_similarities(artist_tags, user_tags)
    shelf.close()

def recommend_artists(user):
    shelf = shelve.open("dataRS.dat")
    #conjunto de artistas que ya ha escuchado el usuario, que no se consideran para recomendar
    listened = set()
    listened = set(a.artist.id for a in UserArtist.objects.filter(user=user))
    res = []
    for artist_id, score in shelf['similarities'][user]:
        if artist_id not in listened:
            artist_name = Artist.objects.get(pk=artist_id).name
            res.append([artist_name, 100 * score])
    shelf.close()
    print(res)
    return res

def compute_similarities(artist_tags, user_tags):
    print('Computing user-artist similarity matrix')
    res = {}
    for u in user_tags:
        top_artists = {}
        for a in artist_tags:
            top_artists[a] = dice_coefficient(user_tags[u], artist_tags[a])
        res[u] = Counter(top_artists).most_common(10)
    return res

def top_artist_tags():
    print('Computing the top-10 tags for each artist')
    artists = {}
    # construye una lista de etiquetas para cada artista
    for element in UserTagArtist.objects.all():
        artist_id = element.artist.id
        tag_id = element.tag.id
        artists.setdefault(artist_id, [])
        artists[artist_id].append(tag_id)
    # extrae las 10 etiquetas más frecuentes de cada artista
    for a in artists:
        artists[a] = set(tag for tag, count in Counter(artists[a]).most_common(10))
    return artists

def top_users_tags(artists_tags):
    print('Computing the tags of the top-5 most listened artists for each user')
    users = {}
    # construye un diccionario {user_id: {artists_id: listen_time}}
    for element in UserArtist.objects.all():
        user = element.user
        artist_id = element.artist.id
        if artist_id in artists_tags:
            users.setdefault(user, {})
            users[user][artist_id] = element.listen_time
    # extrae los cinco artistas con más tiempo de escucha de cada usuario 
    for u in users:
        users[u] = [artist for artist, time in Counter(users[u]).most_common(5)]
    # para cada usuario asocia un conjunto con las etiquetas más frecuentes de esos cincos artistas
    for u in users:
        users[u] = set(
            tag
            for artist in users[u]
            for tag in artists_tags[artist]
        )
    return users

def dice_coefficient(set1, set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))