import dask.dataframe as dd
import pandas
import AuthorNode as author


"""
Pauls comments

To do after CDR
i) Leading whitespace issue

To discuss at meeting:
i) Search by scholar id, search by paper id, store paper id in the paper node class. All author nodes will have an AUTHORID, which could be checked when creating, and used to query
    semantic scholar, along with querying paper ids to recreate the graph.

ii) Discuss how saving directed graphs should work, and the format for reading them. How can i get directed edges?


"""





# to do: leading whitespace cannot be read by dask, must look into this more
def parseData(csv):
    df = dd.read_csv(csv).compute()

    if df.isna().values.any():
       raise ValueError("Error: No columns are allowed to be empty, no leading whitespace is allowed")
    
    offset = 0
    
    # stores as a list all the names (strings) that were put first under the column of person1
    one = df.get(df.columns[0]).tolist()

    # going through the list of person1, this will remove whitespace before/after 
    # and capitalize first letter of each word
    for x in range(len(one)):
        one[x] = one[x].strip()
        one[x] = one[x].title()

    #checks if the CSV is of type 2 which has 4 columns 
    two = None
    if len(df.columns) == 4:
        # stores as a list all the names (strings) that were put first under the column of person2
        two = df.get(df.columns[1]).tolist()

        # going through the list of person2, this will remove whitespace before/after 
        # and capitalize first letter of each word
        for x in range(len(two)):
            two[x] = two[x].strip()
            two[x] = two[x].title()
            
        offset = 1
    elif len(df.columns) != 3:
        raise ValueError("Error: Incorrect format")

    # Gets the relationships and relationship values
    three = []
    keys = df.get(df.columns[1 + offset]).tolist()
    values = df.get(df.columns[2 + offset]).tolist()
    
    # Loops through all relationships, and adds to the three list a dictionary, in which the keys
    # are the relationship, and the values are the corresponding relationship values
    for i in range(len(keys)):
        pairing = dict()
        currkey = keys[i].split(',')
        currvalue = values[i].split(',')

        # Error if not a relationships have a corresponding value, or vice versa
        if len(currkey) != len(currvalue):
            raise ValueError("Error: All relationships must have corresponding value")
            
        # Loops through all relationships given in current cell
        for x in range(len(currkey)):
            key = currkey[x].strip()
            if key.isspace() or not key: #if the key is empty or whitespace an error occurs
                raise ValueError("Error: All relationships must have corresponding value")
            
            value = currvalue[x].strip()
            if value.isspace() or not value: #if the value is empty or whitespace an error occurs
                raise ValueError("Error: All relationships must have corresponding value")
            
            # If the current key marks a directed graph, adjusts value to the correct format
            # Correct format is 'example1/example2'
            if key == 'DIRECTED':
                rel = value.split("/")

                # name1,name2,DIRECTED,mentor/mentee
                if offset == 1:                
                    # Error if too many or too little '/'s are used
                    if len(rel) != 2:
                        raise ValueError("Error: Incorrect directed relationship format")
                    # Error if either side of the '/' is empty
                    if (not rel[0] or not rel[1]):
                        raise ValueError("Error: Incorrect directed relationship format")
                    value = (rel[0].lower(), rel[1].lower())
                # name1,DIRECTED,name2/mentor/mentee
                elif offset == 0:
                    # Error if too many or too little '/'s are used
                    if len(rel) != 3:
                        raise ValueError("Error: Incorrect directed relationship format")
                    
                    # Error if any part is empty
                    if (not rel[0] or not rel[1] or not rel[2]):
                        raise ValueError("Error: Incorrect directed relationship format")
                    
                    # returns (name2,mentor,mentee) such that name1 -> name2, mentor/mentee
                    value = (rel[0].title(), rel[1].lower(), rel[2].lower())

            # Change all non author info to lower case
            elif not (key == 'AUTHORID' or key == 'PAPER'):
                key = key.lower()
                value = value.lower()
            # Saves the key,value pair to the dictionary
            if key in pairing:
                pairing[key].append(value)  # If key already exists, append value to existing list
            else:
                pairing[key] = [value]
        
        three.append(pairing)

    return (one, two, three)

# to do: cannot save graphs with directed edges
def saveData(nodes, filePath):
    names = list()
    attributes = list()
    authors = list()

    # Gets all information out of the list of nodes, and sorts into authors and non authors
    for node in nodes:
        if type(node) is author.AuthorNode:
            authors.append(node)
        else:
            names.append(node.getName())
            attributes.append(node.getAttributes())


    # Formats non author data in the correct way
    data = dict()
    ks = list()
    vs = list()
    for x in attributes:

        keyslist = list(x.keys())
        valuelist = list(x.values())
        values_to_save = list()
        keys_to_save = list()

        # Unpacks list of lists into values
        for y in range(len(valuelist)):
            for z in range(len(valuelist[y])):
                keys_to_save.append(keyslist[y])
                values_to_save.append(valuelist[y][z])

        ks.append(','.join(keys_to_save))
        vs.append(','.join(values_to_save))
        

    for x in authors:
        keys_to_save = list()
        values_to_save = list()
        keys_to_save.append("AUTHORID")
        values_to_save.append(x.authorId)
        for i in range(len(x.papers)):
            keys_to_save.append("PAPER")
            values_to_save.append(x.papers[i].title)

        names.append(x.getName())
        ks.append(','.join(keys_to_save))
        vs.append(','.join(values_to_save))

    # Puts all data into a dictionary
    data["Person 1"] = names
    data['Relationship'] = ks
    data['Relationship Value'] = vs

    # Saves dictionary to csv
    pandas_df = pandas.DataFrame(data)
    df = dd.from_pandas(pandas_df, npartitions=1)
    df.compute().to_csv(filePath, index=False)