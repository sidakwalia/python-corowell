from orator import DatabaseManager
config = {
    'mysql': {
        'driver': 'mysql',
        'host': 'corowell-db.cr2idef2yduw.us-east-2.rds.amazonaws.com',
        'database': 'sys',
        'user': 'admin',
        'password': 'y!E7P^Q6J4inder',
        'prefix': '',
        'charset':'utf8mb4'
    }
}

db = DatabaseManager(config)