from CLI.cli_core import CLICore

def main():
    manager = CLICore()
    manager._create_organization(
        "CoolTestCompany", "contact@cc.com", "Russia"
    )
    manager._create_user(
        "bob", "BobSecure123", "Bob", "Smith", "USA", "English"
    )


if __name__ == "__main__":
    main()