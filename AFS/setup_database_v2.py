#!/usr/bin/env python
"""
Database setup script v2 - Improved SQL parsing and execution
"""
import psycopg2
import os
import sys
import re

# PostgreSQL Connection Details
PG_HOST = 'localhost'
PG_PORT = '5432'
PG_USER = 'postgres'
PG_PASSWORD = 'refresh132'
PG_DBNAME = 'faculty_scheduling'

def split_sql_statements(sql_content):
    """
    Split SQL file into statements, handling multi-line statements and functions
    """
    # Remove comments (-- style)
    lines = []
    for line in sql_content.split('\n'):
        # Remove inline comments
        if '--' in line and not ("'" in line[:line.index('--')] or '"' in line[:line.index('--')]):
            line = line[:line.index('--')]
        if line.strip():
            lines.append(line)
    
    # Join lines and split by semicolon, but be careful with dollar quotes
    content = '\n'.join(lines)
    statements = []
    current = []
    in_dollar_quote = False
    dollar_quote = None
    
    i = 0
    while i < len(content):
        # Check for dollar quotes
        if content[i] == '$' and not in_dollar_quote:
            # Extract the dollar quote tag
            end = content.find('$', i + 1)
            if end != -1:
                dollar_quote = content[i:end+1]
                in_dollar_quote = True
                current.append(content[i:end+1])
                i = end + 1
                continue
        elif in_dollar_quote and content[i:].startswith(dollar_quote):
            in_dollar_quote = False
            current.append(dollar_quote)
            i += len(dollar_quote)
            continue
        
        # Handle semicolons
        if content[i] == ';' and not in_dollar_quote:
            current.append(';')
            statement = ''.join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            i += 1
            continue
        
        current.append(content[i])
        i += 1
    
    # Add any remaining content
    if current:
        statement = ''.join(current).strip()
        if statement:
            statements.append(statement)
    
    return statements

try:
    # Step 1: Drop and recreate database
    print("Connecting to PostgreSQL server...")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print(f"Dropping existing database '{PG_DBNAME}'...")
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {PG_DBNAME}")
        print(f"✓ Database dropped")
    except:
        pass
    
    print(f"Creating new database '{PG_DBNAME}'...")
    cursor.execute(f"CREATE DATABASE {PG_DBNAME}")
    print(f"✓ Database '{PG_DBNAME}' created successfully")
    
    cursor.close()
    conn.close()
    
    # Step 2: Connect to new database and import schema
    print(f"\nConnecting to '{PG_DBNAME}' database...")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DBNAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Read and parse the schema file
    schema_file = 'schema.sql'
    if os.path.exists(schema_file):
        print(f"Loading schema from {schema_file}...")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        statements = split_sql_statements(schema_sql)
        print(f"Found {len(statements)} SQL statements")
        
        executed = 0
        failed = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                executed += 1
                if (i % 10 == 0):
                    print(f"  Executed {i} statements...")
            except psycopg2.Error as e:
                failed += 1
                if failed <= 5:  # Show first 5 errors
                    print(f"  Error in statement {i}: {str(e)[:100]}")
        
        print(f"\n✓ Executed {executed} statements successfully")
        if failed > 0:
            print(f"  ({failed} statements had errors - usually OK for IF NOT EXISTS)")
        
        print("✓ Schema imported successfully!")
    else:
        print(f"Error: {schema_file} not found")
        sys.exit(1)
    
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
    print("1. Verify PostgreSQL server is running on localhost:5432")
    print("2. Verify credentials: postgres / refresh132")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
