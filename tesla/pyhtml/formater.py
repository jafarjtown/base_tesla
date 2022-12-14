
def dot(n):
    return " "*n
def lastIndex(txt, vl):
    return txt.index(vl)
def format(text):
   # text = (text.replace(" ",""))
    text = text.strip()
    lst = []
    indent = 0
    while len(text) > 0:
        index = lastIndex(text, ">")
        if text.startswith("<"):
            lst.append(text[:index+1])
            text = text[index+1:]  
        else:
          
             ind = lastIndex(text, "<")
             lst.append(text[:ind].strip())
             text = text[ind:]
    prev = ""
    #while lst.index(""):
       # (lst.remove(""))
    #print(dir(lst))
    
    for i in lst:
         if i == "":
             continue
         if i.startswith("</") and prev.startswith("</"):
             indent -= 1   
         elif prev.startswith("<") == False and i.startswith("</") == False:
             pass
         elif prev.startswith("</") and i.startswith("<"):
             pass
         elif prev.startswith("</") and i.startswith("<") == False:
             pass
         elif prev.startswith(("<meta","<img","<input","<link")) and i.startswith("</head"):
             indent -= 1
         elif prev.startswith(("<meta","<img","<input","<link")):
             pass

         elif prev.startswith("<") == False and i.startswith("</"):
             indent -= 1
   
         else:
             indent += 1
         text += f"{dot(indent)}{i}\n"
         prev = i
         
    
    return text
    