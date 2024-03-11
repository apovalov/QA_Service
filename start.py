from src.services import UvicornService, TG_Service
from src.query_engine import QueryData


def main():

    query_engine = QueryData()
    # service = TG_Service(query_engine)
    service = UvicornService(query_engine)
    # service = ST_Service(query_engine)
    service.run()

if __name__ == "__main__":
    main()
