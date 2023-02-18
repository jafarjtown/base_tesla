

class Search:
  
    
    def __init__(self, model = None, search_for = None, lookups = None, exact=False):
        self.model = model
        self.search_for = search_for.strip()
        self.lookp_ups = lookups
        self.exact = exact
        if self.model:
            self.objs = self.model
    
    def result(self):
        if len(self.objs) == 0:
            return []
        temp = set()
        for model in self.objs:
            # print(model)
            for f in self.lookp_ups:
                
                if not hasattr(model, f):
                    continue
                
                if not self.exact:
                    if self.search_for.lower() in getattr(model, f).lower():
                        temp.add(model)
                        break
                else:
                    if getattr(model, f).lower() == self.search_for.lower():
                        temp.add(model)
                        break
                    
        return temp            