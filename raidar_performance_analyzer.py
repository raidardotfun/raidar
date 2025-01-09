import matplotlib.pyplot as plt
import pandas as pd

def analyze_performance(meme_data):
    if not isinstance(meme_data, pd.DataFrame):
        meme_data = pd.DataFrame(meme_data)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    ax1.plot(meme_data['date'], meme_data['price'], label='Price', color='blue')
    ax1.set_title(f'Price Performance of {meme_data["name"].iloc[0]}')
    ax1.set_ylabel('Price')
    ax1.legend()

    ax2.plot(meme_data['date'], meme_data['volume'], label='Volume', color='green')
    ax2.set_title('Trading Volume')
    ax2.set_ylabel('Volume')
    ax2.set_xlabel('Date')
    ax2.legend()

    plt.tight_layout()
    plt.show()

    roi = (meme_data['price'].iloc[-1] - meme_data['price'].iloc[0]) / meme_data['price'].iloc[0] * 100
    print(f"ROI since launch: {roi:.2f}%")
