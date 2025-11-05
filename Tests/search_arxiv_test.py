import arxiv
import pytz
from datetime import datetime, time, timedelta

def get_submission_window():
    """
    Calculates the start and end UTC timestamps for the *current*
    arXiv submission window, based on the 14:00 EDT cutoff and
    20:00 EDT announcement time.
    """

    try:
        tz_edt = pytz.timezone('America/New_York')
    except pytz.UnknownTimeZoneError:
        print("Error: 'pytz' library not found. Please run: pip install pytz")
        return None, None

    # --- Define arXiv's key times in their timezone ---
    SUBMISSION_CUTOFF = time(14, 0, 0)
    ANNOUNCEMENT_TIME = time(20, 0, 0) # 8 PM EDT
    # ---

    now_in_edt = datetime.now(tz_edt)

    # 1. Determine which announcement we are "for".
    # This is the date of the window we are targeting.
    target_announcement_date = now_in_edt.date()
    weekday = target_announcement_date.weekday() # Mon=0, Sun=6
    print(weekday)

    start_date = None
    end_date = None


    if weekday in [1, 2, 3] and now_in_edt.time() > ANNOUNCEMENT_TIME: # Monday to Thursday after 8 PM
        # We want todays's listings.
        start_date = target_announcement_date - timedelta(days=1)
        end_date = target_announcement_date
    elif weekday == [1,2,3,4] and now_in_edt.time() < ANNOUNCEMENT_TIME: # Tuesday to Friday before 8 PM
        # We want yesterday's listings.
        start_date = target_announcement_date - timedelta(days=2)
        end_date = target_announcement_date - timedelta(days=1)
    elif weekday == 4 and now_in_edt.time() > ANNOUNCEMENT_TIME: # Friday after 8 PM
        # We want Thursday's listings.
        start_date = target_announcement_date - timedelta(days=2)
        end_date = target_announcement_date - timedelta(days=1)
    elif weekday == 5: # Saturday
        # We want Thursday's listings.
        start_date = target_announcement_date - timedelta(days=3)
        end_date = target_announcement_date - timedelta(days=2)
    elif weekday == 6 and now_in_edt.time() < ANNOUNCEMENT_TIME: # Sunday before 8 PM
        # We want Thursday's listings.
        start_date = target_announcement_date - timedelta(days=4)
        end_date = target_announcement_date - timedelta(days=3)
    elif weekday == 6 and now_in_edt.time() > ANNOUNCEMENT_TIME: # Sunday after 8 PM
        # We want Friday's listings.
        start_date = target_announcement_date - timedelta(days=3)
        end_date = target_announcement_date - timedelta(days=2)
    elif weekday == 0 and now_in_edt.time() < ANNOUNCEMENT_TIME: # Monday before 8 PM
        # We want Friday's listings.
        start_date = target_announcement_date - timedelta(days=4)
        end_date = target_announcement_date - timedelta(days=3)
    elif weekday == 0 and now_in_edt.time() > ANNOUNCEMENT_TIME: # Monday after 8 PM
        # We want Monday's listings.
        start_date = target_announcement_date - timedelta(days=3)
        end_date = target_announcement_date
    else:
        raise ValueError("Unhandled case in submission window calculation.")
    
    # Set time for start and end dates at 14:00 EDT
    start_time_edt = tz_edt.localize(datetime.combine(start_date, SUBMISSION_CUTOFF))
    end_time_edt = tz_edt.localize(datetime.combine(end_date, SUBMISSION_CUTOFF))

    # Convert to UTC, as arXiv API results are in UTC
    start_time_utc = start_time_edt.astimezone(pytz.utc)
    end_time_utc = end_time_edt.astimezone(pytz.utc)

    return start_time_utc, end_time_utc


# 1. Get the submission window
start_utc, end_utc = get_submission_window()

if start_utc is None:
    exit()

client = arxiv.Client()
search = arxiv.Search(
  query = "cat:quant-ph",
  max_results = 200, # Get a larger batch to be safe
  sort_by = arxiv.SortCriterion.SubmittedDate, # Use SubmittedDate
  sort_order = arxiv.SortOrder.Descending
)

print(f"--- Fetching listings for window ---")
print(f"Start: {start_utc}")
print(f"End:   {end_utc}\n")

found_one = False
try:
    for result in client.results(search):
        
        # result.updated is the submission time in UTC
        submission_time_utc = result.updated
        
        # Stop if we've gone past the start of our window
        if submission_time_utc < start_utc:
            break
        
        # Check if the paper is *within* our target window
        if start_utc <= submission_time_utc <= end_utc:
            print(f"[{submission_time_utc}] {result.title}")
            found_one = True

except arxiv.UnexpectedEmptyPageError:
    pass 
except Exception as e:
    print(f"An unexpected error occurred: {e}")

if not found_one:
    print(f"No new listings found in this submission window.")