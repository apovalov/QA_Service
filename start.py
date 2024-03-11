from src.services import UvicornService
from src.query_engine import QueryData


def main():

    query_engine = QueryData()
    service = UvicornService(query_engine)
    service.run()

if __name__ == "__main__":
    main()
