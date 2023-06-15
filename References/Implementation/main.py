from Client import Client
import settings

def main():
        client = Client(settings.measure_rate, settings.save_to_file, settings.save_to_database, settings.use_random_data)
        client.main_loop()

if __name__ == "__main__":
    main()
