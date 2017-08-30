###pseudo
#'rating.csv': 'userId', 'movieId', 'rating', 'timestamp'

#step1: read the ratings.csv file into pivot tables
#step2: normalize the ratings by subtracting the mean and giving all the unrated movies a rating of 0.
#step3: calculate the similarity using cosine similarity.
#step4: for user-to-user CF, setN is a set of users who are most similar to user x and has also rated movie i.
#step5: for item-to-item CF, setN is a set of movies that are similar to movie i and has also been rated by user x.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import operator
import math

def readFile(path):
    '''take a csv file and read it into a list of dictionaries.'''
    output = []
    with open(path, 'r') as content:
        rows = csv.DictReader(content)
        for row in rows:
            output.append(row)
    return output

def pivotTable(list_of_dict, firstKey, secondKey):
    '''convert a list of dict to a pivot table(dict of dict), with firstKey as the row name and secondKey as the column name.'''
    output_dict = {}
    for line in list_of_dict:
        if line[firstKey] not in output_dict:
            inner_dict = {}
            inner_dict[line[secondKey]] = float(line['rating'])
            output_dict[line[firstKey]] = inner_dict
        else:
            output_dict[line[firstKey]][line[secondKey]] = float(line['rating'])
    return output_dict

def getKeys(pivot_table):
    return set(pivot_table.keys())

def normalize(string_rating_dict):
    '''string_rating_dict: a dictionary mapping from movieIds/userIds to rating scores for one user or one movie (one row of pivot_table);
    return: normalized rating scores.'''
    output_dict = {}
    values_list = list(string_rating_dict.values())
    ratings_mean = np.mean(values_list)
    for string in string_rating_dict:
        output_dict[string] = (string_rating_dict[string] - ratings_mean)
    return output_dict

def similarity(objectA, objectB, pivot_table):
    '''using cosine similarity to calculate the similarity bewteen userA and userB or movieA and movieB.
    objectA, objectB: a string;
    return: a floating point number: the similarity between objectA and objectB.'''
    objectA_dict = normalize(pivot_table[objectA])
    objectB_dict = normalize(pivot_table[objectB])
    intersection = set(objectA_dict.keys()) & set(objectB_dict.keys())
    numerator = 0
    for item in intersection:
        numerator += objectA_dict[item] * objectB_dict[item]
    A_squared_sum = 0
    B_squared_sum = 0
    for item in objectA_dict.keys():
        A_squared_sum += (objectA_dict[item]) ** 2
    for item in objectB_dict.keys():
        B_squared_sum += (objectB_dict[item]) ** 2
    denominator = (A_squared_sum ** 0.5) * (B_squared_sum ** 0.5)
    similarity = numerator / denominator
    return similarity

def similarPool(pivot_table, item):
    '''calculate the top n items(users/movies) that has the highest similarity with a given item.
    return: a list of n tuples (item, similarity).'''
    sim_list = []
    for key in pivot_table:
        if len(pivot_table[key]) > 100:
            item_sim = (key, similarity(item, key, pivot_table))
            if not math.isnan(item_sim[1]):
                sim_list.append(item_sim)
    sim_list_sorted = sorted(sim_list, key=operator.itemgetter(1), reverse=True)
    return sim_list_sorted

def topNMostSimilar(pivot_table, row, col, n):
    '''row being the outer key of the pivot table, col being the inner key.
    for user_to_user: setN is a set of users who are most similar to user x and has also rated movie i.
    for movie_to_movie: setN is a set of movies that are similar to movie i and has also been rated by user x.
    row has not rated/been rated by col.'''
    setN = []
    most_similar = similarPool(pivot_table, row)
    for pair in most_similar:
        if col in pivot_table[pair[0]] and not math.isnan(pair[1]):
            setN.append(pair)
    sorted_setN = sorted(setN, key=operator.itemgetter(1), reverse=True)
    return sorted_setN[:n]


def userToUser(user_pivot_table, movie_pivot_table, user, n):
    '''user_pivot_table'''
    recommend_list = []
    all_movies = getKeys(movie_pivot_table)
    unrated_movies = all_movies - set(user_pivot_table[user].keys())
    for movie in unrated_movies:
        setN = topNMostSimilar(user_pivot_table, user, movie, n)
        numer = 0
        denom = 0
        for pair in setN:
            person = pair[0]
            sim = pair[1]
            if not math.isnan(sim):
                numer += user_pivot_table[person][movie] * sim
                denom += sim
        try:
            estimated_rating = numer / denom
        except ZeroDivisionError:
            pass
        if not math.isnan(estimated_rating):
            recommend_list.append((movie, estimated_rating))
    sorted_list = sorted(recommend_list, key=operator.itemgetter(1), reverse=True)
    return sorted_list

def itemToItem(movie_pivot_table, user_pivot_table, user, n):
    '''movie_pivot_table'''
    recommend_list = []
    all_movies = getKeys(movie_pivot_table)
    unrated_movies = all_movies - set(user_pivot_table[user].keys())
    for movie in unrated_movies:
        #print(movie)
        setN = topNMostSimilar(movie_pivot_table, movie, user, n)
        numer = 0
        denom = 0
        for pair in setN:
            film = pair[0]
            sim = float(pair[1])
            if not math.isnan(sim):
                numer += float(user_pivot_table[user][film]) * sim
                denom += sim
        try:
            estimated_rating = float(numer) / denom
        except ZeroDivisionError:
            estimated_rating = 0.0
        if not math.isnan(estimated_rating):
            recommend_list.append((movie, estimated_rating))
        #import ipdb; ipdb.set_trace()
        sorted_list = sorted(recommend_list, key=operator.itemgetter(1), reverse=True)
    return sorted_list

def main():
    list_of_dict = readFile('ratings_with_fake_user_april.csv')
    user_pivot_table = pivotTable(list_of_dict, 'userId', 'movieId')
    movie_pivot_table = pivotTable(list_of_dict, 'movieId', 'userId')
    # star_wars = similarPool(movie_pivot_table, '260')
    # print(star_wars[:10])
    recomend_full = userToUser(user_pivot_table, movie_pivot_table, 'April', 10)
    print(recomend_full[:10])
    # rec_item_to_item = itemToItem(movie_pivot_table, user_pivot_table, 'April', 10)
    # print(rec_item_to_item[:10])

if __name__ == "__main__":
    main()

