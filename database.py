from orator import DatabaseManager
config = {
    'mysql': {
        'driver': 'mysql',
        'host': 'niander-db1.ccpvcviiepyb.us-east-1.rds.amazonaws.com',
        'database': 'niander',
        'user': 'admin',
        'password': '5RZh12r512ca',
        'prefix': '',
        'charset':'utf8mb4'
    }
}

db = DatabaseManager(config)