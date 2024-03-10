from src.services import UvicornService
from src.utils.logging import Logger
from src.query_engine import  QueryData, QueryDataLC


def main():

    query_engine = QueryData()
    service = UvicornService(query_engine)
    service.run()

if __name__ == "__main__":
    main()
