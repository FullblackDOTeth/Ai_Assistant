"""
Visualization module for learning insights
"""

import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
from pathlib import Path
from typing import Dict, List
import json

class LearningVisualizer:
    def __init__(self, learning_manager):
        """Initialize visualizer with learning manager"""
        self.learning_manager = learning_manager
        self.output_dir = Path(__file__).parent.parent.parent / 'data' / 'visualizations'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_interest_network(self) -> str:
        """Create interactive visualization of interest network"""
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes
        for node in self.learning_manager.interest_graph['nodes']:
            topic_id = node.split('_')[1]
            weight = self.learning_manager.user_preferences['topics'].get(topic_id, 0)
            G.add_node(node, weight=weight)
        
        # Add edges
        for node1, neighbors in self.learning_manager.interest_graph['edges'].items():
            for node2 in neighbors:
                weight = self.learning_manager.interest_graph['weights'].get(
                    (node1, node2),
                    0
                )
                G.add_edge(node1, node2, weight=weight)
        
        # Calculate layout
        pos = nx.spring_layout(G)
        
        # Create Plotly figure
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Add edges to trace
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)
        
        # Create node trace
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=[],
                color=[],
                line_width=2
            )
        )
        
        # Add nodes to trace
        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            
            # Node size based on preference weight
            weight = G.nodes[node]['weight']
            node_trace['marker']['size'] += (20 + 30 * weight,)
            node_trace['marker']['color'] += (weight,)
            
            # Node text
            node_trace['text'] += (f"Topic {node.split('_')[1]}<br>Weight: {weight:.2f}",)
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title='Interest Network',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        # Save
        output_file = self.output_dir / 'interest_network.html'
        fig.write_html(str(output_file))
        return str(output_file)

    def create_topic_evolution(self) -> str:
        """Create topic evolution visualization"""
        # Get interest evolution data
        evolution = self.learning_manager._get_interest_evolution()
        if not evolution:
            return None
            
        # Convert to DataFrame
        records = []
        for entry in evolution:
            date = pd.to_datetime(entry['date'])
            for topic_id, weight in entry['topics'].items():
                records.append({
                    'date': date,
                    'topic': f'Topic {topic_id}',
                    'weight': weight
                })
        
        df = pd.DataFrame(records)
        
        # Create figure
        fig = px.line(
            df,
            x='date',
            y='weight',
            color='topic',
            title='Topic Evolution Over Time'
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Topic Weight',
            hovermode='x unified'
        )
        
        # Save
        output_file = self.output_dir / 'topic_evolution.html'
        fig.write_html(str(output_file))
        return str(output_file)

    def create_interaction_summary(self) -> str:
        """Create interaction summary visualization"""
        stats = self.learning_manager._get_interaction_stats()
        if not stats:
            return None
            
        # Create subplots
        fig = go.Figure()
        
        # Interaction types pie chart
        fig.add_trace(
            go.Pie(
                labels=list(stats['interaction_types'].keys()),
                values=list(stats['interaction_types'].values()),
                name="Interaction Types",
                domain=dict(x=[0, 0.5], y=[0, 1])
            )
        )
        
        # Daily activity bar chart
        df = pd.DataFrame(self.learning_manager.interaction_history)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_counts = df.groupby('date').size()
        
        fig.add_trace(
            go.Bar(
                x=daily_counts.index,
                y=daily_counts.values,
                name="Daily Activity",
                xaxis='x2',
                yaxis='y2'
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Interaction Summary",
            grid=dict(rows=1, columns=2, pattern='independent'),
            xaxis2=dict(title="Date", domain=[0.6, 1]),
            yaxis2=dict(title="Number of Interactions"),
            showlegend=True
        )
        
        # Save
        output_file = self.output_dir / 'interaction_summary.html'
        fig.write_html(str(output_file))
        return str(output_file)

    def create_dashboard(self) -> str:
        """Create comprehensive dashboard"""
        # Get all insights
        analysis = self.learning_manager.get_interest_analysis()
        
        # Create HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Learning Insights Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .section {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; }}
                .stat-box {{ 
                    display: inline-block; 
                    padding: 15px; 
                    margin: 10px; 
                    background: #f5f5f5;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Learning Insights Dashboard</h1>
                
                <div class="section">
                    <h2>Overview</h2>
                    <div class="stat-box">
                        Total Interactions: {analysis['interaction_stats']['total_interactions']}
                    </div>
                    <div class="stat-box">
                        Unique Topics: {analysis['interaction_stats']['unique_topics']}
                    </div>
                    <div class="stat-box">
                        Most Active Day: {analysis['interaction_stats']['most_active_day']}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Top Topics</h2>
                    <table>
                        <tr><th>Topic ID</th><th>Weight</th></tr>
                        {''.join(
                            f"<tr><td>Topic {tid}</td><td>{weight:.3f}</td></tr>"
                            for tid, weight in analysis['top_topics'].items()
                        )}
                    </table>
                </div>
                
                <div class="section">
                    <h2>Topic Clusters</h2>
                    {''.join(
                        f"<div class='stat-box'><h3>Cluster {c['cluster_id']}</h3>"
                        f"<p>Strength: {c['strength']:.3f}</p>"
                        f"<p>Topics: {', '.join(t.split('_')[1] for t in c['topics'])}</p></div>"
                        for c in analysis['topic_clusters']
                    )}
                </div>
                
                <div class="section">
                    <h2>Visualizations</h2>
                    <iframe src="interest_network.html" width="100%" height="600px"></iframe>
                    <iframe src="topic_evolution.html" width="100%" height="600px"></iframe>
                    <iframe src="interaction_summary.html" width="100%" height="600px"></iframe>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save dashboard
        output_file = self.output_dir / 'dashboard.html'
        output_file.write_text(html_content)
        return str(output_file)

# Create visualizer instance
def create_visualizer(learning_manager):
    return LearningVisualizer(learning_manager)
