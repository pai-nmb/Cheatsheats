#===============================================================================================================
"""
This script is designed to connect to an OPC UA server, traverse the server's address space, and extract the 
nodeId values of nodes in a specific namespace. The resulting list of NodeIds is then printed. Adjust the 
OPC UA server URL and the target_namespace variable as needed for your specific use case.
"""
#===============================================================================================================

from opcua import Client

def extract_node_ids(node, target_namespace, s_values):
    """
    Function to extract the node id identifiers and put it in a list (so that it can be copied into GetOPCUAValue processor in Nifi)

    Inputs
    node: The current node being processed.
    target_namespace: The desired OPC UA namespace index to filter nodes.
    s_values: A list that will store the extracted 's' values.
    
    """
    if node.nodeid.NamespaceIndex == target_namespace:
        s_attribute = node.nodeid.Identifier
        s_values.append(s_attribute)
    
    for child_node in node.get_children():
        extract_node_ids(child_node, target_namespace, s_values)

# main program        

if __name__ == "__main__":
    url = 'opc.tcp://10.35.1.10:4842' # Replace this with desired connection URL
    client = Client(url=url)

    try:
        client.connect()
        root_node = client.get_root_node()
        target_namespace = 0  # Replace with the desired namespace index

        s_values_list = []
        extract_node_ids(root_node, target_namespace, s_values_list)

        print("List of 's' values:")
        print(s_values_list)

    finally:
        client.disconnect()
