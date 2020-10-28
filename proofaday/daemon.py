import concurrent.futures as futures
import logging
import os
import signal
import socketserver
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from queue import Queue
from typing import Any, NoReturn, Optional, Set

import requests
from bs4 import BeautifulSoup as BS
from daemon import DaemonContext
from requests import exceptions as exs
from typing_extensions import Final

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
    proof_timeout: Final = 1
    max_log_bytes: Final = 1024 * 1024
    max_threads: Final = 5

    def __init__(
        self,
        port: int,
        line_limit: int,
        nprefetch: int,
        debug: int,
        log_path: Path,
        status: Status,
    ) -> None:
        self.status = status
        if not self.status.touch():
            raise ServerError("Status file already exists or couldn't be created.")

        super().__init__((consts.HOST, port), ProofHandler)
        level = {0: logging.NOTSET, 1: logging.INFO}.get(debug, logging.DEBUG)
        self.logger = self.init_logger(level, log_path)
        self.queue: Queue[str] = Queue(maxsize=nprefetch)
        self.limit = line_limit if line_limit > 0 else None

        host, port = self.server_address
        if not self.status.write(pid=os.getpid(), host=host, port=port):
            self.status.remove()
            raise ServerError("Failed to write status file.")

        threading.Thread(
            target=self.fetch_proofs,
            daemon=True,
            name="ServerLoop",
        ).start()

    def init_logger(self, level: int, path: Path) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        if level != logging.NOTSET:
            path.mkdir(parents=True, exist_ok=True)
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
        if status is not None and status["pid"] == os.getpid():
            self.status.remove()

    def fetch_proof(self, name: str = consts.RANDOM) -> Optional[str]:
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
                "Unexpected exception while fetching a proof: %s",
                str(e),
            )
        return None

    def enqueue_proof(self, proof: str) -> None:
        if self.limit is None or len(proof.split("\n")) <= self.limit:
            self.queue.put(proof)

    def fetch_proofs(self) -> NoReturn:
        with futures.ThreadPoolExecutor(
            max_workers=ProofServer.max_threads,
            thread_name_prefix="Fetcher",
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
        try:
            with ProofServer(**kwargs) as server:
                server.serve_forever()
        except ServerError as e:
            sys.exit(str(e))
