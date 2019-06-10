import csv
import json
from nltk import ngrams
from levenstien import leven

with open('food-data.json') as data_file:
    foo = json.load(data_file)

with open('att-data.json') as data_file:
    att = json.load(data_file)

with open('top-data.json') as data_file:
    top = json.load(data_file)

remove_list=["and","or","also" ,"of"]
transform_dict={}
def main_check(list_item):
    total_food_dict={}
    transform_dict.clear()
    for sentence in list_item:
        checkt=[]
        pos=sentence.find("with")
        if sentence.find("with")!=-1:
            sentence1=sentence[:pos-1]
            sentence2=sentence[pos+5:]
            food1_dict=gram_check(sentence1)
            for element in food1_dict:
                total_food_dict[element]=food1_dict[element]
            food2_dict=gram_check(sentence2)
            if food2_dict=={}:
                checkt=top_check(sentence2,checkt)
                for element in food1_dict:
                    for indiv in checkt:
                        food1_dict[element].append(indiv)
                for element in food1_dict:
                    total_food_dict[element]=food1_dict[element]
            else:
                for element in food1_dict:
                    total_food_dict[element]=food1_dict[element]
                for element in food2_dict:
                    total_food_dict[element]=food2_dict[element]
        else:
            food1_dict=gram_check(sentence)
            for element in food1_dict:
                total_food_dict[element]=food1_dict[element]


    return total_food_dict, transform_dict

def gram_check(sentence):
    if len(sentence)==0:
        print("No food item found")
    f_find=0
    item_found=""
    foodl=[]
    attl=[]
    topl=[]
    if sentence.find(" ")==-1:
        max_val=1
    else:
        list=sentence.split(" ")
        max_val=len(list)
    min_val=1
    for gram_len in range(max_val, min_val - 1, -1):
        if f_find==1:
            break
        grams = ngrams(sentence.split(" "), gram_len)
        for gram_list in grams:
            onegram = ""
            for gram in gram_list:
                onegram += gram + " "
            match_string = onegram[:-1]
            if match_string in foo:
                f_find=1
                item_found=match_string
                transform_dict[match_string]=match_string
                foodl.append(match_string)
                break
    if f_find==0:
        for gram_len in range(max_val, min_val - 1, -1):
            if f_find == 1:
                break
            grams = ngrams(sentence.split(" "), gram_len)
            for gram_list in grams:
                onegram = ""
                for gram in gram_list:
                    onegram += gram + " "
                match_string = onegram[:-1]
                match_list=[]
                for element in foo:
                    if element[0]== match_string[0]:
                        match_list.append((leven(match_string,element),element))
                       # print(match_list)
                match_list.sort()
                if match_list[0][0]<0.61:
                    f_find = 1
                    item_found=match_string
                    transform_dict[match_list[0][1]]=match_string
                    foodl.append(match_list[0][1])
       
   
    if f_find==1:
        n_sentence=sentence.replace(item_found,"")
        n_sentence = ' '.join(n_sentence.split())
        attl=att_check(n_sentence,attl)
        topl= top_check(n_sentence,topl)
        dict={}
        new_list=attl+topl
        new_list=set(new_list)
        fin_list=[]
        for element in new_list:
            fin_list.append(element)
        dict[foodl[0]]= fin_list
        return dict

    else:
        print("no food item found ")
        return {}

def top_check(sentence,attl):
    att_f = 0

    if len(sentence) == 0:
        return attl
    for element in sentence.split():
        if element in remove_list:
            sentence=sentence.replace(element,"")
            sentence=' '.join(sentence.split())
    if len(sentence.split()) == 1 and sentence not in remove_list:
        attl.append(sentence)
        return attl
    max = len(sentence.split())
    min = 1
    for gram_len in range(max, min - 1, -1):
        if att_f == 1:
            break
        grams = ngrams(sentence.split(" "), gram_len)
        for gram_list in grams:
            onegram = ""
            for gram in gram_list:
                onegram += gram + " "
            match_string = onegram[:-1]
            if match_string in top:
                att_f = 1
                attl.append(match_string)
                new_sentence = sentence.replace(match_string, "")
                new_sentence=' '.join(new_sentence.split())
                top_check(new_sentence,attl)
                break

    return attl

def att_check(sentence,attl):
    att_f = 0
    if len(sentence) == 0:
        return attl
    for element in sentence.split():
        if element in remove_list:
            sentence=sentence.replace(element,"")
            sentence=' '.join(sentence.split())
    if len(sentence.split()) == 1 and sentence not in remove_list:
        attl.append(sentence)
        return attl
    max = len(sentence.split())
    min = 1
    for gram_len in range(max, min - 1, -1):
        if att_f == 1:
            break
        grams = ngrams(sentence.split(" "), gram_len)
        for gram_list in grams:
            onegram = ""
            for gram in gram_list:
                onegram += gram + " "
            match_string = onegram[:-1]
            if match_string in att:
                att_f = 1
                attl.append(match_string)
                new_sentence = sentence.replace(match_string, "")
                new_sentence=' '.join(new_sentence.split())
                att_check(new_sentence,attl)
                break

    return attl



if __name__=='__main__':
    print(main_check(['mushroom patties']))
