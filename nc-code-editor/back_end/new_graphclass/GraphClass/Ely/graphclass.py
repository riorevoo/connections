import networkx as nx
from nodeclass import Node
from edgeclass import Edge

# Now most of the functions return the id of the node/edge created/updated


class Graph:
    def __init__(self):
        self.nodes = {}  # {node.id: node object}
        self.edges = {}  # {edge.id:edge object}
        self.connections = {}  # {(node1.id, node2.id) : edge.id}
        self.relationships = {}

        """
        self.relationships = {
           "Institution": {
               "UMD": [...] #all nodes with “Institution” relationship, “UMD” value 
               "Yale": [...]
           },
           "Age": {
               "21": [...] #all nodes with “Age” relationship, “21” value
               "34": [...]
           }
           "Coauthor": {
               "Paper Name": [.....] #ALL AUTHOR NODES 
               "Paper Name2": [...]
           }
        }
        """

    def return_nxGraph(self):
        return self.nxGraph

    # assumes new node is to be added
    def add_node(self, name: str, attributes: dict):
        node = Node(name, attributes)
        self.nodes[node.getID()] = node
        print("Creating new node:", node.getName())
        print("Node id:", node.getID())
        print("Node attributes:", node.getAttributes())
        return node

    # updates a existing node
    def update_node(self, node: Node, attributes: dict):
        print("Updating node:", node.getName())
        print("Node id:", node.getID())
        print("Node attributes:", node.getAttributes())
        node.updateAttributes(attributes)
        return node

    # returns list of nodes ids that have the same attribute type and corresponding value
    # which is use to create/update edges
    # also update relationships dict
    # potentially could also split into two functions, but would also have to change functions.py
    def relationship_nodes(self, node: Node, attribute_type: str, attribute_value: str):
        relationship_nodes = []
        node_id = node.getID()
        """
        self.relationships = {
           "Institution": {
               "UMD": [...] #all nodes with “Institution” relationship, “UMD” value 
               "Yale": [...]
           }
        }
        """

        # eg check to see if institution is present
        if attribute_type in self.relationships:

            # eg check to see if UMD is present
            if attribute_value in self.relationships[attribute_type]:

                # to avoid dups; could also switch to sets?
                if node_id not in self.relationships[attribute_type][attribute_value]:

                    # return list of other nodes with same attribute type and value; to be use to create/update edges
                    relationship_nodes = self.relationships[attribute_type][
                        attribute_value
                    ]
                    # update relationships
                    self.relationships[attribute_type][attribute_value].append(node_id)

                # dont need else cuz then the node associated with that particular attribute type and attribute value is already present in relationships
                # and has the corresponding edges

            # if UMD is not present, relationships needs to be updated
            else:
                self.relationships[attribute_type][attribute_value] = [node_id]

        else:
            print(type(attribute_value))
            print(attribute_type)
            temp_dict = {}
            temp_dict[attribute_value] = [node_id]
            self.relationships[attribute_type] = temp_dict

        print("****************************************")
        print(relationship_nodes)
        return relationship_nodes

    # adds a new edge
    def add_edge(self, node1: Node, node2: Node, attributes: dict):
        edge = Edge(node1, node2, attributes)
        self.edges[edge.getID()] = edge
        self.connections[(node1.getID(), node2.getID())] = edge.getID()
        return edge

    # might change later; so keeping it here for now
    def update_edge(self, edge: Edge, attributes: dict):
        edge.updateRelationships(attributes)
        return edge

    # returns a list of nodes that have the inputted name
    def search_named_nodes(self, name: str):
        named_nodes = []
        for node_id, node in self.nodes.items():
            if name == node.getName():
                named_nodes.append(node)
        return named_nodes

    # checks for edges; returns list of edge objects if found
    def search_edge(self, node1: Node, node2: Node = None):
        edge_objects = []

        if node2 is None:
            # If only one node is provided, search for edges connected to that node
            for (n1_id, n2_id), edge_id in self.connections.items():
                if node1.getID() in (n1_id, n2_id):
                    edge_objects.append(self.edges[edge_id])
        else:
            # If two nodes are provided, search for edges between those nodes
            for (n1_id, n2_id), edge_id in self.connections.items():
                if (n1_id == node1.getID() and n2_id == node2.getID()) or (
                    n1_id == node2.getID() and n2_id == node1.getID()
                ):
                    edge_objects.append(self.edges[edge_id])

        return edge_objects

    # first attempt for solving disambiguity
    # named_nodes is the list of nodes with the inputted name
    # returns the node object created/updated
    # NOT NEEDED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def disambiguation(self, named_nodes: list, name: str, attributes: dict):
        if not named_nodes:
            # If there are no nodes with the provided name, create a new node
            new_node = self.add_node(name, attributes)
            return new_node

        print("+++++++++++++++++++++++++++++++++++++++++++")
        for i, node in enumerate(named_nodes, start=1):
            print(f"{i}. {name}")
            print(f"{node.getAttributes()}")
            print()

        last_number = len(named_nodes)

        # Ask the user to choose a node or create a new one
        while True:
            choice = input(
                f"Enter the number of the node you want or 0 to create a new one: "
            )
            if choice.isdigit() and 0 <= int(choice) <= last_number:
                choice = int(choice)
                break
            print("Invalid input. Please enter a valid number.")

        if choice == 0:
            # Create a new node
            # Assuming attributes for the new node are provided by the user
            new_node = self.add_node(name, attributes)
            return new_node

        else:
            # Get the chosen node
            chosen_node = named_nodes[choice - 1]
            chosen_node.updateAttributes(attributes)

            # Now you can use the chosen_node as needed
            print("You chose: ", chosen_node.getName())
            print("with attributes: ", chosen_node.getAttributes())
            print()
            return chosen_node

    def get_node(self, node_id: int):
        if node_id in self.nodes:
            return self.nodes[node_id]
        else:
            return None

    def print_nodes(self):
        for node in self.nodes.values():
            print()
            print(node.getName())
            print(node.getID())
            print(node.getAttributes())

    def print_edges(self):
        print()
        for edge in self.edges.values():
            print("Edge info: ")
            # print(edge.getNode1().getID())
            print(edge.getNode1().getName())
            # print(edge.getNode2().getID())
            print(edge.getNode2().getName())

            print(edge.getRelationships())
            print()

    def print_relationships(self):
        for relationship, nodes in self.relationships.items():
            print(f"{relationship}:")
            for value, associated_nodes in nodes.items():
                print(f"  {value}: {associated_nodes}")