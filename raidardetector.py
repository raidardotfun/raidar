from solana.rpc.api import Client
from solana.publickey import PublicKey
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def detect_trending_memes(solana_client, meme_list):
    # DataFrame with features for meme analysis
    meme_data = pd.DataFrame(meme_list, columns=['name', 'symbol', 'social_mentions', 'volume', 'age', 'trending_score'])
    
    # Features for prediction
    features = ['social_mentions', 'volume', 'age']
    X = meme_data[features]
    y = meme_data['trending_score']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Predict on new memes
    new_memes = solana_client.get_new_meme_coins()  # Assume this method exists in the Solana client
    new_memes_data = pd.DataFrame(new_memes, columns=features)
    predictions = model.predict_proba(new_memes_data)[:, 1]  # Probability of being trending
    
    # Return memes with high probability of trending
    return [meme for meme, prob in zip(new_memes, predictions) if prob > 0.7]
