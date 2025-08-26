from passwd.config_DB import DBNAME, USER, PASSWORD, PORT, HOST


def connect_attr() -> str:
    return (f'dbname={DBNAME} user={USER} password={PASSWORD} '
            f'port={PORT} host={HOST}')
