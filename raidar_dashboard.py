import pandas as pd
from flask import Flask, render_template, jsonify
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json

def fetch_memecoin_data():
    return [
        {'date': '2023-10-01', 'coin': 'MemeCoin1', 'price': 0.001, 'volume': 10000},
        {'date': '2023-10-02', 'coin': 'MemeCoin1', 'price': 0.0012, 'volume': 15000},
        {'date': '2023-10-03', 'coin': 'MemeCoin1', 'price': 0.0011, 'volume': 12000},
        {'date': '2023-10-01', 'coin': 'MemeCoin2', 'price': 0.0005, 'volume': 5000},
        {'date': '2023-10-02', 'coin': 'MemeCoin2', 'price': 0.0006, 'volume': 7000},
        {'date': '2023-10-03', 'coin': 'MemeCoin2', 'price': 0.0007, 'volume': 8000},
    ]

def prepare_data():
    data = fetch_memecoin_data()
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/dashboard')
def dashboard():
    df = prepare_data()
    
    figs = []
    for coin in df['coin'].unique():
        coin_df = df[df['coin'] == coin]
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                            subplot_titles=(f'Price of {coin}', f'Volume of {coin}'))
        
        # Price Line
        fig.add_trace(go.Scatter(x=coin_df['date'], y=coin_df['price'], mode='lines', name='Price'), row=1, col=1)
        
        # Volume Bar
        fig.add_trace(go.Bar(x=coin_df['date'], y=coin_df['volume'], name='Volume'), row=2, col=1)
        
        fig.update_layout(height=600, title_text=f"Performance of {coin}")
        figs.append(fig)
    
    # Convert Plotly figures to JSON for rendering in HTML
    graphJSON = [json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) for fig in figs]
    
    # Calculate ROI for each coin
    roi_data = []
    for coin in df['coin'].unique():
        coin_df = df[df['coin'] == coin]
        start_price = coin_df['price'].iloc[0]
        end_price = coin_df['price'].iloc[-1]
        roi = ((end_price - start_price) / start_price) * 100 if start_price != 0 else 0
        roi_data.append({'coin': coin, 'roi': roi})
    
    return render_template('dashboard.html', graphJSON=graphJSON, roi_data=roi_data)

if __name__ == '__main__':
    app.run(debug=True)
