from flask import Flask, request, jsonify, render_template
from extractor import NERExtractor  
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
ner = NERExtractor()



def generate_graph_image(entities, relationships):
    G = nx.DiGraph()
    
    for entity in entities:
        G.add_node(entity)
    
    for rel in relationships:
        G.add_edge(rel['source'], rel['target'], label=rel['relationship'])
    
    fig, ax = plt.subplots(figsize=(8, 6))  
    pos = nx.spring_layout(G, k=6.0, seed=42) 

    
    nx.draw_networkx_nodes(G, pos, node_color="skyblue", node_size=1000, edgecolors="black", alpha=0.6, ax=ax)

    
    nx.draw_networkx_edges(G, pos, edge_color="gray", width=1.5, connectionstyle="arc3,rad=0.3", arrows=True, ax=ax)
    
   
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold", ax=ax)

    
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, rotate=True, label_pos=0.3,
                                 bbox=dict(facecolor="white", edgecolor="none", alpha=0.5), ax=ax)

    ax.set_xticks([]) 
    ax.set_yticks([]) 
    ax.set_frame_on(False) 
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  

    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.2)  
    buf.seek(0)
    encoded_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return encoded_image


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    result = ner.extract_entities_and_relationships(text)
    if 'error' in result:
        return jsonify(result), 500
    
    graph_image = generate_graph_image(result['entities'], result['relationships'])
    
    return jsonify({'graph': graph_image})

if __name__ == '__main__':
    app.run(debug=True)
