

class Paginator:
    def __init__(self, ls, limit=20, page=1, json=False) -> None:
        self.ls = ls
        self.limit = limit
        self.page = page
        self.json = json
        
        self.__categorize__()
        
    def __categorize__(self):
        self.data = []
        self.pages = 0
        temp = []
        l = 0
        for i in self.ls:
            if l == self.limit:
                self.data.append(temp)
                self.pages += 1
                temp = []
                l = 0
            if self.json:
                i = i.json()    
            temp.append(i)
            l += 1
        if len(temp) != 0:    
            self.data.append(temp) 
            self.pages += 1   
           
    
    def next(self):
        if len(self.data) <= self.page:
            return None
        p = self.page + 1
        return f'?page={p}'
        
        ...
    
    def previous(self):
        if self.page <= 1:
            return None
        p = self.page - 1
        return f'?page={p}'
        ...
        
    def current(self):
        if len(self.data) >= self.page and self.page > 0:
            return self.data[self.page-1]
        return []
        ...     
        
    def pages_lists(self):
        return [i for i in range(self.page - 2, self.page + 3) if (i > 0 and i <= self.pages) ]           