try:
    from etl.load.load import load_data
except ImportError:
    from load.load import load_data

__all__ = ["load_data"]
