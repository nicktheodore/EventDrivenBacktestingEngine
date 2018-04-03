from Strategies.MovingAverageCrossoverStrategy import main
import datetime

fake_json_data = {
    'csv_dir': '~/AlgorithmicTradingProject/Symbols/',  # Absolute path to the CSV data
    'symbol_list': ['AAPL'],
    'initial_capital': 100000.0,
    'heartbeat': 0.0,
    'start_date': datetime.datetime(1990, 1, 1, 0, 0, 0),
    'end_date': datetime.datetime(2001, 1, 1, 0, 0, 0)
}

if __name__ == "__main__":
    main(**fake_json_data)