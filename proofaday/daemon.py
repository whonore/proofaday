import concurrent.futures as futures
import logging
import socketserver
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


class ProofHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data, sock = self.request
        msg = Message.decode(data)
        server: ProofServer = self.server  # type: ignore[assignment]
        logger = server.logger
        logger.info("Received %s from (%s, %d)", msg.action, *self.client_address)

        if msg.action is Action.CHECK:
            reply = ""
        elif msg.action is Action.REQUEST:
            logger.info("Fetching %s", msg.data)
            proof = server.fetch_proof(msg.data)
            reply = proof if proof is not None else ""
        elif msg.action is Action.RANDOM:
            logger.info("Dequeuing proof")
            reply = server.queue.get()
        elif msg.action is Action.KILL:
            logger.info("Shutting down server")
            sock.sendto(b"", self.client_address)
            server.shutdown()
            logger.info("Server shutdown")
            return
        sock.sendto(reply.encode(), self.client_address)


class ProofServer(socketserver.ThreadingUDPServer):
    proof_timeout = 1
    daemon_threads = True

    max_log_bytes = 1024 * 1024
    max_requests = 5

    def __init__(
        self,
        port: int,
        limit: int,
        nprefetch: int,
        debug: int,
        log_path: Path,
        **kwargs: Any
    ) -> None:
        super().__init__((consts.HOST, port), ProofHandler)
        level = {0: logging.NOTSET, 1: logging.INFO}.get(debug, logging.DEBUG)
        self.logger = self.init_logger(level, log_path)
        self.queue: Queue[str] = Queue(maxsize=nprefetch)
        self.limit = limit
        threading.Thread(
            target=self.fetch_proofs, daemon=True, name="ServerLoop"
        ).start()

    def init_logger(self, level: int, path: Path) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        if level != logging.NOTSET:
            handler: logging.Handler = RotatingFileHandler(
                path / "proofaday.log",
                maxBytes=ProofServer.max_log_bytes,
                backupCount=1,
                encoding="utf8",
            )
        else:
            handler = logging.NullHandler()
        handler.setFormatter(logging.Formatter("%(threadName)s: %(message)s"))
        logger.addHandler(handler)
        return logger

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
            max_workers=ProofServer.max_requests, thread_name_prefix="Fetcher"
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


def serve(**kwargs: Any) -> None:
    with ProofServer(**kwargs) as server:
        server.serve_forever()


def main() -> None:
    def pos(arg: str) -> int:
        if int(arg) <= 0:
            raise ValueError("not positive")
        return int(arg)

    parser = ArgumentParser(description="Fetch a random proof")
    parser.add_argument("-d", "--debug", action="count", default=0)
    parser.add_argument(
        "--log-path", dest="log_path", type=Path, default=consts.LOG_PATH
    )
    parser.add_argument("-l", "--limit", type=pos, default=None)
    parser.add_argument(
        "-n",
        "--num-prefetch-proofs",
        dest="nprefetch",
        type=pos,
        default=consts.NPREFETCH,
    )
    parser.add_argument("-p", "--port", type=int, default=consts.PORT)
    parser.add_argument("-k", "--kill-server", dest="kill", action="store_true")
    args = parser.parse_args()

    with DaemonContext():
        serve(**vars(args))


if __name__ == "__main__":
    main()
