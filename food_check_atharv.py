import csv
import json
from nltk import ngrams
from levenstien import leven
from spell_check import correct
temp_food_name = ""
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
          #correct spelling of each sentence
        print("Before sentence")
        print(sentence)
        sentence = correct(sentence)
        print("after")
        print(sentence)
        checkt=[]
        pos=sentence.find("with")
        if sentence.find("with")!=-1:
            #remove word(indexing is letter wise)
            sentence1=sentence[:pos-1]
            sentence2=sentence[pos+5:]
            #print(sentence1)
            #print(sentence2)
            food1_dict=gram_check(sentence1)
            for element in food1_dict:
                total_food_dict[element]=food1_dict[element]
            food2_dict=gram_check(sentence2)
            #Check if food2_dict is empty or not
            if food2_dict=={}:
                checkt=top_check(sentence2,checkt)
                for element in food1_dict:
                    for indiv in checkt:
                        #We are adding the attribute to each food which we got before
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

    #transform_dict will transform our input food to the food which hotel will offer
    return total_food_dict, transform_dict

def gram_check(sentence):
    if len(sentence)==0:
        print("No food item found")
    #flag to check where we have to break the loop
    f_find=0
    item_found=""
    foodl=[]
    attl=[]
    topl=[]
    #max_val will store no. of words in sentence, it will be used in n-grams
    if sentence.find(" ")==-1:
        max_val=1
    else:
        list=sentence.split(" ")
        max_val=len(list)
    min_val=1
    for gram_len in range(max_val, min_val - 1, -1):
        #abhi k liye hata rha hoon, baad mai zaroorat pade to add kar doonga
        #if f_find==1:
           # break
        grams = ngrams(sentence.split(" "), gram_len)
        for gram_list in grams:
            onegram = ""
            for gram in gram_list:     #onegram = gram_list
                onegram += gram + " "
            match_string = onegram[:-1]
            #direct matching
            if match_string in foo:
                f_find=1
                item_found=match_string
                transform_dict[match_string]=match_string
                foodl.append(match_string)
                temp_food_name = match_string
         #abhi k liye hata rha hoon, baad mai zaroorat pade to add kar doonga
                #break
    #no exact matching        
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
                    #apply levenstein on the basis of first character 
                    if element[0] == match_string[0]:
                        #match list is 3D with first index leven
                        match_list.append((leven(match_string,element),element,match_string))
        match_list.sort()
        #0.61 is threshold
        if match_list[0][0]<0.61:
            f_find = 1
            #to find attributes, we are storing match_string(input which got matched), and we store it in item_found
            #later, we will remove item_found from our sentence and rem. part will be checked for attributes
            item_found=match_list[0][2]
            transform_dict[match_list[0][2]]=match_list[0][1]
            #food1 will be return the food which hotel will offer
            foodl.append(match_list[0][1])
            temp_food_name = match_list[0][1]

    if f_find==1:
        #remove the food which we matched earlier
        n_sentence=sentence.replace(item_found,"")
        n_sentence = ' '.join(n_sentence.split())
        attl=att_check(n_sentence,attl)
        topl= top_check(n_sentence,topl)
        dict={}
        new_list=attl+topl
        new_list=set(new_list)
        fin_list=[]
        #fin_list will have all attributes and toppings
        for element in new_list:
            fin_list.append(element)
       # dict[foodl[0]]= fin_list
        dict[temp_food_name] = fin_list
#         idx = idx + 1
        return dict

    else:
        print("no food item found 1")
        return {}

def top_check(sentence,attl):
    att_f = 0
    if len(sentence) == 0:
        return attl
    for element in sentence.split():
        if element in remove_list:
            sentence=sentence.replace(element,"")
            sentence=' '.join(sentence.split())
    if len(sentence.split()) == 1 and sentence not in remove_list and sentence in top :
        attl.append(sentence)
        return attl
    max = len(sentence.split())
    min = 1
    for gram_len in range(max, min - 1, -1):
#         if att_f == 1:
#             break
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
                #break
    return attl

def att_check(sentence,attl):
    att_f = 0
    if len(sentence) == 0:
        return attl
    for element in sentence.split():
        if element in remove_list:
            sentence=sentence.replace(element,"")
            sentence=' '.join(sentence.split())
    #check that if the word is in att(attribute list from data set and it is not in remove_list
    if len(sentence.split()) == 1 and sentence not in remove_list and sentence in att :
        attl.append(sentence)
        return attl
    max = len(sentence.split())
    min = 1
    for gram_len in range(max, min - 1, -1):
#         if att_f == 1:
#             break
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
              #  break
    return attl


if __name__=='__main__':
    print(main_check(['ewjfberugbue']))
