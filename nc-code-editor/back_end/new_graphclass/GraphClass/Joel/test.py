import networkx as nx
import matplotlib.pyplot as plt
from Functions import *
from parse import parseData
   
#x = CreateGraph("connections3.csv")
print("---------------------------------------------------------------------------")
#y = CreateGraph("connections.csv")

#a = GetNodes(x)
#b = GetNodes(y)


#z = MergeGraph(x,y,[(a[0],b[0])])

#z = MergeGraph(x,y,[(a[0],b[0])])
dic = {}
dic["age"] = ["21","22"]
#filter = FilterGraph(z,dic)
#c = GetNodes(z)
#z.print_nodes()
#z.print_edges()
#z.print_relationships()


ssgraph1 = SSCreateGraph("james purtilo")
ssgraph2 = SSCreateGraph("Tim")


merge = MergeGraph(ssgraph1,ssgraph2)


merge.print_nodes()