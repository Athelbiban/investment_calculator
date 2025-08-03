from create_transactions_table import create_transactions_table
from create_cashflow_table import create_cashflow_table
from create_securities_mov_table import create_securities_movement


def main():

    create_transactions_table()
    create_cashflow_table()
    create_securities_movement()


if __name__ == '__main__':
    main()
