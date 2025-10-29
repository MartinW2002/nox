import train_model
import predict
import datetime
import elia 
from datetime import timezone

def main():
    print("What do you want to do?")
    print("1. Train a model")
    print("2. Predict a price")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        outfile = input("Enter output file name for the model: ").strip()
        train_model.train_model(outfile)

    elif choice == "2":
        modelfile = input("Enter model file to load: ").strip()
        print("Choose prediction time:")
        print("1. Next quarter")
        print("2. Custom time (HH:MM)")

        time_choice = input("Enter your choice (1 or 2): ").strip()

        target_time = elia.next_quarter()
        if time_choice == "1":
            target_time = elia.next_quarter()
        elif time_choice == "2":
            custom_time_str = input("Enter the custom time (HH:MM): ").strip()
            hour, minute = map(int, custom_time_str.split(":"))
            today = datetime.date.today()
            target_time = datetime.datetime(today.year, today.month, today.day, hour, minute, tzinfo=timezone.utc)
        else:
            print("Invalid option.")
            return

        print(predict.predict(modelfile, target_time))
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()