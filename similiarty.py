from py2neo import Graph, Node, Relationship
from py2neo.matching import *
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('bert-base-nli-mean-tokens')
if torch.cuda.is_available():
   model = model.to(torch.device("cuda"))
print(model.device)
sentences = []
sentences_nodes = []



graph = Graph("bolt://192.168.112.232:7687", auth=("neo4j", "      "))
relationship_matcher = RelationshipMatcher(graph)

node_matcher = NodeMatcher(graph)
nodes = list(node_matcher.match("Library"))
count = 0
node_list = []
for node in nodes:
    if "description" in node:
        sentences.append(node["description"])
        sentences_nodes.append(node)

sentence_embeddings = model.encode(sentences,show_progress_bar=True)
print(sentence_embeddings.shape)


a = cosine_similarity(sentence_embeddings,sentence_embeddings)

for i, scores in enumerate(a):
    for j, score in enumerate(scores):
        if i == j:
            continue
        if not relationship_matcher.match([sentences_nodes[i], sentences_nodes[j]], r_type="Similarity").exists():
            description_similarity = {"description_similarity": float(score)}
            relationship = Relationship(sentences_nodes[i], "Similarity", sentences_nodes[j], **description_similarity)
            graph.create(relationship)
print(a)