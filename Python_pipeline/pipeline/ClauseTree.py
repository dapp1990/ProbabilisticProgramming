

class Root:


    def __init__(self):
        self.child = None


    def addChild(self,node):
        None



class ClauseTree:

    def __init__(self,node):
        self.node = node
        self.child = None


    def addChild(self,node):
        if self.child is None:
            self.child = node
        else:
            self.child.addChild(node)