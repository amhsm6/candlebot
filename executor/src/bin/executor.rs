use std::pin::Pin;
use async_stream::{stream, try_stream};
use anyhow::Error;
use futures::prelude::*;
use futures::Stream;
use tonic::{Request, Response, Streaming, Status};
use tonic::transport::Server;

use executor::pb::root as pb;
use pb::{Source, Interrupt, FileLoaded, Output};
use pb::executor_server::ExecutorServer;

struct Executor;

#[tonic::async_trait]
impl pb::executor_server::Executor for Executor {
    type LoadStream = Pin<Box<dyn Stream<Item = Result<FileLoaded, Status>> + Send + 'static>>;
    type RunStream = Pin<Box<dyn Stream<Item = Result<Output, Status>> + Send + 'static>>;

    async fn load(&self, request: Request<Source>) -> Result<Response<Self::LoadStream>, Status> {
        let src = request.into_inner();

        println!("{src:?}");

        let resp: Self::LoadStream = Box::pin(try_stream! {
            yield FileLoaded{ name: "a".to_string() };
            yield FileLoaded{ name: "b".to_string() };
            yield FileLoaded{ name: "c".to_string() };
        });

        Ok(resp.into())
    }

    async fn run(&self, request: Request<Streaming<Interrupt>>) -> Result<Response<Self::RunStream>, Status> {
        todo!();
    }
}

async fn start() -> Result<(), Error> {
    println!("Server started on port 5000");

    Server::builder()
        .add_service(ExecutorServer::new(Executor))
        .serve("0.0.0.0:5000".parse()?)
        .await?;

    Ok(())
}

#[tokio::main]
async fn main() {
    match start().await {
        Ok(()) => unreachable!(),
        Err(e) => println!("Error: {e}")
    }
}
