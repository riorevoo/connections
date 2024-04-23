from GraphClass import Graph
from NodeClass import Node
from EdgeClass import Edge
from AuthorNode import AuthorNode
from parse import parseData
import networkx as nx
from SemanticScholarFuncs import *
from pyvis.network import Network

# from SemanticScholarFuncs import generate_author_dict

# if a csv was inputted, it will create nodes based off the csv
# else (in the case of no input) it will just create an empty graph -> user can use AddNodes to add nodes to it
def CreateGraph(csv: str = None):
    graph = Graph()

    # case when we need to create nodes from a csv file
    if csv:
        (names1, names2, attributes) = parseData(csv)

        if names2 is None:
            # iterates through each row of inputs from csv
            for name, attribute in zip(names1, attributes):
                create_graph_helper(graph, name, attribute)

        else:
            for name1, name2, attribute in zip(names1, names2, attributes):

                directed_dict = {}
                
                if 'DIRECTED' in attribute:
                    # stores the tuple of relationship values (like Men
                    # tor,Mentee)
                    directed_dict['DIRECTED'] = attribute.pop('DIRECTED')
                                
                node1 = create_graph_helper(graph, name1, attribute)
                node2 = create_graph_helper(graph, name2, attribute)
                
                # popping out directed will cause an issue if there are at least one new node (from the csv file) that only has a directed relationship with another node
                # this is because each node will have an empty attribute and therefore have no common attributes -> no common attributes means no edge will be created
                # as such we will need to create an edge between two said nodes
                
                # if there was no edge created because the only relationship between two ndoes is directed, we ll need to create the edge
                if directed_dict:
                    edge_list = graph.search_edge(node1,node2)
                    
                    
                    if not edge_list:
                        edge = graph.add_edge(node1,node2,"")
                        
                    else:
                        edge = edge_list[0]
                    
                    for tuple_list in directed_dict['DIRECTED']:
                        # update graph.directed
                        graph.add_directed(node1,node2,tuple_list)
                        # update node1.directed
                        node1.addDirected(node2,tuple_list[1])
                        # update node2.directed
                        node2.addDirected(node1,tuple_list[0])
                        
                        edge_id = edge.getID()
                        
                        # need to consider the case when the edge has already been created and the nodes were switched
                        if graph.edges[edge_id].node1 == node1:
                            graph.edges[edge_id].addDirected(tuple_list)
                            
                        else:
                            tuple_list_rev = (tuple_list[1],tuple_list[0])
                            graph.edges[edge_id].addDirected(tuple_list_rev)

    graph.generateColors()
    return graph


def SSCreateGraph(author_name:str,choice:int=1, numpapers:int=5):
    """
    coauthors_dict:
    PaperNode1: [list of AuthorNodes]
    PaperNode2: [list of AuthorNodes]
    .....
    
    coauthor_mapping:
    AuthorNode.id : AuthorNode
    
    coauthor_list = [list of AuthorNodes]
    
    papers_list = [list of Unique PaperNodes]
    """
    
    (coauthors_dict, coauthor_mapping) = generate_author_dict(author_name,choice, numpapers)
    coauthor_list = list(coauthor_mapping.values())
    #papers_list = list(coauthors_dict.keys())
    
    ssgraph = Graph()
      
    for author in coauthor_list:  
        author.attributes = {}
        author.attributes["COAUTHOR"] = author.papers
        ssgraph.nodes[author.getID()] = author
        
        link_nodes(ssgraph, author, author.getAttributes())
    
    return ssgraph
    


# add nodes to a previously defined graph
# takes in a graph object and a list of nodes to be added to that graph object
# will automatically creates a new node even if a node with the same name already exists -> will not update any exisiting node in the graph
# otherwise the user can use MergeGraph
def AddNodes(graph: Graph, nodes_list: list[Node]):
    new_node_list = []
    new_node = None
    
    for node in nodes_list:
        if isinstance(node, AuthorNode):
            name = node.getName()
            attribute = node.getAttributes()
            aliases = node.aliases
            authorId = node.authorId
            url = node.url
            papers = node.papers
            new_node = graph.add_ssnode(name, attribute, aliases, authorId, url, papers)
            link_nodes(graph, new_node, attribute)
                            

        else:
            name = node.getName()
            attribute = node.getAttributes()
            new_node = graph.add_node(name, attribute)
            link_nodes(graph, new_node, attribute)
            
        new_node_list.append(new_node)
        
    
        
    # handling directed nodes
    for node in nodes_list:
        #print("hello")
        old_index = nodes_list.index(node)
        new_node = new_node_list[old_index]
        # iterating through each node again
        for directed_rel, directed_nodes in node.directed.items():
            
            for directed_node in directed_nodes:
                # iterating through each node directed; we need to see if the node directed is in the list
                if directed_node in nodes_list:
                    #print("hello")
                    directed_index = nodes_list.index(directed_node)
                    directed_node = new_node_list[directed_index]
                    
                    # creating the new node connection
                    #print(new_node_list[old_index].name)
                    new_node.addDirected(directed_node,directed_rel)
                    
                    # key = rel, value = list of nodes
                    #for key,value in directed_node.directed.items():
                        
                            
                    
                    # directed_rel rn is just a str (like mentor) but it should be a tuple like (mentor,mentee)
                    graph.add_directed(new_node,directed_node,directed_rel)
                    
                
    
    graph.generateColors()
    return graph


# creates a new graph centered around chosen_node and other nodes connected to it from the inputted graph
def SubGraph(graph: Graph, chosen_node: Node):

    # is the chosen node even in the graph?
    if chosen_node.getID() not in graph.get_nodes_dict():
        # print("Node is not in the graph")
        raise ValueError("Node is not in the graph")

    subgraph = CreateGraph()

    # returns all edges connected to the chosen node
    connected_edges = graph.search_edge(chosen_node)
    # used to store all nodes in the new graph
    connected_nodes = [chosen_node]
    # iterates to find other nodes in the edge
    for edge in connected_edges:

        node1 = edge.getNode1()
        node2 = edge.getNode2()

        # second node is the chosen node; first node is the other connected node in that edge
        if node1.getID() != chosen_node.getID():
            connected_nodes.append(node1)
        else:
            connected_nodes.append(node2)

    # adding connected nodes to subgraph
    AddNodes(subgraph, connected_nodes)
    subgraph.generateColors()
    return subgraph


# returns a Graph of nodes that have the passed attributes
# if anything is empty/None, it will return everything
# attributes should be a dict like {str:[str]}
def FilterGraph(graph: Graph, attributes: dict = None):

    if not dict:
        raise ValueError("Desired filter is not in dictionary wrapper")

    filter_graph = CreateGraph()
    attributes = format_dict(attributes)

    future_nodes = []

    # get all nodes with relationships and relationship values desired in attributes parameter
    for attr, attr_list in attributes.items():  # "age": "21"
        attr = attr.title()

        if attr in graph.relationships:

            for value, value_list in graph.relationships[attr].items():
                value = value.title()
                if (attr_list and value in attr_list) or not attr_list:
                    for node in value_list:
                        if node not in future_nodes:
                            future_nodes.append(node)

    # get rid of unwanted filter attributes
    for node in future_nodes:
        new_attr = {}

        # go through current node's attributes' keys and values
        for attr, values in node.attributes.items():
            # if relationship in desired filter
            attr = attr.title()
            if attr in attributes:
                # if desired filter has desired values get values that exist
                if attributes[attr] != [] and attributes[attr] != None:
                    new_values = []
                    for v in values:
                        if isinstance(v, str):
                            v = v.title()
                        # this means that the passed in filter dictionary has to be following .title() format
                        if v in attributes[attr]:
                            new_values.append(v)

                    # if there was a desired value in the nodes existing values
                    if new_values != []:
                        new_attr[attr] = values
                # no specified desired values, take all values
                else:
                    new_attr[attr] = values

        node.attributes = new_attr

    AddNodes(filter_graph, future_nodes)
    filter_graph.generateColors()
    return filter_graph


# helper function for FilterGraph
def format_dict(attributes: dict):
    formatted = {}

    for attribute_type, attribute_values in attributes.items():
        attribute_type = attribute_type.title()
        formatted[attribute_type] = []

        if attribute_values and attribute_type != "COAUTHOR".title():
            for attribute_value in attribute_values:
                formatted[attribute_type].append(attribute_value.title())
        else:
            formatted[attribute_type] = attribute_values

    return formatted


# returns a dict
# key is the name
# value is a list of nodes with that name
def Collision(graph1: Graph, graph2: Graph):
    nodes1 = graph1.get_nodes()
    nodes2 = graph2.get_nodes()
    collision_dict = {}

    for node in nodes1:
        node_name = node.getName()
        if node_name in collision_dict:
            collision_dict[node_name].append(node)

        else:
            collision_dict[node_name] = [node]

    for node in nodes2:
        node_name = node.getName()
        if node_name in collision_dict:
            collision_dict[node_name].append(node)

        else:
            collision_dict[node_name] = [node]

    remove = []
    for key, value in collision_dict.items():
        if len(value) <= 1:
            remove.append(key)

    for key in remove:
        del collision_dict[key]

    return collision_dict


"""def clean_graphs(graph1: Graph, graph2: Graph, merge_list: list):
    for tuple in merge_list:
        for node in tuple:
            if node.id in graph1.nodes:
                del graph1.nodes[node.id]
            else:
                del graph2.nodes[node.id]

    return graph1, graph2
"""


def MergeGraph(graph1: Graph, graph2: Graph, merge_list: list = None):

    merge_graph = CreateGraph()

    # no merging
    if merge_list == None or merge_list == []:
        AddNodes(merge_graph, list(graph1.nodes.values()))
        AddNodes(merge_graph, list(graph2.nodes.values()))

    # currently assuming that nodes in merge_list are present in the graphs
    # also currently assuming that the tuples only have nodes with the same name -> prob need a helper function to check
    # also currently assuming that the same node cannot be in multiple diff tuples
    # assumes that nodes in the tuples are in the graph
    else:

        # remove nodes being merge from existing graphs
        # graph1, graph2 = clean_graphs(graph1, graph2, merge_list)

        # stores list of nodes that were merged; used to make sure we dont over merge shit
        merge = []
        # stores new nodes to be added
        nodes_list = []

        for merge_nodes in merge_list:
            # iterating through tuple
            name = None
            attribute = {}
            # checks to see if an authornode was merged
            counter = 0

            aliases = []
            authorId = None
            url = ""
            papers = []

            # for merged nodes
            for node in merge_nodes:
                name = node.name
                merge.append(node.getID())

                # Update attribute dictionary
                for key, value in node.attributes.items():
                    # iterate through each value in relationship values
                    for v in value:
                        if key in attribute and v not in attribute[key]:
                            attribute[key].append(v)
                        # Extend the existing list
                        else:
                            attribute[key] = value
                            break

                    # Add a new key-value pair if it doesn't exist

                if isinstance(node, AuthorNode):
                    # needs to be addressed
                    aliases = list(set(aliases + node.aliases))
                    authorId = node.authorId
                    url = node.url
                    papers = list(set(papers + node.papers))
                    counter = 1

            if counter == 1:
                merged_node = AuthorNode(
                    name, attribute, aliases, authorId, url, papers
                )
            else:
                merged_node = Node(name, attribute)

            # update self.nodes
            nodes_list.append(merged_node)

        all_nodes = list(graph1.nodes.values()) + list(graph2.nodes.values())
        # for unmerged nodes
        for node in all_nodes:
            if node.getID() not in merge:
                nodes_list.append(node)

        AddNodes(merge_graph, nodes_list)

    merge_graph.generateColors()
    return merge_graph


# returns a list of Nodes in a Graph
def GetNodes(graph: Graph):
    return graph.get_nodes()

# helper function for filter
def common_ids(list_of_lists):
    if not list_of_lists:
        return []

    # Convert the first inner list to a set
    result_set = set(list_of_lists[0])

    # Iterate through the rest of the inner lists and find their intersection with the result set
    for lst in list_of_lists[1:]:
        result_set.intersection_update(set(lst))

    # Convert the result set back to a list
    result_list = list(result_set)

    return result_list


# helper function to create graphs -> uses link_nodes which is needed
def create_graph_helper(graph: Graph, name: str, attribute: dict):

    named_nodes = graph.search_named_nodes(name)
    node = None
    # if empty -> no node with the name was found
    if not named_nodes:
        node = graph.add_node(name, attribute)

    # if node with the inputted name was found, it returns a list with one element for which we'll need to update attributes
    else:
        node = graph.update_node(named_nodes[0], attribute)

    link_nodes(graph, node, attribute)
    
    return node


# essentially updates relationships dict and edge information
def link_nodes(graph: Graph, node: Node, attribute: dict):
    # iterates through one row of attributes
    # eg {sex:[male], college:[umd]}
    # it iterates twice in the above example
    for attribute_type, attribute_value in attribute.items():
        temp_dict = {}
        temp_dict[attribute_type] = attribute_value

        # returns list of nodes id with the same attribute type and value that isnt the inputted node
        # note -> do i need to iterate through attribute value or will it always only haev one element
        #      -> i will prob need to iterate cuz of something like college:[umd,umbc]
        for single_attribute_value in attribute_value:
            relationship_nodes = graph.relationship_nodes(
                node, attribute_type, single_attribute_value
            )

            # if empty then there are currently no other nodes with that attribute type and value -> no need to create edges
            # if not empty then we need to create edges
            if relationship_nodes:

                for relationship_node in relationship_nodes:
                    # checks to see if theres an exisitng edge between the two nodes
                    # makes sure it doesnt create an edge with itself
                    if relationship_node != node:
                        relationship_node = graph.get_node(relationship_node.getID())
                        edge = graph.search_edge(node, relationship_node)

                        # if there was no edge
                        if not edge:
                            graph.add_edge(node, relationship_node, temp_dict)

                        # else update the edge
                        else:
                            graph.update_edge(edge[0], temp_dict)


def nodeFromGraph(graph: Graph, name: str):
    name = name.title()
    node_list = []

    for node_id, node in graph.nodes.items():
        if node.name == name:
            node_list.append(node)

    return node_list


def namesInGraph(graph: Graph):
    name_set = set()

    for node_id, node in graph.nodes.items():
        name_set.add(node.name)

    return list(name_set)


def ShortestPath(
    source: Node, target: Node, graph: Graph = None, net: nx = None
) -> list:
    # if 'graph' is 'None', returns a list of node id's, otherwise returns a list of nodes
    sp = nx.shortest_path(net, source=source.id, target=target.id)

    if graph:
        node_sp = []

        for id in sp:
            if id in graph.nodes:
                node_sp.append(graph.nodes[id])
            else:
                raise ValueError("Networkx object and Graph object are not equivalent")

        return node_sp
    else:
        return sp


# this takes the Graph Object with the associated ntx object, and just wraps it in pyvis
def Vis(graph: Graph):

    ntx = Networkx(graph)

    nt = Network("500px", "500px")

    for node_id in ntx.nodes():
        nt.add_node(
            node_id,
            label=ntx.nodes[node_id]["label"],
            title=ntx.nodes[node_id]["title"],
            size=22,
        )

    for u, v, data in ntx.edges(data=True):
        nt.add_edge(
            u, v, title=data["title"], color="rgb{}".format(data["color"]), width=3.6
        )

    # nt.from_nx(ntx)
    nt.toggle_physics(True)
    nt.show(
        "ntx.html", notebook=False
    )  # something between frontend/backend happens here for rendering, but this is the basics


def Networkx(graph):
    ntx = nx.Graph()

    # add nodes to networkx object
    for node_id, node in graph.nodes.items():

        title = titelize(node.attributes)

        if isinstance(node, AuthorNode):
            aliases = "Alisases: " + ", ".join(node.aliases) + "\n"
            papers = paper_string(node.papers)
            title = aliases + papers + title

        ntx.add_node(node_id, title=title, label=node.name)

    # add edges to networkx object
    for (node1_id, node2_id), edge_id in graph.connections.items():
        title = titelize(graph.edges[edge_id].relationships)
        edge_relationships = list(graph.edges[edge_id].relationships.keys())
        color = graph.colors[edge_relationships[0]]

        ntx.add_edge(node1_id, node2_id, title=title, color=color)

    return ntx

def titelize(attributes: dict) -> str:
    title = ""

    # k should be String, v should be List
    for k, v in attributes.items():
        if k != "COAUTHOR":
            title += k + ": " + ", ".join(v) + "\n"

    return title


def paper_string(papers) -> str:
    title = ""

    for paper in papers:
        title += paper.title + ": " + str(paper.year) + "\n"

    return title