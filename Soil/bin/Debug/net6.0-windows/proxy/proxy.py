import asyncio
import shutil
import aiohttp
from aiohttp import web
import ssl
import os
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding
import argparse
import platform
import datetime

parser = argparse.ArgumentParser(
    prog="Soil Proxy",
    description="Redirects requests going to Mihoyo to a server specified by Soil Launcher",
    epilog="what the fuck is an epilog",
)
parser.add_argument("-ho", "--host")
args = parser.parse_args()
SERVER = args.host
REDIRECT_MORE = False

# Create a proxy handler
class ProxyHandler:
    async def handle_request(self, request):
        global REDIRECT_MORE

        uri = str(request.rel_url)

        if REDIRECT_MORE:
            if any(
                domain in uri
                for domain in [
                    "hoyoverse.com",
                    "mihoyo.com",
                    "yuanshen.com",
                    "starrails.com",
                    "bhsr.com",
                    "bh3.com",
                    "honkaiimpact3.com",
                    "zenlesszonezero.com",
                ]
            ):
                if request.method == "CONNECT":
                    return web.Response(
                        headers={"DecryptEndpoint": "Created"}, status=200
                    )

                new_uri = f"{SERVER}{uri}"
                request.match_info["path"] = new_uri
        else:
            if any(
                domain in uri
                for domain in ["hoyoverse.com", "mihoyo.com", "yuanshen.com"]
            ):
                if request.method == "CONNECT":
                    return web.Response(
                        headers={"DecryptEndpoint": "Created"}, status=200
                    )

                new_uri = f"{SERVER}{uri}"
                request.match_info["path"] = new_uri

        return (
            await aiohttp.ClientSession().request(
                request.method, request.match_info["path"], headers=request.headers
            )
        ).web_response

    async def handle_response(self, request, response):
        return response

    async def should_intercept(self, request):
        uri = str(request.rel_url)
        return any(
            domain in uri
            for domain in [
                "hoyoverse.com",
                "mihoyo.com",
                "yuanshen.com",
                "starrails.com",
                "bhsr.com",
                "bh3.com",
                "honkaiimpact3.com",
                "zenlesszonezero.com",
            ]
        )


# Set the proxy address
async def set_proxy_addr(addr):
    global SERVER
    SERVER = addr
    print(f"Set server to {SERVER}")


# Set the redirect_more flag
async def set_redirect_more():
    global REDIRECT_MORE
    REDIRECT_MORE = True


# Create the proxy server
async def create_proxy(proxy_port, certificate_path):
    app = web.Application()
    app.router.add_route("*", "/{path:.*}", ProxyHandler)
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    cert_path = Path(certificate_path)
    pk_path = cert_path / "private.key"
    ca_path = cert_path / "cert.crt"

    if not pk_path.exists() or not ca_path.exists():
        print("Private key or CA certificate not found. Generating them...")
        generate_ca_files(cert_path)

    ssl_context.load_cert_chain(ca_path, pk_path)
    runner = web.AppRunner(app, ssl_context=ssl_context)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", proxy_port)
    await site.start()


# Connect to the local HTTP(S) proxy server
def connect_to_proxy(proxy_port):
    os.system("set http_proxy=http://localhost:"+proxy_port)
    os.system("set https_proxy=https://localhost:"+proxy_port)
    print(f"Connected to the proxy at 127.0.0.1:{proxy_port}")


# Disconnect from the local HTTP(S) proxy server
def disconnect_from_proxy():
    os.system("unset http_proxy=http://localhost:8080")
    os.system("unset https_proxy=https://localhost:8080")
    print("Disconnected from the proxy")


# Generate CA files (Certificate and Private Key)
def generate_ca_files(path):
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    # Serialize and save the private key
    with open("ca_private_key.pem", "wb") as key_file:
        key_file.write(
            private_key.private_bytes(
                Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

    # Create a self-signed CA certificate
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "MADRID SUR 💀😈"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Soil"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, "Soil\'s ugly CA cert."),
        ]
    )

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            datetime.datetime.utcnow()
            + datetime.timedelta(days=3650)  # Valid for 10 years
        )
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    # Serialize and save the CA certificate
    with open("ca_certificate.pem", "wb") as cert_file:
        cert_file.write(ca_cert.public_bytes(Encoding.PEM))


def install_ca_files(cert_path):
    if not os.path.exists(cert_path):
        os.mkdir(cert_path)
        if os.path.exists("./private.key") and os.path.exists("./cert.crt"):
            shutil.move("./private.key", cert_path)
            shutil.move("./cert.crt", cert_path)
            print("Installed certificate")
        else:
            generate_ca_files(cert_path)
            print("Generated certificate and installed")

# Main function
async def main():
    proxy_port = 8080
    certificate_path = (
        os.getcwd()
    )

    # Generate the CA certificate and private key if they don't exist
    cert_path = Path(certificate_path)
    pk_path = cert_path / "private.key"
    ca_path = cert_path / "cert.crt"

    if not pk_path.exists() or not ca_path.exists():
        print("Private key or CA certificate not found. Generating them...")
        generate_ca_files(cert_path)

    # Create the proxy server
    await create_proxy(proxy_port, certificate_path)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    if not os.path.exists("/usr/local/share/ca-certificates"):
        os.mkdir("/usr/local/share/ca-certificates")
        if not os.path.exists("/usr/local/share/ca-certificates/private.key") and not os.path.exists("/usr/local/share/ca-certificates/cert.crt"):
            generate_ca_files("/usr/local/share/ca-certificates/") 
    loop.run_forever()
