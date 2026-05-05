#!/usr/bin/env python
"""
Database setup script - Creates PostgreSQL database and imports schema
"""
import psycopg2
from psycopg2 import sql
import os
import sys
from pathlib import Path

import sqlparse

BASE_DIR = Path(__file__).resolve().parent


def _database_config():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        from urllib.parse import unquote, urlparse

        parsed = urlparse(database_url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': str(parsed.port or '5432'),
            'user': unquote(parsed.username or 'postgres'),
            'password': unquote(parsed.password or ''),
            'dbname': unquote(parsed.path.lstrip('/')),
        }

    return {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': os.getenv('DATABASE_PORT', '5432'),
        'user': os.getenv('DATABASE_USER', 'postgres'),
        'password': os.getenv('DATABASE_PASSWORD', 'refresh132'),
        'dbname': os.getenv('DATABASE_NAME', 'faculty_scheduling'),
    }


PG_CONFIG = _database_config()
PG_HOST = PG_CONFIG['host']
PG_PORT = PG_CONFIG['port']
PG_USER = PG_CONFIG['user']
PG_PASSWORD = PG_CONFIG['password']
PG_DBNAME = PG_CONFIG['dbname']

# Connection to default 'postgres' database to create our database
try:
    print("Connecting to PostgreSQL server...")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database='postgres'  # Connect to default postgres database first
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DBNAME,))
    db_exists = cursor.fetchone()
    
    if not db_exists:
        print(f"Creating database '{PG_DBNAME}'...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(PG_DBNAME)))
        print(f"✓ Database '{PG_DBNAME}' created successfully")
    else:
        print(f"✓ Database '{PG_DBNAME}' already exists")
    
    cursor.close()
    conn.close()
    
    # Now connect to the new database and import schema
    print(f"\nConnecting to '{PG_DBNAME}' database...")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DBNAME
    )
    cursor = conn.cursor()
    
    # Read and execute the schema file
    schema_file = BASE_DIR / 'schema.sql'
    if schema_file.exists():
        print(f"Loading schema from {schema_file.name}...")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split the file safely so PL/pgSQL blocks are preserved.
        statements = sqlparse.split(schema_sql)
        statement_count = 0
        
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue

            try:
                cursor.execute(statement)
                statement_count += 1
            except psycopg2.Error as e:
                # Log error but continue with next statements.
                print(f"  Warning: {e}")
        
        conn.commit()
        print(f"✓ Executed {statement_count} SQL statements")
        print("✓ Schema imported successfully!")
    else:
        print(f"Warning: {schema_file.name} not found. Create tables manually or provide schema file.")
    
    cursor.close()
    conn.close()
    
    print("\n✓ Database setup complete!")
    print(f"  Host: {PG_HOST}")
    print(f"  Port: {PG_PORT}")
    print(f"  Database: {PG_DBNAME}")
    print(f"  User: {PG_USER}")

except psycopg2.OperationalError as e:
    print(f"✗ Connection error: {e}")
    print("\nTroubleshooting:")
    print("1. Verify PostgreSQL server is running")
    print(f"2. Check host: {PG_HOST}, port: {PG_PORT}")
    print(f"3. Verify credentials: {PG_USER}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
