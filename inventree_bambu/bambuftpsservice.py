import ftplib
import ssl

from contextlib import contextmanager
from collections.abc import Generator

class ImplicitFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS subclass supporting implicit FTPS."""

    @property
    def sock(self):
        return self._sock

    @sock.setter
    def sock(self, value):
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value) # hostname verification? add , server_hostname=self.host

        self._sock = value

class BambuFTPSService:

    PORT = 990
    USERNAME = "bblp"
    TIMEOUT = 10

    def __init__(self, host: str, access_token: str):
        self.host = host
        self.access_token = access_token

    def test_connection(self) -> bool:
        with self._create_connection() as ftp:
            return ftp.voidcmd("NOOP").startswith("200")

    def list_directory(self, path: str = "/") -> list[str]:
        """Return the raw directory listing for a path."""
        with self._create_connection() as ftp:
            return ftp.nlst(path)

    def list_directory_details(self, path: str = "/") -> list[str]:
        """Return detailed LIST output for a path."""
        with self._create_connection() as ftp:
            entries: list[str] = []
            ftp.cwd(path)
            ftp.retrlines("LIST", entries.append)
            return entries

    def download_file(self, remote_path: str, local_path: str) -> None:
        """Download a printer file to a local filesystem path."""
        with self._create_connection() as ftp:
            with open(local_path, "wb") as destination:
                ftp.retrbinary(
                    f"RETR {remote_path}",
                    destination.write,
                )

    def upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload a local file to the printer."""
        with self._create_connection() as ftp:
            with open(local_path, "rb") as source:
                ftp.storbinary(
                    f"STOR {remote_path}",
                    source,
                )

    def delete_file(self, remote_path: str) -> None:
        """Delete a file on the printer."""
        with self._create_connection() as ftp:
            ftp.delete(remote_path)

    def create_directory(self, path: str) -> None:
        """Create a directory on the printer."""
        with self._create_connection() as ftp:
            ftp.mkd(path)

    def remove_directory(self, path: str) -> None:
        """Remove an empty directory on the printer."""
        with self._create_connection() as ftp:
            ftp.rmd(path)

    @contextmanager
    def _create_connection(self) -> Generator[ImplicitFTP_TLS, None, None]:
        
        ftp = ImplicitFTP_TLS(timeout=self.TIMEOUT)
        
        try:
            ftp.set_pasv(True)
            ftp.connect(host=self.host, port=self.PORT)
            ftp.login(self.USERNAME, self.access_token)
            ftp.prot_p()

            yield ftp

        finally:
            try:
                if ftp.sock is not None:
                    ftp.quit()
            except (Exception):
                ftp.close()