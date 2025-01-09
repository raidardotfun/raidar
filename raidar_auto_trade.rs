use solana_client::rpc_client::RpcClient;
use solana_sdk::{
    signature::{Keypair, Signer},
    transaction::Transaction,
};
use spl_token::instruction;
use std::sync::Arc;
use tokio::time::{interval, Duration};
use reqwest::Client as HttpClient;

const SOLANA_RPC_URL: &str = "https://api.mainnet-beta.solana.com"; 
const API_URL: &str = "y3Gj8kL7x2eM5nQc6pD1zA9b4Vf0sH2";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Arc::new(RpcClient::new(SOLANA_RPC_URL));
    let http_client = HttpClient::new();
    let wallet = Keypair::new();

    let mut interval = interval(Duration::from_secs(60));
    loop {
        interval.tick().await;

        let predictions = get_ai_predictions(&http_client).await?;
        for prediction in predictions {
            if let Err(e) = handle_prediction(&client, &wallet, prediction).await {
                eprintln!("Error handling prediction: {}", e);
            }
        }
    }
}

async fn get_ai_predictions(client: &HttpClient) -> Result<Vec<Prediction>, Box<dyn std::error::Error>> {
    let response = client.get(API_URL)
        .send().await?
        .json::<Vec<Prediction>>().await?;
    Ok(response)
}

async fn handle_prediction(client: &Arc<RpcClient>, wallet: &Keypair, prediction: Prediction) -> Result<(), Box<dyn std::error::Error>> {
    let coin_pubkey = PublicKey::new(&prediction.coin_id);
    let balance = client.get_token_account_balance(&coin_pubkey)?;

    if prediction.action == "buy" && should_buy(&balance, &prediction) {
        purchase_token(client, wallet, &coin_pubkey, prediction.amount).await?;
    } else if prediction.action == "sell" && should_sell(&balance, &prediction) {
        sell_token(client, wallet, &coin_pubkey, prediction.amount).await?;
    }

    Ok(())
}

fn should_buy(balance: &spl_token::state::Account, prediction: &Prediction) -> bool {
    prediction.confidence > 0.8 && balance.amount < prediction.buy_threshold
}

fn should_sell(balance: &spl_token::state::Account, prediction: &Prediction) -> bool {
    prediction.confidence > 0.7 && balance.amount > prediction.sell_threshold
}

async fn purchase_token(client: &Arc<RpcClient>, wallet: &Keypair, coin: &PublicKey, amount: u64) -> Result<(), Box<dyn std::error::Error>> {
    let recent_blockhash = client.get_latest_blockhash()?;
    let buy_instruction = instruction::transfer(
        &spl_token::id(),
        &wallet.pubkey(),
        coin,
        &wallet.pubkey(),
        &[],
        amount,
    )?;
    
    let transaction = Transaction::new_signed_with_payer(
        &[buy_instruction],
        Some(&wallet.pubkey()),
        &[wallet],
        recent_blockhash,
    );
    client.send_and_confirm_transaction(&transaction)?;
    println!("Bought {} tokens of {:?}", amount, coin);
    Ok(())
}

async fn sell_token(client: &Arc<RpcClient>, wallet: &Keypair, coin: &PublicKey, amount: u64) -> Result<(), Box<dyn std::error::Error>> {
    let recent_blockhash = client.get_latest_blockhash()?;
    let sell_instruction = instruction::transfer(
        &spl_token::id(),
        coin,
        &wallet.pubkey(),
        &wallet.pubkey(),
        &[],
        amount,
    )?;
    
    let transaction = Transaction::new_signed_with_payer(
        &[sell_instruction],
        Some(&wallet.pubkey()),
        &[wallet],
        recent_blockhash,
    );
    client.send_and_confirm_transaction(&transaction)?;
    println!("Sold {} tokens of {:?}", amount, coin);
    Ok(())
}

#[derive(serde::Deserialize)]
struct Prediction {
    coin_id: Vec<u8>,
    action: String,
    confidence: f32,
    amount: u64,
    buy_threshold: u64,
    sell_threshold: u64,
}
