use std::process::Stdio;
use async_stream::try_stream;
use anyhow::Error;
use futures::prelude::*;
use futures::stream::BoxStream;
use tokio::fs;
use tokio::process::Command;
use tokio_util::io::ReaderStream;
use tonic::{Request, Response, Streaming, Status};
use tonic::transport::Server;
use nix::unistd::Pid;
use nix::sys::signal;
use nix::sys::signal::Signal;

use executor::pb::root as pb;
use pb::{Source, Interrupt, FileLoaded, Output};
use pb::executor_server::ExecutorServer;

struct Executor;

#[tonic::async_trait]
impl pb::executor_server::Executor for Executor {
    type LoadStream = BoxStream<'static, Result<FileLoaded, Status>>;
    type RunStream = BoxStream<'static, Result<Output, Status>>;

    async fn load(&self, request: Request<Source>) -> Result<Response<Self::LoadStream>, Status> {
        let Source { files } = request.into_inner();

        println!("Execute: Load");

        let s = try_stream! {
            for file in files {
                println!("Loading {}", file.name);
                fs::write(&file.name, file.data).await
                    .inspect_err(|err| println!("Error: {err}"))?;

                yield FileLoaded { name: file.name };
            }

            println!("Done: Load");
        };

        Ok(s.boxed().into())
    }

    async fn run(&self, request: Request<Streaming<Interrupt>>) -> Result<Response<Self::RunStream>, Status> {
        let interrupt_s = request.into_inner();

        let mut child = Command::new("python3")
            .arg("main.py")
            .stdout(Stdio::piped())
            .spawn()?;

        //FIXME: mpsc
        tokio::spawn(async move {
            interrupt_s.next().await?;

            signal::kill(Pid::from_raw(child.id() as i32), Signal::SIGINT);
        });


        let s = ReaderStream::new(child.stdout.take().ok_or(Status::unknown("Process does not have output"))?)
            .map_err(Status::from)
            .and_then(|bytes| async move {
                String::from_utf8(bytes.to_vec())
                    .map(|data| Output { data })
                    .map_err(|err| Status::from_error(Box::new(err)))
            });

        Ok(s.boxed().into())
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
