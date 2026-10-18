#!/usr/bin/env python3
"""
Generate self-signed development/staging TLS certificates for PrepMaster Nginx.
Production deployments should replace these with Cloudflare Origin CA or Let's Encrypt certificates.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import ipaddress

SSL_DIR = Path(__file__).resolve().parent
CERT_FILE = SSL_DIR / "prepmaster.crt"
KEY_FILE = SSL_DIR / "prepmaster.key"

def generate_certificates():
    print(f"Generating 2048-bit RSA Private Key for PrepMaster...")
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "TR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Istanbul"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Maslak"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PrepMaster Dev CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "prepmaster.local"),
    ])

    san_list = [
        x509.DNSName("localhost"),
        x509.DNSName("prepmaster.local"),
        x509.DNSName("prepmaster.edu.tr"),
        x509.DNSName("*.prepmaster.local"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv4Address("10.247.49.48")),
    ]

    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    # Write private key
    with open(KEY_FILE, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    print(f"Saved private key to: {KEY_FILE}")

    # Write certificate
    with open(CERT_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f"Saved certificate to: {CERT_FILE}")

if __name__ == "__main__":
    generate_certificates()
