from cdlib import algorithms
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

#####################################################################
#########################  FUNÇÕES ##################################

def create_graph():

    # Inicialização do grafo com base nos dados referidos no livro

    email_vertices = pd.read_csv("email_vertices.csv")
    email_edges = pd.read_csv("email_edgelist.csv")

    email_graph = nx.Graph()

    for _, node in email_vertices.iterrows():
        email_graph.add_node(node['id'], dept = node['dept'])

    for _, edge in email_edges.iterrows():
        email_graph.add_edge(edge["from"], edge["to"])

    return email_graph


def get_connected_components(graph):

    # Função para encontrar todos os componentes conectados presentes no grafo

    connected_components = nx.connected_components(graph)

    # Determinando o maior componente conectado

    largest_connected_component = max(connected_components, key=len)

    connected_components = nx.connected_components(graph)

    return [connected_components, largest_connected_component]


def get_louvain_communities(graph):

    # Aplicação do algoritmo de Louvain para buscar comunidades no grafo
    
    louvain_communities = algorithms.louvain(graph)

    # Cálculo da modularidade

    louvain_modularity = louvain_communities.newman_girvan_modularity()

    return [louvain_communities, louvain_modularity]


def get_ground_truth_community(graph):

    # Criação de um dicionário departamento -> id para o ground truth

    gd_department = {}

    for node, dept in graph.nodes.items():
        if dept["dept"] in gd_department.keys():
            gd_department[dept["dept"]].append(node)
        else:
            gd_department[dept["dept"]] = [node]

    # Cálculo da modularidade

    gd_department_modularity = nx.community.modularity(graph, gd_department.values())

    return [gd_department, gd_department_modularity]


def get_labels(grafo):

    # Criação de um dicionário vertice -> departamento

    email_labels = {}

    for id, dept in grafo.nodes.items():
        email_labels[id] = dept["dept"]

    return email_labels

def get_communities(graph, louvain_communities):

    # Criação de um dicionário vértice -> comunidade e ordenação com base nas comunidades de Louvain

    communities = louvain_communities.to_node_community_map()
    communities = [communities[k].pop() for k in list(graph.nodes)]

    return communities

def get_map(communities):

    # Criação de um mapa colorido

    pastel2 = cm.get_cmap('Pastel2', max(communities) + 1)

    return pastel2

def get_communities_by_department(graph, gd_department):

    # Criação de um dicionário vértice -> comunidade e ordenação com base nas comunidades do ground truth

    communities = {}
    for id, key in enumerate(gd_department.keys()):
        for value in gd_department[key]:
            communities[value] = [id]

    communities = [communities[k].pop() for k in list(graph.nodes)]

    return communities


def get_graph_dataframe(graph: nx.Graph, louvain_communities):

    # Criação do dataframe com o id, o departamento e a comunidade dos vértices

    data = {"id": [], "dept": [], "community": []}
    node_community = louvain_communities.to_node_community_map()

    for id, dept in graph.nodes.items():
        data["id"].append(id)
        data["dept"].append(dept["dept"])
        data["community"].append(node_community[id][0])

    return data


def get_dataframe_department_community(graph, louvain_communities):

    # Criação do dataframe com a quantidade de pessoas de cada departamento dentro de uma comunidade

    data = {}
    node_community = louvain_communities.to_node_community_map()

    for id, dept in graph.nodes.items():                       # data = dicionário comunidade ->  lista de departamento 
        if node_community[id][0] in data.keys():               # cada posição na lista representa um departamento
            data[node_community[id][0]][dept["dept"]] += 1     # cada elemento na lista representa o numero de pessoas do
        else:                                                  # departamento naquela comunidade
            data[node_community[id][0]] = [0]*42              
            data[node_community[id][0]][dept["dept"]] += 1 

    return get_dataframe_percentage_department_community(data)

def get_dataframe_percentage_department_community(data):
    # Criação do dataframe com a porcentagem de cada departamento dentro de uma comunidade  

    dept_in_community_percentage = {}

    for community in data.keys():
        number_of_nodes_in_community = sum(data[community])    # dept_in_community_percentage = dicionário comunidade -> porcentagem de pessoas de um departamento naquela comunidade
        dept_in_community_percentage[community] = [0]*42       # cada posição da lista representa um departamento
        for department in range(1, len(data[community])):      # cada elemento da lista contém a porcentagem do departamento na comunidade
            dept_in_community_percentage[community][department] = data[community][department]/number_of_nodes_in_community

    return dept_in_community_percentage

def get_cliques(graph):

    # Geranddo os cliques maximais do grafo

    cliques = nx.find_cliques(graph)

    # Ordenação dos cliques maximais, número de clique do grafo e número de cliques maximais

    maximal_cliques = sorted(cliques, key=len)
    
    clique_number = nx.graph_clique_number(graph)
    
    maximum_clique = maximal_cliques[len(maximal_cliques)-1]

    number_of_maximal_cliques = len(maximal_cliques)

    number_of_cliques_maximum_size = 0

    for clique in reversed(maximal_cliques):
        if len(clique) == clique_number:
            number_of_cliques_maximum_size += 1
        else:
            break
    
    return [maximum_clique, clique_number, number_of_maximal_cliques, number_of_cliques_maximum_size]

#####################################################################



#####################################################################
############################# MAIN ##################################

# QUESTÃO 4:

print("QUESTÃO 4: ")

# Inicializando o grafo

email_graph = create_graph()

# Determinando os componentes conectados do grafo e o maior componente conectado

email_connected_components_data = get_connected_components(email_graph)

# Visualização de todos os componentes conectados do grafo

print("Componentes conectados do grafo:")
for connected_component in email_connected_components_data[0]:
    print(connected_component)

# Visualização do maior componente conectado do grafo

print("Maior componente conectado do grafo: \n", email_connected_components_data[1])

# FIM DA QUESTÃO 4


# QUESTÃO 5:

print("QUESTÃO 5: ")

# Gerando as comunidades de Louvain no grafo e sua modularidade

email_louvain_communities_data = get_louvain_communities(email_graph)

# Visualização das comunidades de Louvain do grafo

print("Comunidades de Louvain do grafo:")

for louvain_community in email_louvain_communities_data[0].communities:
    print(louvain_community)

# Modularidade das comunidades de Louvain do grafo

print("Modularidade:", email_louvain_communities_data[1].score)

# FIM DA QUESTÃO 5


# QUESTÃO 6

print("QUESTÃO 6: ")

# Gerando a comunidade ground truth com base nos departamentos

email_ground_truth_data = get_ground_truth_community(email_graph)

# Visualização das comunidades ground truth

print("comunidades ground truth por departamento:\n", email_ground_truth_data[0])

print("Modularidade do ground truth:", email_ground_truth_data[1], "\nModularidade das comunidades de Louvain:", email_louvain_communities_data[1].score)

# FIM DA QUESTÃO 6


# QUESTÃO 7

print("QUESTÃO 7: ")

print("Visualização das comunidades de louvain do grafo:")

# Mostrando as comunidades de Louvain com base nas funções

communities = get_communities(email_graph, email_louvain_communities_data[0])

np.random.seed(123)
nx.draw_spring(email_graph, labels = get_labels(email_graph), cmap = get_map(communities),
node_color = communities, edge_color = "grey")
plt.show()

print("Visualização das comunidades de ground truth por departamento do grafo:")

# Mostrando as comunidades do ground truth com base nas funções

communities = get_communities_by_department(email_graph, email_ground_truth_data[0])

np.random.seed(123)
nx.draw_spring(email_graph, labels = get_labels(email_graph), cmap = get_map(communities),
node_color = communities, edge_color = "grey")
plt.show()

# FIM DA QUESTÃO 7


# QUESTÃO 8

print("QUESTÃO 8: ")

print("Visualização do mapa de calor com as colunas sendo os departamentos e as linhas sendo as comunidades:")

# Criando o dataframe com os dados do grafo

email_graph_dataframe = get_graph_dataframe(email_graph, email_louvain_communities_data[0])

# Criando o dataframe com as porcentagens de cada departamento em cada comunidade com base no dataframe anterior

email_graph_percentage_dataframe = get_dataframe_department_community(email_graph, email_louvain_communities_data[0])

# Visualização

df = pd.DataFrame(email_graph_percentage_dataframe)
plt.imshow(df, cmap="autumn", interpolation="nearest")
plt.show()

# FIM DA QUESTÃO 8


# QUESTÃO 9

print("QUESTÃO 9: ")

# Gerando os cliques maximais, o numero de clique e o numero de cliques maximais no grafo

email_clique_data = get_cliques(email_graph)

# Visualização

print("Clique máximo:")
print(email_clique_data[0])

print("Número de clique do grafo:")
print(email_clique_data[1])

print("Número de cliques maximais do grafo:")
print(email_clique_data[2])

print("Número de cliques com o tamanho máximo no grafo:")
print(email_clique_data[3])

#####################################################################