import pandas as pd
import random
import csv
import re

positive_list=["add","order","bring","get" ,"increase"]
negative_list=["remove","dont","not","eliminate","withdraw" ,"hate"]
def return_sequence(dict,sentence, transform_dict):
    sentence=sentence.lower()
    element_list=[]
    food_list=[]
    check_dict={}
    test_dict={}
    for idx,word in enumerate(sentence.split()):
        if word in positive_list:
            for match in re.finditer(word, sentence):
                element_list.append((match.start(), word))
                check_dict[word]=1
                test_dict[(match.start() , word)]=0
        elif word in negative_list:
            for match in re.finditer(word, sentence):
                element_list.append((match.start(), word))
                check_dict[word]= -1
                test_dict[(match.start(), word)]=0
    for food_item in dict:
        idx=sentence.find(transform_dict[food_item])
        food_list.append((idx,food_item))

    element_list.sort()
    food_list.sort()
    final_dict={}
    for item in food_list:
        final_dict[item[1]]=[]
        for element in element_list:
            if element[0]>=item[0]:
                break
            elif test_dict[element]==0:
                final_dict[item[1]].append(element[1])
                test_dict[element]=1

    end_dict={}
    for item in final_dict:
        init_sum=0
        for element in final_dict[item]:
            init_sum+=check_dict[element]
        if init_sum==0 and len(final_dict[item])>0:
            end_dict[item]= "remove"
        elif init_sum<=-2:
            end_dict[item]= "add"
        elif init_sum>0:
            end_dict[item]= "add"
        elif init_sum==-1:
            end_dict[item]= "remove"
        else:
            end_dict[item]= "add"

    remove_item=[]
    order_item={}

    for item in final_dict:
        if end_dict[item]=="remove":
            remove_item.append(item)
        elif end_dict[item]== "add":
            order_item[item]=dict[item]


    return remove_item,order_item



if __name__=='__main__':
    print(return_sequence({"paneer":1 , "mushroom":1 ,"tea":1}, "can you please remove the paneer item and I do not want to add the mushroom one and also I do not want to remove the tea."))


