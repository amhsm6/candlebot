use anyhow::Result;
use futures::prelude::*;
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;

use executor::pb::root as pb;
use pb::{Output, Interrupt};
use pb::executor_client::ExecutorClient;

#[tokio::main]
async fn main() -> Result<()> {
    let mut client = ExecutorClient::connect("http://localhost:5000").await?;

    let (tx, rx) = mpsc::channel(15);

    tokio::spawn(async move {
        let task = async {
            tokio::signal::ctrl_c().await?;
            tx.send(Interrupt {}.into()).await?;
            Result::<_>::Ok(())
        };

        match task.await {
            Ok(_) => {}
            Err(err) => println!("Error: {err}")
        }
    });

    client.run(ReceiverStream::new(rx)).await?.into_inner()
        .for_each(|output| {
            match output {
                Ok(Output { data }) => print!("{data}"),
                Err(err) => println!("Error: {err}")
            }

            future::ready(())
        }).await;

    Ok(())
}
