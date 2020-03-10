from argparse import ArgumentParser

parser = ArgumentParser(description='...')

group = parser.add_argument_group('Download Configs')

group.add_argument('-i', '--mes-inicial', dest='start_year',
                   default=DEFAULT_START_YEAR,
                   choices=list(range(DEFAULT_START_YEAR,
                                      DEFAULT_END_YEAR)),
                   type=int, help='Select the first year of the data.')
                   
group.add_argument('-i', '--mes-final', dest='start_year',
                   default=DEFAULT_START_YEAR,
                   choices=list(range(DEFAULT_START_YEAR,
                                      DEFAULT_END_YEAR)),
                   type=int, help='Select the first year of the data.')

group.add_argument('-ey', '--end-year', dest='end_year',
                   default=DEFAULT_END_YEAR,
                   choices=list(range(DEFAULT_START_YEAR,
                                      DEFAULT_END_YEAR)),
                   type=int, help='Select the last year of the data.')

group = parser.add_argument_group('Tesseract Configs')

# group.add_argument('-a', '--agent', dest='agent',
#                    choices=['random'], default=DEFAULT_AGENT, type=str,
#                    help="""Select the type of the agent
#                    to run in the simulator""")
#
# group.add_argument('-A', '--actions', dest='actions',
#                    choices=['all', 'nowait'], default=DEFAULT_ACTIONS,
#                    type=str, help='Select the desired action vector')
#
# group.add_argument('-s', '--stock', dest='stock', default=DEFAULT_STOCK,
#                    type=list, help='Select the stock to make transactions')
#
# group.add_argument('-i', '--insider', dest='insider',
#                    default=DEFAULT_INSIDER, type=str, choices=['random'],
#                    help='Select the type of the insider')
#
# group = parser.add_argument_group('Brokerage Setup')
# group.add_argument('-f', '--fee', dest='fee',
#                    default=DEFAULT_FEE, type=int,
#                    help="""Select the ammount of the transactions fee""")

    args = parser.parse_args()
