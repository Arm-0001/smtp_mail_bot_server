import requests
import json
import random
import string
import threading
import time
from colorama import Fore, Style
import concurrent.futures
from faker import Faker
from fake_useragent import UserAgent

# Debug mode variable
debug_mode = False

# Statistics
total_attempts = 0
total_wins = 0
total_fails = 0
start_time = time.time()

# Lock for thread safety
lock = threading.Lock()

# Faker instance for generating fake data
fake = Faker()
# UserAgent instance for generating random user agents
ua = UserAgent()

def generate_email():
    email_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{email_prefix}@pandabuyspreads.com"
    if debug_mode:
        print(Fore.CYAN + f"Generated email: {email}" + Style.RESET_ALL)
    return email

def generate_name():
    name = fake.name()
    if debug_mode:
        print(Fore.CYAN + f"Generated name: {name}" + Style.RESET_ALL)
    return name

def generate_user_agent():
    user_agent = ua.random
    if debug_mode:
        print(Fore.CYAN + f"Generated user agent: {user_agent}" + Style.RESET_ALL)
    return user_agent

def visit_game(session):
    url = "https://game.scratcher.io/se-royal-spin/visit"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en;q=0.6",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": generate_user_agent(),
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
    }
    body = {"s_source": None}
    if debug_mode:
        print(Fore.CYAN + f"Visiting game with URL: {url} and body: {body}" + Style.RESET_ALL)
    response = session.post(url, headers=headers, json=body)
    if debug_mode:
        print(Fore.CYAN + f"Visit game response status: {response.status_code}" + Style.RESET_ALL)
    if response.status_code == 200:
        if debug_mode:
            print(Fore.GREEN + "Visit game response successful." + Style.RESET_ALL)
        return response.json()
    else:
        if debug_mode:
            print(Fore.RED + "Error visiting game:" + response.text + Style.RESET_ALL)
        return None

def register_game(session, email, name, token):
    url = "https://game.scratcher.io/se-royal-spin/register"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en;q=0.6",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": generate_user_agent(),
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
    }
    body = {
        "token": token,
        "full_name": name,
        "email": email,
        "cb_competition_terms_and_conditions": "1",
        "cb_royal_erbjudanden": "1",
        "__qp_": {},
        "s_source": None
    }
    if debug_mode:
        print(Fore.CYAN + f"Registering game with URL: {url}, email: {email}, and body: {body}" + Style.RESET_ALL)
    response = session.post(url, headers=headers, json=body)
    if debug_mode:
        print(Fore.CYAN + f"Register game response status: {response.status_code}" + Style.RESET_ALL)
    if response.status_code == 200:
        if debug_mode:
            print(Fore.GREEN + "Register game response successful." + Style.RESET_ALL)
        return response.json()
    else:
        if debug_mode:
            print(Fore.RED + "Error registering game:" + response.text + Style.RESET_ALL)
        return None

def run_game(session, token, login_token):
    url = "https://game.scratcher.io/se-royal-spin/finish"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en;q=0.6",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": generate_user_agent(),
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "x-scratcher-login": login_token,
    }
    playing_time = random.randint(5000, 15000)  # Random playing time between 5 and 15 seconds
    body = {
        "data": {"playing_time": playing_time},
        "token": token,
        "s_source": None
    }
    if debug_mode:
        print(Fore.CYAN + f"Running game with URL: {url}, token: {token}, and body: {body}" + Style.RESET_ALL)
    response = session.post(url, headers=headers, json=body)
    if debug_mode:
        print(Fore.CYAN + f"Run game response status: {response.status_code}" + Style.RESET_ALL)
    if response.status_code == 200:
        if debug_mode:
            print(Fore.GREEN + "Run game response successful." + Style.RESET_ALL)
        return response.json()
    else:
        if debug_mode:
            print(Fore.RED + "Error running game:" + response.text + Style.RESET_ALL)
        return None

def log_winner(data):
    if debug_mode:
        print(Fore.YELLOW + f"Logging winner data: {data}" + Style.RESET_ALL)
    with open("winners_log.txt", "a") as log_file:
        log_file.write(json.dumps(data) + "\n")

def play_game():
    global total_attempts, total_wins, total_fails
    session = requests.Session()

    # Step 1: Visit the game
    if debug_mode:
        print(Fore.MAGENTA + "Step 1: Visiting the game." + Style.RESET_ALL)
    visit_response = visit_game(session)
    if visit_response is None:
        with lock:
            total_fails += 1
        return

    # Extract the token from visit response
    token = visit_response.get("token")
    if not token:
        with lock:
            total_fails += 1
        return

    # Step 2: Generate an email and name, then register the game
    if debug_mode:
        print(Fore.MAGENTA + "Step 2: Generating email and name, then registering the game." + Style.RESET_ALL)
    email = generate_email()
    name = generate_name()
    registration_response = register_game(session, email, name, token)
    if registration_response is None:
        with lock:
            total_fails += 1
        return

    # Extract the login token from registration response
    login_token = registration_response.get("login_token")
    if not login_token:
        with lock:
            total_fails += 1
        return

    # Step 3: Run the game using the tokens from registration
    if debug_mode:
        print(Fore.MAGENTA + "Step 3: Running the game." + Style.RESET_ALL)
    game_result = run_game(session, token, login_token)
    if game_result is None:
        with lock:
            total_fails += 1
        return

    # Update statistics
    with lock:
        total_attempts += 1
        if game_result.get("winner"):
            total_wins += 1
            log_winner(game_result)
            if debug_mode:
                print(Fore.GREEN + "Winner logged!" + Style.RESET_ALL)
        else:
            if debug_mode:
                print(Fore.YELLOW + "No winner this time." + Style.RESET_ALL)

def display_stats():
    global total_attempts, total_wins, total_fails, start_time
    while True:
        with lock:
            time.sleep(1)
            elapsed_time = time.time() - start_time
            win_rate = (total_wins / total_attempts) * 100 if total_attempts > 0 else 0
            fail_rate = (total_fails / total_attempts) * 100 if total_attempts > 0 else 0
            speed = total_attempts / elapsed_time if elapsed_time > 0 else 0
            print(Fore.MAGENTA + f"Total Attempts: {total_attempts}, Total Wins: {total_wins}, Win Rate: {win_rate:.2f}%, Fail Rate: {fail_rate:.2f}%, Speed: {speed:.2f} attempts/sec" + Style.RESET_ALL)
def main():
    # Use threading to run multiple game plays in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Start a thread for displaying stats
        executor.submit(display_stats)
        # Start threads for playing the game
        futures = [executor.submit(play_game) for _ in range(1000)]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
