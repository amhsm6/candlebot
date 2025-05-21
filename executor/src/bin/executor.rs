use std::process::Stdio;
use async_stream::try_stream;
use anyhow::Error;
use futures::prelude::*;
use futures::stream::BoxStream;
use tokio::fs;
use tokio::sync::mpsc;
use tokio::process::Command;
use tokio_util::io::ReaderStream;
use tokio_util::sync::PollSender;
use tokio_stream::wrappers::ReceiverStream;
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
    type RunStream = ReceiverStream<Result<Output, Status>>;

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
        let mut interrupt_s = request.into_inner();

        let mut child = Command::new("python3")
            .arg("main.py")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()?;

        let pid = child.id().ok_or(Status::unknown("Child does not have pid"))?;
        let stdout_s = ReaderStream::new(child.stdout.take().ok_or(Status::unknown("Process does not have stdout"))?);
        let stderr_s = ReaderStream::new(child.stderr.take().ok_or(Status::unknown("Process does not have stderr"))?);

        let (tx, rx) = mpsc::channel(15);

        let mut tx2 = tx.clone();
        tokio::spawn(async move {
            match interrupt_s.next().await? {
                Ok(_) => {}
                Err(err) => {
                    let err = Status::from_error(Box::new(err));
                    tx2.send(Err(err)).await
                        .unwrap_or_else(|_| println!("Warn: Process has already finished"));

                    return None;
                }
            }

            println!("Info: Interrupting...");

            match signal::kill(Pid::from_raw(pid as i32), Signal::SIGINT) {
                Ok(_) => {}
                Err(err) => {
                    let err = Status::from_error(Box::new(err));
                    tx2.send(Err(err)).await
                        .unwrap_or_else(|_| println!("Warn: Process has already finished"));

                    return None;
                }
            }

            let status = match child.wait().await {
                Ok(status) => status,
                Err(err) => {
                    tx2.send(Err(err.into())).await
                        .unwrap_or_else(|_| println!("Warn: Process has already finished"));

                    return None;
                }
            };

            println!("Info: Interrupted successfully...");

            println!("Info: Process exited with status {status}");
            match tx2.send(Ok(Output { data: format!("Process exited with status {status}") })).await {
                Ok(_) => {}
                Err(err) => {
                    println!("Warn: Process has already finished");
                    return None;
                }
            }

            Some(())
        });

        tokio::spawn(async move {
            stream::select(stdout_s, stderr_s)
                .map_err(Status::from)
                .and_then(|bytes| {
                    future::ready(
                        String::from_utf8(bytes.to_vec())
                            .map(|data| Output { data })
                            .map_err(|err| Status::from_error(Box::new(err)))
                    )
                })
                .map(Ok)
                .forward(PollSender::new(tx)).await.unwrap();
        });

        Ok(ReceiverStream::new(rx).into())
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
