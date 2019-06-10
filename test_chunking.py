import nltk
from nltk import pos_tag
from nltk import chunk
from nltk.tokenize import word_tokenize
import re
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk import RegexpParser
from nltk import Tree
import json
import pandas as pd
import inflect
from word2number import w2n
from food_check_atharv import main_check
from food_count import count
#It will check and change plural and singular
inflect=inflect.engine()

include=["non-veg","non-vegeterian","vegetarian","veg"]
blacklist1 = ["&", "a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any", "are",
                 "aren", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
                 "by", "can", "couldn","did", "didn", "do", "does", "doesn", "doing", "don", "down", "during",
                 "each", "few", "for", "from", "further", "had", "hadn", "has", "hasn", "have", "haven", "having", "he",
                 "her", "here", "hers", "herself", "dont" , "him", "himself", "his", "how", "if","into", "is", "isn",
                 "it", "its", "itself", "just","me", "mightn", "more","get","most", "mustn", "my","okay",
                 "myself", "needn", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
                 "our", "ours", "ourselves", "out", "over", "own", "re", "same", "shan", "she", "should", "bring",
                 "shouldn", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
                 "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
                 "ve", "very","us","was", "wasn", "we","eat","were", "weren", "what", "when", "where", "which", "while", "who",
                 "whom", "why", "will", "with", "won", "wouldn", "you", "your", "yours", "yourself", "yourselves","What","Who","Which",
                  "Where","can","help","me","Can","do","discover","find","top","How","how","pleasant","good","bad","Preperation","preperation"
                  "nice","teaching","WHo's","who's","great","best","better","mentor","skills","company","scholarships","guide","WHo're","who're",
              "Which","which","some","name","Name","teacher","genuine","actual","Genuine","location","city","state","mentor","able","knowledge"
              "should","increase","improve","skill","Does","does","do","institution","organisation","helper","print","tuition","s"
              ,"college","via","order","food","item","items","options","menu","remove","add","menu","","travel","go","fly","something","anything","could","show","give","want","please","along"]

cuisine=["nepali","nepalese","japanese","thai","chinese","malaysian","mughal","indian","arab","american","europian","english"]
check1_list=["check-in","check-out","check in","check out","move in","move out","available","present",""]
atmost_list=["'s","'ll","'rd","'nd"]
also_check=["chicken","mushroom","masala"]

excp=["rice","chowpsy"]
# sentence="What is the best thing in this hotel??"
# sentence=sentence.replace("?","")
with open('food-data.json') as data_file:
    foo = json.load(data_file)

with open('att-data.json') as data_file:
    att = json.load(data_file)

with open('top-data.json') as data_file:
    top = json.load(data_file)



def check_tell(new_list,idx,element,check_dict):
    list1=sorted(new_list,key=lambda x:x[0])
    if list1==[]:
        return 1
    if idx<list1[0][0]:
        return 1
    check=-1
    echeck=0
    for el in excp:
        if el in check_dict[element]:
            echeck=1
            break
    if inflect.singular_noun(check_dict[element]) is False and echeck==0:
        return 1
    for id,ele in enumerate(list1):
        if id<len(list1)-1:
            if idx>ele[0] and idx<list1[id+1][0]:
                check=ele[1]
    if idx>list1[len(list1)-1][0]:
        check=list1[len(list1)-1][1]
    if check==-1:
        return 1
    else:
        return check


def changew_n(sentence):
    bad_list=[]
    good_list=[]
    for idx,element in enumerate(sentence.split(" ")):
        try:
            # print(element)
            number=w2n.word_to_num(element)
            good_list.append((element,number))
        except Exception as ex:
            continue
    print(good_list)
    for indiv in good_list:
        sentence=sentence.replace(indiv[0],str(indiv[1]))
    return sentence

def get_continuous_chunks(text, label):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    prev = None
    continuous_chunk = []
    current_chunk = []

    for subtree in chunked:
        if type(subtree) == Tree and subtree.label() == label:
            current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    return continuous_chunk

def return_entities(sentence):
    # sentence="so I would like to travel from Gorakhpur to Mumbai on monday.show me the flights."
    sentence=sentence.lower()
    sentence=sentence.replace("."," . ")
    sentence=sentence.replace(","," , ")
    if(sentence.find("'s") is not -1):
        sentence=sentence.replace("'s"," ")
    if (sentence.find("'ll") is not -1):
        sentence = sentence.replace("'ll", " will")
    if (sentence.find(" 'nd") is not -1):
        sentence = sentence.replace("'nd", " ")
    if (sentence.find(" 'rd") is not -1):
        sentence = sentence.replace("'rd", " ")
    if (sentence.find("!") is not -1):
        sentence = sentence.replace("!", " ")
    if (sentence.find("'t") is not -1):
        sentence = sentence.replace("'t", "t")
    sentence = ' '.join(sentence.split())
    sentence_count = sentence
    number_list = count(sentence)
    check_len=sentence.split(" ")
    check_l=len(check_len)
    sentence=sentence.replace("?","")
    sentence=changew_n(sentence)
    original_sentence = sentence
    token_dict={}
    tok=word_tokenize(sentence)
    l_sentence=sentence
    pos=pos_tag(tok)      ## tagging initially to ignore the list of adjectives
    print(pos)
    chunking=nltk.ne_chunk(pos, binary=True)
    # chunking.draw()
    adjectives=[]
    check_pos=["NNP","NN","NNS","RB","JJ","IN"]
    non_list=[]
    sing_list=[]
    check_list=["along"]
    comma_check=[]
    idx=0
    for index,entity in enumerate(pos):
            idx+=1
            if idx<=len(pos)-1:
                if entity[1]=="JJ" and '-' not in entity[0] and entity[0].lower() not in cuisine and pos[index+1][1] not in check_pos:
                    adjectives.append(entity[0])
                elif entity[1]=="CD":
                    non_list.append(entity[0])
                elif entity[1]=="DT":
                    check_list.append(entity[0])
                    sing_list.append(" "+entity[0]+" ")
                if entity[0]==',' and pos[index+1][0] in top and pos[index-1][0] in top:
                    check_list.append(entity[0])
                    comma_check.append(index)
                elif entity[0]=='and' and pos[index+1][0] in top and pos[index-1][0] in top:
                    comma_check.append(index)
                    check_list.append(entity[0])
    #tak_list is dictionary that will store index of a, an, the in sentence
    tak_list={}
    for element in sing_list:
        if element==' a ' or element==' an ':
            for match in re.finditer(element, sentence):
                tak_list[(match.start(),element)]=1


    new_sentence=""
    for idx,wor in enumerate(sentence.split(' ')):
#         try:
#             tmp = wn.synsets(wor)[0].pos()  ## dont want to capitalise verbs
#         except Exception as ex:
#             print(ex)
#             tmp = "r"
        #check_list will store commma, and, and delemiters(DT)
        if wor.lower() in check_list:
            if wor.lower()=="," or wor.lower()=="and":
                if idx in comma_check:
                    continue
                else:
                    new_sentence = new_sentence + wor.lower() + " "
            else:
                continue
        elif  wor in adjectives or wor in non_list:  ## if word is verb or adjective it is not being capitalised
            wor = wor.lower()
            new_sentence = new_sentence + wor + " "
        elif wor in blacklist1:  ## also dont want to capitalise stopwords
            if wor[:1].isupper():
                new_sentence = new_sentence + wor.lower() + " "
            else:
                new_sentence = new_sentence + wor + " "
        elif wor.lower() in blacklist1:
            new_sentence = new_sentence + wor.lower() + " "
        else:
            #Capitalise all first alphabet of words that are not (check_list(remove it!!), adjectives, blaclist)
            new_sentence = new_sentence + wor[:1].upper() + wor[1:] + " "  ## else capitalise all other words
    new_sentence = ' '.join(new_sentence.split())
    if new_sentence.endswith('.'):
        new_sentence=new_sentence[:-1]
    # new_sentence.replace("."," . ")
#    check= '.' in new_sentence this line was of no use
    
    tok=word_tokenize(new_sentence)
    tokens_pos=pos_tag(tok)
    #ne_chunk will combine proper noun
    chunking=nltk.ne_chunk(tokens_pos, binary=True)
    
    #check if there is any sub tree
    new_sentence_list =  [" ".join(w for w, t in elt) for elt in chunking if isinstance(elt, nltk.Tree)]
    print(new_sentence_list)
   # chunking.draw()
    list=[]
    
    #in dict_word value of each word is 0
    dict_word={}
    #print(new_sentence)
    for word in new_sentence.split(" "):
        dict_word[word]=0
    #print(dict_word)
    word_to_token={} #No idea why this is defined
    for word in new_sentence.split(" "):
        word_to_token[word]=word

    # for member in new_sentence_list:
    #     for single_word in member.split(" "):
    #         dict_word[single_word]=1
    stop_list=["with","of"]
    quant_list=[]
    for i, unique in enumerate(tokens_pos):
        sentence=""
        if i< len(tokens_pos)-1:
            #we will take all consecutives nouns and append them to list
            if (unique[1] == "NNP" or unique[1]== "NN") and (tokens_pos[i+1][1]=="NNP" or tokens_pos[i+1][1]=="NNS" or tokens_pos[i+1][1]=="NN" or tokens_pos[i+1][1]=="NNPS"):
                j=i
                loopno=1
                enter=0
             #   print(unique[0])
                while j<len(tokens_pos)-1 and (tokens_pos[j][1]== "NNP" or tokens_pos[j][1]=="NN") and (tokens_pos[j+ 1][1] == "NNP" or tokens_pos[j + 1][1] == "NNS" or tokens_pos[j+1][1]=="NN" or tokens_pos[i+1][1]=="NNPS"):
                    #print("inside")
                    enter=enter+1
                    #dict_word will check which word is taken
                    #sentence will add nouns
                    if (dict_word[tokens_pos[j][0]]==0 and enter==1):
                        sentence+=tokens_pos[j][0]+ " "
                        dict_word[tokens_pos[j][0]]=1
                        sentence+=tokens_pos[j+1][0]+ " "
                        dict_word[tokens_pos[j+1][0]] = 1
                    elif enter!=1 and dict_word[tokens_pos[j + 1][0]]==0:
                        sentence += tokens_pos[j+1][0] + " "
                        dict_word[tokens_pos[j+1][0]] = 1
                    j=j+1
                #remove last space from sentence
                sentence=sentence[:-1]
                for wor in sentence.split():
                    word_to_token[wor]=sentence
                dict_word[tokens_pos[j][0]]=1
                list.append(sentence)
            #here we will check if a Noun is followed by words like "with", "of" ,and then again noun come
            elif i<len(tokens_pos)-2 and (unique[1]== "NNP" or unique[1]=="NN" or unique[1]=="NNS") and tokens_pos[i+1][0] in stop_list and (tokens_pos[i+2][1]=="NNP" or tokens_pos[i+2][1]=="NN" or tokens_pos[i+2][1]=="NNS"):
                j=i
                dict_word[tokens_pos[j][0]]=1
                dict_word[tokens_pos[j+1][0]]=1
                dict_word[tokens_pos[j+2][0]]=1
                sentence+= word_to_token[tokens_pos[j][0]]+" "
                if word_to_token[tokens_pos[j][0]] in list:
                    list.remove(word_to_token[tokens_pos[j][0]])
                sentence += tokens_pos[j+1][0]+ " "
                sentence += tokens_pos[j+2][0]+ " "
                j=j+2
                while j < len(tokens_pos) - 1 and (tokens_pos[j][1] == "NNP" or tokens_pos[j][1]=="NN") and (tokens_pos[j + 1][1] == "NNP" or tokens_pos[j + 1][1] == "NNS"):
                    sentence+= tokens_pos[j+1][0]+ " "
                    dict_word[tokens_pos[j + 1][0]] = 1
                    j=j+1
                sentence=sentence[:-1]
                for wor in sentence.split():
                    word_to_token[wor]=sentence
                list.append(sentence)
            #last noun
            elif unique[1]=="NNP" or unique[1]=="NN" or unique[1]=="NNS" :
                if(dict_word[unique[0]])==0:
                    list.append(unique[0])
            elif unique[1]=="JJ" and '-' in unique[0]:
                list.append(unique[0])
            elif unique[0].lower() in cuisine:
                list.append(unique[0])
    #last noun of sentence
    if tokens_pos[len(tokens_pos)-1][1]=="NNP" or tokens_pos[len(tokens_pos)-1][1]=="NN" or tokens_pos[len(tokens_pos)-1][1]=="NNS":
        if dict_word[tokens_pos[len(tokens_pos)-1][0]]==0:
            list.append(tokens_pos[len(tokens_pos)-1][0])
    #check quantity
    for i, unique in enumerate(tokens_pos):
        if unique[1]=="CD":
            quant_list.append(unique[0])
    new1_list=[]
    original_sentence1 = original_sentence
    
    for key in quant_list:
        idx=original_sentence1.find(key)
        new1_list.append((idx,key))
        #replace the number with some symbol
        original_sentence1 = original_sentence1[:idx] + "$" + original_sentence1[idx+1:] 

    # print(list)
    for element in new_sentence.split(" "):
        if element.lower() in also_check and dict_word[element]==0:
            list.append(element)
    remove_list=[]
    #new_sentence list is subtree
    #mereko pta nhi neeche kya ho rha hai
    for element2 in new_sentence_list:
        for unique2 in list:
            if element2 in unique2 :
                #we want to remove proper substring
                if not element2==unique2:
                    remove_list.append(element2)
    #Remove all elements in remove_list if they are in new_sentence_list
    for element in remove_list:
        if element in new_sentence_list:
            new_sentence_list.remove(element)

    final_list=list+new_sentence_list
    #remove common parts
    set1=set(final_list)
    new_list=[]
    for element in set1:
        new_list.append(element)
    if " " in new_list:
        new_list.remove(" ")
    if '' in new_list:
        new_list.remove('')
    top_list=[]
    #if elements of new_list are not in blacklist, then append them in top_list
    for element in new_list:
        if element.lower() not in blacklist1 and element not in blacklist1:
            top_list.append(element.lower())
    check_dict={}
    check_list=[]
    for element in top_list:
      #order is a noun, so remove it
        if "order " in element:
            element1=element.replace("order ","")
            top_list.remove(element)
            top_list.append(element1)
    sep_list=[]
    food_dict, transform_dict=main_check(top_list)
    print(food_dict)
    nf_list=[]
    for key in food_dict:
        idx=original_sentence.find(transform_dict[key])
        nf_list.append((idx,key))
    new1_list.sort(reverse=True)
    nf_list.sort()
    check_list=[]
    found_dict={}

    pre_dict={}
    for element in tak_list:
        for food in nf_list:
            if element[0]<food[0]:
                pre_dict[food[1]]=element
                break




    c_dict={}
    for i,element in enumerate(nf_list):
        flag=0
        for indiv in new1_list:
            if indiv[0]<element[0] and indiv not in check_list:
                c_dict[element]=indiv
                check_list.append(indiv)
                flag=1
                break
        if flag==0:
            c_dict[element]=(-1,-1)
    final_dict={}
    element_list=[]
    for element in nf_list:
        check=0
        for word in element[1].split():
            if word.endswith('s'):
                check=1
                break
        if check==0:
            element_list.append(element)

    for i,element in enumerate(nf_list):
        if i==0:
            if c_dict[element]==(-1,-1):
                if inflect.singular_noun(element[1].split()[0]) is False or element in element_list or element[1] in pre_dict:
                    final_dict[element[1]]=1
                else:
                    final_dict[element[1]]=2
            else:
                check_list.append(c_dict[element])
                final_dict[element[1]] = c_dict[element][1]

        else:
            if c_dict[element]==(-1,-1):
                if inflect.singular_noun(element[1].split()[0]) is False or element in element_list or element[1] in pre_dict:
                    final_dict[element[1]]=1
                else:
                    final_dict[element[1]]=2
            # elif c_dict[element] in check_list:
            #     if inflect.singular_noun(element[1]) is False or element  in element_list:
            #         final_dict[element[1]]=1
            #     else:
            #         final_dict[element[1]]=2
            else:
                final_dict[element[1]]=c_dict[element][1]
    new_food_dict={}
    for element in food_dict:
        new_food_dict[element]={}
        new_food_dict[element]["attribute"]=[]
        new_food_dict[element]["quantity"]=0
        new_food_dict[element]["topping"]=[]

    for element in food_dict:
        for item in food_dict[element]:
            if item in top:
                new_food_dict[element]["topping"].append(item)
            elif item in att:
                new_food_dict[element]["attribute"].append(item)
            else:
                new_food_dict[element]["attribute"].append(item)
    for element in new_food_dict:
        if element in final_dict:
            new_food_dict[element]["quantity"]=final_dict[element]

    print(new_food_dict)

    print(final_dict)
   # print(number_list)
    return top_list, new_food_dict , transform_dict, number_list


if __name__=='__main__':
    print(return_entities("I want 3 plate chicken lollypop with butter chicken"))
