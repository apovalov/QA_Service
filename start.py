from src.services import UvicornService

def run_uvicorn_service():
    service = UvicornService()
    service.run()

def run_other_service():
    pass

def main():

    run_uvicorn_service()
    # run_other_service()

if __name__ == "__main__":
    main()
