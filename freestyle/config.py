import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Sets up database type and path

# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'stats.db')
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:oraiapp.com@thebi.tryoratio.com:32777/postgres'

# Sets up migration repository for database (may need to be changed for postgresql)

SQLALCHEMY_MIGRATE_REPO ='postgresql://postgres:oraiapp.com@thebi.tryoratio.com:32777/db_repository'

# Adds significant overhead. If server is not running smoothly set to False

SQLALCHEMY_TRACK_MODIFICATIONS = True
