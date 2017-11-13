#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 02:38:00 2017

@author: abhinav
"""

from collections import defaultdict
from v3_parser import removeStopWords,stem,tokenise
import timeit
import math

offset_dic=defaultdict(int)
title_dict=defaultdict(int)
wlist=[]
tlist=[]
no_of_docs

def get_noofdocs():
    global no_of_docs
    with open("tmp/doc_count","r") as fp:
        for line in fp:
            no_of_docs=int(line.strip())

def load_title():
    global tlist
    global title_dict
   # print("innn")
    with open("tmp/title_offset","r") as fp1:
        for line in fp1:
            #print(line)
            line=line.strip().split()
            title_dict[int(line[0].strip())]=int(line[1].strip())
    #print(len(title_dict))
    fp1.close()
    tlist=sorted(list(title_dict.keys()))
    
def bsearch_titleno(docid):
    global title_dict
    global tlist
    pos=0
    low=0
    high=len(tlist)-1
    #print("in titleno, high= "+str(high))
    while low<=high:
        mid=int((low+high)/2)
        if int(tlist[mid])==docid:
            return title_dict[docid]
        elif tlist[mid]<docid:
            pos=mid
            low=mid+1
        else:
            high=mid-1
           
    return title_dict[tlist[pos]]
    
def get_title(fno,docid):
    global title_dict
    with open("tmp/title"+str(fno),"r") as fp:
        for line in fp:
            line=line.split("-")
            if int(line[0]) == docid :
                return line[1].strip("\n")
    
def load_offsetfile():
    global offset_dic
    global wlist
    with open("tmp/offset","r") as fp:
        for line in fp:
            line=line.strip().split(":")
            offset_dic[line[0]]=line[1]
    fp.close()
    wlist=sorted(list(offset_dic.keys()))
    #print(wlist)
    
def bsearch_fileno(word):
    global offset_dic
    global wlist
    pos=0
    low=0
    high=len(wlist)-1
    #print("high="+str(high))
    while low<=high :
        mid=int((low+high)/2)
        if wlist[mid]==word:
            return offset_dic[word]
        elif wlist[mid]<word:
            low=mid+1
        else:
            pos=mid
            high=mid-1
            
    #print(wlist[pos])
    return offset_dic[wlist[pos]]
    
def getList(word,fno):
    with open("tmp/file"+str(fno),"r") as fp:
        for line in fp:
            line=line.strip().split("/")
            if line[0] == word :
                return line[1]
    return []

def rank_simple(posting_dict):
    global no_of_docs
    #print("in file"+str(no_of_docs))
    rank_list=defaultdict(float)
    l=posting_dict.keys()
    
    for word in l:
        postlist=posting_dict[word]
        if len(postlist) != 0:
            postlist=postlist.split(";")
            df=len(postlist)
            idf=math.log10(no_of_docs/df) 
            for doc in postlist:
                doc=doc.split("-")
                doc_id=int(doc[0])
                line=doc[1].split(":")
                freq=int(line[0][1:])
                tf=math.log10(1+freq)
                rank_list[doc_id]+=tf*idf
                     
    return rank_list

def rank_field(posting_dict,query_dict):
    global no_of_docs
    #print("in file"+str(no_of_docs))
    rank_list=defaultdict(float)
    l=posting_dict.keys()
    
    wt={'t':100,'i':80,'c':50,'e':20}
    
    for word in l:
        postlist=posting_dict[word]
        if len(postlist) !=0 :
            postlist=postlist.split(";")
            df=len(postlist)
            idf=math.log10(no_of_docs/df)
            for doc in postlist:
                doc=doc.split("-")
                doc_id=int(doc[0])
                line=doc[1].split(":")
                fields_to_match=query_dict[word]
                freq=0
                for j in line:
                    if j[0]=='b':
                        freq+=int(j[1:])
                for i in fields_to_match:
                    for j in line:
                        if i==j[0] and i!="b":
                            freq+=(int(j[1:])*wt[j[0]])
                tf=math.log10(1+freq)
                rank_list[doc_id]+=tf*idf
                
    return rank_list

def simple_query(query):
    global title_dict
    qwords=tokenise(query)
    qwords=removeStopWords(qwords)
    qwords=stem(qwords)
        
    posting_dict=defaultdict(list)
    for w in qwords:
        #print(w)
        fno=bsearch_fileno(w)
        #print("index fno= "+str(fno))
        posting=getList(w,fno)
        posting_dict[w]=posting
    #print(posting_dict)
    ranked_list=rank_simple(posting_dict)
    #print(ranked_list)
    if len(ranked_list) == 0:
        print("No match found")
    else:
        ranked_list_sort=sorted(ranked_list, key=ranked_list.get,reverse=True)
        #return rank_list_sort
        #print(len(ranked_list_sort))
        for i in range(0,10):
            if i>=len(ranked_list_sort):
                break
            #print(title_dict[ranked_list_sort[i]])
            #print(ranked_list_sort[i])
            fno=bsearch_titleno(ranked_list_sort[i])
            #print("title fno= "+str(fno))
            #print(ranked_list[ranked_list_sort[i]])
            print(get_title(fno,ranked_list_sort[i])+" :- "+str(ranked_list[ranked_list_sort[i]]))

def makedict(qdict,line,val):
    line=tokenise(line)
    line=removeStopWords(line)
    line=stem(line)
    for i in line:
        qdict[i].append(val)
    return qdict
  
def get_field_query_dict(inp):
    val=0
    t,r,b,inf,c,e="","","","","",""
    tmpp=""
    val=len(inp)-1
    i,tf,bf,cf,ef,rf,inff=0,0,0,0,0,0,0
    while i < val:
        x=inp[i]
        y=inp[i+1]
        if "i" == x and ":" == y:
            tf,bf,cf,ef,rf,inff=0,0,0,0,0,1
            i=i+1
        elif "t" == x and ":" == y:
            tf,bf,cf,ef,rf,inff=1,0,0,0,0,0
            i=i+1
        elif "b" == x and ":" == y:
            tf,bf,cf,ef,rf,inff=0,1,0,0,0,0
            i=i+1
        elif "c" == x and ":" == y:
            tf,bf,cf,ef,rf,inff=0,0,1,0,0,0
            i=i+1
        elif "e" == x and ":" == y:
            tf,bf,cf,ef,rf,inff=0,0,0,1,0,0
            i=i+1
        elif "r" == x and ":" == y:
            tf,bf,cf,ef,rf,inff=0,0,0,0,1,0
            i=i+1
        elif tf==1:
            t=t+x
        elif bf==1:
            b=b+x
        elif cf==1:
            c=c+x
        elif ef==1:
            e=e+x
        elif rf==1:
            r=r+x
        elif inff==1:
            inf=inf+x
        i=i+1
    v=1
    l=len(inp)-1
    if tf==v:
        t=t+inp[l]
    elif bf==v:
        b=b+inp[l]
    elif cf==v:
        c=c+inp[l]
    elif ef==v:
        e=e+inp[l]
    elif rf==v:
        r=r+inp[l]
    elif inff==1:
        inf=inf+inp[l]
    qdict=defaultdict(list)
    qdict=makedict(qdict,t,"t")
    qdict=makedict(qdict,b,"b")
    qdict=makedict(qdict,c,"c")
    qdict=makedict(qdict,e,"e")
    qdict=makedict(qdict,inf,"i")
    #print(qdict)
    return qdict
      
def field_query(query):
    global title_dict
    query_dict=get_field_query_dict(query)
    '''query_dict=defaultdict(list)
    query=query.strip().split()
    for l in query:
        l=l.split(":")
        #print(l[1])
        w_n=tokenise(l[1])
        w_n=removeStopWords(w_n)
        w_n=stem(w_n)
        for i in w_n:
            query_dict[i].append(l[0])'''
    
    qwords=list(query_dict.keys())
        
    posting_dict=defaultdict(list)
    for w in qwords:
        fno=bsearch_fileno(w)
        #print("index fno= "+str(fno))
        posting=getList(w,fno)
        posting_dict[w]=posting
    ranked_list=rank_field(posting_dict,query_dict)
    
    if len(ranked_list) == 0:
        print("No match found")
    else:
        ranked_list_sort=sorted(ranked_list, key=ranked_list.get,reverse=True)
        #return rank_list_sort
        #print(len(ranked_list_sort))
        for i in range(0,10):
            if i>=len(ranked_list_sort):
                break
            #print(title_dict[ranked_list_sort[i]])
            fno=bsearch_titleno(ranked_list_sort[i])
            #print("title fno= "+str(fno))
            print(get_title(fno,ranked_list_sort[i])+" :- "+str(ranked_list[ranked_list_sort[i]]))
        
def main():
    load_offsetfile()
    load_title()
    while True:
        print("\n\nEnter Query")
        query=input()
        query=query.lower()
        start = timeit.default_timer()
        if ("i:" in query or "b:" in query or "c:" in query or "t:" in query or "e:" in query):
            #print("in")
            field_query(query)
        else:
            simple_query(query)
        stop = timeit.default_timer()
        print ("\ntime :- "+str(stop - start) )
    
main()