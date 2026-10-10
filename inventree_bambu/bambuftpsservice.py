import ftplib
import ssl

from datetime import datetime
from contextlib import contextmanager
from collections.abc import Generator

class ImplicitFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS subclass supporting implicit FTPS with TLS session reuse."""

    @property
    def sock(self):
        return self._sock

    @sock.setter
    def sock(self, value):
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value)

        self._sock = value

    def ntransfercmd(self, cmd, rest=None):
        conn, size = super(ftplib.FTP_TLS, self).ntransfercmd(cmd, rest)

        control_sock = self.sock

        if control_sock is None:
            raise RuntimeError("FTPS control socket is not connected")

        conn = self.context.wrap_socket(
            conn,
            #server_hostname=self.host,
            session=control_sock.session,
        )

        return conn, size

class BambuFTPSPathError(Exception):
    """Raised when a requested printer filesystem path is invalid."""

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

    def list_directory(self, path: str = "/",) -> list[dict[str, str | bool]]:
        with self._create_connection() as ftp:
            try:
                ftp.cwd(path)
            except ftplib.error_perm as e:
                raise BambuFTPSPathError(path) from e

            lines: list[str] = []
            try:
                ftp.retrlines("LIST", lines.append)
            except ftplib.error_perm:
                return []  # empty directory on some servers

            result = []
            for line in lines:
                # "drwxr-xr-x 2 root root 4096 Oct 08 21:00 cache"
                parts = line.split(maxsplit=8)
                if len(parts) < 9:
                    continue
                name = parts[8]
                if name in (".", ".."):
                    continue
                result.append({
                    "name": name,
                    "is_directory": parts[0].startswith("d"),
                    "size": int(parts[4]) if parts[4].isdigit() else None,
                    "modified": self._parse_list_date(parts[5], parts[6], parts[7])
                })
            return result

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

    def _parse_list_date(self, month: str, day: str, time_or_year: str) -> str | None:
        try:
            if ":" in time_or_year:
                now = datetime.now()
                dt = datetime.strptime(f"{month} {day} {now.year} {time_or_year}", "%b %d %Y %H:%M")
                # No year given means "within the last ~6 months", so a future date belongs to last year
                if dt > now:
                    dt = dt.replace(year=now.year - 1)
            else:
                dt = datetime.strptime(f"{month} {day} {time_or_year}", "%b %d %Y")
            return dt.isoformat()
        except ValueError:
            return None