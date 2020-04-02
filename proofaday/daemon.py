import concurrent.futures as futures
import logging
import os
import signal
import socketserver
import sys
import threading
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler
from pathlib import Path
from queue import Queue
from typing import Any, NoReturn, Optional, Set

import requests
from bs4 import BeautifulSoup as BS  # type: ignore[import]
from daemon import DaemonContext  # type: ignore[import]
from requests import exceptions as exs

import proofaday.constants as consts
from proofaday.message import Action, Message
from proofaday.proof import InvalidProofException, Proof
from proofaday.status import Status


class ServerError(Exception):
    pass


class ProofHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data, sock = self.request
        msg = Message.decode(data)
        server: ProofServer = self.server  # type: ignore[assignment]
        logger = server.logger
        logger.info("Received %s from (%s, %d)", msg.action, *self.client_address)

        if msg.action is Action.REQUEST:
            logger.info("Fetching %s", msg.data)
            proof = server.fetch_proof(msg.data)
            reply = proof if proof is not None else ""
        elif msg.action is Action.RANDOM:
            logger.info("Dequeuing proof")
            reply = server.queue.get()
        sock.sendto(reply.encode(), self.client_address)


class ProofServer(socketserver.ThreadingUDPServer):
    daemon_threads = True
    proof_timeout = 1
    max_log_bytes = 1024 * 1024
    max_threads = 5

    def __init__(
        self,
        port: int,
        limit: int,
        nprefetch: int,
        debug: int,
        log_path: Path,
        status_path: Path,
        **kwargs: Any,
    ) -> None:
        super().__init__((consts.HOST, port), ProofHandler)
        level = {0: logging.NOTSET, 1: logging.INFO}.get(debug, logging.DEBUG)
        self.logger = self.init_logger(level, log_path)
        self.queue: Queue[str] = Queue(maxsize=nprefetch)
        self.limit = limit
        threading.Thread(
            target=self.fetch_proofs, daemon=True, name="ServerLoop"
        ).start()

        self.pid = os.getpid()
        self.status = Status(status_path)
        host, port = self.server_address
        if not self.status.write(pid=self.pid, host=host, port=port):
            self.status.remove()
            raise ServerError("Failed to write status file.")

    def init_logger(self, level: int, path: Path) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        if level != logging.NOTSET:
            handler: logging.Handler = RotatingFileHandler(
                path / consts.LOG_FILE,
                maxBytes=ProofServer.max_log_bytes,
                backupCount=1,
                encoding="utf8",
            )
        else:
            handler = logging.NullHandler()
        handler.setFormatter(logging.Formatter("%(threadName)s: %(message)s"))
        logger.addHandler(handler)
        return logger

    def server_close(self) -> None:
        super().server_close()
        status = self.status.read()
        if status is not None and status["pid"] == self.pid:
            self.status.remove()

    def fetch_proof(self, name: Optional[str] = None) -> Optional[str]:
        if name is None:
            name = consts.RANDOM
        url = consts.URL + name

        try:
            data = requests.get(url, timeout=ProofServer.proof_timeout).text
            html = BS(data, "html.parser")
            proof = Proof(html)
            self.logger.debug(repr(proof))
            return str(proof)
        except (ConnectionResetError, exs.Timeout):
            pass
        except InvalidProofException as e:
            self.logger.exception("Invalid proof: %s", str(e))
        except Exception as e:
            self.logger.exception(
                "Unexpected exception while fetching a proof: %s", str(e)
            )
        return None

    def enqueue_proof(self, proof: str) -> None:
        if self.limit is None or len(proof.split("\n")) <= self.limit:
            self.queue.put(proof)

    def fetch_proofs(self) -> NoReturn:
        with futures.ThreadPoolExecutor(
            max_workers=ProofServer.max_threads, thread_name_prefix="Fetcher"
        ) as pool:
            jobs: Set[futures.Future[Optional[str]]] = set()
            while True:
                njobs = self.queue.maxsize - self.queue.qsize() - len(jobs)
                if len(jobs) == 0:
                    njobs = max(njobs, 1)
                jobs |= {pool.submit(self.fetch_proof) for _ in range(njobs)}
                done, jobs = futures.wait(jobs, return_when=futures.FIRST_COMPLETED)

                for job in done:
                    proof = job.result()
                    if proof is not None:
                        self.enqueue_proof(proof)


def spawn(**kwargs: Any) -> None:
    with DaemonContext(stdout=sys.stdout, stderr=sys.stderr):
        # N.B. shutdown() must be called in a separate thread
        signal.signal(
            signal.SIGTERM,
            lambda signum, frame: threading.Thread(target=server.shutdown).start(),
        )
        with ProofServer(**kwargs) as server:
            server.serve_forever()


def main() -> None:
    def pos(arg: str) -> int:
        if int(arg) <= 0:
            raise ValueError("not positive")
        return int(arg)

    parser = ArgumentParser(description="Proofaday daemon")
    parser.add_argument("action", choices=["start", "stop", "restart"])
    parser.add_argument("-d", "--debug", action="count", default=0)
    parser.add_argument("--log-path", type=Path, default=consts.LOG_PATH)
    parser.add_argument("--status-path", type=Path, default=consts.STATUS_PATH)
    parser.add_argument("-l", "--limit", type=pos, default=None)
    parser.add_argument(
        "-n",
        "--num-prefetch-proofs",
        dest="nprefetch",
        type=pos,
        default=consts.NPREFETCH,
    )
    parser.add_argument("-p", "--port", type=int, default=0)
    args = parser.parse_args()

    status = Status(args.status_path).read()
    if args.action == "start":
        if status is not None:
            sys.exit("Daemon already started.")
        try:
            spawn(**vars(args))
        except ServerError as e:
            sys.exit(str(e))
    elif args.action == "stop":
        if status is None:
            sys.exit("Daemon not running.")
        os.kill(status["pid"], signal.SIGTERM)
        if not Status(args.status_path).wait(exist=False):
            sys.exit("Failed to stop daemon.")
    else:
        sys.exit(f"{args.action} is not yet supported.")


if __name__ == "__main__":
    main()
