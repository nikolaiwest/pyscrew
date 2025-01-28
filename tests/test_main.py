from pyscrew import PyScrew


def main():
    # Initialize PyScrew
    print("Initializing PyScrew...")
    screw = PyScrew()
    
    # Get the data directory
    print("\nAccessing data...")
    data_dir = screw.get_data_directory()
    print(f"Data directory: {data_dir}")
    
    # List available files
    print("\nListing available files:")
    files = screw.list_files()
    for file in files:
        print(f"- {file}")

if __name__ == "__main__":
    main()